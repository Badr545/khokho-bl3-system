# cogs/autopublish.py
import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from cogs.premium import premium_required

AUTOPUBLISH_FILE = "data/autopublish.json"

class AutoPublish(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._ensure()

    def _ensure(self):
        if not os.path.exists(AUTOPUBLISH_FILE):
            with open(AUTOPUBLISH_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load(self):
        try:
            with open(AUTOPUBLISH_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, data):
        with open(AUTOPUBLISH_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    autopublish_group = app_commands.Group(name="autopublish", description="Auto-publication dans les canaux d'annonces")

    @autopublish_group.command(name="add", description="Activer l'auto-publication sur un canal d'annonces")
    async def add_autopublish(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ Permission requise.", ephemeral=True)
        data = self._load()
        ch_list = data.setdefault(str(interaction.guild_id), [])
        if channel.id not in ch_list:
            ch_list.append(channel.id)
            self._save(data)
        await interaction.response.send_message(f"📢 Auto-publication activée pour {channel.mention}.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild:
            return
        data = self._load()
        ch_list = data.get(str(message.guild.id), [])
        if message.channel.id in ch_list:
            try:
                # If announcement channel, publish/crosspost
                if message.channel.is_news():
                    await message.publish()
            except Exception:
                pass

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoPublish(bot))