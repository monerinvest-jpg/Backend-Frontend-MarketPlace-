from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.core.security import decode_token
from app.models.entities import User
from app.utils.token_blacklist import TokenBlacklist


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        # ✅ Проверяем type == "access" (защита от token substitution)
        # ⛔ БЫЛО: jwt.decode(token, settings.secret_key, ...) без проверки type
        payload = decode_token(token, token_type="access")
        user_id = int(payload.get("sub", 0))
        jti = payload.get("jti", "")
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # ✅ Проверяем что токен не в blacklist (logout)
    blacklist = TokenBlacklist()
    if await blacklist.is_access_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # ✅ Проверяем что аккаунт активен
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in {"superadmin", "moderator"}:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


async def require_seller(user: User = Depends(get_current_user)) -> User:
    """✅ Новая зависимость для продавцов"""
    if user.role not in {"seller", "superadmin"}:
        raise HTTPException(status_code=403, detail="Seller role required")
    return user