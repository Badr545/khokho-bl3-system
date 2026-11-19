from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    id: str
    username: str
    discriminator: str
    avatar: Optional[str] = None
    email: Optional[str] = None

class GuildBase(BaseModel):
    id: str
    name: str
    icon: Optional[str] = None
    owner: bool = False
    permissions: int
    has_bot: bool = False

class GuildConfigUpdate(BaseModel):
    prefix: Optional[str] = None
    language: Optional[str] = None # en, fr, ar, darija
    welcome_enabled: Optional[bool] = None
    welcome_channel: Optional[str] = None
    welcome_message: Optional[str] = None
    leave_enabled: Optional[bool] = None
    leave_channel: Optional[str] = None
    automod_enabled: Optional[bool] = None
    anti_spam: Optional[bool] = None
    anti_link: Optional[bool] = None
    anti_caps: Optional[bool] = None
    log_channel: Optional[str] = None

class EconomySettingsUpdate(BaseModel):
    daily_reward: Optional[int] = None
    work_min: Optional[int] = None
    work_max: Optional[int] = None
    currency_symbol: Optional[str] = None

class LevelsSettingsUpdate(BaseModel):
    xp_rate: Optional[float] = None
    level_up_channel: Optional[str] = None
    level_up_message: Optional[str] = None
    role_rewards: Optional[Dict[str, str]] = None # level -> role_id

class SuggestionCreate(BaseModel):
    message: str

class SuggestionResponse(BaseModel):
    id: int
    guild_id: str
    user_id: str
    message: str
    upvotes: int
    downvotes: int
    status: str
    created_at: datetime

class CustomCommandCreate(BaseModel):
    name: str
    response: str

class CustomCommandResponse(BaseModel):
    id: int
    guild_id: str
    name: str
    response: str
    created_by: str
    uses_count: int

class GiveawayCreate(BaseModel):
    channel_id: str
    prize: str
    duration_seconds: int
    winners_count: int = 1

class BotActionRequest(BaseModel):
    action: str
    guild_id: str
    data: Dict[str, Any] = Field(default_factory=dict)

class PremiumCheckoutRequest(BaseModel):
    guild_id: str
    tier: str # basic, pro, ultra
    success_url: str
    cancel_url: str

class PremiumActivateKeyRequest(BaseModel):
    guild_id: str
    key: str

class StatusResponse(BaseModel):
    status: str = "operational"
    bot_online: bool
    latency_ms: float
    guild_count: int
    user_count: int
    uptime_seconds: float