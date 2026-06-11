from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.entities import Referral, User


router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.get("/me")
async def my_referrals(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> list[Referral]:
    result = await session.execute(select(Referral).where(Referral.referrer_id == user.id))
    return list(result.scalars().all())
