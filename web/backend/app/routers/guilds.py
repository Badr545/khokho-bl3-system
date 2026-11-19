from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import httpx
from ..config import settings
from ..auth.deps import get_current_user
from ..auth.discord_oauth import DiscordOAuth
from ..services.guild_service import GuildService
from ..schemas.schemas import GuildBase, GuildConfigUpdate
from ..bot_bridge import bot_bridge

router = APIRouter(prefix="/guilds", tags=["Guilds"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_user_guilds(current_user: Dict[str, Any] = Depends(get_current_user)):
    token = current_user.get("access_token")
    
    # If using dev/mock token, fetch real live bot guilds from Discord API
    if not token or token == "mock_token" or token.startswith("dev_"):
        bot_token = settings.DISCORD_BOT_TOKEN
        if bot_token:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bot {bot_token}"}
                r = await client.get("https://discord.com/api/v10/users/@me/guilds", headers=headers, timeout=5)
                if r.status_code == 200:
                    bot_guilds = r.json()
                    res = []
                    for g in bot_guilds:
                        gid = str(g["id"])
                        # fetch detailed counts
                        g_detail = await client.get(f"https://discord.com/api/v10/guilds/{gid}?with_counts=true", headers=headers, timeout=5)
                        detail_json = g_detail.json() if g_detail.status_code == 200 else {}
                        icon = g.get("icon")
                        icon_url = f"https://cdn.discordapp.com/icons/{gid}/{icon}.png" if icon else None
                        res.append({
                            "id": gid,
                            "name": g["name"],
                            "icon": icon,
                            "icon_url": icon_url,
                            "owner": g.get("owner", True),
                            "permissions": 8,
                            "has_bot": True,
                            "approximate_member_count": detail_json.get("approximate_member_count", 0),
                            "approximate_presence_count": detail_json.get("approximate_presence_count", 0)
                        })
                    return res
        return []

    user_guilds = await DiscordOAuth.get_user_guilds(token)
    bot_guild_ids = set(await DiscordOAuth.get_bot_guilds())

    manageable = []
    for g in user_guilds:
        perms = int(g.get("permissions", 0))
        is_owner = g.get("owner", False)
        # Check MANAGE_GUILD (0x20) or ADMIN (0x8)
        if is_owner or (perms & 0x8) or (perms & 0x20):
            gid = str(g["id"])
            icon = g.get("icon")
            icon_url = f"https://cdn.discordapp.com/icons/{gid}/{icon}.png" if icon else None
            manageable.append({
                "id": gid,
                "name": g["name"],
                "icon": icon,
                "icon_url": icon_url,
                "owner": is_owner,
                "permissions": perms,
                "has_bot": gid in bot_guild_ids
            })
    return manageable

@router.get("/{id}")
async def get_guild_details(id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    conf = await GuildService.get_guild_config(id)
    
    # Enrich with live Discord metadata
    bot_token = settings.DISCORD_BOT_TOKEN
    discord_meta = {}
    if bot_token:
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bot {bot_token}"}
                r = await client.get(f"https://discord.com/api/v10/guilds/{id}?with_counts=true", headers=headers, timeout=5)
                if r.status_code == 200:
                    g = r.json()
                    discord_meta = {
                        "name": g.get("name"),
                        "icon": g.get("icon"),
                        "icon_url": f"https://cdn.discordapp.com/icons/{id}/{g.get('icon')}.png" if g.get("icon") else None,
                        "member_count": g.get("approximate_member_count", 0),
                        "online_count": g.get("approximate_presence_count", 0),
                        "description": g.get("description")
                    }
        except Exception:
            pass

    return {**conf, "discord_meta": discord_meta}

@router.patch("/{id}")
async def update_guild_details(id: str, updates: GuildConfigUpdate, current_user: Dict[str, Any] = Depends(get_current_user)):
    updated = await GuildService.update_guild_config(id, updates.model_dump(exclude_unset=True))
    await bot_bridge.execute_action("sync_settings", id, updates.model_dump(exclude_unset=True))
    return {"status": "success", "config": updated}