from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.entities import Order, OrderItem, Product, Settings, Shop, User
from app.schemas.common import OrderCreateIn
from app.services.commission import calculate_commission
from app.services.delivery.cdek import CDEKProvider


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("")
async def create_order(
    payload: OrderCreateIn,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    if not payload.items:
        raise HTTPException(status_code=400, detail="No items")

    product_ids = [item["product_id"] for item in payload.items]
    products_result = await session.execute(select(Product).where(Product.id.in_(product_ids)))
    products = {product.id: product for product in products_result.scalars().all()}

    subtotal = Decimal("0")
    first_shop_id: int | None = None
    for item in payload.items:
        product = products.get(item["product_id"])
        if not product:
            continue
        qty = int(item["quantity"])
        subtotal += Decimal(product.price) * qty
        first_shop_id = first_shop_id or product.shop_id

    if subtotal == 0:
        raise HTTPException(status_code=400, detail="Invalid items")

    global_commission = await session.execute(
        select(Settings).where(Settings.key == "global_commission_percent")
    )
    global_value = Decimal((global_commission.scalar_one_or_none() or Settings(key="x", value="10")).value)

    shop = None
    if first_shop_id:
        shop_result = await session.execute(select(Shop).where(Shop.id == first_shop_id))
        shop = shop_result.scalar_one_or_none()

    commission_percent = Decimal(shop.commission_percent) if shop and shop.commission_percent else global_value

    delivery = await CDEKProvider().calculate(payload.city, 1200)
    delivery_cost = Decimal(delivery["cost"])
    platform_fee, _ = calculate_commission(subtotal, commission_percent)

    order = Order(
        buyer_id=user.id,
        subtotal=subtotal,
        delivery_cost=delivery_cost,
        total_price=subtotal + delivery_cost,
        platform_fee=platform_fee,
        commission_percent_used=commission_percent,
        delivery_address=payload.address,
    )
    session.add(order)
    await session.flush()

    for item in payload.items:
        product = products.get(item["product_id"])
        if not product:
            continue
        row = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=int(item["quantity"]),
            price_at_time=product.price,
        )
        session.add(row)

    await session.commit()
    return {"order_id": order.id, "total": order.total_price, "delivery": delivery}


@router.get("")
async def list_orders(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> list[Order]:
    result = await session.execute(select(Order).where(Order.buyer_id == user.id))
    return list(result.scalars().all())
