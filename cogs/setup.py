# cogs/setup.py
# =====================================================================
# ─── INTERACTIVE SERVER SETUP WIZARD (Commercial Quality: MEE6 / Carl-bot)
#     Slash Command: /setup (Restricted to Administrators & Server Owner)
#     Prefix Command: +setup
#     Features:
#       - Role Select (admin_role, mod_role, member_role, muted_role, etc.)
#       - Channel Select (logs_channel, welcome_channel, tickets_channel, etc.)
#       - Auto-Create Missing Setup ("Auto-Create Missing" Button)
#       - Interactive Feature Toggles (welcome, auto_mod, logging, etc.)
# =====================================================================

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
from typing import Optional
import config_manager
from database.engine import execute, commit, query_one


ROLE_SPECS = [
    ("verified_role", "Verified", discord.Color.blue()),
    ("member_role", "Verified", discord.Color.blue()),
    ("unverified_role", "Unverified", discord.Color.light_grey()),
    ("staff_role", "Staff", discord.Color.gold()),
    ("muted_role", "Jail", discord.Color.dark_grey()),
    ("jail_role", "Jail", discord.Color.dark_grey()),
    ("verification_staff_role", "Verification Staff", discord.Color.green()),
]

CATEGORY_SPECS = [
    ("Welcome", "WELCOME"),
    ("Verification", "VERIFICATION"),
    ("Jail", "JAIL"),
    ("Staff", "STAFF"),
    ("Logs & Audit", "LOGS"),
    ("Voice", "VOICE"),
]

CHANNEL_SPECS = [
    ("Welcome", "welcome_channel", "welcome"),
    ("Verification", "verification_channel", "verification"),
    ("Verification", "verification_log_channel", "verify-log"),
    ("Jail", "jail_channel", "jail-chat"),
    ("Logs & Audit", "logs_channel", "audit-log"),
    ("Logs & Audit", "mod_logs_channel", "mod-log"),
    ("Staff", "staff_applications_channel", "staff-applications"),
    ("Staff", "staff_application_panel_channel", "apply-for-staff"),
    ("Voice", "vc_rank_channel", "vc-rank"),
]


class VerificationButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify Me", emoji="✅", style=discord.ButtonStyle.success, custom_id="setup:verify:button")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        if not isinstance(member, discord.Member):
            return await interaction.response.send_message("Unable to verify in this context.", ephemeral=True)
        verified = config_manager.get_role(interaction.guild, "verified_role") or config_manager.get_role(interaction.guild, "member_role")
        unverified = config_manager.get_role(interaction.guild, "unverified_role")
        if verified is None:
            return await interaction.response.send_message("Verification role is not configured. Ask an administrator to run `/setup`.", ephemeral=True)
        if verified in member.roles:
            return await interaction.response.send_message("You are already verified.", ephemeral=True)
        try:
            await member.add_roles(verified, reason="Self-service verification")
            if unverified and unverified in member.roles:
                await member.remove_roles(unverified, reason="Self-service verification")
        except discord.Forbidden:
            return await interaction.response.send_message("I cannot update your roles. Please contact staff.", ephemeral=True)
        except discord.HTTPException as exc:
            return await interaction.response.send_message(f"Discord rejected the role update: {exc.text}", ephemeral=True)
        await interaction.response.send_message("✅ You have been verified.", ephemeral=True)


async def reconcile_server(guild: discord.Guild) -> dict:
    """Idempotently create or reuse all core setup objects and persist IDs."""
    report = {
        "roles_created": [], "roles_reused": [],
        "categories_created": [], "categories_reused": [],
        "channels_created": [], "channels_reused": [],
        "messages_created": [], "messages_reused": [],
        "skipped": [],
    }
    cfg = config_manager.get_guild_config(guild)
    roles = cfg.setdefault("roles", {})
    channels = cfg.setdefault("channels", {})

    category_cache = {}
    category_keys = {
        "Welcome": "welcome_category",
        "Verification": "verification_category",
        "Jail": "jail_category",
        "Staff": "staff_category",
        "Logs & Audit": "logs_category",
        "Voice": "voice_category",
    }
    for display_name, key in CATEGORY_SPECS:
        names = {display_name, display_name.lower(), key}
        category = next((c for c in guild.categories if c.name.lower().strip() in {n.lower() for n in names}), None)
        if category:
            category_cache[key] = category
            category_cache[display_name] = category
            config_manager.set_category(guild.id, category_keys[display_name], category.id)
            report["categories_reused"].append(category.name)
            continue
        try:
            category = await guild.create_category(display_name, reason="Self-healing /setup reconciliation")
            category_cache[key] = category
            category_cache[display_name] = category
            config_manager.set_category(guild.id, category_keys[display_name], category.id)
            report["categories_created"].append(category.name)
            await asyncio.sleep(0.2)
        except discord.HTTPException as exc:
            report["skipped"].append(f"Category {display_name}: {exc}")

    for key, name, color in ROLE_SPECS:
        configured_id = roles.get(key)
        role = guild.get_role(configured_id) if configured_id else None
        if role is None:
            role = discord.utils.get(guild.roles, name=name)
        if role:
            config_manager.set_role(guild.id, key, role.id)
            report["roles_reused"].append(name)
            if key == "verification_staff_role":
                try:
                    combined = discord.Permissions(
                        role.permissions.value
                        | discord.Permissions(manage_roles=True, view_audit_log=True).value
                    )
                    await role.edit(
                        permissions=combined,
                        reason="Configure verification staff permissions",
                    )
                except discord.HTTPException:
                    pass
            continue
        try:
            role = await guild.create_role(
                name=name,
                color=color,
                reason="Self-healing /setup reconciliation",
                hoist=key in {"staff_role", "verification_staff_role", "jail_role", "muted_role"},
            )
            config_manager.set_role(guild.id, key, role.id)
            report["roles_created"].append(name)
            if key == "verification_staff_role":
                try:
                    combined = discord.Permissions(
                        role.permissions.value
                        | discord.Permissions(manage_roles=True, view_audit_log=True).value
                    )
                    await role.edit(
                        permissions=combined,
                        reason="Configure verification staff permissions",
                    )
                except discord.HTTPException:
                    pass
            await asyncio.sleep(0.2)
        except discord.HTTPException as exc:
            report["skipped"].append(f"Role {name}: {exc}")

    for category_name, key, name in CHANNEL_SPECS:
        category = category_cache.get(category_name)
        configured_id = channels.get(key)
        channel = guild.get_channel(configured_id) if configured_id else None
        if channel is not None and not isinstance(channel, discord.TextChannel):
            channel = None
        if channel is None:
            channel = discord.utils.get(guild.text_channels, name=name)
        if channel:
            config_manager.set_channel(guild.id, key, channel.id)
            report["channels_reused"].append(channel.name)
            if category is not None and isinstance(channel, discord.TextChannel) and channel.category_id != category.id:
                try:
                    await channel.edit(category=category, reason="Reconcile channel category")
                except discord.HTTPException as exc:
                    report["skipped"].append(f"Move Channel #{channel.name}: {exc}")
            continue
        try:
            channel = await guild.create_text_channel(
                name=name,
                category=category,
                reason="Self-healing /setup reconciliation",
            )
            config_manager.set_channel(guild.id, key, channel.id)
            report["channels_created"].append(channel.name)
            await asyncio.sleep(0.2)
        except discord.HTTPException as exc:
            report["skipped"].append(f"Channel #{name}: {exc}")

    voice_category = category_cache.get("Voice")
    voice_channel_id = channels.get("voice_lounge_channel")
    voice_channel = guild.get_channel(voice_channel_id) if voice_channel_id else None
    if voice_channel is not None and not isinstance(voice_channel, discord.VoiceChannel):
        voice_channel = None
    if voice_channel is None:
        voice_channel = discord.utils.get(guild.voice_channels, name="General Voice")
    if voice_channel:
        config_manager.set_channel(guild.id, "voice_lounge_channel", voice_channel.id)
        report["channels_reused"].append(voice_channel.name)
        if voice_category is not None and voice_channel.category_id != voice_category.id:
            try:
                await voice_channel.edit(category=voice_category, reason="Reconcile voice channel category")
            except discord.HTTPException as exc:
                report["skipped"].append(f"Move Voice Channel {voice_channel.name}: {exc}")
    else:
        try:
            voice_channel = await guild.create_voice_channel(
                "General Voice",
                category=voice_category,
                reason="Self-healing /setup reconciliation",
            )
            config_manager.set_channel(guild.id, "voice_lounge_channel", voice_channel.id)
            report["channels_created"].append(voice_channel.name)
        except discord.HTTPException as exc:
            report["skipped"].append(f"Voice Channel General Voice: {exc}")

    # Reconcile standard verification and jail bindings.
    verified = config_manager.get_role(guild, "verified_role") or config_manager.get_role(guild, "member_role")
    jail = config_manager.get_role(guild, "jail_role") or config_manager.get_role(guild, "muted_role")
    unverified = config_manager.get_role(guild, "unverified_role")
    if verified:
        config_manager.set_role(guild.id, "member_role", verified.id)
    if jail:
        config_manager.set_role(guild.id, "muted_role", jail.id)
    if unverified:
        for ch_key in ("verification_channel", "welcome_channel"):
            ch = config_manager.get_channel(guild, ch_key)
            if ch:
                try:
                    await ch.set_permissions(unverified, view_channel=True, send_messages=False)
                except discord.HTTPException:
                    pass

    verification_channel = config_manager.get_channel(guild, "verification_channel")
    if verification_channel:
        verification_message = None
        try:
            async for message in verification_channel.history(limit=20):
                if message.author.id == guild.me.id and message.embeds:
                    if message.embeds[0].title == "✅ Server Verification":
                        verification_message = message
                        break
        except discord.HTTPException:
            pass
        embed = discord.Embed(
            title="✅ Server Verification",
            description="Press **Verify Me** to receive the Verified role.",
            color=discord.Color.green(),
        )
        view = VerificationButtonView()
        try:
            if verification_message:
                await verification_message.edit(embed=embed, view=view)
                report["messages_reused"] = ["Verification panel"]
            else:
                await verification_channel.send(embed=embed, view=view)
                report["messages_created"] = ["Verification panel"]
        except discord.Forbidden as exc:
            report["skipped"].append(f"Verification panel: {exc}")

    ladder_thresholds = list(range(1, 11))
    ladder = []
    for level, threshold in enumerate(ladder_thresholds, start=1):
        role_name = f"VC Level {level}"
        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            try:
                role = await guild.create_role(
                    name=role_name,
                    color=discord.Color.from_rgb(88, 101, 242),
                    hoist=False,
                    reason="Voice rank ladder setup",
                )
                report["roles_created"].append(role_name)
            except discord.HTTPException as exc:
                report["skipped"].append(f"Rank role {role_name}: {exc}")
                continue
        else:
            report["roles_reused"].append(role_name)
        ladder.append({"threshold": threshold, "role_id": role.id, "name": role_name})
    execute(
        "INSERT INTO vc_rank_config (guild_id, ladder_json) VALUES (?, ?) "
        "ON CONFLICT(guild_id) DO UPDATE SET ladder_json=excluded.ladder_json",
        (guild.id, json.dumps(ladder)),
    )
    commit()

    await config_manager.save_configs_async()
    return report


def build_main_setup_embed(guild: discord.Guild) -> discord.Embed:
    """Constructs the high-level dashboard embed showing the server's current configuration."""
    cfg = config_manager.get_guild_config(guild)
    roles = cfg.get("roles", {})
    channels = cfg.get("channels", {})
    features = cfg.get("features", {})

    def role_val(key):
        rid = roles.get(key)
        return f"<@&{rid}>" if rid and guild.get_role(rid) else "`Not Set`"

    def ch_val(key):
        cid = channels.get(key)
        return f"<#{cid}>" if cid and guild.get_channel(cid) else "`Not Set`"

    def feat_val(key):
        return "✅ `Enabled`" if features.get(key) else "❌ `Disabled`"

    embed = discord.Embed(
        title=f"⚙️ {guild.name} — Server Control Panel",
        description=(
            "Welcome to the commercial setup wizard. Customize roles, channels, "
            "and toggle server modules dynamically without hardcoded files.\n\n"
            "Use the interactive menu buttons below to configure your server."
        ),
        color=discord.Color.from_rgb(88, 101, 242),
        timestamp=discord.utils.utcnow(),
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    # 🎭 Roles Section
    roles_text = (
        f"👑 **Admin Role:** {role_val('admin_role')}\n"
        f"🛡️ **Mod Role:** {role_val('mod_role')}\n"
        f"💚 **Helper Role:** {role_val('helper_role')}\n"
        f"👤 **Member Role:** {role_val('member_role')}\n"
        f"🔒 **Muted / Jail Role:** {role_val('muted_role')}\n"
        f"⏳ **Unverified Role:** {role_val('unverified_role')}"
    )
    embed.add_field(name="🎭 Role Bindings", value=roles_text, inline=True)

    # 📁 Channels Section
    channels_text = (
        f"📜 **Logs Channel:** {ch_val('logs_channel')}\n"
        f"🚨 **Mod Logs:** {ch_val('mod_logs_channel')}\n"
        f"👋 **Welcome Channel:** {ch_val('welcome_channel')}\n"
        f"🚪 **Leaves Channel:** {ch_val('leaves_channel')}\n"
        f"🎫 **Tickets Channel:** {ch_val('tickets_channel')}\n"
        f"🎰 **Casino Channel:** {ch_val('casino_channel')}"
    )
    embed.add_field(name="📁 Channel Bindings", value=channels_text, inline=True)

    # ⚡ Feature Toggles Section
    features_text = (
        f"👋 **Welcome System:** {feat_val('welcome')}\n"
        f"📨 **Welcome DM:** {feat_val('welcome_dm')}\n"
        f"🏷️ **Auto-Role on Join:** {feat_val('auto_role')}\n"
        f"🛡️ **Auto-Moderation:** {feat_val('auto_mod')}\n"
        f"📜 **Audit Logging:** {feat_val('logging')}\n"
        f"🎫 **Ticket System:** {feat_val('tickets')}\n"
        f"💰 **Economy:** {feat_val('economy')}\n"
        f"⭐ **Levels & XP:** {feat_val('levels')}"
    )
    embed.add_field(name="⚡ Active Features", value=features_text, inline=False)

    embed.set_footer(
        text=f"Server ID: {guild.id} • Managed by {guild.me.display_name}",
        icon_url=guild.me.display_avatar.url,
    )
    return embed


# ═══════════════════════════════════════════════════════════════════
# ─── ROLE SELECT VIEW
# ═══════════════════════════════════════════════════════════════════

class RolesSelectView(discord.ui.View):
    def __init__(self, author: discord.Member, target_role_key: str, role_title: str):
        super().__init__(timeout=180)
        self.author = author
        self.target_role_key = target_role_key
        self.role_title = role_title

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ This setup session is not yours!", ephemeral=True)
            return False
        return True

    @discord.ui.select(cls=discord.ui.RoleSelect, placeholder="Select role from list...", max_values=1)
    async def on_role_selected(self, interaction: discord.Interaction, select: discord.ui.RoleSelect):
        selected_role = select.values[0]
        config_manager.set_role(interaction.guild_id, self.target_role_key, selected_role.id)
        
        embed = build_main_setup_embed(interaction.guild)
        view = SetupMainView(self.author)
        await interaction.response.edit_message(
            content=f"✅ Updated **{self.role_title}** to {selected_role.mention}!",
            embed=embed,
            view=view,
        )

    @discord.ui.button(label="Clear Role", style=discord.ButtonStyle.secondary, row=1)
    async def on_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        config_manager.set_role(interaction.guild_id, self.target_role_key, None)
        embed = build_main_setup_embed(interaction.guild)
        view = SetupMainView(self.author)
        await interaction.response.edit_message(
            content=f"🗑️ Cleared binding for **{self.role_title}**.",
            embed=embed,
            view=view,
        )

    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.gray, row=1)
    async def on_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = build_main_setup_embed(interaction.guild)
        view = SetupMainView(self.author)
        await interaction.response.edit_message(content=None, embed=embed, view=view)


class RoleCategorySelect(discord.ui.Select):
    def __init__(self, author: discord.Member):
        self.author = author
        options = [
            discord.SelectOption(label="Admin Role", value="admin_role", emoji="👑", description="Set main server administrator role"),
            discord.SelectOption(label="Mod Role", value="mod_role", emoji="🛡️", description="Set moderator role for timeouts & kicks"),
            discord.SelectOption(label="Helper Role", value="helper_role", emoji="💚", description="Set helper / junior staff role"),
            discord.SelectOption(label="Member Role", value="member_role", emoji="👤", description="Set verified / general member role"),
            discord.SelectOption(label="Muted / Jail Role", value="muted_role", emoji="🔒", description="Set jail / muted quarantine role"),
            discord.SelectOption(label="Unverified Role", value="unverified_role", emoji="⏳", description="Set pending / unverified role"),
        ]
        super().__init__(placeholder="Choose role function to configure...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        chosen_key = self.values[0]
        label = next((o.label for o in self.options if o.value == chosen_key), chosen_key)
        view = RolesSelectView(self.author, chosen_key, label)
        await interaction.response.edit_message(
            content=f"👉 Select the Discord role to assign as **{label}**:",
            embed=None,
            view=view,
        )


# ═══════════════════════════════════════════════════════════════════
# ─── CHANNEL SELECT VIEW
# ═══════════════════════════════════════════════════════════════════

class ChannelsSelectView(discord.ui.View):
    def __init__(self, author: discord.Member, target_channel_key: str, channel_title: str):
        super().__init__(timeout=180)
        self.author = author
        self.target_channel_key = target_channel_key
        self.channel_title = channel_title

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ This setup session is not yours!", ephemeral=True)
            return False
        return True

    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Select text channel...", channel_types=[discord.ChannelType.text], max_values=1)
    async def on_channel_selected(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        selected_ch = select.values[0]
        config_manager.set_channel(interaction.guild_id, self.target_channel_key, selected_ch.id)
        
        embed = build_main_setup_embed(interaction.guild)
        view = SetupMainView(self.author)
        await interaction.response.edit_message(
            content=f"✅ Updated **{self.channel_title}** to {selected_ch.mention}!",
            embed=embed,
            view=view,
        )

    @discord.ui.button(label="Clear Channel", style=discord.ButtonStyle.secondary, row=1)
    async def on_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        config_manager.set_channel(interaction.guild_id, self.target_channel_key, None)
        embed = build_main_setup_embed(interaction.guild)
        view = SetupMainView(self.author)
        await interaction.response.edit_message(
            content=f"🗑️ Cleared binding for **{self.channel_title}**.",
            embed=embed,
            view=view,
        )

    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.gray, row=1)
    async def on_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = build_main_setup_embed(interaction.guild)
        view = SetupMainView(self.author)
        await interaction.response.edit_message(content=None, embed=embed, view=view)


class ChannelCategorySelect(discord.ui.Select):
    def __init__(self, author: discord.Member):
        self.author = author
        options = [
            discord.SelectOption(label="Logs Channel", value="logs_channel", emoji="📜", description="General audit log channel"),
            discord.SelectOption(label="Mod Logs Channel", value="mod_logs_channel", emoji="🚨", description="Moderation strikes, kicks & bans"),
            discord.SelectOption(label="Welcome Channel", value="welcome_channel", emoji="👋", description="Where new members are greeted"),
            discord.SelectOption(label="Leaves Channel", value="leaves_channel", emoji="🚪", description="Member leave notifications"),
            discord.SelectOption(label="Tickets Channel", value="tickets_channel", emoji="🎫", description="Ticket support panel"),
            discord.SelectOption(label="Casino Channel", value="casino_channel", emoji="🎰", description="Gambling and casino channel"),
        ]
        super().__init__(placeholder="Choose channel function to configure...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        chosen_key = self.values[0]
        label = next((o.label for o in self.options if o.value == chosen_key), chosen_key)
        view = ChannelsSelectView(self.author, chosen_key, label)
        await interaction.response.edit_message(
            content=f"👉 Select the Text Channel to assign as **{label}**:",
            embed=None,
            view=view,
        )


# ═══════════════════════════════════════════════════════════════════
# ─── FEATURES TOGGLE VIEW
# ═══════════════════════════════════════════════════════════════════

class FeaturesToggleSelect(discord.ui.Select):
    def __init__(self, author: discord.Member, guild: discord.Guild):
        self.author = author
        cfg = config_manager.get_guild_config(guild)
        feats = cfg.get("features", {})

        options = [
            discord.SelectOption(
                label="Welcome Messages",
                value="welcome",
                emoji="👋",
                description=f"Currently: {'ENABLED' if feats.get('welcome') else 'DISABLED'}",
            ),
            discord.SelectOption(
                label="Welcome Direct Message (DM)",
                value="welcome_dm",
                emoji="📨",
                description=f"Currently: {'ENABLED' if feats.get('welcome_dm') else 'DISABLED'}",
            ),
            discord.SelectOption(
                label="Auto-Role on Join",
                value="auto_role",
                emoji="🏷️",
                description=f"Currently: {'ENABLED' if feats.get('auto_role') else 'DISABLED'}",
            ),
            discord.SelectOption(
                label="Auto-Moderation",
                value="auto_mod",
                emoji="🛡️",
                description=f"Currently: {'ENABLED' if feats.get('auto_mod') else 'DISABLED'}",
            ),
            discord.SelectOption(
                label="Audit Logging",
                value="logging",
                emoji="📜",
                description=f"Currently: {'ENABLED' if feats.get('logging') else 'DISABLED'}",
            ),
            discord.SelectOption(
                label="Ticket Support",
                value="tickets",
                emoji="🎫",
                description=f"Currently: {'ENABLED' if feats.get('tickets') else 'DISABLED'}",
            ),
            discord.SelectOption(
                label="Economy System",
                value="economy",
                emoji="💰",
                description=f"Currently: {'ENABLED' if feats.get('economy') else 'DISABLED'}",
            ),
            discord.SelectOption(
                label="Levels & Rank Cards",
                value="levels",
                emoji="⭐",
                description=f"Currently: {'ENABLED' if feats.get('levels') else 'DISABLED'}",
            ),
        ]
        super().__init__(placeholder="Select a module to toggle ON / OFF...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        feature_key = self.values[0]
        current = config_manager.is_feature_enabled(interaction.guild_id, feature_key)
        new_state = not current
        config_manager.set_feature_toggle(interaction.guild_id, feature_key, new_state)

        embed = build_main_setup_embed(interaction.guild)
        view = FeaturesSubView(self.author, interaction.guild)
        state_str = "✅ **ENABLED**" if new_state else "❌ **DISABLED**"
        await interaction.response.edit_message(
            content=f"Toggled `{feature_key}` → {state_str}",
            embed=embed,
            view=view,
        )


class FeaturesSubView(discord.ui.View):
    def __init__(self, author: discord.Member, guild: discord.Guild):
        super().__init__(timeout=180)
        self.author = author
        self.add_item(FeaturesToggleSelect(author, guild))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ This setup session is not yours!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="🔙 Back to Dashboard", style=discord.ButtonStyle.gray, row=2)
    async def on_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = build_main_setup_embed(interaction.guild)
        view = SetupMainView(self.author)
        await interaction.response.edit_message(content=None, embed=embed, view=view)


# ═══════════════════════════════════════════════════════════════════
# ─── MAIN SETUP VIEW (DASHBOARD)
# ═══════════════════════════════════════════════════════════════════

class ConfirmReconcileView(discord.ui.View):
    def __init__(self, author: discord.Member):
        super().__init__(timeout=180)
        self.author = author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("This setup session is not yours.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirm Reconcile", emoji="✅", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        report = await reconcile_server(interaction.guild)
        lines = [
            f"✅ Created roles: {len(report['roles_created'])}",
            f"♻️ Reused roles: {len(report['roles_reused'])}",
            f"✅ Created categories: {len(report['categories_created'])}",
            f"♻️ Reused categories: {len(report['categories_reused'])}",
            f"✅ Created channels: {len(report['channels_created'])}",
            f"♻️ Reused channels: {len(report['channels_reused'])}",
            f"✅ Created messages: {len(report['messages_created'])}",
            f"♻️ Reused messages: {len(report['messages_reused'])}",
        ]
        for key in ("roles_created", "roles_reused", "categories_created", "categories_reused", "channels_created", "channels_reused", "messages_created", "messages_reused"):
            if report[key]:
                lines.append(f"{key.replace('_', ' ').title()}: {', '.join(report[key][:10])}")
        if report["skipped"]:
            lines.append("⚠️ Skipped:")
            lines.extend(f"- {item}" for item in report["skipped"][:10])
        await interaction.followup.send("\n".join(lines), ephemeral=True)

    @discord.ui.button(label="Cancel", emoji="✖️", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Setup reconciliation cancelled.", embed=None, view=None)

class SetupMainView(discord.ui.View):
    def __init__(self, author: discord.Member):
        super().__init__(timeout=300)
        self.author = author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Had l-menu machi dyalek! Run `/setup` yourself.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Configure Roles", emoji="🎭", style=discord.ButtonStyle.primary, row=0)
    async def btn_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View(timeout=180)
        view.add_item(RoleCategorySelect(self.author))
        view.add_item(discord.ui.Button(label="🔙 Back", style=discord.ButtonStyle.gray, custom_id="back_to_main"))

        async def back_callback(it: discord.Interaction):
            main_v = SetupMainView(self.author)
            await it.response.edit_message(content=None, embed=build_main_setup_embed(it.guild), view=main_v)
        
        view.children[-1].callback = back_callback
        await interaction.response.edit_message(
            content="👇 Select which role function you want to bind:",
            embed=None,
            view=view,
        )

    @discord.ui.button(label="Configure Channels", emoji="📁", style=discord.ButtonStyle.primary, row=0)
    async def btn_channels(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View(timeout=180)
        view.add_item(ChannelCategorySelect(self.author))
        view.add_item(discord.ui.Button(label="🔙 Back", style=discord.ButtonStyle.gray, custom_id="back_to_main_ch"))

        async def back_callback(it: discord.Interaction):
            main_v = SetupMainView(self.author)
            await it.response.edit_message(content=None, embed=build_main_setup_embed(it.guild), view=main_v)
        
        view.children[-1].callback = back_callback
        await interaction.response.edit_message(
            content="👇 Select which channel function you want to bind:",
            embed=None,
            view=view,
        )

    @discord.ui.button(label="Toggle Features", emoji="⚡", style=discord.ButtonStyle.secondary, row=1)
    async def btn_features(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = FeaturesSubView(self.author, interaction.guild)
        await interaction.response.edit_message(
            content="👇 Choose a module from the dropdown below to flip its status:",
            embed=build_main_setup_embed(interaction.guild),
            view=view,
        )

    @discord.ui.button(label="Auto-Create Missing", emoji="🪄", style=discord.ButtonStyle.success, row=1)
    async def btn_auto_create(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Auto-Create Missing Setup:
        Automatically creates missing standard channels and roles with appropriate permissions,
        and saves their IDs directly to config_manager.
        """
        await interaction.response.edit_message(
            content="⚠️ Confirm server reconciliation?\nThis will create or reuse missing categories, channels, roles, rank roles, and setup panels.",
            embed=None,
            view=ConfirmReconcileView(self.author),
        )
        return
        guild = interaction.guild
        bot_member = guild.me

        # Pre-check bot permissions
        missing_perms = []
        if not bot_member.guild_permissions.manage_roles:
            missing_perms.append("Manage Roles")
        if not bot_member.guild_permissions.manage_channels:
            missing_perms.append("Manage Channels")

        if missing_perms:
            return await interaction.response.send_message(
                f"❌ Bot is missing required permissions to auto-create: **{', '.join(missing_perms)}**.\n"
                "Please grant these permissions in Server Settings > Roles and try again.",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=True)

        cfg = config_manager.get_guild_config(guild)
        roles = cfg.get("roles", {})
        channels = cfg.get("channels", {})

        created_roles = []
        created_channels = []

        # 1. Check and Auto-Create Roles
        role_specs = [
            ("admin_role", "🛡️ Administrator", discord.Color.red(), True),
            ("mod_role", "🔨 Moderator", discord.Color.orange(), True),
            ("helper_role", "🗡️ Helper", discord.Color.green(), True),
            ("member_role", "Verified ✓", discord.Color.blue(), False),
            ("muted_role", "🔒 Jailed / Muted", discord.Color.dark_grey(), False),
            ("unverified_role", "Unverified", discord.Color.light_grey(), False),
        ]

        for key, name, color, hoist in role_specs:
            current_id = roles.get(key)
            if not current_id or not guild.get_role(current_id):
                # Search if already exists by name
                existing = discord.utils.get(guild.roles, name=name)
                if existing:
                    config_manager.set_role(guild.id, key, existing.id)
                else:
                    try:
                        new_r = await guild.create_role(
                            name=name,
                            color=color,
                            hoist=hoist,
                            reason="Commercial /setup Auto-Creation Wizard",
                        )
                        config_manager.set_role(guild.id, key, new_r.id)
                        created_roles.append(new_r.name)
                        await asyncio.sleep(0.3)
                    except discord.Forbidden:
                        pass

        # 2. Check and Auto-Create Channels
        # First ensure a Server Logs category exists
        cat_logs = discord.utils.get(guild.categories, name="📊 LOGS & AUDIT")
        if not cat_logs:
            try:
                cat_logs = await guild.create_category(
                    name="📊 LOGS & AUDIT",
                    reason="/setup Auto-Create Logs Category",
                )
            except discord.Forbidden:
                cat_logs = None

        channel_specs = [
            ("logs_channel", "📜-audit-logs", cat_logs),
            ("mod_logs_channel", "🚨-mod-logs", cat_logs),
            ("welcome_channel", "👋-welcome", None),
            ("leaves_channel", "🚪-leaves", None),
            ("tickets_channel", "🎫-tickets", None),
            ("casino_channel", "🎰-casino", None),
        ]

        for key, name, category in channel_specs:
            current_id = channels.get(key)
            if not current_id or not guild.get_channel(current_id):
                existing = discord.utils.get(guild.text_channels, name=name)
                if existing:
                    config_manager.set_channel(guild.id, key, existing.id)
                else:
                    try:
                        new_ch = await guild.create_text_channel(
                            name=name,
                            category=category,
                            reason="Commercial /setup Auto-Creation Wizard",
                        )
                        config_manager.set_channel(guild.id, key, new_ch.id)
                        created_channels.append(new_ch.name)
                        await asyncio.sleep(0.3)
                    except discord.Forbidden:
                        pass

        summary_parts = []
        if created_roles:
            summary_parts.append(f"🎭 **Created Roles:** {', '.join(f'`{r}`' for r in created_roles)}")
        if created_channels:
            summary_parts.append(f"📁 **Created Channels:** {', '.join(f'`#{c}`' for c in created_channels)}")
        if not summary_parts:
            summary_text = "✨ All required roles and channels are already configured and present!"
        else:
            summary_text = "🪄 **Auto-Creation Complete!**\n" + "\n".join(summary_parts)

        updated_embed = build_main_setup_embed(guild)
        await interaction.followup.send(content=summary_text, embed=updated_embed, ephemeral=True)

    @discord.ui.button(label="Close Panel", emoji="✖️", style=discord.ButtonStyle.danger, row=1)
    async def btn_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()


# ═══════════════════════════════════════════════════════════════════
# ─── COG REGISTRATION
# ═══════════════════════════════════════════════════════════════════

class Setup(commands.Cog):
    """Modern Commercial-Grade Setup Wizard for Multi-Server Deployment"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(VerificationButtonView())

    @app_commands.command(
        name="setup",
        description="Interactive server configuration dashboard (Admin / Server Owner only)",
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_slash(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("❌ This command can only be used in a Discord server!", ephemeral=True)

        if not (interaction.user.guild_permissions.administrator or interaction.user.id == interaction.guild.owner_id):
            return await interaction.response.send_message("❌ You must be a Server Administrator or Owner to run `/setup`!", ephemeral=True)

        embed = build_main_setup_embed(interaction.guild)
        view = SetupMainView(interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @commands.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def setup_prefix(self, ctx: commands.Context):
        """+setup — Interactive commercial configuration wizard"""
        embed = build_main_setup_embed(ctx.guild)
        view = SetupMainView(ctx.author)
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Setup(bot))
