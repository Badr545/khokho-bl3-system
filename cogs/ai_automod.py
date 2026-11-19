# cogs/ai_automod.py
import discord
from discord import app_commands
from discord.ext import commands
import os
import aiohttp
from cogs.premium import premium_required

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

class AIAutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    ai_group = app_commands.Group(name="ai_automod", description="Modération par Intelligence Artificielle (Toxique/NSFW)")

    @ai_group.command(name="status", description="Vérifier l'état de l'IA Modératrice")
    async def ai_status(self, interaction: discord.Interaction):
        has_key = bool(OPENAI_KEY)
        embed = discord.Embed(
            title="🧠 IA AutoMod — Analyseur Sémantique",
            description="Détecte en temps réel le cyberharcèlement, les menaces, et l'extrémisme.",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        embed.add_field(name="Moteur IA", value="OpenAI Moderation API", inline=True)
        embed.add_field(name="Clé API Configurée", value="✅ Oui" if has_key else "⚠️ Clé manquante", inline=True)
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild or not OPENAI_KEY:
            return
        if len(message.content) < 5:
            return

        # Query OpenAI moderation endpoint
        try:
            headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/moderations",
                    headers=headers,
                    json={"input": message.content},
                    timeout=2
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get("results", [])
                        if results and results[0].get("flagged"):
                            await message.delete()
                            await message.channel.send(
                                f"🛡️ {message.author.mention}, votre message a été supprimé par l'IA de modération (contenu inapproprié).",
                                delete_after=5
                            )
        except Exception:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(AIAutoMod(bot))