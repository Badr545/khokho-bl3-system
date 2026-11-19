# database/features_schema.py
# =====================================================================
# ─── SEPARATE SQLITE DATABASE: data/features.db
#     Protects data/bot.db from corruption by keeping web, SaaS,
#     and commercial extension tables in an isolated SQLite database.
# =====================================================================
import sqlite3
import os
import threading
from typing import Optional, List, Tuple, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_DB_PATH = os.path.join(BASE_DIR, "data", "features.db")

_lock = threading.RLock()
_conn: Optional[sqlite3.Connection] = None

SCHEMA_SQL = [
    # ─── WEB SESSIONS
    """
    CREATE TABLE IF NOT EXISTS web_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        jwt_token_hash TEXT UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_web_sessions_user ON web_sessions(user_id)",

    # ─── WEB PREMIUM (Commercial SaaS)
    """
    CREATE TABLE IF NOT EXISTS web_premium (
        guild_id INTEGER PRIMARY KEY,
        tier TEXT NOT NULL DEFAULT 'free',
        stripe_customer_id TEXT,
        stripe_subscription_id TEXT,
        premium_until TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_web_premium_tier ON web_premium(tier)",

    # ─── PREMIUM LICENSE KEYS
    """
    CREATE TABLE IF NOT EXISTS premium_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_hash TEXT UNIQUE NOT NULL,
        tier TEXT NOT NULL,
        duration_days INTEGER NOT NULL DEFAULT 30,
        is_redeemed INTEGER NOT NULL DEFAULT 0,
        redeemed_by_guild INTEGER,
        redeemed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,

    # ─── WEB ANALYTICS DAILY
    """
    CREATE TABLE IF NOT EXISTS web_analytics_daily (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        messages_count INTEGER DEFAULT 0,
        members_joined INTEGER DEFAULT 0,
        members_left INTEGER DEFAULT 0,
        voice_minutes INTEGER DEFAULT 0
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_analytics_guild_date ON web_analytics_daily(guild_id, date)",

    # ─── WEB AUDIT LOG
    """
    CREATE TABLE IF NOT EXISTS web_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        details TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_audit_guild ON web_audit(guild_id)",

    # ─── WEB API KEYS (Developer Pro/Ultra Access)
    """
    CREATE TABLE IF NOT EXISTS web_api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER NOT NULL,
        key_hash TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,

    # ─── SUGGESTIONS
    """
    CREATE TABLE IF NOT EXISTS suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        upvotes INTEGER DEFAULT 0,
        downvotes INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_suggestions_guild ON suggestions(guild_id)",

    # ─── BIRTHDAYS
    """
    CREATE TABLE IF NOT EXISTS birthdays (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        day INTEGER NOT NULL,
        month INTEGER NOT NULL,
        year INTEGER,
        UNIQUE(guild_id, user_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_birthdays_date ON birthdays(day, month)",

    # ─── AFK
    """
    CREATE TABLE IF NOT EXISTS afk (
        guild_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        reason TEXT DEFAULT 'AFK',
        since TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(guild_id, user_id)
    )
    """,

    # ─── CUSTOM COMMANDS
    """
    CREATE TABLE IF NOT EXISTS custom_commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        response TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        uses_count INTEGER DEFAULT 0,
        UNIQUE(guild_id, name)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_custom_cmds ON custom_commands(guild_id, name)",

    # ─── APPLICATIONS FORMS
    """
    CREATE TABLE IF NOT EXISTS applications_forms (
        guild_id INTEGER PRIMARY KEY,
        form_json TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,

    # ─── APPLICATIONS SUBMISSIONS
    """
    CREATE TABLE IF NOT EXISTS applications_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        form_data_json TEXT DEFAULT '{}',
        status TEXT DEFAULT 'pending',
        reviewer_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_app_sub_guild ON applications_submissions(guild_id)"
]

def get_connection() -> sqlite3.Connection:
    global _conn
    with _lock:
        if _conn is None:
            os.makedirs(os.path.dirname(FEATURES_DB_PATH), exist_ok=True)
            _conn = sqlite3.connect(FEATURES_DB_PATH, check_same_thread=False)
            _conn.row_factory = sqlite3.Row
            _conn.execute("PRAGMA journal_mode=WAL")
            _conn.execute("PRAGMA synchronous=NORMAL")
        return _conn

def init_features_schema():
    with _lock:
        conn = get_connection()
        for statement in SCHEMA_SQL:
            conn.execute(statement)
        conn.commit()
    print("✅ data/features.db initialized successfully (WAL mode).")

def execute_feat(sql: str, params: Tuple = ()) -> sqlite3.Cursor:
    with _lock:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur

def query_feat_all(sql: str, params: Tuple = ()) -> List[dict]:
    with _lock:
        cur = execute_feat(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]

def query_feat_one(sql: str, params: Tuple = ()) -> Optional[dict]:
    with _lock:
        cur = execute_feat(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None

def commit_feat():
    with _lock:
        if _conn:
            _conn.commit()

# Auto-initialize when imported
init_features_schema()