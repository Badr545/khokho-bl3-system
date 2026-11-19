import json
import os
import aiofiles
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
CONFIG_PATH = os.path.join(BASE_DIR, "data", "guild_configs.json")

class GuildService:
    @staticmethod
    async def load_configs() -> Dict[str, Any]:
        if not os.path.exists(CONFIG_PATH):
            return {}
        try:
            async with aiofiles.open(CONFIG_PATH, mode='r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content) if content else {}
        except Exception:
            return {}

    @staticmethod
    async def save_configs(data: Dict[str, Any]):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        async with aiofiles.open(CONFIG_PATH, mode='w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))

    @classmethod
    async def get_guild_config(cls, guild_id: str) -> Dict[str, Any]:
        configs = await cls.load_configs()
        guild_conf = configs.get(str(guild_id), {})
        
        # Default fallback structure
        return {
            "guild_id": str(guild_id),
            "prefix": guild_conf.get("prefix", "&"),
            "language": guild_conf.get("language", "darija"),
            "features": guild_conf.get("features", {
                "welcome": True,
                "welcome_dm": False,
                "auto_mod": True,
                "logging": True,
                "tickets": True,
                "economy": True,
                "levels": True
            }),
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
                elif k.startswith("welcome_") or k.startswith("leave_") or k in ["anti_spam", "anti_link", "anti_caps"]:
                    configs[gid].setdefault("features", {})[k] = v
                elif k.endswith("_channel"):
                    configs[gid].setdefault("channels", {})[k] = v
                elif k.endswith("_role"):
                    configs[gid].setdefault("roles", {})[k] = v
                else:
                    configs[gid][k] = v

        await cls.save_configs(configs)
        return configs[gid]