# cogs/birthday.py
import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime
from database.features_schema import execute_feat, commit_feat, query_feat_all, query_feat_one

class Birthday(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_birthdays.start()

    def cog_unload(self):
        self.check_birthdays.cancel()

    birthday_group = app_commands.Group(name="birthday", description="Gestion des anniversaires du serveur")

    @birthday_group.command(name="set", description="Enregistrer votre jour et mois d'anniversaire")
    @app_commands.describe(day="Jour (1-31)", month="Mois (1-12)")
    async def set_birthday(self, interaction: discord.Interaction, day: int, month: int):
        if day < 1 or day > 31 or month < 1 or month > 12:
            return await interaction.response.send_message("❌ Date invalide.", ephemeral=True)

        execute_feat(
            """INSERT INTO birthdays (guild_id, user_id, day, month)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(guild_id, user_id) DO UPDATE SET day = ?, month = ?""",
            (interaction.guild.id, interaction.user.id, day, month, day, month)
        )
        commit_feat()
        await interaction.response.send_message(f"🎂 Votre anniversaire a été enregistré pour le **{day:02d}/{month:02d}** !")

    @tasks.loop(hours=24.0)
    async def check_birthdays(self):
        now = datetime.utcnow()
        rows = query_feat_all("SELECT guild_id, user_id FROM birthdays WHERE day = ? AND month = ?", (now.day, now.month))
        for r in rows:
            guild = self.bot.get_guild(r["guild_id"])
            if guild and guild.system_channel:
                await guild.system_channel.send(f"🎉 Joyeux Anniversaire à <@{r['user_id']}> de la part de toute la communauté ! 🎂🥳")

    @check_birthdays.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(Birthday(bot))