import hmac
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, HTTPException, Response, status
from jose import JWTError, jwt
from pydantic import BaseModel

from ..auth.deps import create_access_token
from ..auth.discord_oauth import DiscordOAuth
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_cookie_samesite() -> str:
    same_site = settings.AUTH_COOKIE_SAMESITE.lower()
    if same_site not in {"lax", "strict", "none"}:
        raise HTTPException(status_code=500, detail="AUTH_COOKIE_SAMESITE must be lax, strict, or none")
    if same_site == "none" and not settings.AUTH_COOKIE_SECURE:
        raise HTTPException(status_code=500, detail="SameSite=None requires secure authentication cookies")
    return same_site


class DiscordCallbackRequest(BaseModel):
    code: str
    state: str


@router.get("/discord/start")
async def discord_login_start(response: Response):
    if not settings.SECRET_KEY or not settings.DISCORD_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discord OAuth is not configured",
        )

    same_site = get_cookie_samesite()
    state = jwt.encode(
        {
            "purpose": "discord_oauth_state",
            "nonce": secrets.token_urlsafe(24),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    response.set_cookie(
        key="khokho_oauth_state",
        value=state,
        max_age=600,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=same_site,
        domain=settings.auth_cookie_domain,
        path="/",
    )
    query = urlencode(
        {
            "client_id": settings.DISCORD_CLIENT_ID,
            "redirect_uri": settings.DISCORD_REDIRECT_URI,
            "response_type": "code",
            "scope": "identify guilds",
            "state": state,
        }
    )
    return {"authorization_url": f"https://discord.com/oauth2/authorize?{query}"}


@router.post("/discord/callback")
async def discord_login_callback(
    body: DiscordCallbackRequest,
    response: Response,
    oauth_state: str | None = Cookie(None, alias="khokho_oauth_state"),
):
    if not settings.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured",
        )

    same_site = get_cookie_samesite()
    try:
        state = jwt.decode(body.state, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discord login state is invalid or expired",
        ) from exc

    if state.get("purpose") != "discord_oauth_state" or not state.get("nonce"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Discord login state")
    if not oauth_state or not hmac.compare_digest(body.state, oauth_state):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discord login state does not match this browser")

    oauth_data = await DiscordOAuth.exchange_code(body.code)
    access_token = oauth_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Discord did not return an access token")

    discord_user = await DiscordOAuth.get_user(access_token)
    user = {
        "id": str(discord_user["id"]),
        "username": discord_user.get("global_name") or discord_user["username"],
        "avatar": discord_user.get("avatar"),
    }
    session_token = create_access_token(
        {
            "sub": user["id"],
            "username": user["username"],
            "avatar": user["avatar"],
            "discord_access_token": access_token,
        }
    )

    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=session_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=same_site,
        domain=settings.auth_cookie_domain,
        path="/",
    )
    response.delete_cookie(
        key="khokho_oauth_state",
        domain=settings.auth_cookie_domain,
        path="/",
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=True,
        samesite=same_site,
    )
    return {"user": user}


@router.post("/logout")
async def logout(response: Response):
    same_site = get_cookie_samesite()
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        domain=settings.auth_cookie_domain,
        path="/",
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=True,
        samesite=same_site,
    )
    return {"status": "ok"}
