# cogs/context_menus.py
import discord
from discord import app_commands
from discord.ext import commands

class ReportModal(discord.ui.Modal, title="Signaler à l'Administration"):
    reason = discord.ui.TextInput(label="Raison du signalement", style=discord.TextStyle.paragraph)

    def __init__(self, target_user: discord.User):
        super().__init__()
        self.target_user = target_user

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🚨 Signalement d'Utilisateur (Menu Clic Droit)",
            description=f"**Cible:** {self.target_user.mention} ({self.target_user.id})\n**Raison:** {self.reason.value}",
            color=discord.Color.red()
        )
        embed.set_author(name=f"Signalé par {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        # Send to guild owner or system channel
        if interaction.guild and interaction.guild.system_channel:
            await interaction.guild.system_channel.send(embed=embed)
        await interaction.response.send_message("✅ Signalement transmis au staff.", ephemeral=True)

class ContextMenus(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ctx_report_user = app_commands.ContextMenu(
            name="🚨 Signaler Utilisateur",
            callback=self.report_user_callback
        )
        self.ctx_report_msg = app_commands.ContextMenu(
            name="🚩 Signaler Message",
            callback=self.report_message_callback
        )
        self.bot.tree.add_command(self.ctx_report_user)
        self.bot.tree.add_command(self.ctx_report_msg)

    async def report_user_callback(self, interaction: discord.Interaction, user: discord.Member):
        modal = ReportModal(user)
        await interaction.response.send_modal(modal)

    async def report_message_callback(self, interaction: discord.Interaction, message: discord.Message):
        embed = discord.Embed(
            title="🚩 Signalement de Message Inapproprié",
            description=f"**Auteur:** {message.author.mention}\n**Contenu:** {message.content}\n[Aller au message]({message.jump_url})",
            color=discord.Color.orange()
        )
        embed.set_author(name=f"Signalé par {interaction.user}", icon_url=interaction.user.display_avatar.url)
        if interaction.guild and interaction.guild.system_channel:
            await interaction.guild.system_channel.send(embed=embed)
        await interaction.response.send_message("✅ Message signalé à la modération.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ContextMenus(bot))