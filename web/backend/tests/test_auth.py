import os
import sys
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from jose import jwt

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(os.path.dirname(BACKEND_DIR))
for _module_name in tuple(sys.modules):
    if _module_name == "app" or _module_name.startswith("app."):
        sys.modules.pop(_module_name, None)
sys.path = [BACKEND_DIR] + [path for path in sys.path if os.path.abspath(path or os.getcwd()) != ROOT_DIR]

from app.auth.deps import get_current_user, verify_guild_permission
from app.config import settings
from app.main import app


class AuthenticationTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_session_is_rejected(self):
        with self.assertRaises(HTTPException) as raised:
            await get_current_user(authorization=None, session_token=None)

        self.assertEqual(raised.exception.status_code, 401)

    async def test_valid_session_cookie_resolves_user(self):
        claims = {"sub": "123", "discord_access_token": "discord-token", "username": "member"}
        with patch.object(settings, "SECRET_KEY", "unit-test-secret"):
            token = jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            user = await get_current_user(authorization=None, session_token=token)

        self.assertEqual(user["sub"], "123")

    async def test_guild_access_requires_manage_permission(self):
        user = {"discord_access_token": "discord-token"}
        with patch("app.auth.deps.DiscordOAuth.get_user_guilds", new_callable=AsyncMock) as get_guilds:
            get_guilds.return_value = [{"id": "456", "owner": False, "permissions": "0"}]
            with self.assertRaises(HTTPException) as raised:
                await verify_guild_permission("456", user)

        self.assertEqual(raised.exception.status_code, 403)

    async def test_guild_owner_can_manage_server(self):
        user = {"discord_access_token": "discord-token"}
        with patch("app.auth.deps.DiscordOAuth.get_user_guilds", new_callable=AsyncMock) as get_guilds:
            get_guilds.return_value = [{"id": "456", "owner": True, "permissions": "0"}]
            authorized_user = await verify_guild_permission("456", user)

        self.assertIs(authorized_user, user)

    def test_discord_oauth_sets_http_only_session_cookie(self):
        with (
            patch.object(settings, "SECRET_KEY", "unit-test-secret"),
            patch.object(settings, "DISCORD_CLIENT_ID", "test-client"),
            patch.object(settings, "DISCORD_CLIENT_SECRET", "test-client-secret"),
            patch.object(settings, "AUTH_COOKIE_SECURE", False),
            patch.object(settings, "AUTH_COOKIE_SAMESITE", "lax"),
            patch("app.routers.auth.DiscordOAuth.exchange_code", new_callable=AsyncMock) as exchange_code,
            patch("app.routers.auth.DiscordOAuth.get_user", new_callable=AsyncMock) as get_user,
        ):
            exchange_code.return_value = {"access_token": "discord-access-token"}
            get_user.return_value = {"id": "123", "username": "member"}
            with TestClient(app) as client:
                start = client.get("/api/v1/auth/discord/start")
                state = client.cookies.get("khokho_oauth_state")
                self.assertEqual(start.status_code, 200)
                self.assertTrue(state)

                callback = client.post(
                    "/api/v1/auth/discord/callback",
                    json={"code": "one-time-code", "state": state},
                )
                self.assertEqual(callback.status_code, 200)
                self.assertIn(settings.AUTH_COOKIE_NAME, client.cookies)
                self.assertEqual(client.get("/api/v1/user/me").json()["id"], "123")

                logout = client.post("/api/v1/auth/logout")
                self.assertEqual(logout.status_code, 200)
                self.assertEqual(client.get("/api/v1/user/me").status_code, 401)


if __name__ == "__main__":
    unittest.main()
