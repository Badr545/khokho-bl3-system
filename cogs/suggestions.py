# cogs/suggestions.py
import discord
from discord import app_commands
from discord.ext import commands
from database.features_schema import execute_feat, commit_feat, query_feat_all, query_feat_one

class SuggestionVoteView(discord.ui.View):
    def __init__(self, suggestion_id: int):
        super().__init__(timeout=None)
        self.suggestion_id = suggestion_id

    @discord.ui.button(label="D'accord (0)", style=discord.ButtonStyle.green, custom_id="sugg_up", emoji="👍")
    async def upvote(self, interaction: discord.Interaction, button: discord.ui.Button):
        execute_feat("UPDATE suggestions SET upvotes = upvotes + 1 WHERE id = ?", (self.suggestion_id,))
        commit_feat()
        row = query_feat_one("SELECT upvotes, downvotes FROM suggestions WHERE id = ?", (self.suggestion_id,))
        if row:
            button.label = f"D'accord ({row['upvotes']})"
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.send_message("Vote enregistré !", ephemeral=True)

    @discord.ui.button(label="Pas d'accord (0)", style=discord.ButtonStyle.red, custom_id="sugg_down", emoji="👎")
    async def downvote(self, interaction: discord.Interaction, button: discord.ui.Button):
        execute_feat("UPDATE suggestions SET downvotes = downvotes + 1 WHERE id = ?", (self.suggestion_id,))
        commit_feat()
        row = query_feat_one("SELECT upvotes, downvotes FROM suggestions WHERE id = ?", (self.suggestion_id,))
        if row:
            button.label = f"Pas d'accord ({row['downvotes']})"
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.send_message("Vote enregistré !", ephemeral=True)

class Suggestions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="suggest", description="Soumettre une idée ou suggestion pour le serveur")
    @app_commands.describe(idea="Votre proposition détaillée")
    async def suggest(self, interaction: discord.Interaction, idea: str):
        if not interaction.guild:
            return await interaction.response.send_message("Commande utilisable uniquement sur un serveur.", ephemeral=True)

        cur = execute_feat(
            "INSERT INTO suggestions (guild_id, user_id, message, upvotes, downvotes, status) VALUES (?, ?, ?, 0, 0, 'pending')",
            (interaction.guild.id, interaction.user.id, idea)
        )
        commit_feat()
        sugg_id = cur.lastrowid

        embed = discord.Embed(
            title=f"💡 Suggestion #{sugg_id}",
            description=idea,
            color=discord.Color.from_rgb(88, 101, 242)
        )
        embed.set_author(name=f"{interaction.user}", icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Votez avec les boutons ci-dessous !")

        view = SuggestionVoteView(sugg_id)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Suggestions(bot))