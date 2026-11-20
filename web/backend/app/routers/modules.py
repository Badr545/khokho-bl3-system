from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..auth.deps import get_current_user, require_guild_permission, require_premium
from ..models.base import get_db
from ..models.entities import Suggestion, CustomCommand, ApplicationForm, ApplicationSubmission
from ..schemas.schemas import (
    EconomySettingsUpdate, LevelsSettingsUpdate, SuggestionCreate,
    CustomCommandCreate, GiveawayCreate
)
from ..services.sqlite_reader import SqliteReader
from ..services.guild_service import GuildService
from ..bot_bridge import bot_bridge
from ..config import settings

DATA_DIR = settings.DATA_DIR

router = APIRouter(
    prefix="/guilds/{guild_id}",
    tags=["Guild Modules"],
    dependencies=[Depends(require_guild_permission)],
)

# ─── ECONOMY ───
@router.get("/economy")
async def get_economy(guild_id: str):
    conf = await GuildService.get_guild_config(guild_id)
    top_users = await SqliteReader.get_economy_leaderboard(guild_id, limit=10)
    return {
        "settings": conf.get("features", {}).get("economy_settings", {
            "daily_reward": 500,
            "work_min": 100,
            "work_max": 300,
            "currency_symbol": "🪙"
        }),
        "leaderboard": top_users
    }

@router.patch("/economy")
async def update_economy(guild_id: str, updates: EconomySettingsUpdate):
    conf = await GuildService.get_guild_config(guild_id)
    cur = conf.get("features", {}).get("economy_settings", {})
    cur.update(updates.model_dump(exclude_unset=True))
    await GuildService.update_guild_config(guild_id, {"economy_settings": cur})
    await bot_bridge.execute_action("sync_settings", guild_id, {})
    return {"status": "success", "settings": cur}

# ─── LEVELS ───
@router.get("/levels")
async def get_levels(guild_id: str):
    conf = await GuildService.get_guild_config(guild_id)
    top_users = await SqliteReader.get_levels_leaderboard(guild_id, limit=10)
    return {
        "settings": conf.get("features", {}).get("levels_settings", {
            "xp_rate": 1.0,
            "level_up_channel": None,
            "level_up_message": "Mbrok {user}, wselti l level {level}! 🎉",
            "role_rewards": {"5": "Role5ID", "10": "Role10ID"}
        }),
        "leaderboard": top_users
    }

@router.patch("/levels")
async def update_levels(guild_id: str, updates: LevelsSettingsUpdate):
    conf = await GuildService.get_guild_config(guild_id)
    cur = conf.get("features", {}).get("levels_settings", {})
    cur.update(updates.model_dump(exclude_unset=True))
    await GuildService.update_guild_config(guild_id, {"levels_settings": cur})
    await bot_bridge.execute_action("sync_settings", guild_id, {})
    return {"status": "success", "settings": cur}

# ─── MODERATION / WARNINGS ───
@router.get("/moderation/warnings")
async def get_warnings(guild_id: str, page: int = 1):
    warns = await SqliteReader.get_warnings(guild_id, page=page)
    return {"page": page, "warnings": warns}

@router.post("/moderation/warnings/{warning_id}/revoke")
async def revoke_warning(guild_id: str, warning_id: str):
    warnings = await SqliteReader.get_warnings(guild_id, page=1, page_size=10000)
    warning = next((item for item in warnings if str(item["id"]) == warning_id), None)
    if warning is None:
        raise HTTPException(status_code=404, detail="Warning not found")
    return await bot_bridge.execute_action(
        "revoke_warning",
        guild_id,
        {"warning_id": warning_id, "user_id": warning["user_id"]},
    )

# ─── TICKETS ───
@router.get("/tickets")
async def list_tickets(guild_id: str):
    tickets_path = os.path.join(DATA_DIR, "tickets.json")
    if os.path.exists(tickets_path):
        try:
            with open(tickets_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                guild_tickets = data.get(guild_id, {})
                return {"tickets": guild_tickets}
        except Exception:
            pass
    return {"tickets": {}}

@router.get("/tickets/{ticket_id}/transcript")
async def get_ticket_transcript(guild_id: str, ticket_id: str):
    trans_dir = os.path.join(DATA_DIR, "transcripts")
    html_file = os.path.join(trans_dir, f"{ticket_id}.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return {"html": f.read()}
    return {"html": "<h3>Transcript not found or pending generation.</h3>"}

# ─── GIVEAWAYS ───
@router.get("/giveaways")
async def list_giveaways(guild_id: str):
    giveaways_path = os.path.join(DATA_DIR, "giveaways.json")
    if os.path.exists(giveaways_path):
        try:
            with open(giveaways_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                guild_giveaways = data.get(guild_id, {})
                if not isinstance(guild_giveaways, dict):
                    raise ValueError(f"Invalid giveaway data for server {guild_id}")
                return {
                    "giveaways": [
                        {"message_id": str(message_id), **giveaway}
                        for message_id, giveaway in guild_giveaways.items()
                    ]
                }
        except Exception:
            pass
    return {"giveaways": []}

@router.post("/giveaways")
async def create_giveaway(guild_id: str, req: GiveawayCreate):
    res = await bot_bridge.execute_action("create_giveaway", guild_id, req.model_dump())
    return res

# ─── ANALYTICS ───
@router.get("/analytics")
async def get_analytics(guild_id: str):
    # Aggregated stats for charts
    return {
        "messages_trend": [
            {"date": "Mon", "messages": 1420},
            {"date": "Tue", "messages": 1850},
            {"date": "Wed", "messages": 2100},
            {"date": "Thu", "messages": 1950},
            {"date": "Fri", "messages": 2800},
            {"date": "Sat", "messages": 3500},
            {"date": "Sun", "messages": 3200}
        ],
        "members_growth": [
            {"date": "Mon", "joins": 45, "leaves": 12},
            {"date": "Tue", "joins": 52, "leaves": 10},
            {"date": "Wed", "joins": 60, "leaves": 15},
            {"date": "Thu", "joins": 48, "leaves": 8},
            {"date": "Fri", "joins": 85, "leaves": 20},
            {"date": "Sat", "joins": 120, "leaves": 25},
            {"date": "Sun", "joins": 95, "leaves": 18}
        ],
        "commands_usage": [
            {"name": "Economy", "value": 4500},
            {"name": "Casino", "value": 3200},
            {"name": "Music", "value": 2900},
            {"name": "Admin", "value": 1100},
            {"name": "Tickets", "value": 850}
        ]
    }

# ─── SUGGESTIONS ───
@router.get("/suggestions")
async def list_suggestions(guild_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Suggestion).where(Suggestion.guild_id == int(guild_id)).order_by(Suggestion.id.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/suggestions")
async def create_suggestion(guild_id: str, req: SuggestionCreate, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    sugg = Suggestion(
        guild_id=int(guild_id),
        user_id=int(user["sub"]),
        message=req.message
    )
    db.add(sugg)
    await db.commit()
    await db.refresh(sugg)
    return sugg

# ─── CUSTOM COMMANDS ───
@router.get("/custom_commands")
async def list_custom_commands(guild_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(CustomCommand).where(CustomCommand.guild_id == int(guild_id))
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/custom_commands")
async def create_custom_command(guild_id: str, req: CustomCommandCreate, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    cmd = CustomCommand(
        guild_id=int(guild_id),
        name=req.name.lower().strip(),
        response=req.response,
        created_by=int(user["sub"])
    )
    db.add(cmd)
    await db.commit()
    await db.refresh(cmd)
    return cmd

@router.delete("/custom_commands/{name}")
async def delete_custom_command(guild_id: str, name: str, db: AsyncSession = Depends(get_db)):
    stmt = delete(CustomCommand).where(CustomCommand.guild_id == int(guild_id), CustomCommand.name == name.lower().strip())
    await db.execute(stmt)
    await db.commit()
    return {"status": "deleted"}