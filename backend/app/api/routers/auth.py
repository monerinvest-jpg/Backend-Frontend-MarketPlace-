from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import create_token, hash_password, verify_password
from app.models.entities import User
from app.schemas.auth import LoginIn, RegisterIn, TokenPair


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair)
async def register(payload: RegisterIn, session: AsyncSession = Depends(get_session)) -> TokenPair:
    exists = await session.execute(select(User).where(User.email == payload.email))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        referral_code=f"U{payload.email.split('@')[0][:6].upper()}",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return TokenPair(
        access_token=create_token(str(user.id), "access", 30),
        refresh_token=create_token(str(user.id), "refresh", 60 * 24 * 30),
    )


@router.post("/login", response_model=TokenPair)
async def login(payload: LoginIn, session: AsyncSession = Depends(get_session)) -> TokenPair:
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenPair(
        access_token=create_token(str(user.id), "access", 30),
        refresh_token=create_token(str(user.id), "refresh", 60 * 24 * 30),
    )
