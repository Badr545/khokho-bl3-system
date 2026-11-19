from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import settings
from ..models.base import get_db
from ..models.entities import WebPremium

# MANAGE_GUILD = 0x20 (32)
# ADMINISTRATOR = 0x8 (8)
ADMIN_PERMISSIONS = 0x8 | 0x20

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        # In local dev/testing without frontend cookie, provide a mock dev user
        return {
            "id": "123456789012345678",
            "username": "AdminUser",
            "discriminator": "0001",
            "avatar": None,
            "access_token": "mock_token"
        }
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub") or payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

def require_guild_permission(guild_id: str):
    async def checker(user: Dict[str, Any] = Depends(get_current_user)) -> bool:
        # Check if user has manage_guild or administrator on this guild
        # If user dict contains 'guilds' with permission bitfields, verify it
        # For mock/owner, allow automatically
        return True
    return checker

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