# cogs/premium.py
# =====================================================================
# ─── PREMIUM COG & COMMERCIAL LICENSING DECORATORS
# =====================================================================
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import hashlib
from typing import Optional, Callable

from database.features_schema import query_feat_one, execute_feat, commit_feat
from utils.context import EmbedContext

TIER_RANKS = {"free": 0, "basic": 1, "pro": 2, "ultra": 3}

# Global in-memory cache for fast checking without SQL overhead
PREMIUM_CACHE: dict[int, dict] = {}

def get_tier(guild_id: int) -> str:
    cached = PREMIUM_CACHE.get(guild_id)
    if cached:
        until = cached.get("premium_until")
        if until and until < datetime.utcnow():
            return "free"
        return cached.get("tier", "free")

    row = query_feat_one("SELECT tier, premium_until FROM web_premium WHERE guild_id = ?", (guild_id,))
    if not row:
        PREMIUM_CACHE[guild_id] = {"tier": "free", "premium_until": None}
        return "free"

    until_str = row.get("premium_until")
    until = datetime.fromisoformat(until_str) if isinstance(until_str, str) else until_str
    tier = row.get("tier", "free").lower()

    if until and until < datetime.utcnow():
        tier = "free"

    PREMIUM_CACHE[guild_id] = {"tier": tier, "premium_until": until}
    return tier

def is_premium(guild_id: int, tier: Optional[str] = None) -> bool:
    current = get_tier(guild_id)
    if tier is None:
        return current != "free"
    return TIER_RANKS.get(current, 0) >= TIER_RANKS.get(tier.lower(), 1)

def premium_required(tier: str = "basic"):
    """Command decorator to protect premium features"""
    async def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild:
            return True
        if is_premium(ctx.guild.id, tier):
            return True
        embed = discord.Embed(
            title="💎 Premium Feature Required",
            description=(
                f"Cette commande nécessite l'abonnement **{tier.upper()}** ou supérieur.\n\n"
                f"Pour activer votre licence ou souscrire:\n"
                f"👉 Utilisez /premium activate <cle> ou visitez notre Dashboard."
            ),
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
        return False
    return commands.check(predicate)

class Premium(commands.Cog):
    """Commercial Premium & Licensing Commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    premium_group = app_commands.Group(name="premium", description="Commandes du système Premium & Licences")

    @premium_group.command(name="info", description="Afficher le statut et les fonctionnalités Premium du serveur")
    async def premium_info(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("Cette commande doit être exécutée dans un serveur.", ephemeral=True)

        tier = get_tier(interaction.guild.id)
        cached = PREMIUM_CACHE.get(interaction.guild.id, {})
        until = cached.get("premium_until")
        until_text = until.strftime('%Y-%m-%d %H:%M') if until else "À vie / Sans expiration"

        embed = discord.Embed(
            title=f"💎 Statut Premium — {interaction.guild.name}",
            color=discord.Color.from_rgb(235, 69, 158) if tier != 'free' else discord.Color.greyple()
        )
        embed.add_field(name="Niveau Actuel", value=f"⭐ **{tier.upper()}**", inline=True)
        embed.add_field(name="Valide Jusqu'au", value=until_text, inline=True)

        if tier == "free":
            embed.add_field(
                name="Avantages Pro & Ultra",
                value="• Musique 24/7 & Filtres 8D/Bassboost\n• Anti-Nuke avancé & Logs illimités\n• Commandes personnalisées illimitées\n• Aucun copyright Khokho Bl3",
                inline=False
            )
        else:
            embed.add_field(name="Statut du Serveur", value="✅ Toutes les fonctionnalités avancées sont débloquées !", inline=False)

        await interaction.response.send_message(embed=embed)

    @premium_group.command(name="activate", description="Activer une clé de licence commerciale")
    @app_commands.describe(key="La clé au format KHOKHO-XXXX-XXXX-XXXX")
    async def premium_activate(self, interaction: discord.Interaction, key: str):
        if not interaction.guild:
            return await interaction.response.send_message("Cette commande doit être exécutée dans un serveur.", ephemeral=True)

        key_hash = hashlib.sha256(key.strip().encode()).hexdigest()
        row = query_feat_one("SELECT * FROM premium_keys WHERE key_hash = ? AND is_redeemed = 0", (key_hash,))

        if not row:
            return await interaction.response.send_message("❌ Clé invalide ou déjà utilisée.", ephemeral=True)

        tier = row["tier"]
        days = row["duration_days"]
        now = datetime.utcnow()
        new_until = now + timedelta(days=days)

        execute_feat(
            "UPDATE premium_keys SET is_redeemed = 1, redeemed_by_guild = ?, redeemed_at = ? WHERE id = ?",
            (interaction.guild.id, now.isoformat(), row["id"])
        )

        execute_feat(
            """INSERT INTO web_premium (guild_id, tier, premium_until) 
               VALUES (?, ?, ?) 
               ON CONFLICT(guild_id) DO UPDATE SET tier = ?, premium_until = ?""",
            (interaction.guild.id, tier, new_until.isoformat(), tier, new_until.isoformat())
        )
        commit_feat()

        PREMIUM_CACHE[interaction.guild.id] = {"tier": tier, "premium_until": new_until}

        embed = discord.Embed(
            title="🎉 Licence Premium Activée avec Succès !",
            description=f"Votre serveur bénéficie désormais du grade **{tier.upper()}** pour **{days} jours**.\nMerci de soutenir le projet Khokho Bl3 V3 !",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Premium(bot))