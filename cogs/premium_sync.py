# cogs/premium_sync.py
# =====================================================================
# ─── PERIODIC PREMIUM STATUS SYNC TASK
#     Syncs active subscriptions and tier limits from features.db
#     into bot memory cache every 5 minutes.
# =====================================================================
from discord.ext import commands, tasks
from datetime import datetime
from database.features_schema import query_feat_all
from cogs.premium import PREMIUM_CACHE

class PremiumSync(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sync_loop.start()

    def cog_unload(self):
        self.sync_loop.cancel()

    @tasks.loop(minutes=5.0)
    async def sync_loop(self):
        try:
            rows = query_feat_all("SELECT guild_id, tier, premium_until FROM web_premium")
            now = datetime.utcnow()
            for r in rows:
                gid = r["guild_id"]
                tier = r["tier"]
                until_raw = r.get("premium_until")
                until = datetime.fromisoformat(until_raw) if isinstance(until_raw, str) else until_raw
                if until and until < now:
                    tier = "free"
                PREMIUM_CACHE[gid] = {"tier": tier, "premium_until": until}
        except Exception as e:
            print(f"⚠️ Premium sync error: {e}")

    @sync_loop.before_loop
    async def before_sync(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(PremiumSync(bot))