import os
import sys
import time
import httpx
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings
from .models.base import engine_features, Base
from .auth.deps import get_current_user
from .routers import guilds, modules, premium
from .schemas.schemas import StatusResponse

START_TIME = time.time()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine_features.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("🚀 Web Backend Database Tables Initialized!")

# Public Endpoints
@app.get(f"{settings.API_V1_STR}/status", response_model=StatusResponse, tags=["Public Status"])
async def get_system_status():
    uptime = time.time() - START_TIME
    guild_count = 0
    user_count = 0
    bot_online = False
    ping = 15.0

    # Fetch live counts from Discord Gateway API
    bot_token = settings.DISCORD_BOT_TOKEN
    if bot_token:
        try:
            t0 = time.time()
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bot {bot_token}"}
                r = await client.get("https://discord.com/api/v10/users/@me/guilds", headers=headers, timeout=5)
                ping = round((time.time() - t0) * 1000, 1)
                if r.status_code == 200:
                    bot_online = True
                    guilds_list = r.json()
                    guild_count = len(guilds_list)
                    for g in guilds_list:
                        gid = g["id"]
                        rg = await client.get(f"https://discord.com/api/v10/guilds/{gid}?with_counts=true", headers=headers, timeout=4)
                        if rg.status_code == 200:
                            user_count += rg.json().get("approximate_member_count", 0)
        except Exception:
            pass

    return StatusResponse(
        status="operational",
        bot_online=bot_online,
        latency_ms=ping,
        guild_count=guild_count,
        user_count=user_count,
        uptime_seconds=uptime
    )

@app.get(f"{settings.API_V1_STR}/user/me", tags=["Users"])
async def get_logged_in_user(current_user: dict = Depends(get_current_user)):
    return current_user

# Mount Routers
app.include_router(guilds.router, prefix=settings.API_V1_STR)
app.include_router(modules.router, prefix=settings.API_V1_STR)
app.include_router(premium.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)