# backend/app/api/routers/products.py — ПОЛНАЯ ЗАМЕНА

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.rate_limiter import limiter
from app.models.entities import Product, ProductStatus
from app.schemas.common import ProductOut, PaginationParams

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=dict)
@limiter.limit("60/minute")
async def list_products(
    request,                                    # нужен для limiter
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),       # ✅ Максимум 100 за раз
    category_id: int | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Список активных товаров с пагинацией"""
    
    # ✅ Только активные товары!
    query = select(Product).where(Product.status == ProductStatus.ACTIVE)
    count_query = select(func.count()).select_from(Product).where(
        Product.status == ProductStatus.ACTIVE
    )
    
    if category_id:
        query = query.where(Product.category_id == category_id)
        count_query = count_query.where(Product.category_id == category_id)
    
    # ✅ Пагинация
    query = query.offset(skip).limit(limit)
    
    result = await session.execute(query)
    total_result = await session.execute(count_query)
    
    products = result.scalars().all()
    total = total_result.scalar_one()
    
    return {
        "items": [ProductOut.model_validate(p) for p in products],
        "total": total,
        "skip": skip,
        "limit": limit,
    }