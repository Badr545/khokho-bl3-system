# cogs/sysinfo.py
# ═══════════════════════════════════════════════════════════════════
# ─── SYSINFO — Ysift status kola chwiya
# ═══════════════════════════════════════════════════════════════════
import discord
from discord.ext import commands, tasks
from datetime import datetime
import time
import platform
import botconfig


START_TIME = time.time()


class SysInfo(commands.Cog):
    """Periodic system info"""

    def __init__(self, bot):
        self.bot = bot
        if botconfig.CHANNEL_SYSINFO:
            self.sysinfo_loop.start()

    def cog_unload(self):
        self.sysinfo_loop.cancel()

    def _build_embed(self) -> discord.Embed:
        uptime_sec = int(time.time() - START_TIME)
        d, rem = divmod(uptime_sec, 86400)
        h, rem = divmod(rem, 3600)
        m, s = divmod(rem, 60)
        uptime_str = f"{d}d {h}h {m}m {s}s" if d else f"{h}h {m}m {s}s"

        total_members = sum(g.member_count or 0 for g in self.bot.guilds)
        total_cmds = len(self.bot.commands) + len(self.bot.tree.get_commands())

        embed = discord.Embed(
            title="📊 System Info",
            description=f"**{self.bot.user.name}** status",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(name="⏱️ Uptime", value=f"`{uptime_str}`", inline=True)
        embed.add_field(name="📡 Latency", value=f"`{round(self.bot.latency*1000)}ms`", inline=True)
        embed.add_field(name="🐍 Python", value=f"`{platform.python_version()}`", inline=True)

        embed.add_field(name="🏠 Servers", value=f"`{len(self.bot.guilds)}`", inline=True)
        embed.add_field(name="👥 Users", value=f"`{total_members:,}`", inline=True)
        embed.add_field(name="⚙️ Commands", value=f"`{total_cmds}`", inline=True)

        embed.set_footer(text="Auto-updated")
        return embed

    @tasks.loop(minutes=botconfig.SYSINFO_INTERVAL_MINUTES or 30)
    async def sysinfo_loop(self):
        try:
            channel = self.bot.get_channel(botconfig.CHANNEL_SYSINFO)
            if channel is None:
                return

            # Edit last bot message if exists, wla sift jdid
            async for msg in channel.history(limit=5):
                if msg.author.id == self.bot.user.id and msg.embeds:
                    try:
                        await msg.edit(embed=self._build_embed())
                        return
                    except Exception:
                        break

            await channel.send(embed=self._build_embed())
        except Exception as e:
            print(f"❌ SysInfo loop: {e}")

    @sysinfo_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    # ─── +sysinfo (manual)
    @commands.command(name="sysinfo")
    @commands.has_permissions(administrator=True)
    async def sysinfo_cmd(self, ctx: commands.Context):
        """+sysinfo — Chouf status daba"""
        await ctx.send(embed=self._build_embed())


async def setup(bot):
    await bot.add_cog(SysInfo(bot))