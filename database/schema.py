# database/schema.py
# =====================================================================
# ─── SQLITE SCHEMA — tables + indexes + meta helpers
# =====================================================================
from database.engine import execute, commit


SCHEMA_SQL = [
    # ─── VC RANKS
    """
    CREATE TABLE IF NOT EXISTS vc_ranks (
        guild_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        xp INTEGER NOT NULL DEFAULT 0,
        level INTEGER NOT NULL DEFAULT 0,
        total_seconds INTEGER NOT NULL DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (guild_id, user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS vc_rank_config (
        guild_id INTEGER PRIMARY KEY,
        xp_per_minute INTEGER NOT NULL DEFAULT 2,
        min_users INTEGER NOT NULL DEFAULT 2,
        excluded_channel_ids TEXT NOT NULL DEFAULT '[]',
        ladder_json TEXT NOT NULL DEFAULT '[]',
        announcement_channel_id INTEGER,
        anti_afk_muted INTEGER NOT NULL DEFAULT 1,
        anti_afk_deafened INTEGER NOT NULL DEFAULT 1,
        anti_afk_alone INTEGER NOT NULL DEFAULT 1
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS setup_messages (
        guild_id INTEGER NOT NULL,
        message_key TEXT NOT NULL,
        channel_id INTEGER NOT NULL,
        message_id INTEGER NOT NULL,
        PRIMARY KEY (guild_id, message_key)
    )
    """,
    # ─── ECONOMY
    """
    CREATE TABLE IF NOT EXISTS economy (
        guild_id INTEGER NOT NULL,
        user_id  INTEGER NOT NULL,
        data     TEXT    NOT NULL DEFAULT '{}',
        PRIMARY KEY (guild_id, user_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_economy_guild ON economy(guild_id)",
    "CREATE INDEX IF NOT EXISTS idx_vc_ranks_guild ON vc_ranks(guild_id)",

    # ─── LEVELS
    """
    CREATE TABLE IF NOT EXISTS levels (
        guild_id INTEGER NOT NULL,
        user_id  INTEGER NOT NULL,
        data     TEXT    NOT NULL DEFAULT '{}',
        PRIMARY KEY (guild_id, user_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_levels_guild ON levels(guild_id)",

    # ─── BIR
    """
    CREATE TABLE IF NOT EXISTS bir (
        guild_id INTEGER NOT NULL,
        user_id  INTEGER NOT NULL,
        data     TEXT    NOT NULL DEFAULT '{}',
        PRIMARY KEY (guild_id, user_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_bir_guild ON bir(guild_id)",

    # ─── WARNINGS
    """
    CREATE TABLE IF NOT EXISTS warnings (
        guild_id INTEGER NOT NULL,
        user_id  INTEGER NOT NULL,
        data     TEXT    NOT NULL DEFAULT '[]',
        PRIMARY KEY (guild_id, user_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_warnings_guild ON warnings(guild_id)",

    # ─── BANKING
    """
    CREATE TABLE IF NOT EXISTS banking (
        guild_id INTEGER NOT NULL,
        user_id  INTEGER NOT NULL,
        data     TEXT    NOT NULL DEFAULT '{}',
        PRIMARY KEY (guild_id, user_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_banking_guild ON banking(guild_id)",

    # ─── KV (misc blobs like market)
    """
    CREATE TABLE IF NOT EXISTS kv (
        key   TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,

    # ─── MIGRATION META
    """
    CREATE TABLE IF NOT EXISTS meta (
        key   TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,
]


def init_schema():
    """Sayeb kol tables + indexes ila makayninx."""
    for sql in SCHEMA_SQL:
        execute(sql)
    commit()


def get_meta(key: str, default: str | None = None) -> str | None:
    row = execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_meta(key: str, value: str):
    execute(
        "INSERT INTO meta(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    commit()