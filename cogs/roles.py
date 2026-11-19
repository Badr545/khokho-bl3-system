# cogs/roles.py
# =====================================================================
# ─── ROLE MANAGEMENT — Giverole, Removerole, Massrole, Striprole
# =====================================================================
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from utils.checks import require_role, require_role_prefix
from utils.confirm import confirm_action


class Roles(commands.Cog):
    """Role management: giverole, removerole, massrole, striprole"""

    def __init__(self, bot):
        self.bot = bot

    def _check_hierarchy(self, author: discord.Member, role: discord.Role) -> bool:
        """Check wach l-user 3ndou 7a9 3la had role"""
        if author.id == author.guild.owner_id:
            return True
        return role < author.top_role

    async def _log_role_change(self, guild, target, role, action: str, mod):
        """Log dyal taghyir dyal role f channel dyal logs"""
        cog = self.bot.get_cog("Logs")
        if not cog:
            return
        try:
            ch = cog._channel(guild, "role")
            if not ch:
                return
            emoji = "➕" if action == "add" else "➖"
            color = discord.Color.green() if action == "add" else discord.Color.red()
            embed = discord.Embed(
                title=f"🎭 Role {'Added' if action == 'add' else 'Removed'}",
                color=color,
            )
            embed.set_author(name=str(target), icon_url=target.display_avatar.url)
            embed.add_field(name="👤 User", value=f"{target.mention}\n`{target.id}`", inline=False)
            embed.add_field(name=f"{emoji} Role", value=role.mention, inline=False)
            embed.add_field(name="👮 By", value=mod.mention, inline=False)
            await ch.send(embed=embed)
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════
    # ─── /giverole & +giverole
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="giverole", description="3ti role l member")
    @app_commands.describe(member="L-member", role="Role li bghiti t3ti")
    @require_role("giverole")
    async def giverole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if not self._check_hierarchy(interaction.user, role):
            return await interaction.response.send_message("❌ Ma tqderch t3ti role fo9 dyalek!", ephemeral=True)

        bot_member = interaction.guild.get_member(self.bot.user.id)
        if bot_member and role >= bot_member.top_role:
            return await interaction.response.send_message("❌ Role fo9 role dyal bot!", ephemeral=True)

        if role in member.roles:
            return await interaction.response.send_message(f"⚠️ {member.mention} deja 3endou {role.mention}!", ephemeral=True)

        try:
            await member.add_roles(role, reason=f"Par {interaction.user.name}")
            embed = discord.Embed(
                title="✅ Role Added",
                description=f"**{role.mention}** t-3ta l {member.mention}",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed)
            await self._log_role_change(interaction.guild, member, role, "add", interaction.user)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Ma 3ndich permission!", ephemeral=True)

    @commands.command(name="giverole", aliases=["addrole"])
    @require_role_prefix("giverole")
    @commands.bot_has_permissions(manage_roles=True)
    async def giverole_prefix(self, ctx: commands.Context, member: discord.Member, *, role: discord.Role):
        """+giverole @user @role"""
        if not self._check_hierarchy(ctx.author, role):
            return await ctx.send("❌ Role fo9 dyalek!")
        if role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Role fo9 role dyal bot!")
        if role in member.roles:
            return await ctx.send(f"⚠️ Deja 3endou {role.mention}!")
        try:
            await member.add_roles(role, reason=f"Par {ctx.author.name}")
            await ctx.send(f"✅ **{role.mention}** t-3ta l {member.mention}")
            await self._log_role_change(ctx.guild, member, role, "add", ctx.author)
        except discord.Forbidden:
            await ctx.send("❌ Ma 3ndich permission!")

    # ═══════════════════════════════════════════════════════════
    # ─── /removerole & +removerole
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="removerole", description="Hyed role mn member")
    @app_commands.describe(member="L-member", role="Role li bghiti thyed")
    @require_role("removerole")
    async def removerole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if not self._check_hierarchy(interaction.user, role):
            return await interaction.response.send_message("❌ Ma tqderch thyed role fo9 dyalek!", ephemeral=True)

        if role not in member.roles:
            return await interaction.response.send_message(f"⚠️ {member.mention} ma 3endouch {role.mention}!", ephemeral=True)

        try:
            await member.remove_roles(role, reason=f"Par {interaction.user.name}")
            embed = discord.Embed(
                title="✅ Role Removed",
                description=f"**{role.mention}** t-hyed mn {member.mention}",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed)
            await self._log_role_change(interaction.guild, member, role, "remove", interaction.user)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Ma 3ndich permission!", ephemeral=True)

    @commands.command(name="removerole", aliases=["delrole"])
    @require_role_prefix("removerole")
    @commands.bot_has_permissions(manage_roles=True)
    async def removerole_prefix(self, ctx: commands.Context, member: discord.Member, *, role: discord.Role):
        """+removerole @user @role"""
        if not self._check_hierarchy(ctx.author, role):
            return await ctx.send("❌ Role fo9 dyalek!")
        if role not in member.roles:
            return await ctx.send(f"⚠️ Ma 3endouch {role.mention}!")
        try:
            await member.remove_roles(role, reason=f"Par {ctx.author.name}")
            await ctx.send(f"✅ **{role.mention}** t-hyed mn {member.mention}")
            await self._log_role_change(ctx.guild, member, role, "remove", ctx.author)
        except discord.Forbidden:
            await ctx.send("❌ Ma 3ndich permission!")

    # ═══════════════════════════════════════════════════════════
    # ─── /massrole — Slash
    # ═══════════════════════════════════════════════════════════
    @app_commands.command(name="massrole", description="3ti role l ga3 l-members")
    @app_commands.describe(role="Role li bghiti t3ti", bots="3ti l bots?")
    @require_role("massrole")
    async def massrole(self, interaction: discord.Interaction, role: discord.Role, bots: bool = False):
        if not self._check_hierarchy(interaction.user, role):
            return await interaction.response.send_message("❌ Role fo9 dyalek!", ephemeral=True)

        bot_member = interaction.guild.get_member(self.bot.user.id)
        if bot_member and role >= bot_member.top_role:
            return await interaction.response.send_message("❌ Role fo9 role dyal bot!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        count, failed = 0, 0
        sem = asyncio.Semaphore(5)

        async def add_safe(m):
            nonlocal count, failed
            async with sem:
                try:
                    await m.add_roles(role, reason=f"Massrole par {interaction.user.name}")
                    count += 1
                except Exception:
                    failed += 1
                await asyncio.sleep(0.3)

        tasks = []
        for m in interaction.guild.members:
            if m.bot and not bots:
                continue
            if role in m.roles:
                continue
            tasks.append(add_safe(m))

        await asyncio.gather(*tasks, return_exceptions=True)

        await interaction.followup.send(
            f"✅ **{role.mention}** t-3ta l `{count}` members!\n"
            f"❌ Failed: `{failed}`",
            ephemeral=True,
        )

    # ═══════════════════════════════════════════════════════════
    # ─── +massrole — Prefix
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="massrole")
    @require_role_prefix("massrole")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def massrole_prefix(self, ctx: commands.Context, role: discord.Role, bots: bool = False):
        """+massrole @role [bots]"""
        if not self._check_hierarchy(ctx.author, role):
            return await ctx.send("❌ Role fo9 dyalek!")
        if role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Role fo9 role dyal bot!")

        if not await confirm_action(
            ctx,
            "Mass Role",
            f"3ti {role.mention} l **GA3** l-members?\n"
            f"**Bots:** {'Yes' if bots else 'No'}",
        ):
            return

        msg = await ctx.send("⏳ Kan-3ti role...")

        count, failed = 0, 0
        sem = asyncio.Semaphore(5)

        async def add_safe(m):
            nonlocal count, failed
            async with sem:
                try:
                    await m.add_roles(role, reason=f"Massrole par {ctx.author}")
                    count += 1
                except Exception:
                    failed += 1
                await asyncio.sleep(0.3)

        tasks = [
            add_safe(m) for m in ctx.guild.members
            if (bots or not m.bot) and role not in m.roles
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        await msg.edit(content=(
            f"✅ **{role.mention}** t-3ta l `{count}` members!\n"
            f"❌ Failed: `{failed}`"
        ))

    # ═══════════════════════════════════════════════════════════
    # ─── +striprole
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="striprole")
    @require_role_prefix("massrole")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def striprole(self, ctx: commands.Context, role: discord.Role):
        """+striprole @role — Hyed role mn GA3 l-members"""
        if role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Role fo9 role dyal bot!")
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ Role fo9 dyalek!")

        if len(role.members) == 0:
            return await ctx.send(f"⚠️ {role.mention} ma 3endha ta member!")

        if not await confirm_action(
            ctx,
            "Strip Role",
            f"Hyed {role.mention} mn **GA3** l-members li 3endhom? (`{len(role.members)}` members)",
        ):
            return

        msg = await ctx.send("⏳ Kan-hyed role...")

        count, failed = 0, 0
        for member in list(role.members):
            try:
                await member.remove_roles(role, reason=f"Striprole par {ctx.author}")
                count += 1
                await asyncio.sleep(0.3)
            except Exception:
                failed += 1

        await msg.edit(content=(
            f"✅ **{role.mention}** t-7yed mn `{count}` members!\n"
            f"❌ Failed: `{failed}`"
        ))


async def setup(bot):
    await bot.add_cog(Roles(bot))