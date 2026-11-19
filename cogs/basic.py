# =====================================================================
# ─── BASIC COMMANDS
# =====================================================================
import discord
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime
from utils.checks import require_role, require_role_prefix


class Basic(commands.Cog):
    """Basic commands: ping, say, ms7, userinfo, serverinfo, avatar"""

    def __init__(self, bot):
        self.bot = bot

    # ─── Fonction m3awla bach nsaybo l-embed dyal userinfo
    def _build_userinfo_embed(self, member: discord.Member) -> discord.Embed:
        # Color: nakhdo l-loun dyal l-role l-fo9, ila makanch nakhdo loun default
        color = member.color if member.color != discord.Color.default() else discord.Color.blurple()
        
        embed = discord.Embed(
            title=f"{member.name}",
            color=color
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        # ─── Ligne 1: Username, ID, Joined Server, Joined Discord
        embed.add_field(name="Username", value=f"{member.name}", inline=True)
        embed.add_field(name="User ID", value=f"{member.id}", inline=True)
        
        joined_server = f"<t:{int(member.joined_at.timestamp())}:R>" if member.joined_at else "Unknown"
        joined_discord = f"<t:{int(member.created_at.timestamp())}:R>"
        
        embed.add_field(name="Joined Server", value=joined_server, inline=True)
        embed.add_field(name="Joined Discord", value=joined_discord, inline=True)

        # ─── Roles
        roles = [r.mention for r in member.roles if not r.is_default()]
        roles_str = ", ".join(roles) if roles else "None"
        # Discord kayqbel ghir 1024 character f field, donc ila twel bzaf nqta3oh
        if len(roles_str) > 1024:
            roles_str = roles_str[:1020] + "..."
        embed.add_field(name="Roles", value=roles_str, inline=False)

        # ─── Big Perms (Permissions Kbar)
        perms = []
        if member.guild_permissions.administrator: perms.append("Administrator")
        if member.guild_permissions.manage_guild: perms.append("Manage Server")
        if member.guild_permissions.manage_roles: perms.append("Manage Roles")
        if member.guild_permissions.manage_channels: perms.append("Manage Channels")
        if member.guild_permissions.kick_members: perms.append("Kick Members")
        if member.guild_permissions.ban_members: perms.append("Ban Members")
        
        perms_str = ", ".join(perms) if perms else "None"
        embed.add_field(name="Big Perms", value=perms_str, inline=False)

        # ─── Voice Channel (Ila kan f voice)
        if member.voice and member.voice.channel:
            vc = member.voice.channel
            embed.add_field(name="Voice Channel", value=f"🔊 {vc.mention}", inline=False)
            
            # Members in Channel (Nass li m3ah f voice)
            members_in_vc = [m.mention for m in vc.members]
            if members_in_vc:
                vc_members_str = f"**[{len(members_in_vc)}]** " + ", ".join(members_in_vc)
                if len(vc_members_str) > 1024:
                    vc_members_str = vc_members_str[:1020] + "..."
                embed.add_field(name="Members in Channel", value=vc_members_str, inline=False)

        # ─── Footer
        embed.set_footer(text=f"{member.guild.name} • Today at {datetime.now().strftime('%H:%M')}")
        
        return embed

    # ─── /ping
    @app_commands.command(name="ping", description="Katchouf l-latency dyal l-bot")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.defer()
        msg = await interaction.followup.send("🏓 ...")
        api_ms = round((datetime.now() - msg.created_at.replace(tzinfo=None)).total_seconds() * 1000)
        await msg.edit(content=f"🏓 Pong! | Websocket: `{round(self.bot.latency * 1000)}ms` | API: `{api_ms}ms`")

    # ─── /say
    @app_commands.command(name="say", description="L-bot gha y3awd dakchi li ktabti")
    @app_commands.describe(text_to_say="L-message")
    async def say(self, interaction: discord.Interaction, text_to_say: str):
        await interaction.response.send_message(f"🗣️ {text_to_say}")

    # ─── /ms7
    @app_commands.command(name="ms7", description="Msa7 l-messages")
    @app_commands.describe(amount="Ch7al (max 100)")
    @require_role("ms7")
    @app_commands.checks.bot_has_permissions(manage_messages=True, read_message_history=True)
    async def ms7(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ Cleaned `{len(deleted)}` messages!", ephemeral=True)

    # ─── /userinfo
    @app_commands.command(name="userinfo", description="Ma3loumat dyal user")
    @app_commands.describe(member="L-user")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer()
        if member is None:
            member = interaction.user
        
        embed = self._build_userinfo_embed(member)
        await interaction.followup.send(embed=embed)

    # ─── /serverinfo
    @app_commands.command(name="serverinfo", description="Ma3loumat 3la l-server")
    async def serverinfo(self, interaction: discord.Interaction):
        await interaction.response.defer()
        g = interaction.guild
        embed = discord.Embed(title=f"🏰 {g.name}", color=discord.Color.blue(), timestamp=datetime.now())
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="👑 Owner", value=g.owner.mention if g.owner else "?", inline=True)
        embed.add_field(name="👥 Members", value=f"`{g.member_count}`", inline=True)
        embed.add_field(name="🎭 Roles", value=f"`{len(g.roles)}`", inline=True)
        embed.add_field(name="📅 Created", value=g.created_at.strftime("%Y-%m-%d"), inline=True)
        await interaction.followup.send(embed=embed)

    # ─── /avatar
    @app_commands.command(name="avatar", description="Avatar dyal user")
    @app_commands.describe(member="L-user")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user
        embed = discord.Embed(title=f"🖼️ {member.name}", color=discord.Color.purple())
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ═══════════════ PREFIX COMMANDS ═══════════════

    @commands.command(name="ping")
    async def ping_prefix(self, ctx: commands.Context):
        """&ping"""
        await ctx.send(f"🏓 Pong! | `{round(self.bot.latency * 1000)}ms`")

    @commands.command(name="say", aliases=["echo"])
    async def say_prefix(self, ctx: commands.Context, *, text: str):
        """+say <text> | +echo <text>"""
        await ctx.send(f"🗣️ {text}")

    @commands.command(name="ms7", aliases=["clear", "purge"])
    @require_role_prefix("ms7")
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    async def ms7_prefix(self, ctx: commands.Context, amount: int = 5):
        """+ms7 <amount> | Aliases: +clear, +purge"""
        if amount < 1 or amount > 100:
            return await ctx.send("❌ Bin `1` w `100`!")
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"✅ Cleaned `{len(deleted)-1}`!", delete_after=5)

    @commands.command(name="userinfo", aliases=["u", "ra"]) # 👈 Aliases bach l-7arf u ykhdem
    async def userinfo_prefix(self, ctx: commands.Context, member: discord.Member = None):
        """&userinfo [@user]"""
        if member is None:
            member = ctx.author
            
        embed = self._build_userinfo_embed(member)
        await ctx.send(embed=embed)

    @commands.command(name="serverinfo")
    async def serverinfo_prefix(self, ctx: commands.Context):
        """&serverinfo"""
        g = ctx.guild
        embed = discord.Embed(title=f"🏰 {g.name}", color=discord.Color.blue())
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="👑 Owner", value=g.owner.mention if g.owner else "?", inline=True)
        embed.add_field(name="👥 Members", value=f"`{g.member_count}`", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="avatar", aliases=["a"]) # 👈 Zedt alias a bach ykhdem ila bghiti
    async def avatar_prefix(self, ctx: commands.Context, member: discord.Member = None):
        """&avatar [@user]"""
        if member is None:
            member = ctx.author
        embed = discord.Embed(title=f"🖼️ {member.name}", color=discord.Color.purple())
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Basic(bot))