# config_manager.py
# =====================================================================
# ─── PER-SERVER CONFIGURATION MANAGER (Multi-Server / Guild Isolation)
#     Scalable, async-safe, and thread-safe configuration management
#     supporting per-guild roles, channels, and feature toggles.
# =====================================================================

import os
import json
import asyncio
import threading
from typing import Any, Dict, List, Optional
import discord

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "data", "guild_configs.json")
_lock = threading.RLock()
_CONFIGS: Dict[str, Dict[str, Any]] = {}
_INITIALIZED = False

# Default template per server
DEFAULT_FEATURES = {
    "welcome": True,
    "welcome_dm": False,
    "auto_role": True,
    "auto_mod": True,
    "logging": True,
    "tickets": True,
    "economy": True,
    "levels": True,
}

DEFAULT_ROLES = {
    "admin_role": None,       # Role ID for Administrators
    "mod_role": None,         # Role ID for Moderators
    "helper_role": None,      # Role ID for Helpers
    "staff_role": None,       # Role ID for Staff
    "member_role": None,      # Verified / Member Role ID
    "unverified_role": None,  # Unverified / Muted / Pending Role ID
    "muted_role": None,       # Jail / Muted Role ID
    "verification_staff_role": None,
    "verified_role": None,
    "jail_role": None,
    "move_power_role": None,
}

DEFAULT_CHANNELS = {
    "logs_channel": None,         # General logs
    "mod_logs_channel": None,     # Moderation logs
    "welcome_channel": None,      # Member welcome channel
    "leaves_channel": None,       # Member leave channel
    "tickets_channel": None,      # Tickets panel channel
    "casino_channel": None,       # Casino / Gambling channel
    "verification_channel": None,
    "verification_log_channel": None,
    "jail_channel": None,
    "staff_applications_channel": None,
    "staff_application_panel_channel": None,
    "vc_rank_channel": None,
    "voice_lounge_channel": None,
}

DEFAULT_CATEGORIES = {
    "welcome_category": None,
    "verification_category": None,
    "jail_category": None,
    "staff_category": None,
    "logs_category": None,
    "voice_category": None,
}

DEFAULT_PREFIX = "&"


def _get_default_config(guild_id: int | str, guild_name: str = "") -> Dict[str, Any]:
    return {
        "guild_id": int(guild_id),
        "guild_name": guild_name,
        "prefix": DEFAULT_PREFIX,
        "roles": dict(DEFAULT_ROLES),
        "channels": dict(DEFAULT_CHANNELS),
        "categories": dict(DEFAULT_CATEGORIES),
        "features": dict(DEFAULT_FEATURES),
    }


def _load_configs():
    global _CONFIGS, _INITIALIZED
    with _lock:
        if _INITIALIZED:
            return
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    _CONFIGS = json.load(f)
            except Exception as e:
                print(f"[config_manager] ⚠️ Failed to load {CONFIG_PATH}: {e}")
                _CONFIGS = {}
        else:
            _CONFIGS = {}
        _INITIALIZED = True


def reload_configs():
    """Reload guild settings changed by the dashboard."""
    global _INITIALIZED
    with _lock:
        _INITIALIZED = False
    _load_configs()


def _save_configs_sync():
    with _lock:
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            temp_path = CONFIG_PATH + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(_CONFIGS, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, CONFIG_PATH)
        except Exception as e:
            print(f"[config_manager] ❌ Failed to save configs: {e}")


async def save_configs_async():
    """Async-safe non-blocking write to disk."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _save_configs_sync)


# ═══════════════════════════════════════════════════════════════════
# ─── CORE PUBLIC API
# ═══════════════════════════════════════════════════════════════════

def get_guild_config(guild: discord.Guild | int | str, guild_name: str = "") -> Dict[str, Any]:
    """Retrieve full configuration for a guild with guaranteed complete schema."""
    _load_configs()
    gid = str(guild.id if isinstance(guild, discord.Guild) else guild)
    if isinstance(guild, discord.Guild) and not guild_name:
        guild_name = guild.name

    with _lock:
        if gid not in _CONFIGS:
            _CONFIGS[gid] = _get_default_config(gid, guild_name)
            _save_configs_sync()
        else:
            # Ensure schema integrity for older or incomplete configs
            cfg = _CONFIGS[gid]
            cfg.setdefault("prefix", DEFAULT_PREFIX)
            if "roles" not in cfg:
                cfg["roles"] = dict(DEFAULT_ROLES)
            else:
                for k, v in DEFAULT_ROLES.items():
                    cfg["roles"].setdefault(k, v)

            if "channels" not in cfg:
                cfg["channels"] = dict(DEFAULT_CHANNELS)
            else:
                for k, v in DEFAULT_CHANNELS.items():
                    cfg["channels"].setdefault(k, v)

            if "features" not in cfg:
                cfg["features"] = dict(DEFAULT_FEATURES)
            else:
                for k, v in DEFAULT_FEATURES.items():
                    cfg["features"].setdefault(k, v)

            if "categories" not in cfg:
                cfg["categories"] = dict(DEFAULT_CATEGORIES)
            else:
                for k, v in DEFAULT_CATEGORIES.items():
                    cfg["categories"].setdefault(k, v)

            if guild_name:
                cfg["guild_name"] = guild_name

        return _CONFIGS[gid]


def init_guild_if_missing(guild: discord.Guild) -> bool:
    """Initialize default config when joining a guild. Returns True if newly created."""
    _load_configs()
    gid = str(guild.id)
    with _lock:
        if gid not in _CONFIGS:
            _CONFIGS[gid] = _get_default_config(guild.id, guild.name)
            _save_configs_sync()
            return True
        return False


def set_role(guild_id: int | str, role_key: str, role_id: Optional[int]):
    """Set role mapping for a guild function (e.g., admin_role, mod_role)."""
    cfg = get_guild_config(guild_id)
    with _lock:
        cfg["roles"][role_key] = role_id
        _save_configs_sync()


def get_role_id(guild: discord.Guild | int | str, role_key: str) -> Optional[int]:
    """Get configured role ID for a function, or None."""
    cfg = get_guild_config(guild)
    return cfg["roles"].get(role_key)


def get_role(guild: discord.Guild, role_key: str) -> Optional[discord.Role]:
    """Fetch the discord.Role object configured for a function in this guild."""
    rid = get_role_id(guild, role_key)
    if rid:
        return guild.get_role(rid)
    return None


def set_channel(guild_id: int | str, channel_key: str, channel_id: Optional[int]):
    """Set channel mapping for a guild function (e.g., logs_channel, welcome_channel)."""
    cfg = get_guild_config(guild_id)
    with _lock:
        cfg["channels"][channel_key] = channel_id
        _save_configs_sync()

def set_category(guild_id: int | str, category_key: str, category_id: Optional[int]):
    cfg = get_guild_config(guild_id)
    with _lock:
        cfg.setdefault("categories", dict(DEFAULT_CATEGORIES))[category_key] = category_id
        _save_configs_sync()

def get_category(guild: discord.Guild, category_key: str) -> Optional[discord.CategoryChannel]:
    cid = get_guild_config(guild)["categories"].get(category_key)
    return guild.get_channel(cid) if cid else None


def get_channel_id(guild: discord.Guild | int | str, channel_key: str) -> Optional[int]:
    """Get configured channel ID for a function, or None."""
    cfg = get_guild_config(guild)
    return cfg["channels"].get(channel_key)


def get_channel(guild: discord.Guild, channel_key: str) -> Optional[discord.TextChannel]:
    """Fetch the discord.TextChannel object configured for this guild."""
    cid = get_channel_id(guild, channel_key)
    if cid:
        return guild.get_channel(cid)
    return None


def is_feature_enabled(guild: discord.Guild | int | str, feature_key: str) -> bool:
    """Check if a feature is toggled ON for this server."""
    cfg = get_guild_config(guild)
    return bool(cfg["features"].get(feature_key, False))


def set_feature_toggle(guild_id: int | str, feature_key: str, enabled: bool):
    """Enable or disable a feature toggle."""
    cfg = get_guild_config(guild_id)
    with _lock:
        cfg["features"][feature_key] = bool(enabled)
        _save_configs_sync()
