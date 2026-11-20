import json
import os
import aiofiles
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import settings

CONFIG_PATH = Path(settings.DATA_DIR) / "guild_configs.json"

class GuildService:
    @staticmethod
    async def load_configs() -> Dict[str, Any]:
        if not CONFIG_PATH.exists():
            return {}
        async with aiofiles.open(CONFIG_PATH, mode='r', encoding='utf-8') as f:
            content = await f.read()
        configs = json.loads(content) if content else {}
        if not isinstance(configs, dict):
            raise ValueError(f"Guild configuration file must contain an object: {CONFIG_PATH}")
        return configs

    @staticmethod
    async def save_configs(data: Dict[str, Any]):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        temp_path = CONFIG_PATH.with_suffix(".json.tmp")
        async with aiofiles.open(temp_path, mode='w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        os.replace(temp_path, CONFIG_PATH)

    @classmethod
    async def get_guild_config(cls, guild_id: str) -> Dict[str, Any]:
        configs = await cls.load_configs()
        guild_conf = configs.get(str(guild_id), {})
        features = {
            "welcome": True,
            "welcome_dm": False,
            "auto_role": True,
            "auto_mod": True,
            "logging": True,
            "tickets": True,
            "economy": True,
            "levels": True,
        }
        features.update(guild_conf.get("features", {}))
        return {
            "guild_id": str(guild_id),
            "prefix": guild_conf.get("prefix", "&"),
            "language": guild_conf.get("language", "darija"),
            "features": features,
            "roles": guild_conf.get("roles", {}),
            "channels": guild_conf.get("channels", {})
        }

    @classmethod
    async def update_guild_config(cls, guild_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        configs = await cls.load_configs()
        gid = str(guild_id)
        if gid not in configs:
            configs[gid] = {
                "prefix": "&",
                "language": "darija",
                "features": {},
                "roles": {},
                "channels": {}
            }
        
        for k, v in updates.items():
            if v is not None:
                if k in ["prefix", "language"]:
                    configs[gid][k] = v
                elif k in {"welcome_enabled", "leave_enabled", "automod_enabled", "anti_spam", "anti_link", "anti_caps"}:
                    feature_key = {
                        "welcome_enabled": "welcome",
                        "leave_enabled": "leave",
                        "automod_enabled": "auto_mod",
                    }.get(k, k)
                    configs[gid].setdefault("features", {})[feature_key] = v
                elif k in {"welcome_channel", "leave_channel", "log_channel"}:
                    channel_key = {"leave_channel": "leaves_channel", "log_channel": "logs_channel"}.get(k, k)
                    configs[gid].setdefault("channels", {})[channel_key] = int(v) if str(v).isdecimal() else v
                elif k.endswith("_role"):
                    configs[gid].setdefault("roles", {})[k] = int(v) if str(v).isdecimal() else v
                else:
                    configs[gid].setdefault("features", {})[k] = v

        await cls.save_configs(configs)
        return configs[gid]