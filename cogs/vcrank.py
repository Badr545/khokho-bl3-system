"""Voice-only activity ranks."""
import json
import discord
from discord import app_commands
from discord.ext import commands, tasks

from database.engine import execute, commit, query_one, query_all
import config_manager


def xp_needed(level: int) -> int:
    return 100 + (level * 75)


class VCRank(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sessions: dict[tuple[int, int], float] = {}

    def cog_unload(self):
        self.vc_awarder.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.vc_awarder.is_running():
            self.vc_awarder.start()

    def get_config(self, guild_id: int) -> dict:
        row = query_one("SELECT * FROM vc_rank_config WHERE guild_id=?", (guild_id,))
        if row:
            data = dict(row)
            data["excluded_channel_ids"] = json.loads(data["excluded_channel_ids"])
            data["ladder"] = json.loads(data["ladder_json"])
            return data
        execute(
            "INSERT INTO vc_rank_config (guild_id) VALUES (?)",
            (guild_id,),
        )
        commit()
        return {
            "guild_id": guild_id,
            "xp_per_minute": 2,
            "min_users": 2,
            "excluded_channel_ids": [],
            "ladder": [],
            "announcement_channel_id": None,
            "anti_afk_muted": 1,
            "anti_afk_deafened": 1,
            "anti_afk_alone": 1,
        }

    def qualifies(self, member: discord.Member, config: dict) -> bool:
        state = member.voice
        if state is None or state.channel is None or member.bot:
            return False
        if state.channel.id in config["excluded_channel_ids"]:
            return False
        if config["anti_afk_muted"] and config["anti_afk_deafened"] and state.mute and state.deaf:
            return False
        if config["anti_afk_alone"]:
            humans = [m for m in state.channel.members if not m.bot]
            if len(humans) < config["min_users"]:
                return False
        return True

    @tasks.loop(minutes=1)
    async def vc_awarder(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            config = self.get_config(guild.id)
            for channel in guild.voice_channels:
                if channel.id in config["excluded_channel_ids"]:
                    continue
                humans = [member for member in channel.members if not member.bot]
                for member in humans:
                    if not self.qualifies(member, config):
                        continue
                    row = query_one(
                        "SELECT xp, level, total_seconds FROM vc_ranks WHERE guild_id=? AND user_id=?",
                        (guild.id, member.id),
                    )
                    xp = row["xp"] if row else 0
                    level = row["level"] if row else 0
                    total_seconds = row["total_seconds"] if row else 0
                    xp += config["xp_per_minute"]
                    total_seconds += 60

                    new_level = level
                    while xp >= xp_needed(new_level):
                        xp -= xp_needed(new_level)
                        new_level += 1

                    execute(
                        "INSERT INTO vc_ranks (guild_id,user_id,xp,level,total_seconds,updated_at) "
                        "VALUES (?,?,?,?,?,CURRENT_TIMESTAMP) "
                        "ON CONFLICT(guild_id,user_id) DO UPDATE SET xp=excluded.xp, level=excluded.level, "
                        "total_seconds=excluded.total_seconds, updated_at=CURRENT_TIMESTAMP",
                        (guild.id, member.id, xp, new_level, total_seconds),
                    )
                    if new_level > level:
                        await self.award_ladder_role(guild, member, new_level, config)
                    commit()

    async def award_ladder_role(self, guild: discord.Guild, member: discord.Member, level: int, config: dict):
        ladder = config["ladder"]
        for item in ladder:
            if level >= item["threshold"]:
                role = guild.get_role(item["role_id"])
                if role and role not in member.roles:
                    try:
                        await member.add_roles(role, reason="Voice rank level up")
                    except discord.HTTPException:
                        return
        announcement_id = config["announcement_channel_id"]
        channel = guild.get_channel(announcement_id) if announcement_id else None
        if isinstance(channel, discord.TextChannel):
            try:
                await channel.send(f"🎙️ {member.mention} reached voice level **{level}**!")
            except discord.HTTPException:
                pass

    def format_time(self, seconds: int) -> str:
        hours, remainder = divmod(seconds, 3600)
        minutes = divmod(remainder, 60)[0]
        return f"{hours}h {minutes}m"

    @app_commands.command(name="vcrank", description="Show a user's voice rank")
    @app_commands.describe(member="Member to inspect")
    async def vcrank(self, interaction: discord.Interaction, member: discord.Member | None = None):
        member = member or interaction.user
        row = query_one("SELECT * FROM vc_ranks WHERE guild_id=? AND user_id=?", (interaction.guild.id, member.id))
        xp = row["xp"] if row else 0
        level = row["level"] if row else 0
        total_seconds = row["total_seconds"] if row else 0
        needed = xp_needed(level)
        progress = min(20, int((xp / needed) * 20)) if needed else 20
        bar = "█" * progress + "░" * (20 - progress)
        embed = discord.Embed(title=f"🎙️ Voice Rank — {member.display_name}", color=discord.Color.blurple())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Level", value=str(level), inline=True)
        embed.add_field(name="XP", value=f"{xp}/{needed}", inline=True)
        embed.add_field(name="Voice time", value=self.format_time(total_seconds), inline=True)
        embed.add_field(name="Progress", value=f"`{bar}`", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rank-top", description="Show the top voice activity users")
    async def rank_top(self, interaction: discord.Interaction):
        rows = query_all(
            "SELECT user_id,xp,level,total_seconds FROM vc_ranks WHERE guild_id=? "
            "ORDER BY total_seconds DESC, xp DESC LIMIT 10",
            (interaction.guild.id,),
        )
        if not rows:
            return await interaction.response.send_message("No voice activity has been recorded yet.", ephemeral=True)
        embed = discord.Embed(title="🏆 Voice Rank Leaderboard", color=discord.Color.gold())
        for index, row in enumerate(rows, start=1):
            member = interaction.guild.get_member(row["user_id"])
            name = member.display_name if member else f"User {row['user_id']}"
            embed.add_field(
                name=f"{index}. {name}",
                value=f"Level {row['level']} • {row['xp']} XP • {self.format_time(row['total_seconds'])}",
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    @commands.command(name="vcrank-config")
    @commands.has_permissions(administrator=True)
    async def vcrank_config(self, ctx: commands.Context, xp_per_minute: int = 2, minimum_users: int = 2):
        """+vcrank-config <xp-per-minute> <minimum-users>"""
        config = self.get_config(ctx.guild.id)
        xp_per_minute = max(1, min(100, xp_per_minute))
        minimum_users = max(1, min(20, minimum_users))
        execute(
            "UPDATE vc_rank_config SET xp_per_minute=?, min_users=? WHERE guild_id=?",
            (xp_per_minute, minimum_users, ctx.guild.id),
        )
        commit()
        await ctx.send(
            f"✅ Voice rank configured: {xp_per_minute} XP/min, minimum {minimum_users} humans per VC."
        )

    @commands.command(name="vcrank", aliases=["rank"])
    async def vcrank_prefix(self, ctx: commands.Context, member: discord.Member | None = None):
        member = member or ctx.author
        row = query_one("SELECT * FROM vc_ranks WHERE guild_id=? AND user_id=?", (ctx.guild.id, member.id))
        xp = row["xp"] if row else 0
        level = row["level"] if row else 0
        total_seconds = row["total_seconds"] if row else 0
        await ctx.send(
            f"🎙️ **{member.display_name}** — Voice Level `{level}` | XP `{xp}/{xp_needed(level)}` | Time `{self.format_time(total_seconds)}"
        )

    @commands.command(name="rank-top", aliases=["vcrank-leaderboard"])
    async def rank_top_prefix(self, ctx: commands.Context):
        rows = query_all(
            "SELECT user_id,level,total_seconds FROM vc_ranks WHERE guild_id=? "
            "ORDER BY total_seconds DESC LIMIT 10",
            (ctx.guild.id,),
        )
        if not rows:
            return await ctx.send("No voice activity has been recorded yet.")
        await ctx.send("🏆 **Voice leaderboard:**\n" + "\n".join(
            f"{i}. <@{row['user_id']}> — Level {row['level']} — {self.format_time(row['total_seconds'])}"
            for i, row in enumerate(rows, start=1)
        ))


async def setup(bot: commands.Bot):
    await bot.add_cog(VCRank(bot))
