# utils/checks.py
import discord
from discord import app_commands
from discord.ext import commands
from botconfig import user_has_permission, get_required_roles, _has_role


def require_role(command_name: str):
    """Decorator l Slash Commands — check wach l-user 3endou role."""
    async def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            raise app_commands.CheckFailure("❌ Had command khedma ghir f server!")

        if user_has_permission(interaction.user, command_name):
            return True

        required = get_required_roles(command_name)
        if required:
            # 👇 HNA L-FIX: Converti les IDs (int) l mentions (<@&ID>) w les smiyat l bold (**Name**)
            roles_str = ", ".join(f"<@&{r}>" if isinstance(r, int) else f"**{r}**" for r in required)
            raise app_commands.CheckFailure(
                f"❌ Ma 3ndkch permission! Khass role: {roles_str}"
            )
        raise app_commands.CheckFailure("❌ Ma 3ndkch permission!")

    return app_commands.check(predicate)


def require_role_prefix(command_name: str):
    """Decorator l Prefix Commands — check wach l-user 3endou role."""
    async def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild:
            raise commands.CheckFailure("❌ Had command khedma ghir f server!")

        if user_has_permission(ctx.author, command_name):
            return True

        required = get_required_roles(command_name)
        if required:
            # 👇 HNA L-FIX: Converti les IDs (int) l mentions (<@&ID>) w les smiyat l bold (**Name**)
            roles_str = ", ".join(f"<@&{r}>" if isinstance(r, int) else f"**{r}**" for r in required)
            raise commands.CheckFailure(
                f"❌ Ma 3ndkch permission! Khass role: {roles_str}"
            )
        raise commands.CheckFailure("❌ Ma 3ndkch permission!")

    return commands.check(predicate)


# ═══════════════════════════════════════════════════════════════════
# ─── require_any_role (slash) — Helper w fo9
# ═══════════════════════════════════════════════════════════════════
def require_any_role(*role_refs):
    """Decorator: user khass ykoun 3endou WA7ED mn had roles."""
    async def predicate(interaction: discord.Interaction) -> bool:
        member = interaction.user
        if not isinstance(member, discord.Member) or member.guild is None:
            raise app_commands.CheckFailure("❌ Ghir f server!")
            
        if member.id == member.guild.owner_id:
            return True

        # 👇 Khdemna b _has_role li kat-handli int w str bach l-announce w l-embed ykhdmou
        for ref in role_refs:
            if _has_role(member, ref):
                return True

        raise app_commands.CheckFailure(
            "❌ Khass tkoun **Helper**, **Moderator**, wla **Admin**!"
        )

    return app_commands.check(predicate)


# ═══════════════════════════════════════════════════════════════════
# ─── require_any_role_prefix (prefix)
# ═══════════════════════════════════════════════════════════════════
def require_any_role_prefix(*role_refs):
    """Decorator: prefix — user khass ykoun 3endou WA7ED mn had roles."""
    async def predicate(ctx: commands.Context) -> bool:
        member = ctx.author
        if not isinstance(member, discord.Member) or member.guild is None:
            raise commands.CheckFailure("❌ Ghir f server!")
            
        if member.id == member.guild.owner_id:
            return True

        # 👇 Khdemna b _has_role li kat-handli int w str bach l-announce w l-embed ykhdmou
        for ref in role_refs:
            if _has_role(member, ref):
                return True

        raise commands.CheckFailure(
            "❌ Khass tkoun **Helper**, **Moderator**, wla **Admin**!"
        )

    return commands.check(predicate)