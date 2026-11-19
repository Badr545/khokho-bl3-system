# cogs/antinuke.py
import discord
from discord import app_commands
from discord.ext import commands
import time
import os
import json
from collections import defaultdict
from cogs.premium import is_premium

ANTINUKE_FILE = "data/antinuke.json"

class AntiNuke(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.action_cache = defaultdict(list)
        self._ensure()

    def _ensure(self):
        if not os.path.exists(ANTINUKE_FILE):
            with open(ANTINUKE_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load(self):
        try:
            with open(ANTINUKE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    antinuke_group = app_commands.Group(name="antinuke", description="Système de défense haute sécurité Anti-Nuke")

    @antinuke_group.command(name="status", description="Vérifier la configuration Anti-Nuke du serveur")
    async def an_status(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Réservé aux Administrateurs.", ephemeral=True)

        premium_active = is_premium(interaction.guild.id, "basic")
        embed = discord.Embed(
            title="🛡️ Protection Anti-Nuke & Anti-Rogue Staff",
            description="Surveillance en temps réel des actions destructrices (Bans, Expulsions, Suppressions de canaux/rôles).",
            color=discord.Color.green() if premium_active else discord.Color.gold()
        )
        embed.add_field(name="Seuil Détection", value="3 actions destructrices en 60s", inline=True)
        embed.add_field(name="Sanction Immédiate", value="Révocation des rôles + Bannissement de sécurité", inline=True)
        embed.add_field(name="Statut Licence", value="⭐ Pro Shield Activé" if premium_active else "Standard Shield", inline=True)
        await interaction.response.send_message(embed=embed)

    async def check_action(self, guild: discord.Guild, user: discord.Member, action_name: str):
        if user == guild.owner or user.id == self.bot.user.id:
            return
        now = time.time()
        self.action_cache[user.id].append(now)
        # Filter actions within 60s
        self.action_cache[user.id] = [t for t in self.action_cache[user.id] if now - t <= 60]

        if len(self.action_cache[user.id]) >= 3:
            # Trigger Anti-Nuke mitigation
            try:
                # Strip all dangerous roles
                dangerous = [r for r in user.roles if r.permissions.administrator or r.permissions.manage_guild or r.permissions.ban_members]
                if dangerous:
                    await user.remove_roles(*dangerous, reason="[ANTI-NUKE] Seuil d'actions de sécurité dépassé!")
                
                # Send alert to owner
                if guild.owner:
                    await guild.owner.send(f"🚨 **ALERTE ANTI-NUKE DANS {guild.name}**\nL'utilisateur {user} ({user.id}) a dépassé le seuil de sécurité ({action_name}). Ses permissions ont été immédiatement révoquées !")
            except Exception as e:
                print(f"Anti-Nuke mitigation error: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if isinstance(entry.user, discord.Member):
                await self.check_action(channel.guild, entry.user, "Channel Deletion")

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if isinstance(entry.user, discord.Member):
                await self.check_action(guild, entry.user, "Mass Ban")

async def setup(bot: commands.Bot):
    await bot.add_cog(AntiNuke(bot))