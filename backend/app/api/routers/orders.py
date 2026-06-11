from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.entities import Order, OrderItem, Product, Settings, Shop, User
from app.schemas.common import OrderCreateIn
from app.services.commission import calculate_commission
from app.services.delivery.cdek import CDEKProvider


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", status_code=201)
async def create_order(
    payload: OrderCreateIn,  # ✅ Pydantic-схема с OrderItemIn
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    if not payload.items:
        raise HTTPException(status_code=400, detail="No items")
 
    product_ids = [item.product_id for item in payload.items]  # ✅ .product_id
    products_result = await session.execute(
        select(Product).where(Product.id.in_(product_ids))
    )
    products = {p.id: p for p in products_result.scalars().all()}
 
    subtotal = Decimal("0")
    first_shop_id: int | None = None
 
    # ✅ Единый валидирующий цикл
    for item in payload.items:
        product = products.get(item.product_id)  # ✅ Typed schema
        if not product:
            raise HTTPException(
                status_code=422,
                detail=f"Product {item.product_id} not found"
            )
        if product.status != ProductStatus.ACTIVE:
            raise HTTPException(
                status_code=422,
                detail=f"Product '{product.title}' is not available"
            )
        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=422,
                detail=f"Insufficient stock for '{product.title}': "
                       f"requested {item.quantity}, available {product.quantity}"
            )
        subtotal += Decimal(str(product.price)) * item.quantity
        first_shop_id = first_shop_id or product.shop_id
 
    # ... расчёт доставки, комиссии, создание Order ...
    order = Order(buyer_id=user.id, subtotal=subtotal, ...)
    session.add(order)
    await session.flush()
 
    # ✅ Атомарное уменьшение количества с проверкой
    for item in payload.items:
        result = await session.execute(
            update(Product)
            .where(
                Product.id == item.product_id,
                Product.quantity >= item.quantity,  # ✅ Атомарная проверка
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
                detail=f"Product {item.product_id}: insufficient stock or unavailable"
            )

    # ✅ Создание OrderItem и уменьшение остатков
    for item in payload.items:
        product = products[item.product_id]
        product.quantity -= item.quantity  # ✅ Уменьшаем stock
        session.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price_at_time=product.price,
        ))
 
    await session.commit()
    return {"order_id": order.id, "total": float(order.total_price)}


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
