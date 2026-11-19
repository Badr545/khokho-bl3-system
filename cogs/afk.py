# cogs/afk.py
import discord
from discord.ext import commands
from datetime import datetime
from database.features_schema import execute_feat, commit_feat, query_feat_one, query_feat_all

class AFK(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="afk")
    async def afk_cmd(self, ctx: commands.Context, *, reason: str = "AFK (Absent)"):
        """Définir son statut AFK (préfixe &)"""
        execute_feat(
            """INSERT INTO afk (guild_id, user_id, reason, since)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(guild_id, user_id) DO UPDATE SET reason = ?, since = ?""",
            (ctx.guild.id, ctx.author.id, reason, datetime.utcnow().isoformat(), reason, datetime.utcnow().isoformat())
        )
        commit_feat()
        await ctx.send(f"💤 {ctx.author.mention} est maintenant AFK: **{reason}**")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Check if author was AFK -> remove AFK
        was_afk = query_feat_one("SELECT reason FROM afk WHERE guild_id = ? AND user_id = ?", (message.guild.id, message.author.id))
        if was_afk:
            execute_feat("DELETE FROM afk WHERE guild_id = ? AND user_id = ?", (message.guild.id, message.author.id))
            commit_feat()
            await message.channel.send(f"👋 Bon retour {message.author.mention}, votre statut AFK a été retiré !")

        # Check mentions
        if message.mentions:
            for mentioned in message.mentions:
                row = query_feat_one("SELECT reason, since FROM afk WHERE guild_id = ? AND user_id = ?", (message.guild.id, mentioned.id))
                if row:
                    await message.channel.send(f"💤 **{mentioned.display_name}** est actuellement AFK: {row['reason']}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AFK(bot))