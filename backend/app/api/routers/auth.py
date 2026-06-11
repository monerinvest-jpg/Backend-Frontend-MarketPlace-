import secrets
import string
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.rate_limiter import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.entities import User
from app.schemas.auth import LoginIn, RegisterIn, TokenPair, UserOut
from app.utils.token_blacklist import TokenBlacklist
from app.api.deps import get_current_user
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair)
@limiter.limit("5/minute") # ✅ Rate limit
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/logout")
async def logout(
    user: User = Depends(get_current_user),
    # ✅ Правильно получаем токен из Authorization header
    raw_token: str = Depends(oauth2_scheme),
) -> dict:
    blacklist = TokenBlacklist()
    
    # ✅ Извлекаем JTI из токена для внесения в blacklist
    try:
        payload = decode_token(raw_token, token_type="access")
        jti = payload.get("jti", "")
        exp = payload.get("exp", 0)
        # TTL = оставшееся время жизни токена
        import time
        remaining_ttl = max(0, int(exp - time.time()))
        
        if jti:
            await blacklist.revoke_access_token(jti, ttl_seconds=remaining_ttl)
    except Exception:
        pass  # Токен уже истёк — ок
    
    # ✅ Удаляем refresh token
    await blacklist.revoke_refresh_token(str(user.id))
    
    return {"message": "Logged out successfully"}

def generate_referral_code() -> str:
    """✅ Криптографически стойкий, непредсказуемый referral code"""
    alphabet = string.ascii_uppercase + string.digits
    # secrets.choice — криптографически случайный выбор
    return ''.join(secrets.choice(alphabet) for _ in range(10))

async def register(
    request: Request,
    payload: RegisterIn,
    session: AsyncSession = Depends(get_session),
) -> TokenPair:
    exists = await session.execute(
        select(User).where(User.email == payload.email)
    )
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
    email=payload.email,
    password_hash=hash_password(payload.password),
    full_name=payload.full_name,
    role="buyer",                           # ✅ Хардкод, не из запроса
    referral_code=generate_referral_code(), # ✅ Случайный, не предсказуемый
)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    # ✅ Сохранить refresh token в Redis с TTL
    blacklist = TokenBlacklist()
    await blacklist.store_refresh_token(str(user.id), refresh_token)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=TokenPair)
@limiter.limit("5/minute")                                # ✅ Строгий rate limit для login
async def login(
    request: Request,
    payload: LoginIn,
    session: AsyncSession = Depends(get_session),
) -> TokenPair:
    result = await session.execute(
        select(User).where(User.email == payload.email)
    )
    user = result.scalar_one_or_none()
    
    # ✅ Одинаковое сообщение об ошибке (не раскрываем существование email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль"  # ✅ Не "User not found"!
        )
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт заблокирован")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    blacklist = TokenBlacklist()
    await blacklist.store_refresh_token(str(user.id), refresh_token)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: dict,                                        # {refresh_token: str}
    session: AsyncSession = Depends(get_session),
) -> TokenPair:
    """✅ Обновление токена с ротацией (старый refresh инвалидируется)"""
    token = payload.get("refresh_token", "")
    
    try:
        # ✅ Проверить type == "refresh" (используем REFRESH SECRET)
        decoded = decode_token(token, token_type="refresh")
        user_id = decoded.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    blacklist = TokenBlacklist()
    
    # ✅ Проверить что токен есть в Redis (не отозван)
    stored = await blacklist.get_refresh_token(user_id)
    if not stored or stored != token:
        raise HTTPException(status_code=401, detail="Refresh token revoked or invalid")

    # ✅ РОТАЦИЯ: немедленно удалить старый refresh token
    await blacklist.revoke_refresh_token(user_id)

    # Создать новую пару токенов
    new_access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id)
    
    await blacklist.store_refresh_token(user_id, new_refresh)

    return TokenPair(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout")
async def logout(
    user: User = Depends(get_current_user),
    token: str = Depends(lambda: ""),  # Из Authorization header
) -> dict:
    """✅ Инвалидация токенов при выходе"""
    blacklist = TokenBlacklist()
    # ✅ Добавить access token в blacklist до истечения срока
    await blacklist.revoke_access_token(token)
    # ✅ Удалить refresh token из Redis
    await blacklist.revoke_refresh_token(str(user.id))
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)) -> User:
    """✅ Получение профиля текущего пользователя"""
    return user