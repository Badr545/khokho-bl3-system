"""Persistent, database-backed self-role menus."""
import json
import discord
from discord import app_commands
from discord.ext import commands

from database.features_schema import execute_feat, commit_feat, query_feat_all, query_feat_one


class SelfRoleSelect(discord.ui.Select):
    def __init__(self, menu: dict):
        self.menu = menu
        options = menu["options"]
        mode = menu["selection_mode"]
        super().__init__(
            custom_id=f"selfrole-v2:{menu['message_id']}",
            placeholder="Choose self roles",
            min_values=0 if menu["allow_remove"] else 1,
            max_values=1 if mode == "single" else max(1, min(menu["max_roles"], len(options))),
            options=[
                discord.SelectOption(
                    label=item["label"][:100],
                    value=str(item["role_id"]),
                    emoji=item["emoji"] or None,
                    description=item.get("description", "")[:100] or None,
                )
                for item in options[:25]
            ],
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        if not isinstance(member, discord.Member):
            return await interaction.response.send_message("This menu can only be used in a server.", ephemeral=True)

        selected_ids = {int(value) for value in self.values}
        options = {int(item["role_id"]) for item in self.menu["options"]}
        to_add = []
        to_remove = []
        failed = []

        if self.menu["selection_mode"] == "single":
            for role_id in options:
                role = guild.get_role(role_id)
                if role is None:
                    continue
                if role_id in selected_ids:
                    to_add.append(role)
                elif self.menu["allow_remove"] and role in member.roles:
                    to_remove.append(role)
        else:
            for role_id in options:
                role = guild.get_role(role_id)
                if role is None:
                    failed.append(str(role_id))
                elif role_id in selected_ids and role not in member.roles:
                    to_add.append(role)
                elif self.menu["allow_remove"] and role_id not in selected_ids and role in member.roles:
                    to_remove.append(role)

        try:
            if to_add:
                await member.add_roles(*to_add, reason="Self-role menu")
            if to_remove:
                await member.remove_roles(*to_remove, reason="Self-role menu")
        except discord.Forbidden:
            failed.extend(role.name for role in to_add + to_remove)
        except discord.HTTPException as exc:
            await interaction.response.send_message(f"Discord role update failed: {exc.text}", ephemeral=True)
            return

        lines = []
        if to_add:
            lines.append("✅ Added: " + ", ".join(role.mention for role in to_add))
        if to_remove:
            lines.append("❌ Removed: " + ", ".join(role.mention for role in to_remove))
        if failed:
            lines.append("⚠️ Failed: " + ", ".join(failed))
        await interaction.response.send_message("\n".join(lines) or "No role changes were needed.", ephemeral=True)


class SelfRoleView(discord.ui.View):
    def __init__(self, menu: dict):
        super().__init__(timeout=None)
        self.add_item(SelfRoleSelect(menu))


class SelfRoleModal(discord.ui.Modal, title="Create Self-Role Menu"):
    channel_id = discord.ui.TextInput(label="Target channel ID", required=True, max_length=25)
    title_field = discord.ui.TextInput(label="Embed title", required=True, max_length=100)
    description_field = discord.ui.TextInput(label="Embed description", required=True, style=discord.TextStyle.paragraph, max_length=1000)
    color_field = discord.ui.TextInput(label="Color (hex)", required=False, placeholder="5865F2", max_length=7)
    image_field = discord.ui.TextInput(label="Optional image URL", required=False, max_length=300)
    options_field = discord.ui.TextInput(
        label="Roles: role_id|label|emoji (one per line)",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=4000,
    )
    mode_field = discord.ui.TextInput(label="Selection mode: single or multi", required=True, default="multi", max_length=6)
    max_field = discord.ui.TextInput(label="Maximum roles", required=False, default="1", max_length=2)
    allow_remove_field = discord.ui.TextInput(label="Allow removing roles? yes/no", required=True, default="yes", max_length=3)

    def __init__(self, bot: commands.Bot, message_id: int | None = None):
        super().__init__()
        self.bot = bot
        self.message_id = message_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel_id = int(self.channel_id.value.strip())
            channel = interaction.guild.get_channel(channel_id)
            if not isinstance(channel, discord.TextChannel):
                return await interaction.response.send_message("Target channel ID is invalid or is not a text channel.", ephemeral=True)
        except ValueError:
            return await interaction.response.send_message("Target channel ID must be numeric.", ephemeral=True)

        mode = self.mode_field.value.strip().lower()
        if mode not in {"single", "multi"}:
            return await interaction.response.send_message("Selection mode must be `single` or `multi`.", ephemeral=True)
        try:
            max_roles = max(1, min(25, int(self.max_field.value.strip() or "1")))
            color = int((self.color_field.value.strip() or "5865F2").replace("#", ""), 16)
        except ValueError:
            return await interaction.response.send_message("Maximum roles and color must be valid.", ephemeral=True)

        options = []
        for line in self.options_field.value.splitlines():
            if not line.strip():
                continue
            parts = [part.strip() for part in line.split("|")]
            if len(parts) < 2:
                return await interaction.response.send_message("Each role line must use `role_id|label|emoji`.", ephemeral=True)
            try:
                role_id = int(parts[0])
            except ValueError:
                return await interaction.response.send_message("Role IDs must be numeric.", ephemeral=True)
            if interaction.guild.get_role(role_id) is None:
                return await interaction.response.send_message(f"Role `{role_id}` was not found.", ephemeral=True)
            options.append({"role_id": role_id, "label": parts[1], "emoji": parts[2] if len(parts) > 2 else "", "description": ""})
        if not options:
            return await interaction.response.send_message("Add at least one role.", ephemeral=True)

        allow_remove = self.allow_remove_field.value.strip().lower() in {"yes", "y", "true", "1"}
        menu = {
            "guild_id": interaction.guild.id,
            "channel_id": channel.id,
            "title": self.title_field.value.strip(),
            "description": self.description_field.value.strip(),
            "color": color,
            "image_url": self.image_field.value.strip() or None,
            "selection_mode": mode,
            "max_roles": max_roles,
            "allow_remove": int(allow_remove),
            "options": options,
            "message_id": self.message_id,
        }

        try:
            if self.message_id:
                old = query_feat_one("SELECT channel_id, message_id FROM selfrole_menus WHERE guild_id=? AND message_id=?", (interaction.guild.id, self.message_id))
                if not old:
                    return await interaction.response.send_message("Menu was not found.", ephemeral=True)
                message_channel = interaction.guild.get_channel(old["channel_id"])
                if not isinstance(message_channel, discord.TextChannel):
                    return await interaction.response.send_message("The original menu channel no longer exists.", ephemeral=True)
                if channel.id != old["channel_id"]:
                    try:
                        old_message = await message_channel.fetch_message(old["message_id"])
                        await old_message.delete(reason="Move self-role menu")
                    except discord.NotFound:
                        pass
                    message = await channel.send(embed=self._embed(menu), view=SelfRoleView({**menu, "message_id": 0}))
                    menu["message_id"] = message.id
                    await message.edit(view=SelfRoleView(menu))
                    execute_feat(
                        "UPDATE selfrole_menus SET message_id=?, channel_id=?, title=?, description=?, color=?, image_url=?, selection_mode=?, max_roles=?, allow_remove=?, options_json=? WHERE guild_id=? AND message_id=?",
                        (message.id, channel.id, menu["title"], menu["description"], color, menu["image_url"], mode, max_roles, int(allow_remove), json.dumps(options), interaction.guild.id, old["message_id"]),
                    )
                else:
                    message = await message_channel.fetch_message(old["message_id"])
                    await message.edit(embed=self._embed(menu), view=SelfRoleView({**menu, "message_id": old["message_id"]}))
                    execute_feat(
                        "UPDATE selfrole_menus SET channel_id=?, title=?, description=?, color=?, image_url=?, selection_mode=?, max_roles=?, allow_remove=?, options_json=? WHERE guild_id=? AND message_id=?",
                        (channel.id, menu["title"], menu["description"], color, menu["image_url"], mode, max_roles, int(allow_remove), json.dumps(options), interaction.guild.id, old["message_id"]),
                    )
                commit_feat()
                return await interaction.response.send_message("✅ Self-role menu updated.", ephemeral=True)

            embed = self._embed(menu)
            message = await channel.send(embed=embed)
            menu["message_id"] = message.id
            execute_feat(
                "INSERT INTO selfrole_menus (guild_id,message_id,channel_id,title,description,color,image_url,selection_mode,max_roles,allow_remove,options_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (interaction.guild.id, message.id, channel.id, menu["title"], menu["description"], color, menu["image_url"], mode, max_roles, int(allow_remove), json.dumps(options)),
            )
            commit_feat()
            await message.edit(view=SelfRoleView(menu))
            await interaction.response.send_message(f"✅ Self-role menu posted in {channel.mention}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I lack permission to post or manage that channel.", ephemeral=True)
        except discord.HTTPException as exc:
            await interaction.response.send_message(f"Discord request failed: {exc.text}", ephemeral=True)

    @staticmethod
    def _embed(menu: dict) -> discord.Embed:
        embed = discord.Embed(title=menu["title"], description=menu["description"], color=menu["color"])
        if menu["image_url"]:
            embed.set_image(url=menu["image_url"])
        return embed


class SelfRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        await self.restore_views()

    async def restore_views(self):
        for row in query_feat_all("SELECT * FROM selfrole_menus"):
            try:
                menu = dict(row)
                menu["options"] = json.loads(menu["options_json"])
                menu["allow_remove"] = bool(menu["allow_remove"])
                channel = self.bot.get_channel(menu["channel_id"])
                if isinstance(channel, discord.TextChannel):
                    await channel.fetch_message(menu["message_id"])
                    self.bot.add_view(SelfRoleView(menu))
            except (discord.NotFound, discord.HTTPException, json.JSONDecodeError):
                continue

    @app_commands.command(name="selfrole-setup", description="Create or edit a persistent self-role menu")
    @app_commands.describe(action="create or edit")
    @app_commands.checks.has_permissions(administrator=True)
    async def selfrole_setup(self, interaction: discord.Interaction, action: str = "create", message_id: str = ""):
        if action not in {"create", "edit"}:
            return await interaction.response.send_message("Action must be `create` or `edit`.", ephemeral=True)
        mid = int(message_id) if message_id else None
        await interaction.response.send_modal(SelfRoleModal(self.bot, mid if action == "edit" else None))

    @app_commands.command(name="selfrole-delete", description="Delete a persistent self-role menu")
    @app_commands.checks.has_permissions(administrator=True)
    async def selfrole_delete(self, interaction: discord.Interaction, message_id: str):
        try:
            mid = int(message_id)
        except ValueError:
            return await interaction.response.send_message("Message ID must be numeric.", ephemeral=True)
        row = query_feat_one("SELECT channel_id FROM selfrole_menus WHERE guild_id=? AND message_id=?", (interaction.guild.id, mid))
        if not row:
            return await interaction.response.send_message("Menu was not found.", ephemeral=True)
        channel = interaction.guild.get_channel(row["channel_id"])
        if isinstance(channel, discord.TextChannel):
            try:
                message = await channel.fetch_message(mid)
                await message.delete(reason="Delete self-role menu")
            except discord.NotFound:
                pass
        execute_feat("DELETE FROM selfrole_menus WHERE guild_id=? AND message_id=?", (interaction.guild.id, mid))
        commit_feat()
        await interaction.response.send_message("✅ Self-role menu deleted.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(SelfRoles(bot))
