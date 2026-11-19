from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

BOT_DB_PATH = os.path.join(DATA_DIR, "bot.db")
FEATURES_DB_PATH = os.path.join(DATA_DIR, "features.db")

engine_features = create_async_engine(f"sqlite+aiosqlite:///{FEATURES_DB_PATH}", echo=False)
SessionLocalFeatures = async_sessionmaker(engine_features, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

async def get_db():
    async with SessionLocalFeatures() as session:
        try:
            yield session
        finally:
            await session.close()