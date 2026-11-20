import aiosqlite
import json
import os
import httpx
from typing import List, Dict, Any, Optional
from ..config import settings

BOT_DB_PATH = os.path.join(settings.DATA_DIR, "bot.db")
DISCORD_API_BASE = "https://discord.com/api/v10"

# In-memory member cache to avoid spamming Discord API
MEMBER_CACHE: Dict[str, Dict[str, Any]] = {}

class SqliteReader:
    @staticmethod
    async def _get_discord_token() -> str:
        from ..config import settings
        return settings.DISCORD_BOT_TOKEN

    @classmethod
    async def get_guild_members_map(cls, guild_id: str) -> Dict[str, Dict[str, Any]]:
        cached = MEMBER_CACHE.get(str(guild_id))
        if cached:
            return cached

        token = await cls._get_discord_token()
        if not token:
            return {}

        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bot {token}"}
                r = await client.get(f"{DISCORD_API_BASE}/guilds/{guild_id}/members?limit=1000", headers=headers, timeout=5)
                if r.status_code == 200:
                    members = r.json()
                    member_map = {}
                    for m in members:
                        u = m.get("user", {})
                        uid = str(u.get("id"))
                        member_map[uid] = {
                            "username": u.get("global_name") or u.get("username") or f"User_{uid[-4:]}",
                            "tag": u.get("username"),
                            "avatar": u.get("avatar"),
                            "avatar_url": f"https://cdn.discordapp.com/avatars/{uid}/{u.get('avatar')}.png" if u.get("avatar") else None,
                            "roles": m.get("roles", [])
                        }
                    MEMBER_CACHE[str(guild_id)] = member_map
                    return member_map
        except Exception as e:
            print(f"Error fetching members: {e}")
        return {}

    @classmethod
    async def get_economy_leaderboard(cls, guild_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not os.path.exists(BOT_DB_PATH):
            return []
        
        member_map = await cls.get_guild_members_map(guild_id)
        
        try:
            async with aiosqlite.connect(BOT_DB_PATH) as db:
                # First check for matches on guild_id or across all if single server
                async with db.execute(
                    "SELECT user_id, data FROM economy WHERE guild_id = ? OR guild_id IS NULL OR guild_id = 0",
                    (int(guild_id) if str(guild_id).isdigit() else 0,)
                ) as cursor:
                    rows = await cursor.fetchall()
                    if not rows:
                        async with db.execute("SELECT user_id, data FROM economy") as c2:
                            rows = await c2.fetchall()

                    result = []
                    seen_users = set()
                    for row in rows:
                        uid_raw, data_str = row
                        uid = str(uid_raw)
                        if uid in seen_users:
                            continue
                        seen_users.add(uid)

                        data = json.loads(data_str) if data_str else {}
                        wallet = data.get("wallet", 0)
                        bank = data.get("bank", 0)
                        
                        m_info = member_map.get(uid, {})
                        username = m_info.get("username") or f"User_{uid[-4:]}"
                        avatar_url = m_info.get("avatar_url")

                        result.append({
                            "user_id": uid,
                            "username": username,
                            "avatar_url": avatar_url,
                            "wallet": wallet,
                            "bank": bank,
                            "total": wallet + bank,
                            "net_worth": data.get("net_worth", wallet + bank)
                        })

                    result.sort(key=lambda x: x["total"], reverse=True)
                    return result[:limit]
        except Exception as e:
            print(f"Economy leaderboard error: {e}")
            return []

    @classmethod
    async def get_levels_leaderboard(cls, guild_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not os.path.exists(BOT_DB_PATH):
            return []

        member_map = await cls.get_guild_members_map(guild_id)

        try:
            async with aiosqlite.connect(BOT_DB_PATH) as db:
                async with db.execute(
                    "SELECT user_id, data FROM levels WHERE guild_id = ? OR guild_id IS NULL OR guild_id = 0",
                    (int(guild_id) if str(guild_id).isdigit() else 0,)
                ) as cursor:
                    rows = await cursor.fetchall()
                    if not rows:
                        async with db.execute("SELECT user_id, data FROM levels") as c2:
                            rows = await c2.fetchall()

                    result = []
                    seen_users = set()
                    for row in rows:
                        uid_raw, data_str = row
                        uid = str(uid_raw)
                        if uid in seen_users:
                            continue
                        seen_users.add(uid)

                        data = json.loads(data_str) if data_str else {}
                        xp = data.get("xp", 0)
                        level = data.get("level", 1)
                        messages = data.get("messages", 0)
                        voice_minutes = data.get("voice_minutes", 0)

                        m_info = member_map.get(uid, {})
                        username = m_info.get("username") or f"User_{uid[-4:]}"
                        avatar_url = m_info.get("avatar_url")

                        result.append({
                            "user_id": uid,
                            "username": username,
                            "avatar_url": avatar_url,
                            "xp": xp,
                            "level": level,
                            "messages": messages,
                            "voice_minutes": voice_minutes
                        })

                    result.sort(key=lambda x: x["xp"], reverse=True)
                    return result[:limit]
        except Exception as e:
            print(f"Levels leaderboard error: {e}")
            return []

    @classmethod
    async def get_warnings(cls, guild_id: str, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        if not os.path.exists(BOT_DB_PATH):
            return []
        try:
            async with aiosqlite.connect(BOT_DB_PATH) as db:
                async with db.execute(
                    "SELECT user_id, data FROM warnings WHERE guild_id = ?",
                    (int(guild_id) if str(guild_id).isdigit() else 0,)
                ) as cursor:
                    rows = await cursor.fetchall()
                    all_warns = []
                    for row in rows:
                        uid, data_str = row
                        data = json.loads(data_str) if data_str else {}
                        warn_list = data if isinstance(data, list) else data.get("warnings", [])
                        for index, w in enumerate(warn_list):
                            all_warns.append({
                                "id": str(w.get("id") or f"{uid}-{index}"),
                                "user_id": str(uid),
                                "moderator_id": str(w.get("mod_id", "Unknown")),
                                "reason": w.get("reason", "No reason provided"),
                                "timestamp": w.get("time", "")
                            })
                    start = (page - 1) * page_size
                    return all_warns[start:start + page_size]
        except Exception:
            return []