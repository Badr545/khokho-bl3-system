import asyncio
import json
import uuid
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
import redis.asyncio as aioredis

from .config import settings


class BotBridge:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def get_redis(self) -> aioredis.Redis:
        if self.redis is None:
            self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return self.redis

    async def execute_action(
        self,
        action: str,
        guild_id: str,
        data: Dict[str, Any],
        timeout: float = 5.0,
    ) -> Dict[str, Any]:
        request_id = str(uuid.uuid4())
        payload = {
            "request_id": request_id,
            "action": action,
            "guild_id": str(guild_id),
            "data": data,
        }
        pubsub = None
        try:
            redis = await self.get_redis()
            pubsub = redis.pubsub()
            result_channel = f"bot:results:{request_id}"
            await pubsub.subscribe(result_channel)
            await redis.publish("bot:commands", json.dumps(payload))

            deadline = asyncio.get_running_loop().time() + timeout
            while asyncio.get_running_loop().time() < deadline:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.5)
                if message and message.get("type") == "message":
                    result = json.loads(message["data"])
                    if result.get("status") == "error":
                        raise HTTPException(
                            status_code=status.HTTP_502_BAD_GATEWAY,
                            detail=result.get("message", "The bot could not process this action"),
                        )
                    return result

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The bot did not respond. Verify that it is online and connected to the same Redis server.",
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not reach the bot bridge. Verify that the API and bot share a working Redis connection.",
            ) from exc
        finally:
            if pubsub is not None:
                await pubsub.aclose()

    async def close(self):
        if self.redis is not None:
            await self.redis.aclose()
            self.redis = None


bot_bridge = BotBridge()
