# cogs/bump.py
import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import asyncio
from datetime import datetime

BUMP_FILE = "data/bump.json"

class Bump(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._ensure()

    def _ensure(self):
        if not os.path.exists(BUMP_FILE):
            with open(BUMP_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load(self):
        try:
            with open(BUMP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, data):
        with open(BUMP_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    bump_group = app_commands.Group(name="bump", description="Rappels de bump Disboard automatiques")

    @bump_group.command(name="setup", description="Configurer le salon de rappel Disboard")
    async def setup_bump(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("❌ Permission requise.", ephemeral=True)
        data = self._load()
        data[str(interaction.guild_id)] = {"channel_id": channel.id, "last_bump": None}
        self._save(data)
        await interaction.response.send_message(f"⏰ Rappel Bump configuré sur {channel.mention}. Un rappel sera envoyé 2h après chaque bump !")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Disboard Bot ID = 302050872383242240
        if message.author.id == 302050872383242240 or (message.embeds and "bump" in (message.embeds[0].description or "").lower()):
            data = self._load()
            conf = data.get(str(message.guild.id))
            if conf:
                ch_id = conf.get("channel_id")
                await message.channel.send("🎉 **Merci d'avoir bump le serveur !** Je vous préviendrai dans exactement 2 heures.")
                
                async def wait_reminder():
                    await asyncio.sleep(7200) # 2 hours
                    ch = self.bot.get_channel(ch_id)
                    if ch:
                        await ch.send("⏰ **C'est l'heure de bump !** Tapez /bump pour faire monter le serveur !")

                asyncio.create_task(wait_reminder())

async def setup(bot: commands.Bot):
    await bot.add_cog(Bump(bot))