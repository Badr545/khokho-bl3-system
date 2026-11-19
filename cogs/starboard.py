# cogs/starboard.py
import discord
from discord import app_commands
from discord.ext import commands
import os
import json

STARBOARD_FILE = "data/starboard.json"

class Starboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._ensure()

    def _ensure(self):
        if not os.path.exists(STARBOARD_FILE):
            with open(STARBOARD_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load(self):
        try:
            with open(STARBOARD_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, data):
        with open(STARBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    starboard_group = app_commands.Group(name="starboard", description="Panthéon des meilleurs messages Starboard")

    @starboard_group.command(name="setup", description="Définir le salon et le seuil d'étoiles")
    @app_commands.describe(channel="Le salon où les étoiles sont affichées", threshold="Nombre d'étoiles requis (défaut 3)")
    async def setup_starboard(self, interaction: discord.Interaction, channel: discord.TextChannel, threshold: int = 3):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ Permission requise.", ephemeral=True)
        data = self._load()
        data[str(interaction.guild_id)] = {"channel_id": channel.id, "threshold": threshold, "starred": []}
        self._save(data)
        await interaction.response.send_message(f"⭐ Starboard configuré sur {channel.mention} avec un seuil de **{threshold}** étoiles.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) != "⭐":
            return
        data = self._load()
        conf = data.get(str(payload.guild_id))
        if not conf:
            return

        channel = self.bot.get_channel(payload.channel_id)
        if not channel or not isinstance(channel, discord.TextChannel):
            return

        message = await channel.fetch_message(payload.message_id)
        rx = discord.utils.get(message.reactions, emoji="⭐")
        if rx and rx.count >= conf.get("threshold", 3):
            starred_list = conf.get("starred", [])
            if message.id in starred_list:
                return
            conf.setdefault("starred", []).append(message.id)
            self._save(data)

            target_ch = self.bot.get_channel(conf["channel_id"])
            if target_ch and isinstance(target_ch, discord.TextChannel):
                embed = discord.Embed(
                    description=message.content,
                    color=discord.Color.gold(),
                    timestamp=message.created_at
                )
                embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                embed.add_field(name="Source", value=f"[Aller au message]({message.jump_url})")
                await target_ch.send(f"⭐ **{rx.count}** | {channel.mention}", embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Starboard(bot))