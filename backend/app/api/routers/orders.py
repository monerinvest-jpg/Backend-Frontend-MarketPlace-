# backend/app/api/routers/orders.py — ИСПРАВЛЕНИЕ race condition

from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.entities import (
    Order, OrderItem, Product, ProductStatus, RoleEnum, User
)
from app.schemas.common import OrderCreateIn

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", status_code=201)
async def create_order(
    payload: OrderCreateIn,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    if not payload.items:
        raise HTTPException(status_code=400, detail="No items")

    product_ids = [item.product_id for item in payload.items]
    products_result = await session.execute(
        select(Product).where(Product.id.in_(product_ids))
    )
    products = {p.id: p for p in products_result.scalars().all()}

    subtotal = Decimal("0")

    # Валидация
    for item in payload.items:
        product = products.get(item.product_id)
        if not product:
            raise HTTPException(422, f"Product {item.product_id} not found")
        if product.status != ProductStatus.ACTIVE:
            raise HTTPException(422, f"Product '{product.title}' unavailable")
        if product.quantity < item.quantity:
            raise HTTPException(
                422,
                f"Insufficient stock for '{product.title}': "
                f"requested {item.quantity}, available {product.quantity}"
            )
        subtotal += Decimal(str(product.price)) * item.quantity

    # Создание заказа
    order = Order(
        buyer_id=user.id,
        subtotal=subtotal,
        total_price=subtotal,  # + delivery_cost - discount (упрощённо)
        delivery_address=payload.delivery_address,
    )
    session.add(order)
    await session.flush()

    # ✅ АТОМАРНОЕ уменьшение stock — БЕЗ второго цикла!
    for item in payload.items:
        result = await session.execute(
            update(Product)
            .where(
                Product.id == item.product_id,
                Product.quantity >= item.quantity,   # атомарная проверка
                Product.status == ProductStatus.ACTIVE,
            )
            .values(quantity=Product.quantity - item.quantity)
            .returning(Product.id)
        )
        updated = result.fetchone()
        if not updated:
            await session.rollback()
            raise HTTPException(
                status_code=409,
                detail=f"Product {item.product_id}: insufficient stock or became unavailable"
            )

    # ✅ Создание OrderItem (без повторного изменения quantity!)
    for item in payload.items:
        product = products[item.product_id]
        session.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price_at_time=product.price,  # цена зафиксирована
        ))

    await session.commit()
    return {"order_id": order.id, "total": float(order.total_price)}


@router.get("/{order_id}")
async def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # ✅ IDOR-защита
    is_admin = user.role in {RoleEnum.SUPERADMIN, RoleEnum.MODERATOR}
    if order.buyer_id != user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "id": order.id,
        "status": order.status,
        "total_price": float(order.total_price),
        "delivery_address": order.delivery_address,
        "created_at": str(order.created_at),
    }