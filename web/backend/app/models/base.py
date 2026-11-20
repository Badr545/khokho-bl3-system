from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from ..config import settings

os.makedirs(settings.DATA_DIR, exist_ok=True)

BOT_DB_PATH = os.path.join(settings.DATA_DIR, "bot.db")
FEATURES_DB_PATH = os.path.join(settings.DATA_DIR, "features.db")

engine_features = create_async_engine(f"sqlite+aiosqlite:///{FEATURES_DB_PATH}", echo=False)
SessionLocalFeatures = async_sessionmaker(engine_features, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

async def get_db():
    async with SessionLocalFeatures() as session:
        try:
            yield session
        finally:
            await session.close()