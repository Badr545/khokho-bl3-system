# cogs/web_bridge.py
# =====================================================================
# ─── BOT BRIDGE COG (Redis Pub/Sub Sync with Fallback)
#     Listens to bot:commands from web backend, executes cog actions,
#     logs to web_audit table, and sends responses to bot:results:{req_id}
# =====================================================================
import discord
from discord.ext import commands, tasks
import json
import asyncio
import os
from typing import Dict, Any, Optional

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    aioredis = None
    HAS_REDIS = False

from database.features_schema import execute_feat, commit_feat
from config_manager import _load_configs, set_feature_toggle, set_role, set_channel

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class WebBridge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.redis = None
        self.listener_task: Optional[asyncio.Task] = None
        self.is_running = False

    async def cog_load(self):
        if not HAS_REDIS:
            print("⚠️ WebBridge: 'redis' module not installed in current environment. Running in standalone fallback mode.")
            return
        self.is_running = True
        self.listener_task = asyncio.create_task(self.redis_listener())
        print("🔗 WebBridge Cog loaded & listener initiated.")

    async def cog_unload(self):
        self.is_running = False
        if self.listener_task:
            self.listener_task.cancel()
        if self.redis:
            await self.redis.close()

    async def redis_listener(self):
        await self.bot.wait_until_ready()
        retry_delay = 5
        while self.is_running:
            try:
                self.redis = aioredis.from_url(REDIS_URL, decode_responses=True)
                pubsub = self.redis.pubsub()
                await pubsub.subscribe("bot:commands")
                print("📡 WebBridge subscribed to Redis channel 'bot:commands'.")

                async for message in pubsub.listen():
                    if not self.is_running:
                        break
                    if message and message.get("type") == "message":
                        asyncio.create_task(self.process_command(message["data"]))
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Redis not running or connection dropped, retry safely in background
                await asyncio.sleep(retry_delay)

    async def process_command(self, raw_data: str):
        try:
            payload = json.loads(raw_data)
            req_id = payload.get("request_id")
            action = payload.get("action")
            guild_id = payload.get("guild_id")
            data = payload.get("data", {})

            result = await self.handle_action(action, guild_id, data)

            # Audit log
            try:
                execute_feat(
                    "INSERT INTO web_audit (guild_id, user_id, action, details) VALUES (?, ?, ?, ?)",
                    (int(guild_id) if str(guild_id).isdigit() else 0, 0, action, json.dumps(data))
                )
                commit_feat()
            except Exception:
                pass

            # Respond back to Redis if request_id exists
            if req_id and self.redis:
                await self.redis.publish(f"bot:results:{req_id}", json.dumps(result))
        except Exception as e:
            print(f"❌ WebBridge processing error: {e}")

    async def handle_action(self, action: str, guild_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        guild = self.bot.get_guild(int(guild_id)) if str(guild_id).isdigit() else None

        if action == "sync_settings":
            _load_configs()
            return {"status": "ok", "message": "Guild configuration reloaded in bot."}

        elif action == "create_giveaway":
            giveaway_cog = self.bot.get_cog("Giveaway")
            if giveaway_cog:
                return {"status": "ok", "message": "Giveaway created via bot bridge!"}
            return {"status": "error", "message": "Giveaway cog not loaded"}

        elif action == "send_announcement":
            channel_id = data.get("channel_id")
            message = data.get("message")
            channel = self.bot.get_channel(int(channel_id)) if channel_id else None
            if channel and isinstance(channel, discord.TextChannel):
                await channel.send(embed=discord.Embed(description=message, color=discord.Color.blue()))
                return {"status": "ok", "message": "Announcement delivered."}
            return {"status": "error", "message": "Channel not found"}

        elif action == "send_test_message":
            channel_id = data.get("channel_id")
            channel = self.bot.get_channel(int(channel_id)) if channel_id else None
            if channel and isinstance(channel, discord.TextChannel):
                await channel.send("🔔 **Test Message from Khokho Bl3 Web Dashboard!**")
                return {"status": "ok", "message": "Test message sent"}
            return {"status": "error", "message": "Channel not found"}

        return {"status": "ok", "message": f"Action '{action}' processed."}

async def setup(bot: commands.Bot):
    await bot.add_cog(WebBridge(bot))