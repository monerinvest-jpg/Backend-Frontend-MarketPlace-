from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.core.db import get_session
from app.models.entities import Order, Product, Settings, Shop, User
from app.schemas.common import SettingIn


router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/dashboard")
async def dashboard(session: AsyncSession = Depends(get_session)) -> dict:
    users_count = len((await session.execute(select(User))).scalars().all())
    orders = (await session.execute(select(Order))).scalars().all()
    revenue = sum(float(order.total_price) for order in orders)
    return {"users": users_count, "orders": len(orders), "revenue": revenue}


@router.patch("/products/{product_id}/status")
async def moderate_product(product_id: int, status: str, reason: str = "", session: AsyncSession = Depends(get_session)) -> dict:
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.status = status
    product.moderation_reason = reason or None
    await session.commit()
    return {"ok": True}


@router.patch("/shops/{shop_id}/commission")
async def set_shop_commission(shop_id: int, commission_percent: float | None, session: AsyncSession = Depends(get_session)) -> dict:
    result = await session.execute(select(Shop).where(Shop.id == shop_id))
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    shop.commission_percent = commission_percent
    await session.commit()
    return {"ok": True}


@router.get("/settings")
async def list_settings(session: AsyncSession = Depends(get_session)) -> list[Settings]:
    result = await session.execute(select(Settings).order_by(Settings.key.asc()))
    return list(result.scalars().all())


@router.post("/settings")
async def upsert_setting(payload: SettingIn, session: AsyncSession = Depends(get_session)) -> dict:
    result = await session.execute(select(Settings).where(Settings.key == payload.key))
    row = result.scalar_one_or_none()
    if row:
        row.value = payload.value
    else:
        session.add(Settings(key=payload.key, value=payload.value))
    await session.commit()
    return {"ok": True}
