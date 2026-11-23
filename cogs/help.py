# cogs/help.py
# =====================================================================
# ─── HELP SYSTEM — &help (public) + /help (public) + +help (staff only)
# =====================================================================
import discord
from discord import app_commands
from discord.ext import commands

from botconfig import (
    user_has_permission, is_known_command, _has_role,
    ADMIN_ROLES, MODERATOR_ROLES, HELPER_ROLES, STAFF_ROLES,
)

# ═══════════════════════════════════════════════════════════════════
# ─── HELP CATEGORIES
# ═══════════════════════════════════════════════════════════════════
HELP_CATEGORIES = {
    # ═══════════════ PUBLIC CATEGORIES ═══════════════
    "🏠 Home": {
        "description": "L-basics — bda mn hna",
        "commands": [
            ("help",       "Affichi had l-menu",                     "/help",                     "public"),
            ("cmds",       "Menu b prefix",                          "&help",                     "public"),
            ("ping",       "Latency dyal l-bot",                     "/ping",                     "public"),
            ("serverinfo", "Ma3loumat 3la l-server",                 "/serverinfo",               "public"),
            ("userinfo",   "Ma3loumat 3la user",                     "/userinfo [@user]",         "public"),
            ("avatar",     "Avatar dyal user",                       "/avatar [@user]",           "public"),
            ("banner",     "Banner dyal user",                       "/banner [@user]",           "public"),
        ],
    },
    "🎮 Games": {
        "description": "Al3ab w tfasli7",
        "commands": [
            ("8ball",     "S'el chi soual",                         "/8ball <question>",         "public"),
            ("roll",      "Rmi dice",                               "/roll [sides]",             "public"),
            ("coinflip",  "Rmi coin (pile wla face)",               "/coinflip",                 "public"),
            ("dice",      "Zhar b emojis",                          "/dice [count]",             "public"),
            ("slots",     "Makanat l-haz (bla flous)",              "/slots",                    "public"),
            ("rps",       "Rock Paper Scissors",                    "/rps <choice>",             "public"),
            ("trivia",    "Soual culture",                          "/trivia",                   "public"),
            ("guess",     "Khamen ra9m",                            "&guess",                    "public"),
            ("poll",      "Sondage",                                "/poll <question>",          "public"),
        ],
    },
    "🎯 Game Requests": {
        "description": "3ayet l-gamers — ping role dyal game",
        "commands": [
            ("ff",         "Invite Free Fire players",     "&ff",         "public"),
            ("pes",        "Invite PES players",           "&pes",        "public"),
            ("valo",       "Invite Valorant players",      "&valo",       "public"),
            ("roblox",     "Invite Roblox players",        "&roblox",     "public"),
            ("listgames",  "Chouf games configurés",       "&listgames",  "public"),
        ],
    },
    "💰 Economy": {
        "description": "Nizam l-flous (Coins)",
        "commands": [
            ("balance",     "Chouf l-balance",                      "/balance [@user]",          "public"),
            ("coins",       "Chouf l-balance (+coins)",             "&coins [@user]",            "public"),
            ("daily",       "Rati yawmi",                           "/daily",                    "public"),
            ("work",        "Khdm w jib flous (10s)",               "/work",                     "public"),
            ("rob",         "Srq chi wa7ed",                        "/rob @user",                "public"),
            ("pay",         "Sift flous l chi wa7ed",               "/pay @user <amount>",       "public"),
            ("gamble",      "Qamr flousek",                         "/gamble <amount>",          "public"),
            ("collect",     "Jme3 income mn roles (30min)",         "/collect",                  "public"),
        ],
    },
    "🔮 Bir": {
        "description": "العملة الثانية — non-transferable",
        "commands": [
            ("bir",     "Chouf l-Bir dyalk",       "&bir [@user]",   "public"),
            ("birwork", "Khdm bash tjib Bir",      "&bw",            "public"),
            ("birtop",  "Top 10 Bir",              "&bt",            "public"),
        ],
    },
    "🎖️ Rank & Levels": {
        "description": "Nizam l-levels w XP",
        "commands": [
            ("rankcard", "Rank Card dyalk",   "/rankcard [@user]",   "public"),
            ("rcard",    "Rank Card (prefix)", "&rcard [@user]",      "public"),
            ("rank",     "Rank (info)",       "/rank [@user]",       "public"),
            ("vcrank",   "Voice activity rank", "/vcrank [@user]", "public"),
            ("rank-top", "Voice activity leaderboard", "/rank-top", "public"),
            ("levels",   "Top 10 levels",     "/levels",             "public"),
            ("toprank",  "Top 10 rank",       "/toprank",            "public"),
        ],
    },
    "🎲 Gambling": {
        "description": "Kasino dyal bot — ghir f Casino channels 🎰",
        "commands": [
            ("cf",     "🪙 Coinflip (50/50)",                    "&cf <amount> <pile|face>",         "public"),
            ("d",      "🎲 Dice (5x)",                            "&d <amount> <1-6>",                "public"),
            ("rl",     "🔴 Roulette (2x / 14x)",                  "&rl <amount> <red|black|green>",   "public"),
            ("s",      "🎰 Slots (10x max)",                      "&s <amount>",                      "public"),
            ("bj",     "🃏 Blackjack (Hit / Stand / Double)",    "&bj <amount>",                     "public"),
            ("hl",     "📈 High-Low (Higher / Lower)",            "&hl <amount>",                     "public"),
            ("mines",  "💣 Mines (5x5 grid)",                     "&mines <amount> [bombs]",          "public"),
            ("crash",  "🚀 Crash (Cash Out 9bel crash)",          "&crash <amount>",                  "public"),
            ("bac",    "🎴 Baccarat (Player / Banker / Tie)",     "&bac <amount>",                    "public"),
            ("poker",  "🃏 Video Poker (Hold / Draw)",            "&poker <amount>",                  "public"),
            ("tower",  "🗼 Tower (8 floors, 1 mn 3)",             "&tower <amount>",                  "public"),
            ("rlt",    "🎡 Roulette Interactive (buttons)",       "&rlt <amount>",                    "public"),
            ("hr",     "🐎 Horse Race (5 horses)",                "&hr <1-5> <amount>",               "public"),
            ("wheel",  "🎡 Wheel of Fortune (10x)",               "&wheel <amount>",                  "public"),
            ("plinko", "🎯 Plinko (low/medium/high)",             "&plinko <amount> [risk]",          "public"),
        ],
    },
    "🛒 Shop": {
        "description": "Chri roles b flousek + income",
        "commands": [
            ("shop",    "Chouf l-shop",    "/shop",           "public"),
            ("buy",     "Chri item",       "/buy <item_key>", "public"),
            ("collect", "Jme3 income",     "/collect",        "public"),
        ],
    },
    "🏆 Tournaments": {
        "description": "Tournament system — prize pool",
        "commands": [
            ("tournament",         "List open tournaments",       "&tournament",                          "public"),
            ("tournament create",  "Sayeb tournament",            "&tournament create <game> <entry> <max>","public"),
            ("tournament join",    "Dkhol f tournament",          "&tournament join <id>",                "public"),
            ("tournament start",   "Bda tournament (host only)",  "&tournament start <id>",               "public"),
            ("tournament leave",   "Kherj + refund",              "&tournament leave <id>",               "public"),
        ],
    },
    "🏴‍☠️ Heist": {
        "description": "Team bank robbery (min 3 players)",
        "commands": [
            ("heist",        "Chouf active heist",                "&heist",                    "public"),
            ("heist start",  "Bda heist (min 1,000)",             "&heist start <amount>",     "public"),
            ("heist join",   "Dkhol f heist",                     "&heist join",               "public"),
            ("heist go",     "Bda l-heist (host only)",           "&heist go",                 "public"),
        ],
    },
    "🏆 Leaderboards": {
        "description": "Top 10 dyal kolchi",
        "commands": [
            ("lb",        "Top 10 Coins",   "&lb",        "public"),
            ("topmoney",  "Top 10 Coins",   "/topmoney",  "public"),
            ("bt",        "Top 10 Bir",     "&bt",        "public"),
            ("toprank",   "Top 10 Rank",    "/toprank",   "public"),
        ],
    },
    
    # ═══════════════ ⚔️ CLANS (PUBLIC) ═══════════════
    "⚔️ Clans": {
        "description": "Nizam dyal clans (voice points, roles)",
        "commands": [
            ("clanhelp",     "Help dyal clan system",            "&clanhelp",             "public"),
            ("clans",        "List dyal ga3 les clans",          "&clans",                "public"),
            ("myclan",       "Chouf clan dyalek",                "&myclan",               "public"),
            ("mypoints",     "Chouf sway3 dyalek",               "&mypoints",             "public"),
            ("mytime",       "Chouf sway3 dyalek",               "&mytime",               "public"),
            ("usertime",     "Chouf sway3 dyal chi member",      "&usertime @user",       "public"),
            ("lbc",          "Top 10 Clans f server",            "&lbc",                  "public"),
            ("claninfo",     "Chouf info dyal chi clan",         "&claninfo <Name>",      "public"),
            ("clanlist",     "List dyal members",                "&clanlist <Name>",      "public"),
            ("topc",         "Top members f clan dyalek",        "&topc",                 "public"),
            ("leaveclan",    "Kherj mn clan",                    "&leaveclan",            "public"),
            ("adduser",      "Zid member (Co-Leader)",           "&adduser @user",        "public"),
            ("removeuser",   "Hyed member (Co-Leader)",          "&removeuser @user",     "public"),
            ("addcol",       "3ti Co-Leader (Leader)",           "&addcol @user",         "public"),
            ("removecol",    "Hyed Co-Leader (Leader)",          "&removecol @user",      "public"),
            ("set-owner",    "3ti l-owner (Leader)",             "&set-owner @user",      "public"),
            ("settag",       "Beddel tag dyal clan",             "&settag <TAG>",         "public"),
            ("clansetup",    "Beddel color/icon",                "&clansetup <color|icon> <val>", "public"),
        ],
    },
    
    "ℹ️ Info": {
        "description": "Ma3loumat mn l-internet w dyal server",
        "commands": [
            ("anime",     "Ma3loumat anime",                        "/anime <title>",            "public"),
            ("manga",     "Ma3loumat manga",                        "/manga <title>",            "public"),
            ("weather",   "Weather f chi mdina",                    "/weather <city>",           "public"),
            ("translate", "Traduchi text",                          "/translate <text> <to>",    "public"),
            ("lyrics",    "Lyrics dyal gheniya",                    "/lyrics <artist> <title>",  "public"),
            ("members",   "Statistiques dyal members",              "/members",                  "public"),
            ("bots",      "L-lista dyal bots",                      "/bots",                     "public"),
            ("invites",   "Invitations dyal server",                "/invites",                  "public"),
            ("serverstats", "📊 Stats kamla dyal server",           "+serverstats",              "public"),
            ("roleinfo",    "🎭 Info 3la chi role (members, perms)","+roleinfo @role",           "public"),
            ("roleslist",   "📋 List dyal ga3 les roles w members", "+roleslist",                "public"),
            ("channels",    "📋 List dyal ga3 channels",            "+channels",                 "public"),
        ],
    },
    "🎨 Utility": {
        "description": "Adawat mfidin",
        "commands": [
            ("math",      "7sab riyadi",         "/math <expression>",    "public"),
            ("base64",    "Encode/Decode base64","/base64 <text> <mode>", "public"),
            ("password",  "Générer password qwi","/password [length]",    "public"),
            ("uuid",      "Générer UUID",        "/uuid",                 "public"),
            ("timestamp", "Discord timestamp",   "/timestamp <datetime>", "public"),
        ],
    },
    "🎙️ Temp Voice": {
        "description": "Temp Voice — OneTap + Control",
        "commands": [
            ("ot",  "Creeyi temp VC",       "/ot",                "public"),
            ("vc",  "Control VC dyalk",     "&vc <action>",       "public"),
        ],
    },

    # ═══════════════ ADMIN / STAFF CATEGORIES ═══════════════
    
    # 👇 ZIDNA HAD L-CATEGORY DYAL JAIL MOD
    "🚔 Jail Mod": {
        "description": "Adawat dyal Jail Mod (Sjen w Fek)",
        "commands": [
            ("jail",   "🔒 Sjen member (hyed kolchi roles)", "+jail @user [reason]", "jail_mod"),
            ("rta7",   "🔓 7ayed jail (rejje3 roles)",       "+rta7 @user",          "jail_mod"),
            ("unjail", "🔓 Alias dyal rta7",                 "+unjail @user",        "jail_mod"),
        ],
    },
    
    "🛠️ Moderation": {
        "description": "Adawat dyal moderation",
        "commands": [
            ("ms7",         "Msa7 messages",              "+ms7 <amount>",             "moderation"),
            ("kick",        "Kherrej user",               "+kick @user [reason]",      "moderation"),
            ("ban",         "Ban user",                   "+ban @user [days] [reason]","moderation"),
            ("unban",       "Unban user",                 "+unban <user_id> [reason]", "moderation"),
            ("warn",        "Warning l member",           "+warn @user [reason]",      "moderation"),
            ("warnings",    "Chouf warnings",             "+warnings @user",           "moderation"),
            ("history",     "Chouf history dyal user",    "+history @user",            "moderation"),
            ("clearwarns",  "Msa7 warnings",              "+clearwarns @user",         "moderation"),
            ("slowmode",    "Slow mode f channel",        "+slowmode <seconds>",       "moderation"),
            ("lock",        "Qfel channel",               "+lock",                     "moderation"),
            ("unlock",      "Ftah channel",               "+unlock",                   "moderation"),
            ("timeout",     "⏱️ Timeout member (1h/30m/1d/7d)",  "+timeout @user <dur>",  "moderation"),
            ("untimeout",   "⏱️ 7ayed timeout",                    "+untimeout @user",      "moderation"),
            ("case",        "Chouf case dyal moderation",         "+case <id>",            "moderation"),
            ("cases",       "Chouf cases dyal user",              "+case user @user",      "moderation"),
        ],
    },
    "🛡️ Verification": {
        "description": "T-verifi l-members w 3tihom roles dyal games",
        "commands": [
            ("verify",   "3mmer l-form dyal user",         "+verify @user",        "verification"),
            ("vb",       "Verify Basic + Game Roles",      "+vb <ID|@user>",       "verification"),
            ("vg",       "Verify Girl + Game Roles",       "+vg <ID|@user>",       "verification"),
            ("vcheck",   "Chouf info dyal verification",   "+vcheck @user",        "verification"),
            ("vlist",    "List dyal pending w verified",   "+vlist [pending|verified]", "verification"),
            ("unverify", "Hyed l-verification",            "+unverify @user",      "verification"),
        ],
    },
    "🧩 Server Systems": {
        "description": "Setup, self roles, and staff applications",
        "commands": [
            ("setup", "Reconcile and configure server resources", "/setup", "admin_only"),
            ("selfrole-setup", "Create or edit a persistent self-role menu", "/selfrole-setup", "admin_only"),
            ("selfrole-delete", "Delete a persistent self-role menu", "/selfrole-delete <message_id>", "admin_only"),
            ("applystaff-setup", "Create or repost the staff application panel", "/applystaff-setup", "admin_only"),
            ("vcrank-config", "Configure voice XP and anti-AFK rules", "/vcrank-config", "admin_only"),
        ],
    },
    "🎭 Roles": {
        "description": "Adawat dyal roles",
        "commands": [
            ("giverole",   "3ti role l member",    "+giverole @user @role",   "moderation"),
            ("removerole", "Hyed role mn member",  "+removerole @user @role", "moderation"),
            ("massrole",   "3ti role l kolchi",    "+massrole @role",         "admin_only"),
            ("striprole",  "🧹 Hyed role mn GA3 l-members", "+striprole @role", "admin_only"),
        ],
    },
    "🔧 Channels": {
        "description": "Channel manager — create/delete/rename/move/bulk",
        "commands": [
            ("cm",       "Channel manager menu",       "+cm",                              "moderation"),
            ("channel",  "Channel commands",           "+channel create/delete/rename/...", "moderation"),
            ("category", "Category commands",          "+category create/delete/rename",    "moderation"),
        ],
    },
    "🎙️ Voice Admin": {
        "description": "Bot voice control",
        "commands": [
            ("botjoin",      "Bot ydkhol l voice",     "+join",      "admin_only"),
            ("botleave",     "Bot ykhrej mn voice",    "+leave",     "admin_only"),
            ("voice247",  "Status dyal voice 24/7", "+voice247",  "admin_only"),
        ],
    },
    "📢 Announcements": {
        "description": "Announcements (Event / Meeting / News)",
        "commands": [
            ("announce", "Styled announcement (3 types)", "+announce <type> <title> ...", "moderation"),
            ("embed",    "Embed custom",                    "+embed <title> <desc>",         "moderation"),
        ],
    },
    
    "⚔️ Clan Manager": {
        "description": "Commands dyal l-Manager dyal les clans",
        "commands": [
            ("createclan",       "Sayeb clan jdid",                "+createclan @leader <Name>", "clan_manager"),
            ("deleteclan",       "Msa7 chi clan",                  "+deleteclan <Name>",         "clan_manager"),
            ("renameclan",       "Beddel smiya dyal clan",         "+renameclan <old> <new>",    "clan_manager"),
            ("updaterole",       "Beddel role dyal clan",          "+updaterole <clan> @role",   "clan_manager"),
            ("giveclan",         "3ti l-owner b l-9owa",           "+giveclan <clan> @user",     "clan_manager"),
            ("forceaddmember",   "Zid member b l-9owa",            "+forceaddmember @user <clan>","clan_manager"),
            ("clearcoleaders",   "Msa7 co-leaders li khraj mn server","+clearcoleaders",           "clan_manager"),
            ("resetpoints",      "Reset sway3 dyal ga3 les clans", "+resetpoints",               "clan_manager"),
            ("clan-of-the-week", "3ti Clan of the week",           "+clan-of-the-week <clan>",   "clan_manager"),
            ("update-limits",    "Beddel limits dyal clan",        "+update-limits <clan> <type> <num>","clan_manager"),
            ("removeclan-of-the-week",  "kat7yd clan of the week l chi clan",    "+removeclan-of-the-week <clan>",   "clan_manager"),
        ],
    },
    
    "🔐 Permissions": {
        "description": "Dynamic role permissions",
        "commands": [
            ("perms",    "Permissions manager",           "+perms",                     "admin_only"),
            ("perms grant",  "3ti perm l role",           "+perms grant @role <group>", "admin_only"),
            ("perms revoke", "Hyed perm",                 "+perms revoke @role <group>","admin_only"),
            ("perms list",   "Chouf perms",               "+perms list",                "admin_only"),
            ("myperms",  "Chouf perms dyalek",            "&myperms / +myperms",        "public"),
        ],
    },
    
    "🔒 Staff Only": {
        "description": "Commands ghir l-Staff l-fo9",
        "commands": [
            ("addmod",     "Zid role f Moderators",                 "+addmod @role",          "admin_only"),
            ("removemod",  "Hyed role mn Moderators",               "+removemod @role",       "admin_only"),
            ("listroles",  "Chouf roles configurés",                "+listroles",             "admin_only"),
            ("checkperm",  "Check permission dyal command",         "+checkperm <command>",   "admin_only"),
            ("setserver",  "Auto-create categories/channels/roles", "+setserver confirm",     "admin_only"),
            ("fixroles",   "Fix colors + perms + tartib dyal roles","+fixroles confirm",      "admin_only"),
            ("sysinfo",    "Chouf status dyal bot",                 "+sysinfo",               "admin_only"),
            ("allcmds",    "List dyal GA3 commands",                "&allcmds",               "public"),
        ],
    },
}

PUBLIC_CATEGORIES = [
    "🏠 Home", "🎮 Games", "🎯 Game Requests", "💰 Economy", "🔮 Bir",
    "🎖️ Rank & Levels", "🎲 Gambling", "🛒 Shop",
    "🏆 Tournaments", "🏴‍☠️ Heist", "🏆 Leaderboards",
    "⚔️ Clans", 
    "ℹ️ Info", "🎨 Utility", "🎙️ Temp Voice",
]

ADMIN_CATEGORIES = [
    "🚔 Jail Mod", # 👈 Zidna hadi
    "🛡️ Verification", "🛠️ Moderation", "🎭 Roles", "🔧 Channels", "🎙️ Voice Admin",
    "📢 Announcements", 
    "⚔️ Clan Manager", 
    "🔐 Permissions",
    "🔒 Staff Only",
]



@commands.command(name="allcmds")
async def allcmds_prefix(self, ctx: commands.Context):
    """&allcmds — List dyal GA3 commands m9assmin 3la l-Cogs"""
    
    # كنقسمو الأوامر على حساب الـ Cog
    cogs_cmds = {}
    for cmd in self.bot.commands:
        cog_name = cmd.cog_name or "No Cog"
        if cog_name not in cogs_cmds:
            cogs_cmds[cog_name] = []
        cogs_cmds[cog_name].append(cmd)

    embed = discord.Embed(
        title="📋 All Bot Commands (By Cog)",
        description=f"Total: **{len(self.bot.commands)}** commands",
        color=discord.Color.blurple()
    )

    for cog_name, cmds in sorted(cogs_cmds.items()):
        cmds.sort(key=lambda c: c.name)
        cmd_list = []
        for c in cmds:
            aliases = f" *(Aliases: {', '.join(c.aliases)})*" if c.aliases else ""
            cmd_list.append(f"`{c.name}`{aliases}")
        
        # Discord kiy7taj l-fields matfotoch 1024 chars, donc n9t3ohom
        text = "\n".join(cmd_list)
        if len(text) > 1024:
            text = text[:1020] + "..."
        
        embed.add_field(
            name=f"📁 {cog_name} ({len(cmds)})",
            value=text,
            inline=False
        )
        
        # Ila l-embed 3mer bzaf, nsifto w nsaybo wa7ed jdid
        if len(embed.fields) == 24:
            await ctx.send(embed=embed)
            embed = discord.Embed(
                title="📋 All Bot Commands (Cont.)",
                color=discord.Color.blurple()
            )
    
    if embed.fields:
        await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════════════════
# ─── STAFF CHECK
# ═══════════════════════════════════════════════════════════════════
def _is_staff(member: discord.Member) -> bool:
    if member is None or member.guild is None:
        return False
    if member.id == member.guild.owner_id:
        return True

    all_staff_roles = ADMIN_ROLES + MODERATOR_ROLES + HELPER_ROLES + STAFF_ROLES
    return any(_has_role(member, r) for r in all_staff_roles)

# ═══════════════════════════════════════════════════════════════════
# ─── UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════
class CategorySelect(discord.ui.Select):
    def __init__(self, categories, user, page: int = 0, total_pages: int = 1):
        options = [
            discord.SelectOption(
                label=cat.split(" ", 1)[1],
                emoji=cat.split(" ", 1)[0],
                value=cat,
                description=HELP_CATEGORIES[cat]["description"][:100],
            )
            for cat in categories[:25]
        ]
        if total_pages > 1:
            placeholder = f"📂 Categories ({page + 1}/{total_pages})..."
        else:
            placeholder = "Khtar category..."
        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options,
            row=page,
        )
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ Had l-menu machi dyalek!", ephemeral=True)
        category = self.values[0]
        embed = build_category_embed(category, interaction.user)
        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self, categories, user, mode: str = "public"):
        super().__init__(timeout=180)
        self.user = user
        self.mode = mode

        if categories:
            chunks = [categories[i:i + 25] for i in range(0, len(categories), 25)]
            total = len(chunks)
            for i, chunk in enumerate(chunks):
                self.add_item(CategorySelect(chunk, user, page=i, total_pages=total))

    @discord.ui.button(label="Home", emoji="🏠", style=discord.ButtonStyle.secondary, row=2)
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ Machi dyalek!", ephemeral=True)
        embed = build_home_embed(interaction.user, self.mode)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Close", emoji="✖️", style=discord.ButtonStyle.danger, row=2)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ Machi dyalek!", ephemeral=True)
        await interaction.message.delete()

# ═══════════════════════════════════════════════════════════════════
# ─── BUILDERS
# ═══════════════════════════════════════════════════════════════════
def build_home_embed(user: discord.Member, mode: str = "public") -> discord.Embed:
    is_admin_help = mode == "admin"

    if is_admin_help:
        title = "🔒 Staff Help Menu"
        desc = (
            "**Marhba f l-menu dyal l-Staff!**\n\n"
            "Khtar **category** mn l-dropdown bash tchouf l-commands.\n\n"
            "🔹 **Admin commands:** `+command`\n"
            "💡 Ila bghiti l-public help → st3mel `&help`"
        )
        color = discord.Color.dark_red()
    else:
        title = "📖 Public Help Menu"
        desc = (
            "**Marhba f l-menu dyal l-bot!**\n\n"
            "Khtar **category** mn l-dropdown bash tchouf l-commands.\n\n"
            "🔹 **Slash:** `/command`\n"
            "🔸 **Prefix:** `&command`"
        )
        color = discord.Color.blurple()

    embed = discord.Embed(title=title, description=desc, color=color, timestamp=discord.utils.utcnow())
    embed.set_footer(text=f"Requested by {user.name}", icon_url=user.display_avatar.url)

    categories_list = []
    cats = ADMIN_CATEGORIES if is_admin_help else PUBLIC_CATEGORIES
    for cat_name in cats:
        visible = get_visible_commands(cat_name, user)
        if visible:
            categories_list.append(f"{cat_name} — `{len(visible)} commands`")

    if categories_list:
        embed.add_field(name="📂 Categories", value="\n".join(categories_list), inline=False)

    return embed


def build_category_embed(category: str, user: discord.Member) -> discord.Embed:
    data = HELP_CATEGORIES[category]
    emoji, name = category.split(" ", 1)

    embed = discord.Embed(
        title=f"{emoji} {name}",
        description=data["description"],
        color=discord.Color.from_rgb(88, 101, 242),
        timestamp=discord.utils.utcnow(),
    )

    visible = get_visible_commands(category, user)
    if not visible:
        embed.add_field(name="⚠️ Ma 3ndkch permission", value="Ma 3ndkch permission f had category.", inline=False)
        return embed

    for cmd_name, desc, usage, _ in visible:
        embed.add_field(name=f"🔹 {cmd_name}", value=f"{desc}\n**Usage:** `{usage}`", inline=False)

    embed.set_footer(text=f"{len(visible)} commands • {user.name}", icon_url=user.display_avatar.url)
    return embed


def get_visible_commands(category: str, user: discord.Member):
    data = HELP_CATEGORIES.get(category, {})
    visible = []
    for cmd in data.get("commands", []):
        cmd_name = cmd[0]
        if not is_known_command(cmd_name):
            visible.append(cmd)
        elif user_has_permission(user, cmd_name):
            visible.append(cmd)
    return visible


def get_visible_categories(user: discord.Member, mode: str = "public"):
    cats = ADMIN_CATEGORIES if mode == "admin" else PUBLIC_CATEGORIES
    visible = []
    for cat in cats:
        if get_visible_commands(cat, user):
            visible.append(cat)
    return visible


def _find_category(raw: str, cats: list) -> str | None:
    raw = raw.lower().strip()
    for cat_name in cats:
        label = cat_name.split(" ", 1)[1].lower().strip() if " " in cat_name else cat_name.lower()
        if raw == label:
            return cat_name
    for cat_name in cats:
        label = cat_name.split(" ", 1)[1].lower().strip() if " " in cat_name else cat_name.lower()
        if raw and raw in label:
            return cat_name
    return None

# ═══════════════════════════════════════════════════════════════════
# ─── COG
# ═══════════════════════════════════════════════════════════════════
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _send_help_menu(self, ctx: commands.Context, command: str = None, mode: str = "public"):
        if command:
            return await self._show_command_details_prefix(ctx, command, mode=mode)

        user = ctx.author
        categories = get_visible_categories(user, mode=mode)

        if not categories:
            msg = "⚠️ Ma 3ndkch permission l hta admin command!" if mode == "admin" else "⚠️ Ma 3ndkch permission l hta command!"
            return await ctx.send(msg)

        embed = build_home_embed(user, mode=mode)
        view = HelpView(categories, user, mode=mode)
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="help", description="Affichi l-menu dyal l-commands (Public)")
    @app_commands.describe(command="(Optionnel) Category wla smiya dyal command")
    async def help_slash(self, interaction: discord.Interaction, command: str = None):
        if command:
            return await self._show_command_details(interaction, command, mode="public")

        user = interaction.user
        categories = get_visible_categories(user, mode="public")

        if not categories:
            return await interaction.response.send_message("⚠️ Ma 3ndkch permission l hta command!", ephemeral=True)

        embed = build_home_embed(user, mode="public")
        view = HelpView(categories, user, mode="public")
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command(name="help")
    async def help_prefix(self, ctx: commands.Context, command: str = None):
        """&help (public) • +help (staff only)"""
        if ctx.prefix == "+":
            if not _is_staff(ctx.author):
                return
            mode = "admin"
        else:
            mode = "public"

        await self._send_help_menu(ctx, command, mode=mode)

    @commands.command(name="cmds")
    async def cmds_prefix(self, ctx: commands.Context, command: str = None):
        """&cmds [command|category] — Alias dyal &help (Public)"""
        await self._send_help_menu(ctx, command, mode="public")

    @commands.command(name="allcmds")
    async def allcmds_prefix(self, ctx: commands.Context):
        """&allcmds — List dyal GA3 commands"""
        all_cmds = sorted(self.bot.commands, key=lambda c: c.name)
        if not all_cmds:
            return await ctx.send("❌ Ma kaynch commands!")

        chunks = []
        current = []
        for c in all_cmds:
            current.append(c)
            if len(current) == 20:
                chunks.append(current)
                current = []
        if current:
            chunks.append(current)

        for i, chunk in enumerate(chunks[:10]):
            embed = discord.Embed(
                title=f"📋 All Commands ({len(all_cmds)})" if i == 0 else f"📋 Part {i+1}",
                description=f"Page {i+1}/{len(chunks[:10])}",
                color=discord.Color.blurple(),
            )
            for c in chunk:
                aliases = f"\n*Aliases: {', '.join(c.aliases)}*" if c.aliases else ""
                embed.add_field(
                    name=f"`{c.name}`",
                    value=f"{c.help or '—'}{aliases}"[:200],
                    inline=False,
                )
            await ctx.send(embed=embed)

    async def _show_command_details(self, interaction: discord.Interaction, query: str, mode: str = "public"):
        raw = query.lower().strip().replace("/", "").replace("&", "").replace("+", "")
        cats = ADMIN_CATEGORIES if mode == "admin" else PUBLIC_CATEGORIES

        cat_match = _find_category(raw, cats)
        if cat_match:
            embed = build_category_embed(cat_match, interaction.user)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        for cat_name in cats:
            data = HELP_CATEGORIES[cat_name]
            for cmd in data["commands"]:
                if cmd[0] == raw:
                    if not user_has_permission(interaction.user, raw):
                        return await interaction.response.send_message("❌ Ma 3ndkch permission!", ephemeral=True)
                    emoji = cat_name.split(" ", 1)[0]
                    embed = discord.Embed(title=f"{emoji} `{cmd[0]}`", description=cmd[1], color=discord.Color.blurple())
                    embed.add_field(name="📁 Category", value=cat_name, inline=True)
                    embed.add_field(name="📝 Usage", value=f"`{cmd[2]}`", inline=False)
                    return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.send_message(f"❌ Ma l9itch `{raw}` (machi category wla command)!", ephemeral=True)

    async def _show_command_details_prefix(self, ctx: commands.Context, query: str, mode: str = "public"):
        raw = query.lower().strip().replace("/", "").replace("&", "").replace("+", "")
        cats = ADMIN_CATEGORIES if mode == "admin" else PUBLIC_CATEGORIES

        cat_match = _find_category(raw, cats)
        if cat_match:
            embed = build_category_embed(cat_match, ctx.author)
            return await ctx.send(embed=embed)

        for cat_name in cats:
            data = HELP_CATEGORIES[cat_name]
            for cmd in data["commands"]:
                if cmd[0] == raw:
                    if not user_has_permission(ctx.author, raw):
                        return await ctx.send("❌ Ma 3ndkch permission!")
                    emoji = cat_name.split(" ", 1)[0]
                    embed = discord.Embed(title=f"{emoji} `{cmd[0]}`", description=cmd[1], color=discord.Color.blurple())
                    embed.add_field(name="📁 Category", value=cat_name, inline=True)
                    embed.add_field(name="📝 Usage", value=f"`{cmd[2]}`", inline=False)
                    return await ctx.send(embed=embed)

        await ctx.send(f"❌ Ma l9itch `{raw}` (machi category wla command)!")


async def setup(bot):
    await bot.add_cog(Help(bot))