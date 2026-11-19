# cogs/serverstats.py
# =====================================================================
# ─── SERVER STATS & INFO — Stats, Role Info, Roles List
# =====================================================================
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

class ServerStats(commands.Cog):
    """Stats dyal server + info 3la roles"""

    def __init__(self, bot):
        self.bot = bot

    # ═══════════════════════════════════════════════════════════
    # ─── /serverstats & +serverstats
    # ═══════════════════════════════════════════════════════════
    def _build_serverstats(self, guild: discord.Guild) -> discord.Embed:
        online = sum(1 for m in guild.members if m.status != discord.Status.offline)
        bots = sum(1 for m in guild.members if m.bot)
        humans = guild.member_count - bots

        embed = discord.Embed(
            title=f"📊 Stats — {guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "?", inline=True)
        embed.add_field(name="📅 Created", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="🆔 ID", value=f"`{guild.id}`", inline=True)

        embed.add_field(name="👥 Total Members", value=f"`{guild.member_count}`", inline=True)
        embed.add_field(name="🟢 Online", value=f"`{online}`", inline=True)
        embed.add_field(name="👤 Humans / 🤖 Bots", value=f"`{humans}` / `{bots}`", inline=True)

        embed.add_field(name="💬 Channels", value=f"`{len(guild.channels)}`", inline=True)
        embed.add_field(name="🎭 Roles", value=f"`{len(guild.roles)}`", inline=True)
        embed.add_field(name="🚀 Boosts", value=f"Level `{guild.premium_tier}` (`{guild.premium_subscription_count}` boosts)", inline=True)

        embed.set_footer(text=f"Requested by {guild.me.name}", icon_url=guild.me.display_avatar.url)
        return embed

    @app_commands.command(name="serverstats", description="📊 Stats kamla dyal server")
    async def serverstats_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self._build_serverstats(interaction.guild))

    @commands.command(name="serverstats", aliases=["ss", "stats"])
    async def serverstats_prefix(self, ctx: commands.Context):
        """+serverstats — Stats kamla dyal server"""
        await ctx.send(embed=self._build_serverstats(ctx.guild))

    # ═══════════════════════════════════════════════════════════
    # ─── /roleinfo & +roleinfo
    # ═══════════════════════════════════════════════════════════
    def _build_roleinfo(self, role: discord.Role) -> discord.Embed:
        embed = discord.Embed(
            title=f"🎭 Role Info — {role.name}",
            color=role.color if role.color != discord.Color.default() else discord.Color.blurple(),
            timestamp=datetime.now()
        )

        embed.add_field(name="🆔 ID", value=f"`{role.id}`", inline=True)
        embed.add_field(name="🎨 Color", value=f"`{str(role.color)}`", inline=True)
        embed.add_field(name="📅 Created", value=f"<t:{int(role.created_at.timestamp())}:R>", inline=True)

        embed.add_field(name="👥 Members", value=f"`{len(role.members)}`", inline=True)
        embed.add_field(name="📊 Position", value=f"`#{len(role.guild.roles) - role.position}`", inline=True)
        embed.add_field(name="🔔 Mentionable", value=f"`{role.mentionable}`", inline=True)

        # Permissions dyal role
        perms = []
        if role.permissions.administrator: perms.append("Administrator")
        if role.permissions.manage_guild: perms.append("Manage Server")
        if role.permissions.manage_roles: perms.append("Manage Roles")
        if role.permissions.manage_channels: perms.append("Manage Channels")
        if role.permissions.kick_members: perms.append("Kick Members")
        if role.permissions.ban_members: perms.append("Ban Members")
        if role.permissions.manage_messages: perms.append("Manage Messages")
        
        perms_str = ", ".join(perms) if perms else "None"
        embed.add_field(name="🔑 Big Permissions", value=perms_str, inline=False)

        # Top 5 members li 3ndhom had role
        if len(role.members) > 0:
            top_members = [m.mention for m in list(role.members)[:5]]
            embed.add_field(name="👤 Some Members", value=", ".join(top_members), inline=False)

        embed.set_footer(text=f"Requested by {role.guild.me.name}")
        return embed

    @app_commands.command(name="roleinfo", description="🎭 Info 3la chi role")
    @app_commands.describe(role="L-role li bghiti tchouf info dyalo")
    async def roleinfo_slash(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(embed=self._build_roleinfo(role))

    @commands.command(name="roleinfo", aliases=["ri"])
    async def roleinfo_prefix(self, ctx: commands.Context, *, role: discord.Role):
        """+roleinfo @role — Info 3la chi role"""
        await ctx.send(embed=self._build_roleinfo(role))

    # ═══════════════════════════════════════════════════════════
    # ─── /roleslist & +roleslist
    # ═══════════════════════════════════════════════════════════
    def _build_roleslist(self, guild: discord.Guild) -> discord.Embed:
        embed = discord.Embed(
            title=f"📋 Roles List — {guild.name}",
            description=f"Total: `{len(guild.roles) - 1}` roles",
            color=discord.Color.blurple(),
        )
        
        roles = [r for r in guild.roles if not r.is_default()]
        roles.reverse()  # mn l-fo9 l-te7t
        
        lines = []
        for r in roles[:30]:
            lines.append(f"{r.mention} — `{len(r.members)}` members (Pos: {r.position})")
        
        embed.description = "\n".join(lines) if lines else "Ma kaynch roles!"
        if len(roles) > 30:
            embed.set_footer(text=f"... w {len(roles) - 30} roles khrin.")
            
        return embed

    @app_commands.command(name="roleslist", description="📋 List dyal ga3 les roles w ch7al fihom")
    async def roleslist_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self._build_roleslist(interaction.guild))

    @commands.command(name="roleslist", aliases=["rlist"])
    async def roleslist_prefix(self, ctx: commands.Context):
        """+roleslist — List dyal ga3 les roles"""
        await ctx.send(embed=self._build_roleslist(ctx.guild))


async def setup(bot):
    await bot.add_cog(ServerStats(bot))