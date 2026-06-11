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

    for item in payload.items:
    product = products.get(item.product_id)  # ✅ Используем typed schema
    if not product:
        raise HTTPException(
            status_code=422,
            detail=f"Product {item.product_id} not found"
        )
    
    # ✅ Проверка что товар активен
    if product.status != ProductStatus.ACTIVE:
        raise HTTPException(
            status_code=422,
            detail=f"Product '{product.title}' is not available"
        )
    
    # ✅ Проверка остатков
    if product.quantity < item.quantity:
        raise HTTPException(
            status_code=422,
            detail=f"Insufficient stock for '{product.title}': "
                   f"requested {item.quantity}, available {product.quantity}"
        )

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
    product = products.get(item.product_id)
    if product:
        product.quantity -= item.quantity  # ✅ Уменьшаем остаток

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


@router.get("/{order_id}")
async def get_order(
    order_id: int,
    user: User = Depends(get_current_user),          # ✅ Аутентификация обязательна
    session: AsyncSession = Depends(get_session),
) -> dict:
    result = await session.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # ✅ IDOR-защита: проверяем что заказ принадлежит текущему пользователю
    # Исключение: администратор может смотреть любой заказ
    if order.buyer_id != user.id and user.role not in {"superadmin", "moderator"}:
        raise HTTPException(
            status_code=403,           # ✅ 403, не 404 (чтобы не скрывать факт существования)
            detail="Access denied"     # ✅ Не раскрываем детали
        )
    
    return {
        "id": order.id,
        "status": order.status,
        "total_price": order.total_price,
        "delivery_address": order.delivery_address,
        "created_at": order.created_at,
    }
