from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.models.entities import Product


router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def list_products(session: AsyncSession = Depends(get_session)) -> list[Product]:
    result = await session.execute(select(Product))
    return list(result.scalars().all())
