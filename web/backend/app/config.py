import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Khokho Bl3 V3 API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("NEXTAUTH_SECRET", "supersecret-jwt-key-khokho-bl3-v3-production-key-999")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    DISCORD_CLIENT_ID: str = os.getenv("DISCORD_CLIENT_ID", "")
    DISCORD_CLIENT_SECRET: str = os.getenv("DISCORD_CLIENT_SECRET", "")
    DISCORD_REDIRECT_URI: str = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:3000/api/auth/callback/discord")
    DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_TOKEN", "")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///../../../data/bot.db")
    FEATURES_DB_URL: str = os.getenv("FEATURES_DB_URL", "sqlite+aiosqlite:///../../../data/features.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_BASIC: str = os.getenv("STRIPE_PRICE_BASIC", "price_basic_mock")
    STRIPE_PRICE_PRO: str = os.getenv("STRIPE_PRICE_PRO", "price_pro_mock")
    STRIPE_PRICE_ULTRA: str = os.getenv("STRIPE_PRICE_ULTRA", "price_ultra_mock")

    API_INTERNAL_KEY: str = os.getenv("API_INTERNAL_KEY", "internal_secret_bridge_key_123")
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://khokhobl3.com"
    ]

    class Config:
        case_sensitive = True
        extra = "allow"

settings = Settings()