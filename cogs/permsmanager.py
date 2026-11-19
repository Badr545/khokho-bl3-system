# cogs/permsmanager.py
# ═══════════════════════════════════════════════════════════════════
# ─── PERMISSIONS MANAGER — 3ti role perms 3la group dyal commands
# ═══════════════════════════════════════════════════════════════════
import discord
from discord.ext import commands
import json
import os
import botconfig

DATA_FILE = "data/dynamic_perms.json"


def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return {int(g): {int(r): v for r, v in d.items()} for g, d in raw.items()}
    except Exception:
        return {}


def _save():
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(DYNAMIC, f, indent=2, ensure_ascii=False)


DYNAMIC = _load()
# {guild_id: {role_id: [group1, group2, ...]}}


# ═══════════════════════════════════════════════════════════════════
# ─── PUBLIC API (kayst3mlha botconfig.user_has_permission)
# ═══════════════════════════════════════════════════════════════════
def has_dynamic_perm(member: discord.Member, command_name: str) -> bool:
    """Check wach member 3endou role li 3endha dynamic perm l had command."""
    gid = member.guild.id
    guild_perms = DYNAMIC.get(gid, {})
    if not guild_perms:
        return False

    # Find which groups contain this command
    command_groups = set()
    for group_name, data in botconfig.COMMAND_PERMISSIONS.items():
        if command_name in data["commands"]:
            command_groups.add(group_name)

    if not command_groups:
        return False

    member_role_ids = {r.id for r in member.roles}
    for role_id, groups in guild_perms.items():
        if role_id in member_role_ids:
            if any(g in command_groups for g in groups):
                return True
    return False


# ═══════════════════════════════════════════════════════════════════
# ─── COG
# ═══════════════════════════════════════════════════════════════════
class PermsManager(commands.Cog):
    """Manage dynamic role permissions"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="perms", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def perms_group(self, ctx: commands.Context):
        """+perms — Help"""
        groups = list(botconfig.COMMAND_PERMISSIONS.keys())
        embed = discord.Embed(
            title="🔐 Permissions Manager",
            description="Give/revoke command-group access to roles.",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="Available Groups",
            value="\n".join(f"• `{g}`" for g in groups),
            inline=False,
        )
        embed.add_field(
            name="Commands",
            value=(
                "`+perms grant @role <group>` — 3ti perm\n"
                "`+perms revoke @role <group>` — hyed perm\n"
                "`+perms list` — chouf kolchi\n"
                "`+perms check @role` — chouf perms dyal role\n"
                "`+perms reset` — reset kolchi"
            ),
            inline=False,
        )
        await ctx.send(embed=embed)

    @perms_group.command(name="grant")
    @commands.has_permissions(administrator=True)
    async def grant(self, ctx: commands.Context, role: discord.Role, group: str):
        """+perms grant @role <group>"""
        group = group.lower().strip()
        if group not in botconfig.COMMAND_PERMISSIONS:
            return await ctx.send(
                f"❌ Group `{group}` ma kaynch!\n"
                f"Groups: {', '.join(f'`{g}`' for g in botconfig.COMMAND_PERMISSIONS)}"
            )

        guild_perms = DYNAMIC.setdefault(ctx.guild.id, {})
        role_groups = set(guild_perms.get(role.id, []))
        role_groups.add(group)
        guild_perms[role.id] = sorted(role_groups)
        _save()

        embed = discord.Embed(
            title="✅ Permission Granted",
            description=f"Role {role.mention} → `{group}`",
            color=discord.Color.green(),
        )
        cmds = botconfig.COMMAND_PERMISSIONS[group]["commands"]
        embed.add_field(
            name=f"Commands ({len(cmds)})",
            value=" ".join(f"`{c}`" for c in cmds[:20])
            + (f" +{len(cmds)-20}" if len(cmds) > 20 else ""),
            inline=False,
        )
        await ctx.send(embed=embed)

    @perms_group.command(name="revoke")
    @commands.has_permissions(administrator=True)
    async def revoke(self, ctx: commands.Context, role: discord.Role, group: str):
        """+perms revoke @role <group>"""
        group = group.lower().strip()
        guild_perms = DYNAMIC.get(ctx.guild.id, {})
        if role.id not in guild_perms or group not in guild_perms[role.id]:
            return await ctx.send(f"⚠️ Role {role.mention} ma 3ndhach `{group}`!")

        guild_perms[role.id].remove(group)
        if not guild_perms[role.id]:
            del guild_perms[role.id]
        _save()
        await ctx.send(f"✅ Revoked `{group}` mn {role.mention}")

    @perms_group.command(name="list")
    async def list_perms(self, ctx: commands.Context):
        """+perms list"""
        guild_perms = DYNAMIC.get(ctx.guild.id, {})
        if not guild_perms:
            return await ctx.send("📋 Ma kaynch perms dynamiques!")

        embed = discord.Embed(
            title="🔐 Dynamic Permissions",
            color=discord.Color.blurple(),
        )
        for role_id, groups in guild_perms.items():
            role = ctx.guild.get_role(role_id)
            role_str = role.mention if role else f"`{role_id}` (❌)"
            embed.add_field(
                name=role_str,
                value=", ".join(f"`{g}`" for g in groups),
                inline=False,
            )
        await ctx.send(embed=embed)

    @perms_group.command(name="check")
    async def check(self, ctx: commands.Context, role: discord.Role):
        """+perms check @role"""
        guild_perms = DYNAMIC.get(ctx.guild.id, {})
        groups = guild_perms.get(role.id, [])
        if not groups:
            return await ctx.send(f"📋 {role.mention} ma 3ndhach dynamic perms.")
        embed = discord.Embed(
            title=f"🔐 {role.name}",
            description=", ".join(f"`{g}`" for g in groups),
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @perms_group.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx: commands.Context):
        """+perms reset"""
        from utils.confirm import confirm_action
        if not await confirm_action(
            ctx,
            "Reset Permissions",
            "Ghadi ymsa7 **GA3** dynamic perms f had server. Continue?",
        ):
            return
        DYNAMIC.pop(ctx.guild.id, None)
        _save()
        await ctx.send("✅ Reset kolchi.")

    # ─── +myperms
    @commands.command(name="myperms")
    async def myperms(self, ctx: commands.Context):
        """+myperms — Chouf perms dyalk"""
        guild_perms = DYNAMIC.get(ctx.guild.id, {})
        my_roles = {r.id for r in ctx.author.roles}
        my_groups = set()
        for role_id, groups in guild_perms.items():
            if role_id in my_roles:
                my_groups.update(groups)

        if ctx.author.id == ctx.guild.owner_id:
            return await ctx.send("👑 Nta owner — 3endek kolchi.")

        if not my_groups:
            return await ctx.send("❌ Ma 3endekch dynamic perms.")

        embed = discord.Embed(
            title="🔐 Your Permissions",
            description="\n".join(f"• `{g}`" for g in sorted(my_groups)),
            color=discord.Color.green(),
        )
        embed.set_footer(text=f"{ctx.author.name}")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(PermsManager(bot))