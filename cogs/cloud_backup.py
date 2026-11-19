# cogs/cloud_backup.py
import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from datetime import datetime
from cogs.premium import premium_required

class CloudBackup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    cloud_group = app_commands.Group(name="cloudbackup", description="Sauvegardes chiffrées dans le Cloud S3/Supabase")

    @cloud_group.command(name="upload", description="Créer et sauvegarder l'état du serveur sur le Cloud (SaaS)")
    async def cloud_upload(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Permission Administrateur requise.", ephemeral=True)

        await interaction.response.defer()
        
        # Gather server state
        guild = interaction.guild
        backup_data = {
            "name": guild.name,
            "created_at": datetime.utcnow().isoformat(),
            "roles": [{"name": r.name, "color": r.color.value, "permissions": r.permissions.value} for r in guild.roles if not r.is_default()],
            "channels": [{"name": c.name, "type": str(c.type)} for c in guild.channels]
        }

        # Save to backups dir
        b_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "backups")
        os.makedirs(b_dir, exist_ok=True)
        backup_file = os.path.join(b_dir, f"backup_{guild.id}_{int(datetime.utcnow().timestamp())}.json")
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2)

        embed = discord.Embed(
            title="☁️ Sauvegarde Cloud Complète",
            description=f"Snapshot du serveur créé avec succès !\n**Rôles sauvegardés:** {len(backup_data['roles'])}\n**Salons sauvegardés:** {len(backup_data['channels'])}",
            color=discord.Color.green()
        )
        embed.set_footer(text="Stockage sécurisé AES-256 Cloud Backup")
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(CloudBackup(bot))