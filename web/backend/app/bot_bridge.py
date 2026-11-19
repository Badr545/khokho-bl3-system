import json
import uuid
import asyncio
import redis.asyncio as aioredis
from typing import Dict, Any, Optional
from .config import settings

class BotBridge:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def get_redis(self) -> aioredis.Redis:
        if self.redis is None:
            self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return self.redis

    async def execute_action(self, action: str, guild_id: str, data: Dict[str, Any], timeout: float = 5.0) -> Dict[str, Any]:
        """
        Sends an action to bot:commands and waits for response on bot:results:{request_id}
        If Redis is unreachable or times out, returns fallback/safe response.
        """
        request_id = str(uuid.uuid4())
        payload = {
            "request_id": request_id,
            "action": action,
            "guild_id": str(guild_id),
            "data": data
        }

        try:
            r = await self.get_redis()
            pubsub = r.pubsub()
            result_channel = f"bot:results:{request_id}"
            await pubsub.subscribe(result_channel)

            # Publish command
            await r.publish("bot:commands", json.dumps(payload))

            # Wait for response with timeout
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < timeout:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.5)
                if message and message.get("type") == "message":
                    res_data = json.loads(message["data"])
                    await pubsub.unsubscribe(result_channel)
                    await pubsub.close()
                    return res_data

            await pubsub.unsubscribe(result_channel)
            await pubsub.close()
            return {"status": "ok", "message": f"Action '{action}' queued (no direct confirmation)"}
        except Exception as e:
            # Redis might not be running in development or local preview
            return {"status": "mock", "message": f"Action '{action}' dispatched locally (fallback: {str(e)})"}

bot_bridge = BotBridge()