from fastapi import Cookie, Depends, HTTPException, status, Header
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import settings
from ..models.base import get_db
from ..models.entities import WebPremium
from .discord_oauth import DiscordOAuth

# MANAGE_GUILD = 0x20 (32)
# ADMINISTRATOR = 0x8 (8)
ADMIN_PERMISSIONS = 0x8 | 0x20

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(
    authorization: Optional[str] = Header(None),
    session_token: Optional[str] = Cookie(None, alias=settings.AUTH_COOKIE_NAME),
) -> Dict[str, Any]:
    token = authorization.removeprefix("Bearer ").strip() if authorization and authorization.startswith("Bearer ") else session_token
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("sub") is None or payload.get("discord_access_token") is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

async def verify_guild_permission(guild_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
    if not guild_id.isdecimal():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid server ID")
    guilds = await DiscordOAuth.get_user_guilds(user["discord_access_token"])
    guild = next((item for item in guilds if str(item.get("id")) == str(guild_id)), None)
    if guild is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this server")

    permissions = int(guild.get("permissions", 0))
    if not guild.get("owner", False) and not (permissions & ADMIN_PERMISSIONS):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manage Server permission is required")
    return user


async def require_guild_permission(
    guild_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return await verify_guild_permission(guild_id, user)

def require_premium(tier: str = "basic"):
    TIER_LEVELS = {"free": 0, "basic": 1, "pro": 2, "ultra": 3}
    required_level = TIER_LEVELS.get(tier.lower(), 1)

    async def checker(guild_id: str, db: AsyncSession = Depends(get_db)) -> bool:
        stmt = select(WebPremium).where(WebPremium.guild_id == int(guild_id))
        res = await db.execute(stmt)
        record = res.scalars().first()
        current_tier = record.tier.lower() if record and record.tier else "free"
        
        # Check expiration if premium_until is set
        if record and record.premium_until and record.premium_until < datetime.utcnow():
            current_tier = "free"

        user_level = TIER_LEVELS.get(current_tier, 0)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires a '{tier.capitalize()}' subscription or higher."
            )
        return True
    return checker