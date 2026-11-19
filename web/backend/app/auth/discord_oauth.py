import httpx
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from ..config import settings

DISCORD_API_BASE = "https://discord.com/api/v10"

class DiscordOAuth:
    @staticmethod
    async def exchange_code(code: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            data = {
                "client_id": settings.DISCORD_CLIENT_ID,
                "client_secret": settings.DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.DISCORD_REDIRECT_URI,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            r = await client.post(f"{DISCORD_API_BASE}/oauth2/token", data=data, headers=headers)
            if r.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Discord OAuth token exchange failed: {r.text}"
                )
            return r.json()

    @staticmethod
    async def get_user(access_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            r = await client.get(f"{DISCORD_API_BASE}/users/@me", headers=headers)
            if r.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to fetch Discord user profile"
                )
            return r.json()

    @staticmethod
    async def get_user_guilds(access_token: str) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            r = await client.get(f"{DISCORD_API_BASE}/users/@me/guilds", headers=headers)
            if r.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to fetch Discord user guilds"
                )
            return r.json()

    @staticmethod
    async def get_bot_guilds() -> List[str]:
        if not settings.DISCORD_BOT_TOKEN:
            return []
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}"}
            r = await client.get(f"{DISCORD_API_BASE}/users/@me/guilds", headers=headers)
            if r.status_code != 200:
                return []
            guilds = r.json()
            return [str(g["id"]) for g in guilds]