# cogs/verification.py
"""Verification — Staff y3mmer info → Staff akhor ydir +vb/+vg <ID>."""
import discord
from discord.ext import commands
import json
import os
from datetime import datetime

import botconfig

# ═══════════════════════════════════════════════════════════════════
# ─── CONFIG
# ═══════════════════════════════════════════════════════════════════
VERIF_LOG_CHANNEL = "verify-info"
VERIF_DATA_DIR    = "data"
VERIF_JSON_FILE   = os.path.join(VERIF_DATA_DIR, "verification.json")

ROLE_VB = botconfig.ROLE_VB
ROLE_VG = botconfig.ROLE_VG

EMOJI_VERIFY = "✅"


# ═══════════════════════════════════════════════════════════════════
# ─── JSON HELPERS
# ═══════════════════════════════════════════════════════════════════
def _ensure_data_dir():
    os.makedirs(VERIF_DATA_DIR, exist_ok=True)


def _load_json() -> dict:
    _ensure_data_dir()
    if not os.path.exists(VERIF_JSON_FILE):
        return {}
    try:
        with open(VERIF_JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_json(data: dict):
    _ensure_data_dir()
    with open(VERIF_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════
# ─── MODAL — STAFF kay3mmer INFO (bla ma y3ti role)
# ═══════════════════════════════════════════════════════════════════
class VerificationModal(discord.ui.Modal, title="📋 Verification Form"):

    inviter_id = discord.ui.TextInput(
        label="🔗 Chkon sift lik had user? (ID)",
        placeholder="ID dyal li sift lik had user / fin l9itih",
        required=True,
        max_length=30,
    )
    real_name = discord.ui.TextInput(
        label="📝 Smiya l-7a9i9iya",
        placeholder="Smiya dyal l-user",
        required=True,
        max_length=50,
    )
    age = discord.ui.TextInput(
        label="🎂 3mer",
        placeholder="R9m bo7do (ex: 19)",
        required=True,
        max_length=3,
    )
    games = discord.ui.TextInput(
        label="🎮 Games li kayl3b",
        placeholder="VALORANT, FREE FIRE, PES...",
        required=True,
        max_length=200,
        style=discord.TextStyle.paragraph,
    )
    notes = discord.ui.TextInput(
        label="📌 Notes (optionnel)",
        placeholder="Chi notes zayda 3la l-user",
        required=False,
        max_length=300,
        style=discord.TextStyle.paragraph,
    )

    def __init__(self, bot: commands.Bot, target: discord.Member, verifier: discord.Member):
        super().__init__()
        self.bot = bot
        self.target = target
        self.verifier = verifier

    async def on_submit(self, interaction: discord.Interaction):
        user = self.target
        staff = self.verifier
        guild = interaction.guild

        # ═══ 1. Save f JSON (status = pending, bla roles!)
        data = _load_json()
        data[str(user.id)] = {
            "user_id": user.id,
            "username": str(user),
            "user_tag": user.name,
            "display_name": user.display_name,
            "joined_at": user.joined_at.isoformat() if user.joined_at else None,
            "guild_id": guild.id,
            "answers": {
                "inviter_id": self.inviter_id.value.strip(),
                "real_name":  self.real_name.value.strip(),
                "age":        self.age.value.strip(),
                "games":      self.games.value.strip(),
                "notes":      self.notes.value.strip() if self.notes.value else "",
            },
            "status": "pending",
            "filled_at": datetime.utcnow().isoformat(),
            "filled_by_id": staff.id,
            "filled_by_name": str(staff),
            "filled_by_tag": staff.name,
            "verified_at": None,
            "verified_by_id": None,
            "verified_by_name": None,
            "verify_type": None,
        }
        _save_json(data)

        # ═══ 2. Sift f log channel
        log_ch = discord.utils.get(guild.text_channels, name=VERIF_LOG_CHANNEL)
        if log_ch is None:
            log_ch = discord.utils.find(
                lambda c: "verif" in c.name.lower() and isinstance(c, discord.TextChannel),
                guild.channels,
            )

        if log_ch:
            embed = discord.Embed(
                title="📝 Verification Info (PENDING)",
                description=(
                    f"**Stenaya...**\n"
                    f"Staff akhor khass ydir:\n"
                    f"`+vb {user.id}` (Verified Basic)\n"
                    f"wla `+vg {user.id}` (Verified Girl)"
                ),
                color=discord.Color.orange(),
                timestamp=datetime.utcnow(),
            )
            embed.set_author(name=str(user), icon_url=user.display_avatar.url)
            embed.add_field(name="👤 User", value=f"{user.mention}\n`{user.id}`", inline=False)
            embed.add_field(name="🔗 Inviter ID", value=f"`{self.inviter_id.value}`", inline=False)
            embed.add_field(name="📝 Smiya", value=self.real_name.value, inline=True)
            embed.add_field(name="🎂 3mer", value=self.age.value, inline=True)
            embed.add_field(name="🎮 Games", value=self.games.value[:1024], inline=False)
            if self.notes.value:
                embed.add_field(name="📌 Notes", value=self.notes.value[:1024], inline=False)
            embed.add_field(
                name="📝 Info filled by",
                value=f"{staff.mention}\n`{staff.id}`",
                inline=False,
            )
            embed.set_footer(text=f"ID: {user.id} • PENDING")
            try:
                await log_ch.send(embed=embed)
            except Exception:
                pass

        # ═══ 3. Reply l staff
        try:
            msg = (
                f"✅ **Info tsawbet!**\n"
                f"👤 {user.mention} → `pending`\n"
                f"📝 Staff akhor khass ydir:\n"
                f"`+vb {user.id}` wla `+vg {user.id}`"
            )
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
# ─── VIEW (Button bash yfte7 modal)
# ═══════════════════════════════════════════════════════════════════
class _ModalView(discord.ui.View):
    def __init__(self, bot, target: discord.Member, verifier: discord.Member):
        super().__init__(timeout=180)
        self.bot = bot
        self.target = target
        self.verifier = verifier

    @discord.ui.button(
        label="3mmer Formulaire",
        emoji="📋",
        style=discord.ButtonStyle.green,
    )
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.verifier.id:
            return await interaction.response.send_message(
                "❌ Machi dyalek! Dir `+verify @user` b nafsek.",
                ephemeral=True,
            )
        modal = VerificationModal(self.bot, self.target, self.verifier)
        await interaction.response.send_modal(modal)


# ═══════════════════════════════════════════════════════════════════
# ─── VERIFICATION COG
# ═══════════════════════════════════════════════════════════════════
class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        _ensure_data_dir()

    # ═══════════════════════════════════════════════════════════
    # ─── STAFF CHECK
    # ═══════════════════════════════════════════════════════════
    def _is_staff(self, member: discord.Member) -> bool:
        if member.guild_permissions.administrator:
            return True
        if member.guild_permissions.manage_roles:
            return True
        staff_names = (
            "verifier", "staff", "staff team", "moderator",
            "administrator", "helper", "superveseur",
        )
        return any(r.name.lower().strip() in staff_names for r in member.roles)

    # ═══════════════════════════════════════════════════════════
    # ─── +verify @user → STAFF kay3mmer INFO (bla roles)
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="verify", aliases=["vform"])
    @commands.guild_only()
    async def verify_staff(self, ctx, member: discord.Member = None):
        """+verify @user — 3mmer INFO dyal user (bla role)"""
        if not self._is_staff(ctx.author):
            return await ctx.send(
                f"❌ {ctx.author.mention} — Staff only (`Manage Roles`).",
                delete_after=10,
            )
        if member is None:
            return await ctx.send("❌ **Usage:** `+verify @user`", delete_after=8)
        if member.bot:
            return await ctx.send("❌ Bots!", delete_after=8)

        await ctx.send(
            f"{ctx.author.mention} 👇 **3mmer info dyal {member.mention}:**\n",
            view=_ModalView(self.bot, member, ctx.author),
            delete_after=180,
        )

    # ═══════════════════════════════════════════════════════════
    # ─── +vb <ID|@user> → 3ti role Verified Basic
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="vb")
    @commands.guild_only()
    async def vb(self, ctx, target: str = None):
        """+vb <ID|@user> — 3ti role VB + Game Roles + log chkon verifa"""
        if not self._is_staff(ctx.author):
            return await ctx.send(f"❌ {ctx.author.mention} — Staff only!", delete_after=8)
        if target is None:
            return await ctx.send("❌ **Usage:** `+vb <ID>` wla `+vb @user`", delete_after=8)

        member = await self._resolve_member(ctx, target)
        if member is None:
            return await ctx.send(f"❌ Ma l9itch member b `{target}`", delete_after=8)
        if member.bot:
            return await ctx.send("❌ Bots!", delete_after=8)

        role = ctx.guild.get_role(ROLE_VB)
        if role is None:
            return await ctx.send(f"❌ Role `{ROLE_VB}` ma kaynch!")

        if role in member.roles:
            return await ctx.send(f"⚠️ {member.mention} 3ndo deja {role.mention}!", delete_after=8)

        try:
            await member.add_roles(role, reason=f"+vb by {ctx.author}")
        except discord.Forbidden:
            return await ctx.send("❌ Hierarchy mochkil!")
        except Exception as e:
            return await ctx.send(f"❌ {e}")

        unv = discord.utils.get(ctx.guild.roles, name="Unverified")
        if unv and unv in member.roles:
            try:
                await member.remove_roles(unv, reason="+vb")
            except Exception:
                pass

        added_games, not_found_games = await self._assign_game_roles(ctx, member)

        data = _load_json()
        entry = data.get(str(member.id), {})
        if "answers" not in entry:
            entry["answers"] = {}
        entry.update({
            "user_id": member.id,
            "username": str(member),
            "guild_id": ctx.guild.id,
            "status": "verified",
            "verify_type": "vb",
            "verified_at": datetime.utcnow().isoformat(),
            "verified_by_id": ctx.author.id,
            "verified_by_name": str(ctx.author),
            "verified_by_tag": ctx.author.name,
        })
        data[str(member.id)] = entry
        _save_json(data)

        # ─── Log via Logs cog
        logs_cog = self.bot.get_cog("Logs")
        if logs_cog:
            try:
                await logs_cog.log_verification(
                    ctx.guild, member, "vb", ctx.author,
                    extra=f"Games: {', '.join(r.name for r in added_games)}" if added_games else None,
                )
            except Exception:
                pass

        msg = f"✅ {member.mention} wla **Verified** ({role.mention})!\n👮 By: {ctx.author.mention}"
        if added_games:
            msg += f"\n🎮 **Games added:** {', '.join(r.mention for r in added_games)}"
        if not_found_games:
            msg += f"\n⚠️ **Roles ma l9itchhomch:** `{', '.join(not_found_games)}`"

        await ctx.send(msg)

    # ═══════════════════════════════════════════════════════════
    # ─── +vg <ID|@user> → 3ti role Verified Girl
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="vg")
    @commands.guild_only()
    async def vg(self, ctx, target: str = None):
        """+vg <ID|@user> — 3ti roles VB + VG + Game Roles"""
        if not self._is_staff(ctx.author):
            return await ctx.send(f"❌ {ctx.author.mention} — Staff only!", delete_after=8)
        if target is None:
            return await ctx.send("❌ **Usage:** `+vg <ID>` wla `+vg @user`", delete_after=8)

        member = await self._resolve_member(ctx, target)
        if member is None:
            return await ctx.send(f"❌ Ma l9itch member b `{target}`", delete_after=8)
        if member.bot:
            return await ctx.send("❌ Bots!", delete_after=8)

        role_vb = ctx.guild.get_role(ROLE_VB)
        role_vg = ctx.guild.get_role(ROLE_VG)

        missing = [str(r) for r in (ROLE_VB, ROLE_VG) if ctx.guild.get_role(r) is None]
        if missing:
            return await ctx.send(f"❌ Roles ma kaynin: {', '.join(f'`{m}`' for m in missing)}")

        to_add = [r for r in (role_vb, role_vg) if r not in member.roles]
        if not to_add:
            return await ctx.send(f"⚠️ {member.mention} 3ndo deja had roles!", delete_after=8)

        try:
            await member.add_roles(*to_add, reason=f"+vg by {ctx.author}")
        except discord.Forbidden:
            return await ctx.send("❌ Hierarchy mochkil!")
        except Exception as e:
            return await ctx.send(f"❌ {e}")

        unv = discord.utils.get(ctx.guild.roles, name="Unverified")
        if unv and unv in member.roles:
            try:
                await member.remove_roles(unv, reason="+vg")
            except Exception:
                pass

        added_games, not_found_games = await self._assign_game_roles(ctx, member)

        data = _load_json()
        entry = data.get(str(member.id), {})
        if "answers" not in entry:
            entry["answers"] = {}
        entry.update({
            "user_id": member.id,
            "username": str(member),
            "guild_id": ctx.guild.id,
            "status": "verified",
            "verify_type": "vg",
            "verified_at": datetime.utcnow().isoformat(),
            "verified_by_id": ctx.author.id,
            "verified_by_name": str(ctx.author),
            "verified_by_tag": ctx.author.name,
        })
        data[str(member.id)] = entry
        _save_json(data)

        logs_cog = self.bot.get_cog("Logs")
        if logs_cog:
            try:
                await logs_cog.log_verification(
                    ctx.guild, member, "vg", ctx.author,
                    extra=f"Games: {', '.join(r.name for r in added_games)}" if added_games else None,
                )
            except Exception:
                pass

        added = ", ".join(r.mention for r in to_add)
        msg = f"✅ {member.mention} wla **Verified + Girl**!\n➕ {added}\n👮 By: {ctx.author.mention}"
        if added_games:
            msg += f"\n🎮 **Games added:** {', '.join(r.mention for r in added_games)}"
        if not_found_games:
            msg += f"\n⚠️ **Roles ma l9itchhomch:** `{', '.join(not_found_games)}`"

        await ctx.send(msg)

    # ═══════════════════════════════════════════════════════════
    # ─── +vcheck @user
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="vcheck", aliases=["verifinfo", "vinfo"])
    @commands.guild_only()
    async def vcheck(self, ctx, member: discord.Member):
        """+vcheck @user — Chouf info dyal verification"""
        if not self._is_staff(ctx.author):
            return await ctx.send(f"❌ Staff only!", delete_after=8)

        data = _load_json()
        entry = data.get(str(member.id))
        if not entry:
            return await ctx.send(f"❌ {member.mention} ma 3ndo ta verification!")

        a = entry.get("answers", {})
        status = entry.get("status", "?")
        color = {
            "pending": discord.Color.orange(),
            "verified": discord.Color.green(),
            "unverified": discord.Color.red(),
        }.get(status, discord.Color.blurple())

        embed = discord.Embed(
            title=f"📋 Verification — {member}",
            color=color,
        )
        embed.add_field(name="👤 User", value=f"{member.mention}\n`{member.id}`", inline=False)
        embed.add_field(name="🔗 Inviter ID", value=f"`{a.get('inviter_id', '—')}`", inline=False)
        embed.add_field(name="📝 Smiya", value=a.get("real_name", "—"), inline=True)
        embed.add_field(name="🎂 3mer", value=a.get("age", "—"), inline=True)
        embed.add_field(name="🎮 Games", value=a.get("games", "—")[:1024], inline=False)
        if a.get("notes"):
            embed.add_field(name="📌 Notes", value=a["notes"][:1024], inline=False)

        embed.add_field(name="📌 Status", value=f"`{status}`", inline=True)
        embed.add_field(name="🏷️ Type", value=f"`{entry.get('verify_type') or '—'}`", inline=True)

        if entry.get("filled_by_name"):
            embed.add_field(
                name="📝 Info filled by",
                value=f"`{entry['filled_by_name']}`\n`{entry.get('filled_by_id', '—')}`",
                inline=True,
            )
        if entry.get("verified_by_name"):
            embed.add_field(
                name="✅ Verified by",
                value=f"`{entry['verified_by_name']}`\n`{entry.get('verified_by_id', '—')}`",
                inline=True,
            )
        if entry.get("verified_at"):
            embed.add_field(name="🕐 Verified at", value=f"`{entry['verified_at']}`", inline=False)

        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # ─── +unverify @user
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="unverify", aliases=["unvb"])
    @commands.guild_only()
    async def unverify(self, ctx, member: discord.Member):
        if not self._is_staff(ctx.author):
            return await ctx.send(f"❌ Staff only!", delete_after=8)

        roles_to_remove = []
        for rid in (ROLE_VB, ROLE_VG):
            r = ctx.guild.get_role(rid)
            if r and r in member.roles:
                roles_to_remove.append(r)

        if not roles_to_remove:
            return await ctx.send(f"⚠️ {member.mention} ma 3ndo ta role verified!", delete_after=8)

        try:
            await member.remove_roles(*roles_to_remove, reason=f"+unverify by {ctx.author}")
        except Exception as e:
            return await ctx.send(f"❌ {e}")

        unv = discord.utils.get(ctx.guild.roles, name="Unverified")
        if unv and unv not in member.roles:
            try:
                await member.add_roles(unv, reason="+unverify")
            except Exception:
                pass

        data = _load_json()
        if str(member.id) in data:
            data[str(member.id)]["status"] = "unverified"
            data[str(member.id)]["unverified_at"] = datetime.utcnow().isoformat()
            data[str(member.id)]["unverified_by_id"] = ctx.author.id
            data[str(member.id)]["unverified_by_name"] = str(ctx.author)
            _save_json(data)

        await ctx.send(f"✅ {member.mention} wla **Unverified**.")

    # ═══════════════════════════════════════════════════════════
    # ─── +vlist
    # ═══════════════════════════════════════════════════════════
    @commands.command(name="vlist")
    @commands.guild_only()
    async def vlist(self, ctx, mode: str = "all"):
        """+vlist [pending|verified|all]"""
        if not self._is_staff(ctx.author):
            return await ctx.send(f"❌ Staff only!", delete_after=8)

        data = _load_json()
        if not data:
            return await ctx.send("📭 Ma kaynch verification!")

        mode = mode.lower()
        if mode == "pending":
            entries = [e for e in data.values() if e.get("status") == "pending"]
            title = f"📝 Pending ({len(entries)})"
            color = discord.Color.orange()
        elif mode == "verified":
            entries = [e for e in data.values() if e.get("status") == "verified"]
            title = f"✅ Verified ({len(entries)})"
            color = discord.Color.green()
        else:
            entries = list(data.values())
            title = f"📋 All ({len(entries)})"
            color = discord.Color.blurple()

        entries.sort(key=lambda x: x.get("filled_at") or x.get("verified_at") or "", reverse=True)

        embed = discord.Embed(title=title, color=color)
        lines = []
        for e in entries[:20]:
            uid = e.get("user_id", "?")
            status = e.get("status", "?")
            vtype = e.get("verify_type") or "?"
            filled_by = e.get("filled_by_name", "?")
            if status == "pending":
                lines.append(f"<@{uid}> — `{status}` — filled by `{filled_by}`")
            else:
                lines.append(f"<@{uid}> — `{vtype}` — by `{e.get('verified_by_name', '?')}`")
        if not lines:
            lines = ["—"]
        embed.description = "\n".join(lines)
        if len(entries) > 20:
            embed.set_footer(text=f"+{len(entries) - 20} akhrin...")
        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════
    # ─── HELPERS
    # ═══════════════════════════════════════════════════════════
    async def _assign_game_roles(self, ctx, member):
        data = _load_json()
        entry = data.get(str(member.id), {})
        games_text = entry.get("answers", {}).get("games", "")

        if not games_text:
            return [], []

        games_list = [g.strip() for g in games_text.split(",") if g.strip()]

        added_roles = []
        not_found = []

        for game in games_list:
            role = discord.utils.find(lambda r: r.name.lower().strip() == game.lower().strip(), ctx.guild.roles)

            if role:
                if role not in member.roles:
                    try:
                        await member.add_roles(role, reason="Auto-assigned from Verification Games")
                        added_roles.append(role)
                    except discord.Forbidden:
                        not_found.append(f"{game} (Permission)")
            else:
                not_found.append(game)

        return added_roles, not_found

    async def _resolve_member(self, ctx, target: str):
        target = target.strip("<@!>")
        if not target.isdigit():
            return None
        try:
            uid = int(target)
        except ValueError:
            return None
        member = ctx.guild.get_member(uid)
        if member is None:
            try:
                member = await ctx.guild.fetch_member(uid)
            except Exception:
                return None
        return member


async def setup(bot):
    await bot.add_cog(Verification(bot))