# backend/app/api/deps.py — ИСПРАВЛЕНИЕ role check

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import decode_token
from app.models.entities import RoleEnum, User   # ✅ Импортируем RoleEnum
from app.utils.token_blacklist import TokenBlacklist

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        payload = decode_token(token, token_type="access")
        user_id = int(payload.get("sub", 0))
        jti = payload.get("jti", "")
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # ✅ Проверяем blacklist
    blacklist = TokenBlacklist()
    if await blacklist.is_access_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    # ✅ Enum-сравнение, не строки
    if user.role not in {RoleEnum.SUPERADMIN, RoleEnum.MODERATOR}:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


async def require_seller(user: User = Depends(get_current_user)) -> User:
    # ✅ Enum-сравнение
    if user.role not in {RoleEnum.SELLER, RoleEnum.SUPERADMIN}:
        raise HTTPException(status_code=403, detail="Seller role required")
    return user