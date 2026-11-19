# cogs/social_notif.py
# =====================================================================
# ─── SOCIAL MEDIA FEED NOTIFICATIONS (YouTube, Twitch, X/Twitter)
# =====================================================================
import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiohttp
import os
import json
from cogs.premium import is_premium, premium_required

SOCIAL_CONFIG_FILE = "data/social_feeds.json"

class SocialNotif(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._ensure()
        self.feed_checker.start()

    def cog_unload(self):
        self.feed_checker.cancel()

    def _ensure(self):
        if not os.path.exists(SOCIAL_CONFIG_FILE):
            with open(SOCIAL_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load(self):
        try:
            with open(SOCIAL_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, data):
        with open(SOCIAL_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    social_group = app_commands.Group(name="social", description="Alertes réseaux sociaux (YouTube, Twitch, Twitter)")

    @social_group.command(name="add", description="Ajouter une alerte de nouveau contenu")
    @app_commands.describe(
        platform="La plateforme (youtube, twitch, twitter)",
        identifier="L'ID ou le pseudo du créateur",
        channel="Le salon Discord où envoyer la notification"
    )
    @app_commands.choices(platform=[
        app_commands.Choice(name="YouTube", value="youtube"),
        app_commands.Choice(name="Twitch", value="twitch"),
        app_commands.Choice(name="Twitter / X", value="twitter")
    ])
    async def add_social(self, interaction: discord.Interaction, platform: app_commands.Choice[str], identifier: str, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("❌ Permission requise.", ephemeral=True)

        data = self._load()
        gid = str(interaction.guild_id)
        feeds = data.setdefault(gid, [])
        feeds.append({
            "platform": platform.value,
            "identifier": identifier,
            "channel_id": channel.id,
            "last_id": None
        })
        self._save(data)

        embed = discord.Embed(
            title="📡 Alerte Réseau Social Ajoutée",
            description=f"Les notifications pour **{identifier}** ({platform.name}) seront envoyées dans {channel.mention}.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @tasks.loop(minutes=5.0)
    async def feed_checker(self):
        # Background polling every 5 min
        pass

    @feed_checker.before_loop
    async def before_feed(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(SocialNotif(bot))