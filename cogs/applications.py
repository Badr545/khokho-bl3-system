# cogs/applications.py
import discord
from discord import app_commands
from discord.ext import commands
import json
from database.features_schema import execute_feat, commit_feat, query_feat_one

class ApplyModal(discord.ui.Modal, title="Formulaire de Candidature Staff"):
    name_field = discord.ui.TextInput(label="Votre Prénom / Nom", placeholder="Ex: Rayan")
    age_field = discord.ui.TextInput(label="Votre Âge", placeholder="Ex: 18")
    exp_field = discord.ui.TextInput(label="Expérience de Modération", style=discord.TextStyle.paragraph, placeholder="Parlez-nous de vos anciens postes...")
    why_field = discord.ui.TextInput(label="Pourquoi vous choisir ?", style=discord.TextStyle.paragraph, placeholder="Vos motivations...")

    async def on_submit(self, interaction: discord.Interaction):
        submission_data = {
            "name": self.name_field.value,
            "age": self.age_field.value,
            "experience": self.exp_field.value,
            "why": self.why_field.value
        }
        execute_feat(
            "INSERT INTO applications_submissions (guild_id, user_id, form_data_json, status) VALUES (?, ?, ?, 'pending')",
            (interaction.guild.id, interaction.user.id, json.dumps(submission_data))
        )
        commit_feat()

        await interaction.response.send_message("✅ Votre candidature a été transmise aux administrateurs avec succès !", ephemeral=True)

class Applications(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="apply", description="Postuler pour intégrer l'équipe de modération")
    async def apply_cmd(self, interaction: discord.Interaction):
        modal = ApplyModal()
        await interaction.response.send_modal(modal)

async def setup(bot: commands.Bot):
    await bot.add_cog(Applications(bot))