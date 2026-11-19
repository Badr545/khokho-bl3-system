# cogs/counting.py
import discord
from discord import app_commands
from discord.ext import commands
import os
import json

COUNTING_FILE = "data/counting.json"

class Counting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._ensure()

    def _ensure(self):
        if not os.path.exists(COUNTING_FILE):
            with open(COUNTING_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load(self):
        try:
            with open(COUNTING_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, data):
        with open(COUNTING_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    counting_group = app_commands.Group(name="counting", description="Jeu du comptage communautaire")

    @counting_group.command(name="setup", description="Définir le salon de comptage")
    async def counting_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ Permission requise.", ephemeral=True)
        data = self._load()
        data[str(interaction.guild_id)] = {"channel_id": channel.id, "current": 0, "last_user": None}
        self._save(data)
        await interaction.response.send_message(f"🔢 Salon de comptage configuré sur {channel.mention}. Commencez à partir de 1 !")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        data = self._load()
        conf = data.get(str(message.guild.id))
        if not conf or message.channel.id != conf.get("channel_id"):
            return

        content = message.content.strip()
        if not content.isdigit():
            return

        num = int(content)
        current = conf.get("current", 0)
        last_user = conf.get("last_user")

        if message.author.id == last_user:
            await message.add_reaction("❌")
            await message.channel.send(f"⚠️ {message.author.mention}, vous ne pouvez pas compter deux fois de suite ! Réinitialisation à 0.")
            conf["current"] = 0
            conf["last_user"] = None
            self._save(data)
            return

        if num == current + 1:
            await message.add_reaction("✅")
            conf["current"] = num
            conf["last_user"] = message.author.id
            self._save(data)
        else:
            await message.add_reaction("❌")
            await message.channel.send(f"💥 Mauvais numéro {message.author.mention} ! Le nombre attendu était **{current + 1}**. Le compteur retombe à 0.")
            conf["current"] = 0
            conf["last_user"] = None
            self._save(data)

async def setup(bot: commands.Bot):
    await bot.add_cog(Counting(bot))