from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any
from datetime import datetime, timedelta
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ..config import settings
from ..models.base import get_db
from ..models.entities import WebPremium, PremiumKey
from ..schemas.schemas import PremiumCheckoutRequest, PremiumActivateKeyRequest
from ..auth.deps import get_current_user

router = APIRouter(prefix="/premium", tags=["Premium & Billing"])

if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

@router.get("/tiers")
async def get_premium_tiers():
    return {
        "tiers": [
            {
                "id": "free",
                "name": "Free Tier",
                "price": 0,
                "features": [
                    "All 51 standard bot cogs",
                    "1 active ticket at a time",
                    "1 active giveaway",
                    "100 economy cmds / day",
                    "3 custom commands"
                ]
            },
            {
                "id": "basic",
                "name": "Basic SaaS",
                "price": 5,
                "price_id": settings.STRIPE_PRICE_BASIC,
                "features": [
                    "Unlimited tickets & transcripts",
                    "5 concurrent giveaways",
                    "500 economy cmds / day",
                    "10 custom commands",
                    "Custom Embed builder web sync",
                    "No bot branding in footer"
                ]
            },
            {
                "id": "pro",
                "name": "Pro Tier",
                "price": 10,
                "price_id": settings.STRIPE_PRICE_PRO,
                "features": [
                    "Unlimited everything",
                    "Full Analytics & CSV Export",
                    "REST API developer access",
                    "50 custom commands",
                    "Music Audio Filters (8D, Bassboost, Nightcore)",
                    "Priority 24/7 Support"
                ]
            },
            {
                "id": "ultra",
                "name": "Ultra / White-Label",
                "price": 20,
                "price_id": settings.STRIPE_PRICE_ULTRA,
                "features": [
                    "Full White-Label (Custom bot name & avatar)",
                    "Dedicated support line",
                    "Unlimited custom commands",
                    "Custom domain for dashboard",
                    "24/7 Voice & Music presence"
                ]
            }
        ]
    }

@router.post("/checkout")
async def create_checkout_session(req: PremiumCheckoutRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    if not settings.STRIPE_SECRET_KEY:
        # Mock Stripe URL for local demo
        return {"checkout_url": f"{req.success_url}?session_id=mock_session_12345&guild_id={req.guild_id}&tier={req.tier}"}

    try:
        price_map = {
            "basic": settings.STRIPE_PRICE_BASIC,
            "pro": settings.STRIPE_PRICE_PRO,
            "ultra": settings.STRIPE_PRICE_ULTRA
        }
        price_id = price_map.get(req.tier.lower())
        if not price_id:
            raise HTTPException(status_code=400, detail="Invalid tier specified")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{req.success_url}?session_id={{CHECKOUT_SESSION_ID}}&guild_id={req.guild_id}&tier={req.tier}",
            cancel_url=req.cancel_url,
            client_reference_id=f"{req.guild_id}:{req.tier}",
            metadata={"guild_id": req.guild_id, "tier": req.tier}
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not settings.STRIPE_WEBHOOK_SECRET:
        return {"status": "ignored_no_secret"}

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        guild_id_str = metadata.get("guild_id")
        tier = metadata.get("tier", "basic")

        if guild_id_str:
            gid = int(guild_id_str)
            stmt = select(WebPremium).where(WebPremium.guild_id == gid)
            res = await db.execute(stmt)
            premium = res.scalars().first()
            if not premium:
                premium = WebPremium(guild_id=gid)
                db.add(premium)

            premium.tier = tier
            premium.stripe_customer_id = session.get("customer")
            premium.stripe_subscription_id = session.get("subscription")
            premium.premium_until = datetime.utcnow() + timedelta(days=32)
            await db.commit()

    return {"status": "success"}

@router.post("/activate")
async def activate_key(req: PremiumActivateKeyRequest, db: AsyncSession = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    import hashlib
    key_hashed = hashlib.sha256(req.key.strip().encode()).hexdigest()

    stmt = select(PremiumKey).where(PremiumKey.key_hash == key_hashed, PremiumKey.is_redeemed == False)
    res = await db.execute(stmt)
    key_obj = res.scalars().first()

    if not key_obj:
        raise HTTPException(status_code=400, detail="Invalid or already redeemed premium key.")

    gid = int(req.guild_id)
    key_obj.is_redeemed = True
    key_obj.redeemed_by_guild = gid
    key_obj.redeemed_at = datetime.utcnow()

    # Update or insert WebPremium
    p_stmt = select(WebPremium).where(WebPremium.guild_id == gid)
    p_res = await db.execute(p_stmt)
    premium = p_res.scalars().first()
    if not premium:
        premium = WebPremium(guild_id=gid)
        db.add(premium)

    premium.tier = key_obj.tier
    duration = timedelta(days=key_obj.duration_days)
    if premium.premium_until and premium.premium_until > datetime.utcnow():
        premium.premium_until += duration
    else:
        premium.premium_until = datetime.utcnow() + duration

    await db.commit()
    return {
        "status": "success",
        "message": f"Successfully activated {key_obj.tier.upper()} tier for {key_obj.duration_days} days!",
        "tier": key_obj.tier,
        "expires_at": premium.premium_until.isoformat()
    }