# cogs/logs.py
# ═══════════════════════════════════════════════════════════════════
# ─── LOGS — Split channels (kol haja f channel dyalha)
# ═══════════════════════════════════════════════════════════════════
import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import botconfig

INVITE_CACHE: dict[int, dict[str, int]] = {}


class Logs(commands.Cog):
    """Logs m9asmin 3la 7sab l-type"""

    def __init__(self, bot):
        self.bot = bot

    # ═══════════════════════════════════════════════════════════
    # ─── HELPERS
    # ═══════════════════════════════════════════════════════════
    def _channel(self, guild, key: str):
        # 1. First check per-server configured channel in config_manager
        try:
            import config_manager
            # Check moderation logs vs general logs
            if key in ("moderation", "kick", "ban", "timeout", "jail", "warn"):
                mod_ch = config_manager.get_channel(guild, "mod_logs_channel")
                if mod_ch:
                    return mod_ch
            gen_ch = config_manager.get_channel(guild, "logs_channel")
            if gen_ch:
                return gen_ch
        except Exception:
            pass

        # 2. Fallback to botconfig environment IDs
        cid = botconfig.CHANNEL_LOGS.get(key, 0)
        if not cid:
            return None
        return guild.get_channel(cid)

    async def _log(self, guild, key: str, embed: discord.Embed):
        if guild is None:
            return
        # Check per-server feature toggle
        try:
            import config_manager
            if not config_manager.is_feature_enabled(guild, "logging"):
                return
        except Exception:
            pass

        ch = self._channel(guild, key)
        if ch is None:
            return
        try:
            await ch.send(embed=embed)
        except Exception:
            pass

    async def _fetch_audit(self, guild, action, target_id=None, timeout=3.0):
        await asyncio.sleep(1.0)
        try:
            async for entry in guild.audit_logs(limit=10, action=action):
                if target_id is not None:
                    tgt = getattr(entry.target, "id", None)
                    if tgt != target_id:
                        continue
                return entry.user, entry.reason
        except Exception:
            return None, None
        return None, None

    def _mod_line(self, user, reason=None) -> str:
        parts = [f"par {user.mention}" if user else "par *??*"]
        if reason:
            parts.append(f"— `{reason}`")
        return " ".join(parts)

    # ═══════════════════════════════════════════════════════════
    # ─── INVITE CACHE
    # ═══════════════════════════════════════════════════════════
    async def _cache_invites(self, guild):
        try:
            invites = await guild.invites()
            INVITE_CACHE[guild.id] = {inv.code: inv.uses or 0 for inv in invites}
        except Exception:
            INVITE_CACHE[guild.id] = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self._cache_invites(guild)
        print(f"✅ Logs ready: {len(self.bot.guilds)} guilds")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self._cache_invites(guild)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        INVITE_CACHE.setdefault(invite.guild.id, {})[invite.code] = invite.uses or 0

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        if invite.guild and invite.guild.id in INVITE_CACHE:
            INVITE_CACHE[invite.guild.id].pop(invite.code, None)

    async def _find_inviter(self, guild):
        old = INVITE_CACHE.get(guild.id, {})
        try:
            new = await guild.invites()
        except Exception:
            return None, None
        inviter, code = None, None
        for inv in new:
            if old.get(inv.code, 0) < (inv.uses or 0):
                inviter, code = inv.inviter, inv.code
                break
        INVITE_CACHE[guild.id] = {inv.code: inv.uses or 0 for inv in new}
        return inviter, code

    # ═══════════════════════════════════════════════════════════
    # ─── MEMBER JOIN (b invite)
    # ═══════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_member_join(self, member):
        inviter, code = await self._find_inviter(member.guild)
        inv_line = (
            f"mn {inviter.mention} (`{code}`)" if inviter else "**bla invite**"
        )

        # Log dyal join (channel dyalha)
        embed = discord.Embed(
            title="📥 Member Joined",
            color=discord.Color.green(),
            timestamp=datetime.utcnow(),
        )
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        embed.add_field(name="👤 User", value=f"{member.mention}\n`{member.id}`", inline=False)
        embed.add_field(name="🔗 Invite", value=inv_line, inline=False)
        embed.add_field(name="📅 Account", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="👥 Members", value=f"`{member.guild.member_count}`", inline=True)
        await self._log(member.guild, "join", embed)

        # Same event f logs-member
        embed2 = discord.Embed(
            description=f"📥 **{member}** dkhel • {inv_line}",
            color=discord.Color.green(),
        )
        await self._log(member.guild, "member", embed2)

    # ═══════════════════════════════════════════════════════════
    # ─── MEMBER LEAVE / KICK / BAN
    # ═══════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        kicker, reason = await self._fetch_audit(
            member.guild, discord.AuditLogAction.kick, target_id=member.id
        )
        banner, _ = await self._fetch_audit(
            member.guild, discord.AuditLogAction.ban, target_id=member.id
        )
        if banner is not None:
            return

        if kicker:
            embed = discord.Embed(
                title="👢 Member Kicked",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow(),
            )
            embed.set_author(name=str(member), icon_url=member.display_avatar.url)
            embed.add_field(name="👤 User", value=f"{member.mention}\n`{member.id}`", inline=False)
            embed.add_field(name="👮 Mod", value=self._mod_line(kicker, reason), inline=False)
        else:
            embed = discord.Embed(
                title="📤 Member Left",
                color=discord.Color.red(),
                timestamp=datetime.utcnow(),
            )
            embed.set_author(name=str(member), icon_url=member.display_avatar.url)
            embed.add_field(name="👤 User", value=f"{member.mention}\n`{member.id}`", inline=False)

        embed.add_field(name="👥 Members", value=f"`{member.guild.member_count}`", inline=True)
        await self._log(member.guild, "member", embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        banner, reason = await self._fetch_audit(
            guild, discord.AuditLogAction.ban, target_id=user.id
        )
        embed = discord.Embed(
            title="🔨 Member Banned",
            color=discord.Color.dark_red(),
            timestamp=datetime.utcnow(),
        )
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        embed.add_field(name="👤 User", value=f"{user.mention}\n`{user.id}`", inline=False)
        embed.add_field(name="👮 Mod", value=self._mod_line(banner, reason), inline=False)
        await self._log(guild, "moderation", embed)

    # ═══════════════════════════════════════════════════════════
    # ─── ROLE ADD/REMOVE (channel dyalha!)
    # ═══════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles == after.roles:
            return

        added = [r for r in after.roles if r not in before.roles]
        removed = [r for r in before.roles if r not in after.roles]

        actor, reason = await self._fetch_audit(
            after.guild,
            discord.AuditLogAction.member_role_update,
            target_id=after.id,
        )
        mod_line = self._mod_line(actor, reason)

        for r in added:
            embed = discord.Embed(
                title="🎭 Role Added",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )
            embed.set_author(name=str(after), icon_url=after.display_avatar.url)
            embed.add_field(name="👤 User", value=f"{after.mention}\n`{after.id}`", inline=False)
            embed.add_field(name="➕ Role", value=r.mention, inline=False)
            embed.add_field(name="👮 By", value=mod_line, inline=False)
            await self._log(after.guild, "role", embed)

        for r in removed:
            embed = discord.Embed(
                title="🎭 Role Removed",
                color=discord.Color.red(),
                timestamp=datetime.utcnow(),
            )
            embed.set_author(name=str(after), icon_url=after.display_avatar.url)
            embed.add_field(name="👤 User", value=f"{after.mention}\n`{after.id}`", inline=False)
            embed.add_field(name="➖ Role", value=r.mention, inline=False)
            embed.add_field(name="👮 By", value=mod_line, inline=False)
            await self._log(after.guild, "role", embed)

    # ═══════════════════════════════════════════════════════════
    # ─── MESSAGE DELETE / EDIT
    # ═══════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return
        deleter, _ = await self._fetch_audit(
            message.guild,
            discord.AuditLogAction.message_delete,
            target_id=message.author.id,
            timeout=2.0,
        )
        by = f"par {deleter.mention}" if deleter and deleter.id != message.author.id else "par *sahbo*"
        content = (message.content or "*[empty/attachment]*")[:500]
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            description=f"> {content}",
            color=discord.Color.dark_red(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="👤 Author", value=message.author.mention, inline=True)
        embed.add_field(name="📍 Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="👮 By", value=by, inline=True)
        await self._log(message.guild, "message", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild:
            return
        if before.content == after.content:
            return
        embed = discord.Embed(
            title="📝 Message Edited",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="👤 Author", value=before.author.mention, inline=True)
        embed.add_field(name="📍 Channel", value=before.channel.mention, inline=True)
        embed.add_field(name="📄 Before", value=f"> {(before.content or '')[:400]}", inline=False)
        embed.add_field(name="📄 After", value=f"> {(after.content or '')[:400]}", inline=False)
        await self._log(before.guild, "message", embed)

    # ═══════════════════════════════════════════════════════════
    # ─── VOICE
    # ═══════════════════════════════════════════════════════════
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                description=f"🔊 **{member.name}** dkhel `{after.channel.name}`",
                color=discord.Color.green(),
            )
            await self._log(member.guild, "voice", embed)
            return

        if before.channel is not None and after.channel is None:
            embed = discord.Embed(
                description=f"🔇 **{member.name}** khrej mn `{before.channel.name}`",
                color=discord.Color.red(),
            )
            await self._log(member.guild, "voice", embed)
            return

        if before.channel != after.channel:
            embed = discord.Embed(
                description=f"🔀 **{member.name}** t7arek `{before.channel.name}` → `{after.channel.name}`",
                color=discord.Color.orange(),
            )
            await self._log(member.guild, "voice", embed)

    # ═══════════════════════════════════════════════════════════
    # ─── PUBLIC: called mn commands
    # ═══════════════════════════════════════════════════════════
    async def log_moderation(
        self, guild, action: str, target: discord.Member,
        mod: discord.Member, reason: str = "N/A"
    ):
        emoji = {
            "warn": "⚠️", "kick": "👢", "ban": "🔨",
            "timeout": "⏱️", "jail": "🔒", "unjail": "🔓",
            "unban": "✅", "untimeout": "🔓",
        }.get(action, "📝")
        embed = discord.Embed(
            title=f"{emoji} Moderation: {action.title()}",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow(),
        )
        embed.set_author(name=str(target), icon_url=target.display_avatar.url)
        embed.add_field(name="👤 Target", value=f"{target.mention}\n`{target.id}`", inline=False)
        embed.add_field(name="👮 Mod", value=mod.mention, inline=False)
        embed.add_field(name="📝 Reason", value=reason, inline=False)
        await self._log(guild, "moderation", embed)

    async def log_verification(
        self, guild, member: discord.Member, verify_type: str,
        staff: discord.Member, extra: str = None
    ):
        color = discord.Color.green() if verify_type == "vb" else discord.Color.pink()
        embed = discord.Embed(
            title=f"✅ Verified — {verify_type.upper()}",
            color=color,
            timestamp=datetime.utcnow(),
        )
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        embed.add_field(name="👤 User", value=f"{member.mention}\n`{member.id}`", inline=False)
        embed.add_field(name="✅ By", value=staff.mention, inline=False)
        if extra:
            embed.add_field(name="ℹ️ Info", value=extra[:1000], inline=False)
        await self._log(guild, "verification", embed)


async def setup(bot):
    await bot.add_cog(Logs(bot))