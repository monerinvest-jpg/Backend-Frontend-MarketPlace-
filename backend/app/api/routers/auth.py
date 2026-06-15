# backend/app/api/routers/auth.py — ПОЛНАЯ РЕАЛИЗАЦИЯ register()

import secrets
import string
import time
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from app.core.db import get_session
from app.core.rate_limiter import limiter
from app.core.security import (
    create_access_token, create_refresh_token,
    decode_token, hash_password, verify_password,
)
from app.models.entities import Referral, ReferralType, RoleEnum, User
from app.schemas.auth import LoginIn, RegisterIn, TokenPair, UserOut
from app.utils.token_blacklist import TokenBlacklist
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def generate_referral_code() -> str:
    """Криптографически стойкий referral code"""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(10))


@router.post("/register", response_model=TokenPair, status_code=201)
@limiter.limit("5/minute")
async def register(
    request: Request,
    payload: RegisterIn,
    session: AsyncSession = Depends(get_session),
) -> TokenPair:
    # 1. Проверка дубликата email
    existing = await session.execute(
        select(User).where(User.email == payload.email.lower().strip())
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email уже зарегистрирован")

    # 2. Генерация уникального referral_code (с защитой от коллизий)
    for _ in range(10):
        code = generate_referral_code()
        exists = await session.execute(
            select(User).where(User.referral_code == code)
        )
        if not exists.scalar_one_or_none():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate referral code")

    # 3. Обработка реферального кода приглашателя
    referrer: User | None = None
    if getattr(payload, "referral_code", None):
        res = await session.execute(
            select(User).where(User.referral_code == payload.referral_code)
        )
        referrer = res.scalar_one_or_none()

    # 4. Создание пользователя
    user = User(
        email=payload.email.lower().strip(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role=RoleEnum.BUYER,
        referral_code=code,
    )
    session.add(user)
    await session.flush()  # получаем user.id

    # 5. Создание реферальной связи если есть приглашатель
    if referrer:
        session.add(Referral(
            referrer_id=referrer.id,
            referred_user_id=user.id,
            type=ReferralType.BUYER,
            code=payload.referral_code,
        ))

    # 6. Генерация токенов
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    # 7. Сохранить refresh token в Redis
    blacklist = TokenBlacklist()
    await blacklist.store_refresh_token(str(user.id), refresh_token)

    await session.commit()
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenPair)
@limiter.limit("5/minute")
async def login(
    request: Request,
    payload: LoginIn,
    session: AsyncSession = Depends(get_session),
) -> TokenPair:
    result = await session.execute(
        select(User).where(User.email == payload.email.lower().strip())
    )
    user = result.scalar_one_or_none()

    # ✅ Одинаковое сообщение — не раскрываем существование email
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт заблокирован")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    blacklist = TokenBlacklist()
    await blacklist.store_refresh_token(str(user.id), refresh_token)

    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
async def logout(
    user: User = Depends(get_current_user),
    raw_token: str = Depends(oauth2_scheme),
) -> dict:
    blacklist = TokenBlacklist()
    try:
        payload = decode_token(raw_token, token_type="access")
        jti = payload.get("jti", "")
        exp = payload.get("exp", 0)
        remaining_ttl = max(0, int(exp - time.time()))
        if jti:
            await blacklist.revoke_access_token(jti, ttl_seconds=remaining_ttl)
    except Exception:
        pass
    await blacklist.revoke_refresh_token(str(user.id))
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: dict,
    session: AsyncSession = Depends(get_session),
) -> TokenPair:
    """Обновление токена с ротацией"""
    token = payload.get("refresh_token", "")
    try:
        decoded = decode_token(token, token_type="refresh")
        user_id = decoded.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    blacklist = TokenBlacklist()
    stored = await blacklist.get_refresh_token(user_id)
    if not stored or stored != token:
        raise HTTPException(status_code=401, detail="Refresh token revoked or invalid")

    # ✅ Ротация: немедленно удалить старый
    await blacklist.revoke_refresh_token(user_id)

    new_access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id)
    await blacklist.store_refresh_token(user_id, new_refresh)

    return TokenPair(access_token=new_access, refresh_token=new_refresh)


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)) -> User:
    return user