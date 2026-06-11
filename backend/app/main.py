from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api.router import api_router
from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models.entities import Settings


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}


@app.on_event("startup")
async def ensure_settings_seed() -> None:
    defaults = {
        "global_commission_percent": "10",
        "referral_buyer_bonus_amount": "300",
        "referral_buyer_min_order_amount": "2500",
        "referral_seller_bonus_amount": "1500",
        "referral_bonus_max_discount_percent": "30",
        "enable_premoderation": "true",
        "yookassa_shop_id": settings.yookassa_shop_id,
        "yookassa_secret_key": settings.yookassa_secret_key,
        "cdek_client_id": settings.cdek_client_id,
        "cdek_client_secret": settings.cdek_client_secret,
    }
    async with AsyncSessionLocal() as session:
        for key, value in defaults.items():
            existing = await session.execute(select(Settings).where(Settings.key == key))
            if not existing.scalar_one_or_none():
                session.add(Settings(key=key, value=value))
        await session.commit()
