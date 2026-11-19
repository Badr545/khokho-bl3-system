# cogs/clans.py
# =====================================================================
# ─── ULTIMATE CLAN SYSTEM (Embeds, English, Auto ID, Confirmations)
# =====================================================================
import discord
from discord.ext import commands, tasks
import json
import os
import time
import asyncio
import random
import string

CLANS_FILE = "data/clans.json"

def _load():
    if not os.path.exists(CLANS_FILE): return {}
    try:
        with open(CLANS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: return {}

def _save(data):
    os.makedirs("data", exist_ok=True)
    with open(CLANS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

CLANS = _load()

# ═══════════════════════════════════════════════════════════════════
# ─── ⚙️ L-IDs DYAL LES ROLES
# ═══════════════════════════════════════════════════════════════════
CLAN_MANAGER_ROLE_ID = 1570285658482679829    
CLAN_LEADER_ROLE_ID = 1570285101185765416     
CLAN_COLEADER_ROLE_ID = 1570285368174190592   
CLAN_OF_THE_WEEK_ROLE_ID = 1570312239217647768 
# ═══════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════
# ─── ⚙️ SMYAT DYAL LES CATEGORIES
# ═══════════════════════════════════════════════════════════════════
CATEGORY_TEXT_NAME = "CLANS CHATS"
CATEGORY_VOICE_NAME = "CLANS VOICES"
# ═══════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════
# ─── HELPERS
# ═══════════════════════════════════════════════════════════════════
def generate_clan_id():
    while True:
        cid = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if not any(c.get("id") == cid for gd in CLANS.values() for c in gd.get("clans", {}).values()):
            return cid

def get_guild_data(gid):
    gid = str(gid)
    if gid not in CLANS: CLANS[gid] = {"clans": {}, "users": {}}
    return CLANS[gid]

def get_user(gid, uid):
    gd = get_guild_data(gid)
    uid = str(uid)
    if uid not in gd["users"]: gd["users"][uid] = {"clan": None, "weekly": 0, "total": 0}
    return gd["users"][uid]

def get_clan(gid, clan_id):
    return get_guild_data(gid)["clans"].get(str(clan_id))

def get_clan_by_user(gid, uid):
    u = get_user(gid, uid)
    if not u["clan"]: return None
    return get_clan(gid, u["clan"])

def get_clan_by_query(gid, query):
    query = query.lower().strip()
    for cid, c in get_guild_data(gid)["clans"].items():
        if c["name"].lower() == query or c.get("id", "").lower() == query:
            return c
    return None

# ─── EMBED BUILDERS ───
def error_embed(msg):
    return discord.Embed(description=f"❌ {msg}", color=discord.Color.red())

def success_embed(msg):
    return discord.Embed(description=f"✅ {msg}", color=discord.Color.green())

def info_embed(title, desc, color=discord.Color.gold()):
    embed = discord.Embed(title=title, description=desc, color=color)
    embed.set_footer(text="Clan System")
    return embed

def format_time(s):
    h, m = s // 3600, (s % 3600) // 60
    return f"{h}h {m}m"

# ─── PERMISSIONS ───
def is_manager():
    async def predicate(ctx):
        if ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.administrator: return True
        if CLAN_MANAGER_ROLE_ID and discord.utils.get(ctx.author.roles, id=CLAN_MANAGER_ROLE_ID): return True
        raise commands.CheckFailure("You need the **Clan Manager** role to use this command.")
    return commands.check(predicate)

def is_leader():
    async def predicate(ctx):
        if ctx.author.id == ctx.guild.owner_id: return True
        c = get_clan_by_user(ctx.guild.id, ctx.author.id)
        if c and c["leader"] == str(ctx.author.id): return True
        if CLAN_LEADER_ROLE_ID and discord.utils.get(ctx.author.roles, id=CLAN_LEADER_ROLE_ID): return True
        raise commands.CheckFailure("You need to be a **Clan Leader** to use this command.")
    return commands.check(predicate)

def is_staff():
    async def predicate(ctx):
        if ctx.author.id == ctx.guild.owner_id: return True
        c = get_clan_by_user(ctx.guild.id, ctx.author.id)
        if c and (c["leader"] == str(ctx.author.id) or str(ctx.author.id) in c.get("coleaders", [])): return True
        if CLAN_LEADER_ROLE_ID and discord.utils.get(ctx.author.roles, id=CLAN_LEADER_ROLE_ID): return True
        if CLAN_COLEADER_ROLE_ID and discord.utils.get(ctx.author.roles, id=CLAN_COLEADER_ROLE_ID): return True
        raise commands.CheckFailure("You need to be a **Leader** or **Co-Leader** to use this command.")
    return commands.check(predicate)

# ─── ROLE SYNC ───
async def sync_roles(guild, c, member):
    add, rem = [], []
    clan_role = guild.get_role(c.get("role_id"))
    if clan_role and clan_role not in member.roles: add.append(clan_role)
    
    if CLAN_LEADER_ROLE_ID:
        r = guild.get_role(CLAN_LEADER_ROLE_ID)
        if r:
            if c["leader"] == str(member.id):
                if r not in member.roles: add.append(r)
            elif r in member.roles: rem.append(r)
                
    if CLAN_COLEADER_ROLE_ID:
        r = guild.get_role(CLAN_COLEADER_ROLE_ID)
        if r:
            if str(member.id) in c.get("coleaders", []):
                if r not in member.roles: add.append(r)
            elif r in member.roles: rem.append(r)
            
    if CLAN_OF_THE_WEEK_ROLE_ID:
        r = guild.get_role(CLAN_OF_THE_WEEK_ROLE_ID)
        if r:
            if c.get("clan_of_week"):
                if r not in member.roles: add.append(r)
            elif r in member.roles: rem.append(r)

    try:
        if add: await member.add_roles(*add)
        if rem: await member.remove_roles(*rem)
    except: pass

async def remove_roles(guild, member, c):
    rem = []
    for rid in [c.get("role_id"), CLAN_LEADER_ROLE_ID, CLAN_COLEADER_ROLE_ID, CLAN_OF_THE_WEEK_ROLE_ID]:
        if rid:
            r = guild.get_role(rid)
            if r and r in member.roles: rem.append(r)
    try:
        if rem: await member.remove_roles(*rem)
    except: pass

# ═══════════════════════════════════════════════════════════════════
# ─── UI VIEWS (BUTTONS)
# ═══════════════════════════════════════════════════════════════════

class ConfirmView(discord.ui.View):
    """View for the author to confirm/cancel a sensitive command."""
    def __init__(self, author):
        super().__init__(timeout=60)
        self.author = author
        self.value = None

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ This confirmation menu is not for you.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.defer()

class TargetAcceptView(discord.ui.View):
    """View for a target member to accept/decline an action."""
    def __init__(self, target):
        super().__init__(timeout=60)
        self.target = target
        self.value = None

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("❌ This prompt is not for you.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="✅")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger, emoji="❌")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.defer()

# ═══════════════════════════════════════════════════════════════════
# ─── MAIN COG
# ═══════════════════════════════════════════════════════════════════
class Clans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_voice = {}
        self.autosave.start()

    def cog_unload(self):
        self.autosave.cancel()
        self._update_all_voice()
        _save(CLANS)

    def _update_all_voice(self):
        now = time.time()
        for (gid, uid), start in list(self.active_voice.items()):
            dur = int(now - start)
            u = get_user(gid, uid)
            u["weekly"] += dur
            u["total"] += dur
            self.active_voice[(gid, uid)] = now

    @tasks.loop(minutes=2)
    async def autosave(self):
        self._update_all_voice()
        _save(CLANS)

    @autosave.before_loop
    async def before_autosave(self): await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot: return
        key = (member.guild.id, member.id)
        now = time.time()
        if before.channel is None and after.channel is not None:
            self.active_voice[key] = now
        elif before.channel is not None:
            if key in self.active_voice:
                dur = int(now - self.active_voice.pop(key))
                if dur > 0:
                    u = get_user(member.guild.id, member.id)
                    u["weekly"] += dur
                    u["total"] += dur
            if after.channel is not None:
                self.active_voice[key] = now

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=error_embed(str(error)))

    # ═══════════════════════════════════════════════════════════════════
    # ─── BASIC COMMANDS
    # ═══════════════════════════════════════════════════════════════════

    @commands.command(name="clanhelp", aliases=["chelp"])
    async def help_cmd(self, ctx):
        embed = info_embed("⚔️ Clan System Commands", "Here is a list of all available commands:")
        embed.add_field(name="👤 Member", value="`myclan`, `mypoints`, `mytime`, `usertime`, `lbc`, `claninfo`, `topc`, `clanlist`, `leaveclan`", inline=False)
        embed.add_field(name="⭐ Co-Leader", value="`adduser`, `removeuser`", inline=False)
        embed.add_field(name="👑 Leader", value="`addcol`, `removecol`, `set-owner`, `settag`, `clansetup`", inline=False)
        embed.add_field(name="🛡️ Manager", value="`+createclan`, `+deleteclan`, `+renameclan`, `+updaterole`, `+giveclan`, `+forceaddmember`, `+clearcoleaders`, `+resetpoints`, `+clan-of-the-week`, `+removeclan-of-the-week`, `+update-limits`", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="clans", aliases=["allclans", "listclans"])
    async def list_all_clans(self, ctx):
        gd = get_guild_data(ctx.guild.id)
        if not gd["clans"]: return await ctx.send(embed=error_embed("No clans found in this server."))
        
        embed = info_embed("⚔️ Registered Clans", "List of all clans in this server:")
        
        for cid, c in gd["clans"].items():
            pts = sum(get_user(ctx.guild.id, uid)["weekly"] for uid in c["members"])
            role = ctx.guild.get_role(c.get("role_id"))
            role_mention = role.mention if role else "None"
            embed.add_field(
                name=f"🏷️ [{c.get('id', 'N/A')}] {c['name']}",
                value=f"👑 **Leader:** <@{c['leader']}>\n👥 **Members:** `{len(c['members'])}/{c.get('max_members', 20)}`\n⏱️ **Weekly Points:** `{format_time(pts)}`\n🎭 **Role:** {role_mention}",
                inline=True
            )
        await ctx.send(embed=embed)

    @commands.command(name="myclan")
    async def myclan(self, ctx):
        c = get_clan_by_user(ctx.guild.id, ctx.author.id)
        if not c: return await ctx.send(embed=error_embed("You are not in a clan."))
        
        pts = sum(get_user(ctx.guild.id, uid)["weekly"] for uid in c["members"])
        embed = discord.Embed(title=f"⚔️ {c['name']}", color=c.get("color", 0))
        embed.description = f"**Clan ID:** `{c.get('id', 'N/A')}`"
        embed.add_field(name="👑 Leader", value=f"<@{c['leader']}>", inline=True)
        embed.add_field(name="👥 Members", value=f"`{len(c['members'])}/{c.get('max_members', 20)}`", inline=True)
        embed.add_field(name="⏱️ Weekly Points", value=f"`{format_time(pts)}`", inline=True)
        if c.get("clan_of_week"): embed.set_footer(text="🏆 Clan of the Week")
        await ctx.send(embed=embed)

    @commands.command(name="mypoints")
    async def mypoints(self, ctx):
        u = get_user(ctx.guild.id, ctx.author.id)
        embed = info_embed("⏱️ Your Voice Time", f"**Weekly:** `{format_time(u['weekly'])}`\n**Total:** `{format_time(u['total'])}`")
        await ctx.send(embed=embed)

    @commands.command(name="mytime")
    async def mytime(self, ctx): await self.mypoints(ctx)

    @commands.command(name="usertime")
    async def usertime(self, ctx, member: discord.Member):
        u = get_user(ctx.guild.id, member.id)
        embed = info_embed(f"⏱️ {member.name}'s Voice Time", f"**Weekly:** `{format_time(u['weekly'])}`\n**Total:** `{format_time(u['total'])}`")
        await ctx.send(embed=embed)

    @commands.command(name="lbc")
    async def lb(self, ctx):
        gd = get_guild_data(ctx.guild.id)
        if not gd["clans"]: return await ctx.send(embed=error_embed("No clans found."))
        
        c_list = [(c["name"], c.get("id", "N/A"), sum(get_user(ctx.guild.id, uid)["weekly"] for uid in c["members"])) for cid, c in gd["clans"].items()]
        c_list.sort(key=lambda x: x[2], reverse=True)
        
        desc = "".join(f"**{i+1}.** {n} `[{cid}]` — `{format_time(p)}`\n" for i, (n, cid, p) in enumerate(c_list[:10]))
        await ctx.send(embed=info_embed("⚔️ Top 10 Clans (Weekly)", desc))

    @commands.command(name="claninfo")
    async def info(self, ctx, *, query: str):
        c = get_clan_by_query(ctx.guild.id, query)
        if not c: return await ctx.send(embed=error_embed(f"No clan found matching `{query}`."))
        
        pts = sum(get_user(ctx.guild.id, uid)["weekly"] for uid in c["members"])
        embed = info_embed(f"⚔️ {c['name']}", f"**Clan ID:** `{c.get('id', 'N/A')}`")
        embed.add_field(name="👑 Leader", value=f"<@{c['leader']}>", inline=True)
        embed.add_field(name="👥 Members", value=f"`{len(c['members'])}/{c.get('max_members', 20)}`", inline=True)
        embed.add_field(name="⏱️ Weekly Points", value=f"`{format_time(pts)}`", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="clanlist")
    async def clanlist(self, ctx, *, query: str):
        c = get_clan_by_query(ctx.guild.id, query)
        if not c: return await ctx.send(embed=error_embed(f"No clan found matching `{query}`."))
        
        members = [f"👑 <@{c['leader']}>" if uid == c['leader'] else f"⭐ <@{uid}>" if uid in c.get('coleaders', []) else f"👤 <@{uid}>" for uid in c["members"]]
        await ctx.send(embed=info_embed(f"📋 Members of {c['name']} [{c.get('id', 'N/A')}]", "\n".join(members)))

    @commands.command(name="topc")
    async def top(self, ctx):
        c = get_clan_by_user(ctx.guild.id, ctx.author.id)
        if not c: return await ctx.send(embed=error_embed("You are not in a clan."))
        
        members = [(uid, get_user(ctx.guild.id, uid)["weekly"]) for uid in c["members"]]
        members.sort(key=lambda x: x[1], reverse=True)
        
        desc = "".join(f"**{i+1}.** <@{uid}> — `{format_time(pts)}`\n" for i, (uid, pts) in enumerate(members[:10]))
        await ctx.send(embed=info_embed(f"⚔️ Top Members in {c['name']}", desc))

    # ═══════════════════════════════════════════════════════════════════
    # ─── SENSITIVE COMMANDS (CONFIRMATIONS)
    # ═══════════════════════════════════════════════════════════════════

    @commands.command(name="leaveclan", aliases=["cleave"])
    async def leave(self, ctx):
        u = get_user(ctx.guild.id, ctx.author.id)
        if not u["clan"]: return await ctx.send(embed=error_embed("You are not in a clan."))
        
        view = ConfirmView(ctx.author)
        msg = await ctx.send(embed=info_embed("⚠️ Confirmation Required", "Are you sure you want to leave your clan? This action cannot be undone."), view=view)
        await view.wait()
        
        if not view.value:
            return await msg.edit(embed=error_embed("Action cancelled."), view=None)

        gd = get_guild_data(ctx.guild.id)
        c = gd["clans"][u["clan"]]

        if c["leader"] == str(ctx.author.id) and len(c["members"]) > 1:
            new_leader = c.get("coleaders", [None])[0] if c.get("coleaders") else next((m for m in c["members"] if m != str(ctx.author.id)), None)
            if new_leader:
                c["leader"] = new_leader
                if new_leader in c.get("coleaders", []): c["coleaders"].remove(new_leader)
                mem = ctx.guild.get_member(int(new_leader))
                if mem: await sync_roles(ctx.guild, c, mem)

        c["members"].remove(str(ctx.author.id))
        if str(ctx.author.id) in c.get("coleaders", []): c["coleaders"].remove(str(ctx.author.id))
        await remove_roles(ctx.guild, ctx.author, c)
        
        if not c["members"]: 
            role = ctx.guild.get_role(c.get("role_id"))
            if role: await role.delete()
            t_ch = ctx.guild.get_channel(c.get("text_channel_id")) if c.get("text_channel_id") else None
            v_ch = ctx.guild.get_channel(c.get("voice_channel_id")) if c.get("voice_channel_id") else None
            if t_ch: await t_ch.delete()
            if v_ch: await v_ch.delete()
            del gd["clans"][u["clan"]]
            
        u["clan"] = None
        _save(CLANS)
        await msg.edit(embed=success_embed("You have successfully left the clan."), view=None)

    @commands.command(name="adduser")
    @is_staff()
    async def adduser(self, ctx, member: discord.Member):
        c = get_clan_by_user(ctx.guild.id, ctx.author.id)
        u = get_user(ctx.guild.id, member.id)
        
        if u["clan"]: return await ctx.send(embed=error_embed("This user is already in a clan."))
        if len(c["members"]) >= c.get("max_members", 20): return await ctx.send(embed=error_embed("Clan is full."))
        
        view = TargetAcceptView(member)
        msg = await ctx.send(embed=info_embed("📩 Clan Invitation", f"{member.mention}, **{ctx.author.name}** invited you to join **{c['name']}** `[{c.get('id', 'N/A')}]`.\nDo you accept?"), view=view)
        await view.wait()
        
        if view.value:
            u["clan"] = c["name"].lower()
            c["members"].append(str(member.id))
            _save(CLANS)
            await sync_roles(ctx.guild, c, member)
            await msg.edit(embed=success_embed(f"{member.mention} has joined the clan!"), view=None)
        else:
            await msg.edit(embed=error_embed(f"{member.mention} declined the invitation."), view=None)

    @commands.command(name="removeuser")
    @is_staff()
    async def removeuser(self, ctx, member: discord.Member):
        c = get_clan_by_user(ctx.guild.id, ctx.author.id)
        if str(member.id) not in c["members"]: return await ctx.send(embed=error_embed("This user is not in your clan."))
        if str(member.id) == c["leader"]: return await ctx.send(embed=error_embed("You cannot remove the Clan Leader."))
        
        view = ConfirmView(ctx.author)
        msg = await ctx.send(embed=info_embed("⚠️ Confirmation Required", f"Are you sure you want to kick **{member.name}** from the clan?"), view=view)
        await view.wait()
        
        if not view.value:
            return await msg.edit(embed=error_embed("Action cancelled."), view=None)

        c["members"].remove(str(member.id))
        if str(member.id) in c.get("coleaders", []): c["coleaders"].remove(str(member.id))
        get_user(ctx.guild.id, member.id)["clan"] = None
        await remove_roles(ctx.guild, member, c)
        _save(CLANS)
        await msg.edit(embed=success_embed(f"{member.mention} has been removed from the clan."), view=None)

    @commands.command(name="addcol")
    @is_leader()
    async def addcol(self, ctx, member: discord.Member):
        c = get_clan_by_user(ctx.guild.id, ctx.author.id)
        if str(member.id) not in c["members"]: return await ctx.send(embed=error_embed("User is not in your clan."))
        
        max_col = c.get("max_coleaders", 2)
        if len(c.get("coleaders", [])) >= max_col: 
            return await ctx.send(embed=error_embed(f"Co-Leader limit reached (Max: {max_col})."))
        
        view = TargetAcceptView(member)
        msg = await ctx.send(embed=info_embed("⭐ Co-Leader Promotion", f"{member.mention}, the Leader wants to promote you to **Co-Leader**.\nDo you accept?"), view=view)
        await view.wait()
        
        if view.value:
            if str(member.id) not in c.setdefault("coleaders", []):
                c["coleaders"].append(str(member.id))
                _save(CLANS)
                await sync_roles(ctx.guild, c, member)
                await msg.edit(embed=success_embed(f"{member.mention} is now a **Co-Leader**."), view=None)
        else:
            await msg.edit(embed=error_embed(f"{member.mention} declined the promotion."), view=None)

    @commands.command(name="removecol")
    @is_leader()
    async def removecol(self, ctx, member: discord.Member):
        c = get_clan_by_user(ctx.guild.id, ctx.author.id)
        if str(member.id) not in c.get("coleaders", []):
            return await ctx.send(embed=error_embed("This user is not a Co-Leader."))
            
        view = ConfirmView(ctx.author)
        msg = await ctx.send(embed=info_embed("⚠️ Confirmation Required", f"Are you sure you want to demote **{member.name}** from Co-Leader?"), view=view)
        await view.wait()
        
        if not view.value:
            return await msg.edit(embed=error_embed("Action cancelled."), view=None)

        c["coleaders"].remove(str(member.id))
        _save(CLANS)
        await sync_roles(ctx.guild, c, member)
        await msg.edit(embed=success_embed(f"{member.mention} is no longer a Co-Leader."), view=None)

    @commands.command(name="set-owner")
    @is_leader()
    async def set_owner(self, ctx, member: discord.Member):
        c = get_clan_by_user(ctx.guild.id, ctx.author.id)
        if str(member.id) not in c["members"]: return await ctx.send(embed=error_embed("User is not in your clan."))
        
        view = TargetAcceptView(member)
        msg = await ctx.send(embed=info_embed("👑 Leadership Transfer", f"{member.mention}, the current Leader wants to transfer Clan Leadership to you.\nDo you accept?"), view=view)
        await view.wait()
        
        if view.value:
            old = ctx.guild.get_member(int(c["leader"]))
            c["leader"] = str(member.id)
            if str(member.id) in c.get("coleaders", []): c["coleaders"].remove(str(member.id))
            _save(CLANS)
            
            if old: await sync_roles(ctx.guild, c, old)
            await sync_roles(ctx.guild, c, member)
            await msg.edit(embed=success_embed(f"{member.mention} is now the new **Clan Leader**."), view=None)
        else:
            await msg.edit(embed=error_embed(f"{member.mention} declined the leadership transfer."), view=None)

    @commands.command(name="settag")
    @is_leader()
    async def settag(self, ctx, tag: str):
        c = get_clan_by_user(ctx.guild.id, ctx.author.id)
        c["tag"] = tag[:5].upper()
        _save(CLANS)
        await ctx.send(embed=success_embed(f"Clan tag updated to `[{c['tag']}]`."))

    @commands.command(name="clansetup")
    @is_leader()
    async def clansetup_cmd(self, ctx, setting: str, *, value: str):
        c = get_clan_by_user(ctx.guild.id, ctx.author.id)
        role = ctx.guild.get_role(c.get("role_id"))
        if not role: return await ctx.send(embed=error_embed("Clan role not found."))
        
        if setting.lower() == "color":
            try:
                color = int(value.replace("#", ""), 16)
                await role.edit(color=discord.Color(color))
                c["color"] = color
                _save(CLANS)
                await ctx.send(embed=success_embed(f"Clan color updated to `{value}`."))
            except:
                await ctx.send(embed=error_embed("Invalid color format! (Example: `#FF0000`)"))
        elif setting.lower() == "icon":
            try:
                await role.edit(unicode_emoji=value)
                await ctx.send(embed=success_embed(f"Clan icon updated to `{value}`."))
            except:
                await ctx.send(embed=error_embed("Invalid icon! Please use a single emoji (Example: 🛡️)."))
        else:
            await ctx.send(embed=error_embed("Usage: `&clansetup color #HEX` or `&clansetup icon 🛡️`"))

    # ═══════════════════════════════════════════════════════════════════
    # ─── MANAGER COMMANDS (WITH CONFIRMATIONS)
    # ═══════════════════════════════════════════════════════════════════

    @commands.command(name="createclan")
    @is_manager()
    async def create(self, ctx, leader: discord.Member, *, name: str):
        if get_clan_by_query(ctx.guild.id, name): return await ctx.send(embed=error_embed("A clan with this name already exists."))
        existing_role = discord.utils.get(ctx.guild.roles, name=name)
        if existing_role: return await ctx.send(embed=error_embed(f"A role named `{name}` already exists."))
            
        u = get_user(ctx.guild.id, leader.id)
        if u["clan"]: return await ctx.send(embed=error_embed("This user is already in a clan."))
        
        try:
            role = await ctx.guild.create_role(name=name, reason="Clan created")
        except:
            return await ctx.send(embed=error_embed("Failed to create role (Missing Permissions)."))
        
        clan_id = generate_clan_id()
        category_text = discord.utils.find(lambda c: CATEGORY_TEXT_NAME in c.name, ctx.guild.categories)
        category_voice = discord.utils.find(lambda c: CATEGORY_VOICE_NAME in c.name, ctx.guild.categories)

        if not category_text:
            try: category_text = await ctx.guild.create_category(f"💬 | {CATEGORY_TEXT_NAME}")
            except: pass
        if not category_voice:
            try: category_voice = await ctx.guild.create_category(f"🔊 | {CATEGORY_VOICE_NAME}")
            except: pass

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False, connect=False),
            role: discord.PermissionOverwrite(view_channel=True, connect=True, send_messages=True, read_message_history=True),
        }
        for r in ctx.guild.roles:
            if r.permissions.administrator or r.permissions.manage_channels:
                overwrites[r] = discord.PermissionOverwrite(view_channel=True, connect=True)

        text_ch = None
        voice_ch = None
        try:
            text_ch = await ctx.guild.create_text_channel(name=f"💬・{name}", category=category_text, overwrites=overwrites)
            voice_ch = await ctx.guild.create_voice_channel(name=f"🔊 {name}", category=category_voice, overwrites=overwrites)
        except Exception as e:
            print(f"Error creating clan channels: {e}")

        c = {
            "id": clan_id, "name": name, "leader": str(leader.id), "members": [str(leader.id)], 
            "coleaders": [], "tag": "", "role_id": role.id, 
            "text_channel_id": text_ch.id if text_ch else None,
            "voice_channel_id": voice_ch.id if voice_ch else None,
            "color": 0, "max_members": 20, "max_coleaders": 2, "clan_of_week": False
        }
        
        get_guild_data(ctx.guild.id)["clans"][name.lower()] = c
        u["clan"] = name.lower()
        _save(CLANS)
        await sync_roles(ctx.guild, c, leader)
        
        embed = info_embed("⚔️ Clan Created Successfully", f"**Clan Name:** {name}\n**Clan ID:** `{clan_id}`\n**Leader:** {leader.mention}")
        if text_ch: embed.add_field(name="Channels Created", value=f"{text_ch.mention} | {voice_ch.mention}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="deleteclan")
    @is_manager()
    async def delete(self, ctx, *, query: str):
        c = get_clan_by_query(ctx.guild.id, query)
        if not c: return await ctx.send(embed=error_embed(f"No clan found matching `{query}`."))
        
        view = ConfirmView(ctx.author)
        msg = await ctx.send(embed=info_embed("⚠️ DANGER: Delete Clan", f"Are you sure you want to **DELETE** the clan **{c['name']}** `[{c.get('id', 'N/A')}]`?\nThis will remove all members, roles, and channels."), view=view)
        await view.wait()
        
        if not view.value:
            return await msg.edit(embed=error_embed("Action cancelled."), view=None)

        gd = get_guild_data(ctx.guild.id)
        role = ctx.guild.get_role(c.get("role_id"))
        if role: 
            try: await role.delete()
            except: pass
            
        text_ch = ctx.guild.get_channel(c.get("text_channel_id")) if c.get("text_channel_id") else None
        voice_ch = ctx.guild.get_channel(c.get("voice_channel_id")) if c.get("voice_channel_id") else None
        
        if text_ch:
            try: await text_ch.delete()
            except: pass
        if voice_ch:
            try: await voice_ch.delete()
            except: pass

        for uid in c["members"]: 
            gd["users"][uid]["clan"] = None
            m = ctx.guild.get_member(int(uid))
            if m: await remove_roles(ctx.guild, m, c)
                
        del gd["clans"][c["name"].lower()]
        _save(CLANS)
        await msg.edit(embed=success_embed(f"Clan **{c['name']}** `[{c.get('id', 'N/A')}]` has been deleted completely."), view=None)

    @commands.command(name="renameclan")
    @is_manager()
    async def renameclan(self, ctx, old_query: str, *, new_name: str):
        c = get_clan_by_query(ctx.guild.id, old_query)
        if not c: return await ctx.send(embed=error_embed(f"No clan found matching `{old_query}`."))
        if get_clan_by_query(ctx.guild.id, new_name): return await ctx.send(embed=error_embed("New name is already in use."))
        
        view = ConfirmView(ctx.author)
        msg = await ctx.send(embed=info_embed("⚠️ Confirmation Required", f"Rename clan **{c['name']}** to **{new_name}**?"), view=view)
        await view.wait()
        
        if not view.value: return await msg.edit(embed=error_embed("Action cancelled."), view=None)

        role = ctx.guild.get_role(c.get("role_id"))
        if role: 
            try: await role.edit(name=new_name)
            except: pass
        
        text_ch = ctx.guild.get_channel(c.get("text_channel_id")) if c.get("text_channel_id") else None
        voice_ch = ctx.guild.get_channel(c.get("voice_channel_id")) if c.get("voice_channel_id") else None
        
        if text_ch:
            try: await text_ch.edit(name=f"💬・{new_name}")
            except: pass
        if voice_ch:
            try: await voice_ch.edit(name=f"🔊 {new_name}")
            except: pass
            
        gd = get_guild_data(ctx.guild.id)
        old_name_lower = c["name"].lower()
        c["name"] = new_name
        gd["clans"][new_name.lower()] = c
        del gd["clans"][old_name_lower]
        
        for uid in c["members"]: gd["users"][uid]["clan"] = new_name.lower()
        _save(CLANS)
        
        await msg.edit(embed=success_embed(f"Clan successfully renamed to **{new_name}** (ID: `{c.get('id', 'N/A')}`)."), view=None)

    @commands.command(name="resetpoints")
    @is_manager()
    async def resetpoints(self, ctx):
        view = ConfirmView(ctx.author)
        msg = await ctx.send(embed=info_embed("⚠️ Confirmation Required", "Are you sure you want to reset **ALL** weekly voice points for every user?"), view=view)
        await view.wait()
        
        if not view.value: return await msg.edit(embed=error_embed("Action cancelled."), view=None)
        
        gd = get_guild_data(ctx.guild.id)
        for u in gd["users"].values(): u["weekly"] = 0
        _save(CLANS)
        await msg.edit(embed=success_embed("Weekly voice points have been reset for all users."), view=None)

    @commands.command(name="clan-of-the-week")
    @is_manager()
    async def clan_of_week(self, ctx, *, query: str):
        c = get_clan_by_query(ctx.guild.id, query)
        if not c: return await ctx.send(embed=error_embed(f"No clan found matching `{query}`."))
        
        view = ConfirmView(ctx.author)
        msg = await ctx.send(embed=info_embed("🏆 Clan of the Week", f"Are you sure you want to set **{c['name']}** as the Clan of the Week?\nThis will apply the role to all its members."), view=view)
        await view.wait()
        
        if not view.value: return await msg.edit(embed=error_embed("Action cancelled."), view=None)

        gd = get_guild_data(ctx.guild.id)
        cotw_role = ctx.guild.get_role(CLAN_OF_THE_WEEK_ROLE_ID)
        
        for cid, old_c in gd["clans"].items():
            if old_c.get("clan_of_week"):
                old_c["clan_of_week"] = False
                if cotw_role:
                    for uid in old_c["members"]:
                        m = ctx.guild.get_member(int(uid))
                        if m and cotw_role in m.roles:
                            try: await m.remove_roles(cotw_role)
                            except: pass

        c["clan_of_week"] = True
        if cotw_role:
            for uid in c["members"]:
                m = ctx.guild.get_member(int(uid))
                if m and cotw_role not in m.roles:
                    try: await m.add_roles(cotw_role)
                    except: pass
        _save(CLANS)
        await msg.edit(embed=success_embed(f"**{c['name']}** is now the **Clan of the Week**! Role applied to members."), view=None)

    @commands.command(name="removeclan-of-the-week", aliases=["removecotw", "delcotw"])
    @is_manager()
    async def remove_clan_of_week(self, ctx):
        """+removeclan-of-the-week — Hyed لقب Clan of the Week"""
        view = ConfirmView(ctx.author)
        msg = await ctx.send(embed=info_embed("⚠️ Confirmation Required", "Are you sure you want to **REMOVE** the Clan of the Week title and role from the current clan?"), view=view)
        await view.wait()
        
        if not view.value: 
            return await msg.edit(embed=error_embed("Action cancelled."), view=None)

        gd = get_guild_data(ctx.guild.id)
        cotw_role = ctx.guild.get_role(CLAN_OF_THE_WEEK_ROLE_ID)
        found = False
        
        for cid, c in gd["clans"].items():
            if c.get("clan_of_week"):
                c["clan_of_week"] = False
                found = True
                if cotw_role:
                    for uid in c["members"]:
                        m = ctx.guild.get_member(int(uid))
                        if m and cotw_role in m.roles:
                            try: await m.remove_roles(cotw_role)
                            except: pass
                            
        _save(CLANS)
        
        if found:
            await msg.edit(embed=success_embed("Clan of the Week has been **REMOVED** successfully. The role was taken from all members."), view=None)
        else:
            await msg.edit(embed=error_embed("❌ No clan is currently set as Clan of the Week."), view=None)

    @commands.command(name="updaterole")
    @is_manager()
    async def updaterole(self, ctx, query: str, role: discord.Role):
        """+updaterole <clan> @role — Beddel role dyal clan"""
        c = get_clan_by_query(ctx.guild.id, query)
        if not c:
            return await ctx.send(embed=error_embed(f"No clan found matching `{query}`."))

        old_role = ctx.guild.get_role(c.get("role_id"))
        view = ConfirmView(ctx.author)
        msg = await ctx.send(
            embed=info_embed(
                "⚠️ Confirmation Required",
                f"Change role dyal **{c['name']}** mn {old_role.mention if old_role else 'None'} → {role.mention}?"
            ),
            view=view,
        )
        await view.wait()
        if not view.value:
            return await msg.edit(embed=error_embed("Action cancelled."), view=None)

        c["role_id"] = role.id
        _save(CLANS)
        await msg.edit(embed=success_embed(f"Role updated to {role.mention}."), view=None)

    @commands.command(name="giveclan")
    @is_manager()
    async def giveclan(self, ctx, query: str, member: discord.Member):
        """+giveclan <clan> @user — 3ti l-owner b l-9owa"""
        c = get_clan_by_query(ctx.guild.id, query)
        if not c:
            return await ctx.send(embed=error_embed(f"No clan found matching `{query}`."))
        if str(member.id) not in c["members"]:
            return await ctx.send(embed=error_embed("User is not in this clan."))
        if c["leader"] == str(member.id):
            return await ctx.send(embed=error_embed("User is already the leader."))

        view = ConfirmView(ctx.author)
        msg = await ctx.send(
            embed=info_embed(
                "⚠️ Confirmation Required",
                f"Give leadership of **{c['name']}** to {member.mention}?"
            ),
            view=view,
        )
        await view.wait()
        if not view.value:
            return await msg.edit(embed=error_embed("Action cancelled."), view=None)

        old_leader = ctx.guild.get_member(int(c["leader"]))
        c["leader"] = str(member.id)
        if str(member.id) in c.get("coleaders", []):
            c["coleaders"].remove(str(member.id))
        _save(CLANS)

        if old_leader:
            await sync_roles(ctx.guild, c, old_leader)
        await sync_roles(ctx.guild, c, member)
        await msg.edit(
            embed=success_embed(f"{member.mention} is now the new leader."),
            view=None,
        )

    @commands.command(name="forceaddmember")
    @is_manager()
    async def forceaddmember(self, ctx, member: discord.Member, query: str):
        """+forceaddmember @user <clan> — Zid member b l-9owa"""
        c = get_clan_by_query(ctx.guild.id, query)
        if not c:
            return await ctx.send(embed=error_embed(f"No clan found matching `{query}`."))
        if len(c["members"]) >= c.get("max_members", 20):
            return await ctx.send(embed=error_embed("Clan is full."))

        u = get_user(ctx.guild.id, member.id)

        # Remove mn clan 9dim ila kayn
        if u["clan"]:
            old_c = get_clan_by_user(ctx.guild.id, member.id)
            if old_c and str(member.id) in old_c["members"]:
                old_c["members"].remove(str(member.id))
                if str(member.id) in old_c.get("coleaders", []):
                    old_c["coleaders"].remove(str(member.id))
                if old_c["leader"] == str(member.id) and old_c["members"]:
                    new_l = old_c["members"][0]
                    old_c["leader"] = new_l

        u["clan"] = c["name"].lower()
        c["members"].append(str(member.id))
        _save(CLANS)
        await sync_roles(ctx.guild, c, member)
        await ctx.send(embed=success_embed(f"{member.mention} added to **{c['name']}**."))

    @commands.command(name="clearcoleaders")
    @is_manager()
    async def clearcoleaders(self, ctx):
        """+clearcoleaders — Msa7 co-leaders li khraj mn server"""
        gd = get_guild_data(ctx.guild.id)
        removed = 0
        for cid, c in gd["clans"].items():
            for uid in list(c.get("coleaders", [])):
                m = ctx.guild.get_member(int(uid))
                if m is None or str(m.id) not in c["members"]:
                    c["coleaders"].remove(uid)
                    removed += 1
        _save(CLANS)
        await ctx.send(embed=success_embed(f"Removed `{removed}` invalid co-leaders."))

    @commands.command(name="update-limits")
    @is_manager()
    async def update_limits(self, ctx, query: str, type_: str, num: int):
        """+update-limits <clan> <members|coleaders> <num>"""
        c = get_clan_by_query(ctx.guild.id, query)
        if not c:
            return await ctx.send(embed=error_embed(f"No clan found matching `{query}`."))

        t = type_.lower()
        if t == "members":
            if num < len(c["members"]):
                return await ctx.send(embed=error_embed("Num smaller than current members."))
            c["max_members"] = num
        elif t == "coleaders":
            if num < len(c.get("coleaders", [])):
                return await ctx.send(embed=error_embed("Num smaller than current coleaders."))
            c["max_coleaders"] = num
        else:
            return await ctx.send(embed=error_embed("Type must be `members` or `coleaders`."))

        _save(CLANS)
        await ctx.send(embed=success_embed(f"`{t}` limit updated to `{num}` for **{c['name']}**."))


async def setup(bot):
    await bot.add_cog(Clans(bot))