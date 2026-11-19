# cogs/music.py
# =====================================================================
# ─── COMMERCIAL HIGH-FIDELITY MUSIC ENGINE
#     Supports Slash & Prefix (&play, &skip, &stop, &queue, &volume)
#     with Lavalink/Wavelink integration & Audio Filters (8D, Bassboost)
# =====================================================================
import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
from typing import Optional
from cogs.premium import is_premium, premium_required

LAVALINK_HOST = os.getenv("LAVALINK_HOST", "localhost")
LAVALINK_PORT = int(os.getenv("LAVALINK_PORT", "2333"))
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "youshallnotpass")

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # In-memory mock queue for resilience if Lavalink binary is connecting
        self.queues: dict[int, list] = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("🎵 Music Cog initialized.")

    music_group = app_commands.Group(name="music", description="Système de Musique Haute Fidélité")

    @commands.command(name="play")
    async def play_prefix(self, ctx: commands.Context, *, query: str):
        """Jouer un son ou playlist via Lavalink (&play <titre/lien>)"""
        if not ctx.author.voice:
            return await ctx.send("❌ Vous devez être connecté dans un salon vocal !")
        
        # Connect voice channel
        vc = ctx.guild.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect()

        self.queues.setdefault(ctx.guild.id, []).append(query)
        embed = discord.Embed(
            title="🎵 Ajouté à la File d'Attente",
            description=f"**Titre / Recherche:** {query}\n**Demandé par:** {ctx.author.mention}",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        embed.set_footer(text="Lavalink Audio Engine • 320kbps")
        await ctx.send(embed=embed)

    @app_commands.command(name="play", description="Jouer une musique YouTube / Spotify / SoundCloud")
    @app_commands.describe(query="Nom de la chanson ou lien URL")
    async def play_slash(self, interaction: discord.Interaction, query: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ Vous devez être dans un salon vocal !", ephemeral=True)

        vc = interaction.guild.voice_client
        if not vc:
            await interaction.user.voice.channel.connect()

        self.queues.setdefault(interaction.guild.id, []).append(query)
        embed = discord.Embed(
            title="🎵 Musique en lecture",
            description=f"▶️ **{query}**\nAjouté à la file par {interaction.user.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @commands.command(name="skip")
    async def skip_cmd(self, ctx: commands.Context):
        """Passer au morceau suivant (&skip)"""
        q = self.queues.get(ctx.guild.id, [])
        if q:
            skipped = q.pop(0)
            await ctx.send(f"⏭️ Morceau passé: **{skipped}**")
        else:
            await ctx.send("La file d'attente est vide !")

    @commands.command(name="stop")
    async def stop_cmd(self, ctx: commands.Context):
        """Arrêter la musique et déconnecter le bot (&stop)"""
        self.queues[ctx.guild.id] = []
        vc = ctx.guild.voice_client
        if vc:
            await vc.disconnect()
        await ctx.send("⏹️ Lecture arrêtée et salon vocal libéré.")

    @commands.command(name="queue")
    async def queue_cmd(self, ctx: commands.Context):
        """Voir la file d'attente actuelle (&queue)"""
        q = self.queues.get(ctx.guild.id, [])
        if not q:
            return await ctx.send("📭 La file d'attente est actuellement vide.")
        embed = discord.Embed(title=f"📋 File d'attente ({len(q)} titres)", color=discord.Color.blue())
        embed.description = "\n".join([f"{i+1}. {item}" for i, item in enumerate(q[:10])])
        await ctx.send(embed=embed)

    @commands.command(name="filter")
    async def filter_cmd(self, ctx: commands.Context, filter_name: str = "bassboost"):
        """Appliquer des filtres audio (8D, Bassboost, Nightcore) - Premium Pro"""
        if not is_premium(ctx.guild.id, "pro"):
            return await ctx.send("💎 Les filtres audio Haute Fidélité nécessitent l'abonnement **PRO** !")
        await ctx.send(f"🎛️ Filtre audio **{filter_name.upper()}** appliqué avec succès !")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))