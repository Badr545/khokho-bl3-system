# cogs/admin.py
# =====================================================================
# ─── ADMIN COMMANDS (Role-Based + Warn + Jail + Timeout + Unban)
#     Prefix: + (action) / - (remove)
# =====================================================================
import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import utcnow
from datetime import timedelta
from utils.checks import require_role, require_role_prefix
from utils.confirm import confirm_action
from data_manager import WARNINGS, save_warnings as _save_warnings
import botconfig
import json
import os
import asyncio

# ═══════════════════════════════════════════════════════════════════
# ─── JAIL CONFIG
# ═══════════════════════════════════════════════════════════════════
JAIL_ROLE_ID = botconfig.JAIL_ROLE_ID
JAIL_FILE = "data/jail.json"


def _load_jailed():
    if not os.path.exists(JAIL_FILE):
        return {}
    try:
        with open(JAIL_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return {int(g): {int(u): v for u, v in d.items()} for g, d in raw.items()}
    except Exception as e:
        print(f"⚠️ Load jail failed: {e}")
        return {}


def _save_jailed():
    os.makedirs("data", exist_ok=True)
    try:
        with open(JAIL_FILE, "w", encoding="utf-8") as f:
            json.dump(JAILED, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Save jail failed: {e}")


JAILED: dict = _load_jailed()


def parse_duration(s: str) -> int:
    """'1h30m' → seconds. Rje3 -1 ila format ghalat."""
    if not s:
        return -1
    s = s.strip().lower()
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    total = 0
    num = ""
    for c in s:
        if c.isdigit():
            num += c
        elif c in units:
            if not num:
                return -1
            total += int(num) * units[c]
            num = ""
        else:
            return -1
    if num:
        total += int(num)
    return total if total > 0 else -1


# ═══════════════════════════════════════════════════════════════════
# ─── WARN ROLES CONFIG
# ═══════════════════════════════════════════════════════════════════
WARN_ROLES = {
    1: ["❗First Warning", "First Warning"],
    2: ["‼️Second Warning", "Second Warning"],
    3: ["⁉️Last Warning", "Last Warning"],
}
WARN_JAIL_AT = 4  # 4th warn → auto-jail


class Admin(commands.Cog):
    """Admin: kick, ban, warn, warnings, slowmode, lock, unlock, jail, rta7, timeout"""

    def __init__(self, bot):
        self.bot = bot

    # ═══════════════════════════════════════════════════════════
    # ─── LOG HELPER
    # ═══════════════════════════════════════════════════════════
    async def _log(self, guild, action, target, mod, reason="N/A"):
        cog = self.bot.get_cog("Logs")
        if cog:
            try:
                await cog.log_moderation(guild, action, target, mod, reason)
            except Exception:
                pass

    # ═══════════════════════════════════════════════════════════
    # ─── WARN SYSTEM HELPERS
    # ═══════════════════════════════════════════════════════════
    def _get_warnings(self, guild_id: int, user_id: int) -> list:
        return WARNINGS.get(guild_id, {}).get(user_id, [])

    def _find_warn_role(self, guild, threshold: int):
        for name in WARN_ROLES.get(threshold, []):
            role = discord.utils.get(guild.roles, name=name)
            if role:
                return role
        return None

    async def _apply_warn_roles(self, member: discord.Member, count: int):
        for threshold in sorted(WARN_ROLES.keys()):
            role = self._find_warn_role(member.guild, threshold)
            if role is None:
                continue
            try:
                if count == threshold and role not in member.roles:
                    await member.add_roles(role, reason=f"Warn #{count}")
                elif count < threshold and role in member.roles:
                    await member.remove_roles(role, reason=f"Warn cleared (count={count})")
            except discord.Forbidden:
                pass

    async def _jail_member(self, guild, member, reason: str):
        jail_role = guild.get_role(JAIL_ROLE_ID)
        if jail_role is None:
            return False, "Jail role ma kaynch!"
        if guild.me.top_role.position <= jail_role.position:
            return False, "Jail role fo9 role dyal bot!"
        if guild.id in JAILED and member.id in JAILED[guild.id]:
            return False, "Deja msjoun!"

        saved_roles = [
            r.id for r in member.roles
            if not r.is_default() and r.id != JAIL_ROLE_ID
        ]
        JAILED.setdefault(guild.id, {})[member.id] = {
            "roles": saved_roles,
            "reason": reason,
            "mod": self.bot.user.id,
            "time": discord.utils.utcnow().isoformat(),
        }
        _save_jailed()

        try:
            removable = [
                r for r in member.roles
                if not r.is_default() and r.id != JAIL_ROLE_ID
            ]
            if removable:
                await member.remove_roles(*removable, reason=f"Auto-jail: {reason}")
            await member.add_roles(jail_role, reason=f"Auto-jail: {reason}")
        except discord.Forbidden:
            return False, "Ma 3ndich permission!"
        except Exception as e:
            return False, str(e)

        try:
            await member.send(
                f"🔒 **T-sjenti f {guild.name}**\n"
                f"**Reason:** {reason}\n"
                f"Bash ttla9: `+rta7` (wla 3ayet l-staff)"
            )
        except discord.Forbidden:
            pass

        return True, "OK"

    async def _apply_warn_punishment(self, member: discord.Member, count: int):
        if count >= WARN_JAIL_AT:
            ok, msg = await self._jail_member(
                member.guild, member,
                reason=f"Auto-jail: {count} warnings",
            )
            if ok:
                return "jail"
            return f"jail_failed:{msg}"
        return None

    def _format_action(self, punishment: str) -> str | None:
        if not punishment:
            return None
        if punishment == "jail":
            return "🔒 **JAILED** (auto at 4 warnings)"
        if punishment.startswith("jail_failed:"):
            err = punishment.split(":", 1)[1]
            return f"⚠️ **Jail failed:** `{err}`"
        return f"⚡ **{punishment.upper()}**"

    # ═══════════════════════════════════════════════════════════
    # ─── +aji / +move (Move Members Power)
    # ═══════════════════════════════════════════════════════════
    def has_move_power():
        async def predicate(ctx):
            if ctx.author.guild_permissions.administrator:
                return True
            # Role dyal Move Power
            if any(r.id == 1522731513291083776 for r in ctx.author.roles):
                return True
            # Staff Roles mn botconfig
            import botconfig
            staff_roles = botconfig.ADMIN_ROLES + botconfig.MODERATOR_ROLES + botconfig.HELPER_ROLES + botconfig.STAFF_ROLES
            if any(r.id in staff_roles for r in ctx.author.roles):
                return True
            
            raise commands.CheckFailure("❌ Ma 3ndekch l-7a9 b had command! (Khass tkoun Staff wla 3ndek Move Power)")
        return commands.check(predicate)

    @commands.command(name="move", aliases=["aji"])
    @has_move_power()
    @commands.bot_has_permissions(move_members=True)
    async def move_prefix(self, ctx, *, args: str = None):
        """
        +aji @user → yjib l-user l3ndek
        +aji @user1 @user2 → y-sift user1 l3nd user2
        +aji <user_id> <channel_id> → y-sift l-user l-channel mo3ayana
        """
        
        # 👇 إلا كتب غير +aji بلا ما يحط شي حاجة، يطلع ليه هاد الـ Embed
        if not args:
            embed = discord.Embed(
                title="⚙️ Command: move",
                description="Moves a member to another voice channel.",
                color=discord.Color.blurple()
            )
            embed.add_field(name="Aliases", value="`aji`", inline=False)
            embed.add_field(
                name="Usage", 
                value="`+move [user] [user or channel]`\n`+move all`", 
                inline=False
            )
            embed.add_field(
                name="Examples", 
                value=(
                    "`+move @Reda` (bring to you)\n"
                    "`+move @Reda @ProBot` (move to user)\n"
                    "`+move @Reda General` (move to channel)\n"
                    "`+move all` (move everyone to your channel)"
                ), 
                inline=False
            )
            return await ctx.send(embed=embed)
            
        # 👇 هنا زدنا خدمة +move all (كيجبد گاع الناس اللي فـ الـ Voice lـ channel ديالك)
        if args.lower() == "all":
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send("❌ Khass tkoun nta f voice channel bash tjib l-nass l3ndek!")
            
            target_channel = ctx.author.voice.channel
            count = 0
            msg = await ctx.send("⏳ Kanjib l-nass... (Stena chwiya)")
            
            for channel in ctx.guild.voice_channels:
                if channel.id == target_channel.id:
                    continue
                for member in channel.members:
                    if member.id != self.bot.user.id:
                        try:
                            await member.move_to(target_channel)
                            count += 1
                            await asyncio.sleep(0.3) # bash manaklouch Rate Limit
                        except:
                            pass
            return await msg.edit(content=f"✅ Jbedt `{count}` members l {target_channel.mention}!")
        
        parts = args.split()
        
        if len(parts) == 1:
            # Syntax 1: +aji @user
            try:
                target = await commands.MemberConverter().convert(ctx, parts[0])
            except:
                return await ctx.send("❌ Ma l9itch l-user!")
                
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.send("❌ Khass tkoun nta f voice channel bash tjib l-user l3ndek!")
                
            if not target.voice or not target.voice.channel:
                return await ctx.send("❌ Had l-user machi f voice channel!")
                
            try:
                await target.move_to(ctx.author.voice.channel)
                await ctx.send(f"✅ {target.mention} tnaqel l {ctx.author.voice.channel.mention}!")
            except discord.Forbidden:
                await ctx.send("❌ Ma 3ndich permission nnaqel had l-user!")
            except Exception as e:
                await ctx.send(f"❌ Mochkil: `{e}`")

        elif len(parts) == 2:
            # Syntax 2 & 3: +aji @user1 @user2 OR +aji @user1 <channel_name/id>
            try:
                target = await commands.MemberConverter().convert(ctx, parts[0])
            except:
                return await ctx.send("❌ L-user l-welani (target) ma l9itouch!")
                
            # Try to interpret second argument as Member
            try:
                target2 = await commands.MemberConverter().convert(ctx, parts[1])
                if not target2.voice or not target2.voice.channel:
                    return await ctx.send(f"❌ {target2.mention} machi f voice channel!")
                dest_channel = target2.voice.channel
            except:
                # If not a member, try as VoiceChannel
                try:
                    clean_ch = parts[1].replace("<#", "").replace(">", "")
                    dest_channel = await commands.VoiceChannelConverter().convert(ctx, clean_ch)
                except:
                    return await ctx.send("❌ Ma l9itch la l-user t-tani la l-channel (Voice)!")

            if not target.voice or not target.voice.channel:
                return await ctx.send("❌ L-user l-welani machi f voice channel!")
                
            try:
                await target.move_to(dest_channel)
                await ctx.send(f"✅ {target.mention} tnaqel l {dest_channel.mention}!")
            except discord.Forbidden:
                await ctx.send("❌ Ma 3ndich permission nnaqel had l-user!")
            except Exception as e:
                await ctx.send(f"❌ Mochkil: `{e}`")
                
        else:
            await ctx.send("❌ Kteb chi haja ghalta. Kteb `+aji` bash tchouf l-usage.")

    # ═══════════════════════════════════════════════════════════
    # ─── +warn (no confirm — mashi destructive)
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="warn")
    @require_role_prefix("warn")
    async def warn_prefix(self, ctx: commands.Context, member: discord.Member,
                          *, reason: str = "Ma 3endich reason"):
        """+warn @user [reason]"""
        if member.bot:
            return await ctx.send("❌ Ma tqderch t-warni bot!")
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ Role fo9 dyalek!")

        guild_id = ctx.guild.id
        WARNINGS.setdefault(guild_id, {}).setdefault(member.id, []).append({
            "reason": reason,
            "mod": ctx.author.id,
            "time": discord.utils.utcnow().isoformat(),
        })
        _save_warnings()
        count = len(WARNINGS[guild_id][member.id])

        await self._apply_warn_roles(member, count)
        punishment = await self._apply_warn_punishment(member, count)

        embed = discord.Embed(
            title="⚠️ Warning",
            description=f"{member.mention} t-3ta warning!",
            color=discord.Color.orange(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="📝 Reason", value=reason, inline=False)
        embed.add_field(name="👮 Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="📊 Total", value=f"`{count}`", inline=True)

        role_gained = None
        for threshold in sorted(WARN_ROLES.keys()):
            if count == threshold:
                role_gained = self._find_warn_role(ctx.guild, threshold)
                break
        if role_gained:
            embed.add_field(name="🎭 Role Added", value=role_gained.mention, inline=True)

        action_text = self._format_action(punishment)
        if action_text:
            embed.add_field(name="⚡ Action", value=action_text, inline=False)

        await ctx.send(embed=embed)

        # Log
        await self._log(ctx.guild, "warn", member, ctx.author, reason)

        try:
            dm = discord.Embed(
                title=f"⚠️ T-3titi warning f {ctx.guild.name}",
                description=f"**Reason:** {reason}\n**Total:** `{count}`",
                color=discord.Color.orange(),
            )
            if action_text:
                dm.add_field(name="⚡ Action", value=action_text, inline=False)
            await member.send(embed=dm)
        except discord.Forbidden:
            pass

    # ═══════════════════════════════════════════════════════════
    # ─── +warnings / +history
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="warnings", aliases=["history", "warns"])
    @require_role_prefix("warnings")
    async def warnings_prefix(self, ctx: commands.Context, member: discord.Member):
        """+warnings @user / +history @user"""
        warns = self._get_warnings(ctx.guild.id, member.id)

        embed = discord.Embed(
            title=f"📋 History — {member.name}",
            color=discord.Color.orange(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        if warns:
            for i, w in enumerate(warns[:10], 1):
                mod = ctx.guild.get_member(w.get("mod"))
                mod_name = mod.mention if mod else "?"
                embed.add_field(
                    name=f"#{i} — {w.get('time', '?')[:10]}",
                    value=f"**Reason:** {w['reason'][:100]}\n**By:** {mod_name}",
                    inline=False,
                )
            if len(warns) > 10:
                embed.set_footer(text=f"... w {len(warns) - 10} khrin • Total: {len(warns)}")
        else:
            embed.description = "✅ Ma 3endouch warnings!"

        # Cases from ModerationCases
        cog = self.bot.get_cog("ModerationCases")
        if cog:
            try:
                rows = cog.get_user_cases(ctx.guild.id, member.id, limit=5)
                if rows:
                    lines = [
                        f"`#{r['id']}` {r['case_type'].upper()} — {r['reason'][:60]}"
                        for r in rows
                    ]
                    embed.add_field(
                        name=f"📁 Mod Cases ({len(rows)})",
                        value="\n".join(lines),
                        inline=False,
                    )
            except Exception:
                pass

        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # ─── +clearwarns (with confirm)
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="clearwarns")
    @require_role_prefix("clearwarns")
    async def clearwarns_prefix(self, ctx: commands.Context, member: discord.Member):
        """+clearwarns @user"""
        warns = self._get_warnings(ctx.guild.id, member.id)
        if not warns:
            return await ctx.send(f"⚠️ {member.mention} ma 3endouch warnings!")

        if not await confirm_action(
            ctx,
            "Clear Warnings",
            f"Clear **{len(warns)}** warnings dyal {member.mention}?",
        ):
            return

        guild_id = ctx.guild.id
        if guild_id in WARNINGS and member.id in WARNINGS[guild_id]:
            del WARNINGS[guild_id][member.id]
            _save_warnings()
        await self._apply_warn_roles(member, 0)
        await ctx.send(f"✅ Warnings dyal {member.mention} t-mas7ou!")

    # ═══════════════════════════════════════════════════════════
    # ─── +kick (with confirm)
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="kick")
    @require_role_prefix("kick")
    @commands.bot_has_permissions(kick_members=True)
    async def kick_prefix(self, ctx: commands.Context, member: discord.Member,
                          *, reason: str = "Ma 3endich reason"):
        """+kick @user [reason]"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ Role fo9 dyalek!")

        if not await confirm_action(
            ctx,
            "Kick Member",
            f"Kick {member.mention}?\n**Reason:** {reason}",
        ):
            return

        try:
            await member.send(f"⛔ T-kickiti mn **{ctx.guild.name}**. Reason: {reason}")
        except discord.Forbidden:
            pass

        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.mention} t-kicka! `{reason}`")

        await self._log(ctx.guild, "kick", member, ctx.author, reason)

    # ═══════════════════════════════════════════════════════════
    # ─── +ban (with confirm)
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="ban")
    @require_role_prefix("ban")
    @commands.bot_has_permissions(ban_members=True)
    async def ban_prefix(self, ctx: commands.Context, member: discord.Member,
                         delete_days: int = 0, *, reason: str = "Ma 3endich reason"):
        """+ban @user [delete_days] [reason]"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ Role fo9 dyalek!")
        if delete_days < 0 or delete_days > 7:
            return await ctx.send("❌ `delete_days`: 0-7!")

        if not await confirm_action(
            ctx,
            "Ban Member",
            f"Ban {member.mention}?\n**Reason:** {reason}\n**Delete days:** {delete_days}",
        ):
            return

        await member.ban(reason=reason, delete_message_days=delete_days)
        await ctx.send(f"🔨 {member.mention} t-bana! `{reason}`")

        await self._log(ctx.guild, "ban", member, ctx.author, reason)

    # ═══════════════════════════════════════════════════════════
    # ─── +unban
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="unban")
    @require_role_prefix("ban")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban_prefix(self, ctx: commands.Context, user_id: int, *, reason: str = "Ma 3endich reason"):
        """+unban <user_id> [reason]"""
        try:
            user = discord.Object(id=user_id)
            await ctx.guild.unban(user, reason=f"{ctx.author}: {reason}")
        except discord.NotFound:
            return await ctx.send(f"❌ `{user_id}` machi banned!")
        except discord.Forbidden:
            return await ctx.send("❌ Ma 3ndich permission!")
        except Exception as e:
            return await ctx.send(f"❌ `{e}`")

        embed = discord.Embed(
            title="✅ Unban",
            description=f"`{user_id}` t-unbana!",
            color=discord.Color.green(),
        )
        embed.add_field(name="📝 Reason", value=reason, inline=False)
        embed.add_field(name="👮 Mod", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # ─── +slowmode
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="slowmode")
    @require_role_prefix("slowmode")
    async def slowmode_prefix(self, ctx: commands.Context, seconds: int = 0):
        """+slowmode [seconds]"""
        if seconds < 0 or seconds > 21600:
            return await ctx.send("❌ 0-21600!")
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"✅ Slow mode: `{seconds}s`")

    # ═══════════════════════════════════════════════════════════
    # ─── +lock / +unlock
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="lock")
    @require_role_prefix("lock")
    async def lock_prefix(self, ctx: commands.Context):
        """+lock"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔒 T-qfel!")

    @commands.command(name="unlock")
    @require_role_prefix("unlock")
    async def unlock_prefix(self, ctx: commands.Context):
        """+unlock"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔓 T-fta7!")

    # ═══════════════════════════════════════════════════════════
    # ─── JAIL HELPERS
    # ═══════════════════════════════════════════════════════════
    async def _do_jail(self, ctx: commands.Context, member: discord.Member, reason: str):
        if member.bot:
            return await ctx.send("❌ Ma tqderch tsjen bot!")
        if member.id == ctx.guild.owner_id:
            return await ctx.send("❌ Ma tqderch tsjen l-owner!")
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ Role fo9 dyalek!")

        jail_role = ctx.guild.get_role(JAIL_ROLE_ID)
        if jail_role is None:
            return await ctx.send(f"❌ Jail role (`{JAIL_ROLE_ID}`) ma kaynch!")
        if ctx.guild.me.top_role.position <= jail_role.position:
            return await ctx.send("❌ Jail role fo9 role dyal bot! 7arrek role dyal bot fo9.")

        guild_id = ctx.guild.id
        if guild_id in JAILED and member.id in JAILED[guild_id]:
            return await ctx.send(f"⚠️ {member.mention} deja msjoun! St3vel `+rta7` bash ttla9o.")

        if not await confirm_action(
            ctx,
            "Jail Member",
            f"Jail {member.mention}?\n**Reason:** {reason}\n\n⚠️ Ghadi yt7ydo **GA3** roles dyalo.",
        ):
            return

        saved_roles = [r.id for r in member.roles if not r.is_default() and r.id != JAIL_ROLE_ID]
        JAILED.setdefault(guild_id, {})[member.id] = {
            "roles": saved_roles,
            "reason": reason,
            "mod": ctx.author.id,
            "time": discord.utils.utcnow().isoformat(),
        }
        _save_jailed()

        try:
            removable = [r for r in member.roles if not r.is_default() and r.id != JAIL_ROLE_ID]
            if removable:
                await member.remove_roles(*removable, reason=f"Jail: {reason}")
            await member.add_roles(jail_role, reason=f"Jail: {reason}")
        except discord.Forbidden:
            return await ctx.send("❌ Ma 3ndich permission!")
        except Exception as e:
            return await ctx.send(f"❌ `{e}`")

        embed = discord.Embed(
            title="🔒 Jail",
            description=f"{member.mention} t-sjen!",
            color=discord.Color.dark_red(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="📝 Reason", value=reason, inline=False)
        embed.add_field(name="👮 Mod", value=ctx.author.mention, inline=True)
        embed.add_field(name="🎭 Roles Saved", value=f"`{len(saved_roles)}`", inline=True)
        embed.set_footer(text="Bash tla9o: +rta7 @user")
        await ctx.send(embed=embed)

        await self._log(ctx.guild, "jail", member, ctx.author, reason)

        try:
            await member.send(
                f"🔒 **T-sjenti f {ctx.guild.name}**\n"
                f"**Reason:** {reason}\n"
                f"Bash ttla9: **+rta7** (wla 3ayet l-staff)"
            )
        except discord.Forbidden:
            pass

    async def _do_unjail(self, ctx: commands.Context, member: discord.Member):
        jail_role = ctx.guild.get_role(JAIL_ROLE_ID)
        guild_id = ctx.guild.id
        data = JAILED.get(guild_id, {}).get(member.id)

        if not data and (jail_role is None or jail_role not in member.roles):
            return await ctx.send(f"❌ {member.mention} machi msjoun!")

        restored = 0
        try:
            if jail_role and jail_role in member.roles:
                await member.remove_roles(jail_role, reason=f"Unjail par {ctx.author}")

            if data:
                saved_ids = data.get("roles", [])
                to_restore = []
                for rid in saved_ids:
                    r = ctx.guild.get_role(rid)
                    if r is None or r in member.roles:
                        continue
                    if r >= ctx.guild.me.top_role:
                        continue
                    to_restore.append(r)
                if to_restore:
                    await member.add_roles(*to_restore, reason="Unjail restore")
                    restored = len(to_restore)
        except discord.Forbidden:
            return await ctx.send("❌ Ma 3ndich permission!")
        except Exception as e:
            return await ctx.send(f"❌ `{e}`")

        if guild_id in JAILED and member.id in JAILED[guild_id]:
            del JAILED[guild_id][member.id]
            _save_jailed()

        embed = discord.Embed(
            title="🔓 Unjail",
            description=f"{member.mention} t-fta7!",
            color=discord.Color.green(),
        )
        embed.add_field(name="🎭 Roles Restored", value=f"`{restored}`", inline=True)
        embed.add_field(name="👮 Mod", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)

        await self._log(ctx.guild, "unjail", member, ctx.author, "N/A")

        try:
            await member.send(f"🔓 **T-fta7ti mn jail f {ctx.guild.name}**")
        except discord.Forbidden:
            pass

    # ═══════════════════════════════════════════════════════════
    # ─── +jail / +rta7
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="jail", aliases=["unjail", "rta7"])
    @require_role_prefix("jail")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def jail_prefix(self, ctx: commands.Context, member: discord.Member,
                          *, reason: str = "Ma 3endich reason"):
        """+jail @user [reason] — Sjen member | +rta7 @user — 7ayed jail"""
        if ctx.invoked_with in ("unjail", "rta7"):
            return await self._do_unjail(ctx, member)
        return await self._do_jail(ctx, member, reason)

    # ═══════════════════════════════════════════════════════════
    # ─── +timeout (with confirm on apply only)
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="timeout", aliases=["mute"])
    @require_role_prefix("timeout")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout_prefix(self, ctx: commands.Context, member: discord.Member,
                             *, args: str = ""):
        """
        +timeout @user <duration> [reason]  → Timeout
        -timeout @user                      → Remove timeout
        """
        # ─── REMOVE TIMEOUT (-timeout)
        if ctx.prefix == "-":
            try:
                await member.timeout(None, reason=f"Timeout removed par {ctx.author}")
            except discord.Forbidden:
                return await ctx.send("❌ Ma 3ndich permission!")
            except Exception as e:
                return await ctx.send(f"❌ `{e}`")

            embed = discord.Embed(
                title="✅ Timeout Removed",
                description=f"{member.mention} wella free!",
                color=discord.Color.green(),
            )
            embed.add_field(name="👮 Mod", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)

            try:
                await member.send(f"✅ **T-7ayed lik timeout f {ctx.guild.name}**")
            except discord.Forbidden:
                pass
            return

        # ─── APPLY TIMEOUT
        if not args:
            return await ctx.send(
                "❌ Usage: `+timeout @user <duration> [reason]`\n"
                "Ex: `+timeout @user 1h spamming`\n"
                "Bash thayd: `-timeout @user`"
            )

        parts = args.split(maxsplit=1)
        duration = parts[0]
        reason = parts[1] if len(parts) > 1 else "Ma 3endich reason"

        if member.bot:
            return await ctx.send("❌ Ma tqderch timeout l bot!")
        if member.id == ctx.guild.owner_id:
            return await ctx.send("❌ Ma tqderch timeout l-owner!")
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ Role fo9 dyalek!")

        secs = parse_duration(duration)
        if secs <= 0:
            return await ctx.send("❌ Duration ghalta! Ex: `1h`, `30m`, `1d`, `7d`")
        if secs > 28 * 86400:
            return await ctx.send("❌ Max 28d!")

        if not await confirm_action(
            ctx,
            "Timeout Member",
            f"Timeout {member.mention} for `{duration}`?\n**Reason:** {reason}",
        ):
            return

        until = discord.utils.utcnow() + timedelta(seconds=secs)
        try:
            await member.timeout(until, reason=f"{ctx.author}: {reason}")
        except discord.Forbidden:
            return await ctx.send("❌ Ma 3ndich permission!")
        except Exception as e:
            return await ctx.send(f"❌ `{e}`")

        embed = discord.Embed(
            title="⏱️ Timeout",
            description=f"{member.mention} t-timeout!",
            color=discord.Color.orange(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="⏰ Until", value=f"<t:{int(until.timestamp())}:R>", inline=True)
        embed.add_field(name="📝 Reason", value=reason, inline=False)
        embed.add_field(name="👮 Mod", value=ctx.author.mention, inline=True)
        embed.set_footer(text="Bash thayd: -timeout @user")
        await ctx.send(embed=embed)

        await self._log(ctx.guild, "timeout", member, ctx.author, reason)

        try:
            await member.send(
                f"⏱️ **T-timeout f {ctx.guild.name}**\n"
                f"**Until:** <t:{int(until.timestamp())}:R>\n"
                f"**Reason:** {reason}"
            )
        except discord.Forbidden:
            pass

    # ═══════════════════════════════════════════════════════════
    # ─── +untimeout / +unmute
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="untimeout", aliases=["unmute"])
    @require_role_prefix("timeout")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def untimeout_prefix(self, ctx: commands.Context, member: discord.Member):
        """+untimeout @user — 7ayed timeout"""
        try:
            await member.timeout(None, reason=f"Untimeout par {ctx.author}")
        except discord.Forbidden:
            return await ctx.send("❌ Ma 3ndich permission!")
        except Exception as e:
            return await ctx.send(f"❌ `{e}`")

        embed = discord.Embed(
            title="✅ Timeout Removed",
            description=f"{member.mention} wella free!",
            color=discord.Color.green(),
        )
        embed.add_field(name="👮 Mod", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)

        await self._log(ctx.guild, "untimeout", member, ctx.author, "N/A")


async def setup(bot):
    await bot.add_cog(Admin(bot))