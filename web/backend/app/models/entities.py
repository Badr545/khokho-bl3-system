from sqlalchemy import Column, Integer, String, BigInteger, Text, DateTime, Boolean, Float
from datetime import datetime
from .base import Base

class WebSession(Base):
    __tablename__ = "web_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True, nullable=False)
    jwt_token_hash = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

class WebPremium(Base):
    __tablename__ = "web_premium"
    guild_id = Column(BigInteger, primary_key=True, index=True)
    tier = Column(String(50), default="free") # free, basic, pro, ultra
    stripe_customer_id = Column(String(100), nullable=True)
    stripe_subscription_id = Column(String(100), nullable=True)
    premium_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class WebAnalyticsDaily(Base):
    __tablename__ = "web_analytics_daily"
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    date = Column(String(20), index=True, nullable=False) # YYYY-MM-DD
    messages_count = Column(Integer, default=0)
    members_joined = Column(Integer, default=0)
    members_left = Column(Integer, default=0)
    voice_minutes = Column(Integer, default=0)

class WebAudit(Base):
    __tablename__ = "web_audit"
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

class WebApiKey(Base):
    __tablename__ = "web_api_keys"
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Suggestion(Base):
    __tablename__ = "suggestions"
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    message = Column(Text, nullable=False)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    status = Column(String(50), default="pending") # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

class Birthday(Base):
    __tablename__ = "birthdays"
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    user_id = Column(BigInteger, index=True, nullable=False)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=True)

class Afk(Base):
    __tablename__ = "afk"
    guild_id = Column(BigInteger, primary_key=True, nullable=False)
    user_id = Column(BigInteger, primary_key=True, nullable=False)
    reason = Column(String(500), default="AFK")
    since = Column(DateTime, default=datetime.utcnow)

class CustomCommand(Base):
    __tablename__ = "custom_commands"
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    response = Column(Text, nullable=False)
    created_by = Column(BigInteger, nullable=False)
    uses_count = Column(Integer, default=0)

class ApplicationForm(Base):
    __tablename__ = "applications_forms"
    guild_id = Column(BigInteger, primary_key=True, index=True)
    form_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)

class ApplicationSubmission(Base):
    __tablename__ = "applications_submissions"
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, index=True, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    form_data_json = Column(Text, default="{}")
    status = Column(String(50), default="pending") # pending, accepted, rejected
    reviewer_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PremiumKey(Base):
    __tablename__ = "premium_keys"
    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    tier = Column(String(50), nullable=False) # basic, pro, ultra
    duration_days = Column(Integer, default=30)
    is_redeemed = Column(Boolean, default=False)
    redeemed_by_guild = Column(BigInteger, nullable=True)
    redeemed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)