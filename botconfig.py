# =====================================================================
# ─── KHOKHO BL3 BOT — CONFIG (read from .env)
# =====================================================================
import os
import discord
from dotenv import load_dotenv

load_dotenv()


# ═══════════════════════════════════════════════════════════════════
# ─── HELPERS
# ═══════════════════════════════════════════════════════════════════
def _int(key: str, default: int = 0) -> int:
    v = os.getenv(key, "")
    try:
        return int(v.strip()) if v.strip() else default
    except ValueError:
        return default


def _str(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _bool(key: str, default: bool = False) -> bool:
    v = os.getenv(key, "").strip().lower()
    if not v:
        return default
    return v in ("1", "true", "yes", "on")


# ═══════════════════════════════════════════════════════════════════
# ─── BOT
# ═══════════════════════════════════════════════════════════════════
BOT_OWNER_ID = _int("BOT_OWNER_ID")

# ═══════════════════════════════════════════════════════════════════
# ─── ROLES
# ═══════════════════════════════════════════════════════════════════
ADMIN_ROLES = [
    r for r in [
        _int("ROLE_FOUNDER"),
        _int("ROLE_COMMUNITY_MANAGER"),
        _int("ROLE_ADMINISTRATOR"),
    ] if r
]

MODERATOR_ROLES = [
    r for r in [
        _int("ROLE_MODERATOR"),
        _int("ROLE_SUPERVISEUR"),
    ] if r
]

HELPER_ROLES = [
    r for r in [
        _int("ROLE_HELPER"),
    ] if r
]

STAFF_ROLES = [_int("ROLE_STAFF_TEAM")] if _int("ROLE_STAFF_TEAM") else []
STAFF_ROLES += [_int("ROLE_STAFF")] if _int("ROLE_STAFF") else []

CLAN_MANAGER_ROLES = ADMIN_ROLES + (
    [_int("ROLE_CLAN_MANAGER")] if _int("ROLE_CLAN_MANAGER") else []
)

BYPASS_ROLES = ADMIN_ROLES + (
    [_int("ROLE_BYPASS")] if _int("ROLE_BYPASS") else []
)

ANNOUNCER_ROLES = HELPER_ROLES + STAFF_ROLES + MODERATOR_ROLES + ADMIN_ROLES

# ═══════════════════════════════════════════════════════════════════
# ─── CHANNELS
# ═══════════════════════════════════════════════════════════════════
CHANNEL_LOGS = {
    "general":      _int("CHANNEL_LOG_GENERAL"),
    "member":       _int("CHANNEL_LOG_MEMBER"),
    "message":      _int("CHANNEL_LOG_MESSAGE"),
    "voice":        _int("CHANNEL_LOG_VOICE"),
    "channel":      _int("CHANNEL_LOG_CHANNEL"),
    "role":         _int("CHANNEL_LOG_ROLE"),
    "moderation":   _int("CHANNEL_LOG_MODERATION"),
    "join":         _int("CHANNEL_LOG_JOIN"),
    "verification": _int("CHANNEL_LOG_VERIFICATION"),
}

CHANNEL_SYSINFO = _int("CHANNEL_SYSINFO")
SYSINFO_INTERVAL_MINUTES = _int("SYSINFO_INTERVAL_MINUTES", 30)

WELCOME_CHANNEL_NAME = _str("NAME_WELCOME_CHANNEL", "𝑾𝒆𝒍𝒄𝒐𝒎")
LEAVES_CHANNEL_NAME = _str("NAME_LEAVES_CHANNEL", "leaves")
VERIFIED_ROLE_NAME = _str("NAME_VERIFIED_ROLE", "Verified ✓")
UNVERIFIED_ROLE_NAME = _str("NAME_UNVERIFIED_ROLE", "Unverified")

WELCOME_CHANNEL_ID = _int("CHANNEL_WELCOME")
LEAVES_CHANNEL_ID = _int("CHANNEL_LEAVES")
VERIF_LOG_CHANNEL_ID = _int("CHANNEL_VERIF_LOG")

VOICE_CHANNEL_ID = _int("CHANNEL_VOICE_24_7")
TEMP_VOICE_TRIGGER_ID = _int("CHANNEL_TEMPVERIF_TRIGGER")
CASINO_CHANNEL_ID = _int("CHANNEL_CASINO") or None

GUILD_JOIN_LOG_CHANNEL_ID = _int("CHANNEL_GUILD_JOIN_LOG")

# ═══════════════════════════════════════════════════════════════════
# ─── VOICE / VERIFICATION
# ═══════════════════════════════════════════════════════════════════
JAIL_ROLE_ID = _int("ROLE_JAIL")
JAIL_MOD_ROLE_ID = _int("ROLE_JAIL_MOD")           # 👈 هادا رول الستاف (اللي كيدير +jail)
VERIF_ROLE_ID = _int("ROLE_VERIFIED")
CM_ROLE_ID = _int("ROLE_COMMUNITY_MANAGER")
ROLE_VB = _int("ROLE_VB")
ROLE_VG = _int("ROLE_VG")

# ═══════════════════════════════════════════════════════════════════
# ─── GAMBLING
# ═══════════════════════════════════════════════════════════════════
CASINO_CATEGORY_KEYWORDS = ["casino", "🎰", "🎲", "bet", "gamble", "grow casino"]

# ═══════════════════════════════════════════════════════════════════
# ─── FLAGS
# ═══════════════════════════════════════════════════════════════════
AUTO_ROLE_ENABLED = _bool("AUTO_ROLE_ENABLED", True)
WELCOME_DM_ENABLED = _bool("WELCOME_DM_ENABLED", True)

# ═══════════════════════════════════════════════════════════════════
# ─── PERMISSIONS
# ═══════════════════════════════════════════════════════════════════
COMMAND_PERMISSIONS = {
    # 👇 MODERATOR + ADMIN (Kick, Ban, Jail...)
    "moderation": {
        "roles": ADMIN_ROLES + MODERATOR_ROLES,
        "commands": [
            "kick", "ban", "unban", "warn", "warnings", "ms7", "slowmode", "lock", "unlock",
            "clearwarns", "giverole", "removerole", "massrole",
            "jail", "rta7", "timeout", "untimeout", "mute", "unmute", "case", "cases",
        ],
    },
    
    # 👇 🔥 الجديد: JAIL MOD (غير السجن والفك)
    "jail_mod": {
        "roles": [JAIL_MOD_ROLE_ID] if JAIL_MOD_ROLE_ID else [],
        "commands": [
            "jail", "unjail", "rta7"
        ],
    },
    
    # 👇 HELPER (صلاحيات متوسطة، فوق staff team)
    "HELPER": {
        "roles": HELPER_ROLES,
        "commands": [
            "warn", "warnings", "clearwarns", "ms7", 
            "timeout", "untimeout", "mute", "unmute", "temprole",
            "lock", "unlock", "serverstats", "ss", "stats"
        ],
    },
    
    # 👇 STAFF TEAM (صلاحيات خفيفة، تحت helper)
    "staff_moderation": {
        "roles": STAFF_ROLES,
        "commands": [
            "warn", "warnings", "ms7", "roleinfo", "ri", "roleslist", "rl", "channels"
        ],
    },
    
    "admin_only": {
        "roles": ADMIN_ROLES,
        "commands": [
            "reload", "shutdown", "eval", "config",
            "addmod", "removemod", "listroles", "checkperm",
            "massrole", "setserver", "fixroles",
        ],
    },
    
    "announcement": {
        "roles": ANNOUNCER_ROLES,
        "commands": ["announce", "embed"],
    },
    
    "verification": {
        "roles": ADMIN_ROLES + ([VERIF_ROLE_ID] if VERIF_ROLE_ID else []),
        "commands": [
            "verify", "vform", "vb", "vg", "vcheck", "vinfo", "vlist", "unverify", "unvb",
        ],
    },
    
    "clan_manager": {
        "roles": CLAN_MANAGER_ROLES,
        "commands": [
            "createclan", "deleteclan", "renameclan", "updaterole",
            "giveclan", "forceaddmember", "clearcoleaders",
            "resetpoints", "clan-of-the-week", "update-limits",
            "removeclan-of-the-week", "removecotw", "delcotw",
        ],
    },
    
    "public": {
        "roles": [],
        "commands": [
            "ping", "say", "userinfo", "serverinfo", "avatar", "help", "cmds",
            "anime", "manga", "weather", "translate", "lyrics",
            "banner", "roles", "members", "bots", "invites",
            "8ball", "roll", "coinflip", "poll", "trivia", "rps", "dice",
            "guess", "slots","set",
            "math", "base64", "password", "uuid", "timestamp",
            "balance", "coins", "daily", "work", "rob", "pay", "gamble",
            "shop", "buy", "collect",
            "rank", "rankcard", "rcard", "levels", "toprank",
            "topmoney", "lb", "leaderboard",
            "cf", "d", "rl", "s", "bj", "rp", "mines", "crash", "bac",
            "poker", "vp", "tower", "tw", "rlt", "hr", "wheel", "plinko", "pl",
            "bir", "birwork", "bw", "birtop", "bt",
            "ot", "vc",
            "heist", "tournament", "tourney", "tr",
            "clanhelp", "clans", "myclan", "mypoints", "mytime", "usertime",
            "lbc", "claninfo", "clanlist", "topc", "leaveclan",
            "adduser", "removeuser", "addcol", "removecol",
            "set-owner", "settag", "clansetup",
        ],
    },
}

# ═══════════════════════════════════════════════════════════════════
# ─── ROLE HELPERS
# ═══════════════════════════════════════════════════════════════════
ROLE_NAME_TO_ID: dict = {}


def _has_role(member: discord.Member, role_ref) -> bool:
    if member is None or member.guild is None:
        return False
    if isinstance(role_ref, int):
        return any(r.id == role_ref for r in member.roles)
    if isinstance(role_ref, str):
        if any(r.name == role_ref for r in member.roles):
            return True
        rid = ROLE_NAME_TO_ID.get(role_ref)
        if rid and any(r.id == rid for r in member.roles):
            return True
    return False


def is_known_command(command_name: str) -> bool:
    for data in COMMAND_PERMISSIONS.values():
        if command_name in data["commands"]:
            return True
    return False


def get_required_roles(command_name: str) -> list:
    seen, result = set(), []
    for data in COMMAND_PERMISSIONS.values():
        if command_name not in data["commands"]:
            continue
        for role in data["roles"]:
            key = (type(role).__name__, role)
            if key in seen:
                continue
            seen.add(key)
            result.append(role)
    return result


def user_has_permission(member, command_name: str) -> bool:
    if not isinstance(member, discord.Member) or member.guild is None:
        return False
    if member.id == member.guild.owner_id:
        return True

    for bypass in BYPASS_ROLES:
        if _has_role(member, bypass):
            return True

    # Dynamic perms (from permsmanager cog)
    try:
        from cogs.permsmanager import has_dynamic_perm
        if has_dynamic_perm(member, command_name):
            return True
    except Exception:
        pass

    # Per-Guild dynamic role check from config_manager
    try:
        import config_manager
        guild_cfg = config_manager.get_guild_config(member.guild)
        g_roles = guild_cfg.get("roles", {})
        admin_rid = g_roles.get("admin_role")
        mod_rid = g_roles.get("mod_role")
        helper_rid = g_roles.get("helper_role")
        
        # If user has configured admin_role, permit all moderation & admin
        if admin_rid and any(r.id == admin_rid for r in member.roles):
            return True
            
        # If user has mod_role, permit moderation commands
        if mod_rid and any(r.id == mod_rid for r in member.roles):
            if command_name in COMMAND_PERMISSIONS.get("moderation", {}).get("commands", []):
                return True
                
        # If user has helper_role, permit helper commands
        if helper_rid and any(r.id == helper_rid for r in member.roles):
            if command_name in COMMAND_PERMISSIONS.get("HELPER", {}).get("commands", []):
                return True
    except Exception:
        pass

    if not is_known_command(command_name):
        return True

    required = get_required_roles(command_name)
    if not required:
        return True

    return any(_has_role(member, r) for r in required)