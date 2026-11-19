# cogs/custom_commands.py
import discord
from discord import app_commands
from discord.ext import commands
from database.features_schema import execute_feat, commit_feat, query_feat_all, query_feat_one

class CustomCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    custom_group = app_commands.Group(name="customcmd", description="Gestion des commandes personnalisées")

    @custom_group.command(name="add", description="Créer une nouvelle commande personnalisée")
    @app_commands.describe(name="Nom de la commande", response="Réponse texte ({user}, {server}, {channel})")
    async def add_cmd(self, interaction: discord.Interaction, name: str, response: str):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("❌ Permission requise.", ephemeral=True)

        cmd_name = name.lower().strip()
        execute_feat(
            """INSERT INTO custom_commands (guild_id, name, response, created_by)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(guild_id, name) DO UPDATE SET response = ?""",
            (interaction.guild.id, cmd_name, response, interaction.user.id, response)
        )
        commit_feat()
        await interaction.response.send_message(f"✅ Commande personnalisée &{cmd_name} créée avec succès !")

    @custom_group.command(name="list", description="Lister toutes les commandes personnalisées du serveur")
    async def list_cmds(self, interaction: discord.Interaction):
        rows = query_feat_all("SELECT name, uses_count FROM custom_commands WHERE guild_id = ?", (interaction.guild.id,))
        if not rows:
            return await interaction.response.send_message("Aucune commande personnalisée sur ce serveur.", ephemeral=True)

        embed = discord.Embed(title=f"📜 Commandes Personnalisées ({len(rows)})", color=discord.Color.blue())
        desc = "\n".join([f"• &{r['name']} ({r['uses_count']} utilisations)" for r in rows])
        embed.description = desc
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        content = message.content.strip()
        if content.startswith("&"):
            cmd_name = content[1:].split()[0].lower()
            row = query_feat_one("SELECT response FROM custom_commands WHERE guild_id = ? AND name = ?", (message.guild.id, cmd_name))
            if row:
                resp = row["response"]
                resp = resp.replace("{user}", message.author.mention)
                resp = resp.replace("{server}", message.guild.name)
                resp = resp.replace("{channel}", message.channel.mention)
                
                execute_feat("UPDATE custom_commands SET uses_count = uses_count + 1 WHERE guild_id = ? AND name = ?", (message.guild.id, cmd_name))
                commit_feat()
                await message.channel.send(resp)

async def setup(bot: commands.Bot):
    await bot.add_cog(CustomCommands(bot))