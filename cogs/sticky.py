# cogs/sticky.py
import discord
from discord import app_commands
from discord.ext import commands
import os
import json

STICKY_FILE = "data/sticky.json"

class Sticky(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._ensure()

    def _ensure(self):
        if not os.path.exists(STICKY_FILE):
            with open(STICKY_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load(self):
        try:
            with open(STICKY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, data):
        with open(STICKY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    sticky_group = app_commands.Group(name="sticky", description="Messages épinglés dynamiques (Sticky Messages)")

    @sticky_group.command(name="set", description="Créer ou remplacer un message sticky")
    @app_commands.describe(channel="Le salon cible", message="Le texte qui reste toujours en bas")
    async def set_sticky(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("❌ Permission requise.", ephemeral=True)
        data = self._load()
        data[str(channel.id)] = {"text": message, "last_msg_id": None}
        self._save(data)
        await interaction.response.send_message(f"📌 Sticky message configuré sur {channel.mention}.")

    @sticky_group.command(name="remove", description="Supprimer le message sticky d'un salon")
    async def remove_sticky(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("❌ Permission requise.", ephemeral=True)
        data = self._load()
        if str(channel.id) in data:
            del data[str(channel.id)]
            self._save(data)
        await interaction.response.send_message(f"🗑️ Sticky message retiré de {channel.mention}.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        data = self._load()
        conf = data.get(str(message.channel.id))
        if not conf:
            return

        last_id = conf.get("last_msg_id")
        if last_id:
            try:
                old = await message.channel.fetch_message(last_id)
                await old.delete()
            except Exception:
                pass

        embed = discord.Embed(
            description=f"📌 **Message Épinglé:**\n\n{conf['text']}",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        new_msg = await message.channel.send(embed=embed)
        conf["last_msg_id"] = new_msg.id
        self._save(data)

async def setup(bot: commands.Bot):
    await bot.add_cog(Sticky(bot))