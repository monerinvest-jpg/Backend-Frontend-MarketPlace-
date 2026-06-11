from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.referrals import ReferralOut
from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.entities import Referral, User
from pydantic import BaseModel
from decimal import Decimal
 
class ReferralOut(BaseModel):
    id: int
    referred_user_id: int
    type: str
    code: str
    reward_paid: bool
    model_config = {"from_attributes": True}


router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.get("/me", response_model=list[ReferralOut])  # ✅ response_model
async def my_referrals(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ReferralOut]:
    result = await session.execute(
        select(Referral).where(Referral.referrer_id == user.id)
    )
    return [ReferralOut.model_validate(r) for r in result.scalars().all()]
