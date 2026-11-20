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
from config_manager import reload_configs
from data_manager import WARNINGS, save_warnings

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
            await self.redis.aclose()

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
                print(f"⚠️ WebBridge Redis connection failed: {e}")
                await asyncio.sleep(retry_delay)
            finally:
                if self.redis:
                    await self.redis.aclose()
                    self.redis = None

    async def process_command(self, raw_data: str):
        req_id = None
        try:
            payload = json.loads(raw_data)
            req_id = payload.get("request_id")
            action = payload.get("action")
            guild_id = payload.get("guild_id")
            data = payload.get("data", {})

            result = await self.handle_action(action, guild_id, data)

            try:
                execute_feat(
                    "INSERT INTO web_audit (guild_id, user_id, action, details) VALUES (?, ?, ?, ?)",
                    (int(guild_id) if str(guild_id).isdigit() else 0, 0, action, json.dumps(data))
                )
                commit_feat()
            except Exception as e:
                print(f"⚠️ WebBridge audit log failed: {e}")

            if req_id and self.redis:
                await self.redis.publish(f"bot:results:{req_id}", json.dumps(result))
        except Exception as e:
            print(f"❌ WebBridge processing error: {e}")
            if req_id and self.redis:
                try:
                    await self.redis.publish(
                        f"bot:results:{req_id}",
                        json.dumps({"status": "error", "message": "The bot failed to process the requested action."}),
                    )
                except Exception as publish_error:
                    print(f"❌ WebBridge could not publish an error response: {publish_error}")

    async def handle_action(self, action: str, guild_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        guild = self.bot.get_guild(int(guild_id)) if str(guild_id).isdigit() else None

        if action == "sync_settings":
            if guild is None:
                return {"status": "error", "message": "The bot is not in this server"}
            reload_configs()
            return {"status": "ok", "message": "Guild configuration reloaded in bot."}

        if guild is None:
            return {"status": "error", "message": "The bot is not in this server"}

        if action == "create_giveaway":
            channel_id = data.get("channel_id")
            channel = guild.get_channel(int(channel_id)) if str(channel_id).isdigit() else None
            if not isinstance(channel, discord.TextChannel):
                return {"status": "error", "message": "Text channel not found in this server"}
            giveaway_cog = self.bot.get_cog("Giveaway")
            if not giveaway_cog:
                return {"status": "error", "message": "Giveaway cog not loaded"}
            host = guild.me
            if host is None:
                return {"status": "error", "message": "The bot member could not be resolved"}
            message = await giveaway_cog.start_giveaway(
                channel,
                str(data.get("prize", "")),
                int(data.get("duration_seconds", 0)),
                int(data.get("winners_count", 1)),
                host,
            )
            return {"status": "ok", "message": "Giveaway created", "message_id": str(message.id)}

        if action == "revoke_warning":
            user_id = data.get("user_id")
            warning_id = str(data.get("warning_id", ""))
            if not str(user_id).isdigit() or not warning_id:
                return {"status": "error", "message": "A valid user and warning ID are required"}
            uid = int(user_id)
            warnings = WARNINGS.get(guild.id, {}).get(uid, [])
            index = next(
                (
                    index
                    for index, warning in enumerate(warnings)
                    if str(warning.get("id") or f"{uid}-{index}") == warning_id
                ),
                None,
            )
            if index is None:
                return {"status": "error", "message": "Warning not found"}
            warnings.pop(index)
            if not warnings:
                WARNINGS[guild.id].pop(uid, None)
            save_warnings()

            member = guild.get_member(uid)
            admin_cog = self.bot.get_cog("Admin")
            if member and admin_cog:
                await admin_cog._apply_warn_roles(member, len(warnings))
            return {"status": "ok", "message": "Warning revoked"}

        if action == "send_announcement":
            channel_id = data.get("channel_id")
            message_text = data.get("message")
            channel = guild.get_channel(int(channel_id)) if str(channel_id).isdigit() else None
            if channel and isinstance(channel, discord.TextChannel):
                await channel.send(embed=discord.Embed(description=str(message_text)[:4096], color=discord.Color.blue()))
                return {"status": "ok", "message": "Announcement delivered."}
            return {"status": "error", "message": "Channel not found"}

        if action == "send_test_message":
            channel_id = data.get("channel_id")
            channel = guild.get_channel(int(channel_id)) if str(channel_id).isdigit() else None
            if channel and isinstance(channel, discord.TextChannel):
                await channel.send("🔔 **Test Message from Khokho Bl3 Web Dashboard!**")
                return {"status": "ok", "message": "Test message sent"}
            return {"status": "error", "message": "Channel not found"}

        return {"status": "error", "message": f"Unsupported bot action: {action}"}

async def setup(bot: commands.Bot):
    await bot.add_cog(WebBridge(bot))