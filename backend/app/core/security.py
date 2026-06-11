import uuid
from datetime import datetime, timedelta, timezone

import jwt                                              # ✅ PyJWT, не python-jose!
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    """✅ Создаёт access token с коротким TTL (15 мин)"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": "access",                               # ✅ Обязательное поле type
        "jti": str(uuid.uuid4()),                       # ✅ JWT ID для blacklist
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()),
    }
    # ✅ Используем settings.secret_key — только для access!
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """✅ Создаёт refresh token с TTL 7 дней (было 30!)"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": "refresh",                              # ✅ Тип = refresh
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.refresh_token_expire_minutes)).timestamp()),
    }
    # ✅ ОТДЕЛЬНЫЙ секрет для refresh! Не settings.secret_key!
    return jwt.encode(payload, settings.refresh_secret_key, algorithm=ALGORITHM)


def decode_token(token: str, token_type: str = "access") -> dict:
    """✅ Декодирует токен с проверкой типа"""
    # ✅ Выбираем секрет в зависимости от типа токена
    secret = (
        settings.secret_key if token_type == "access" 
        else settings.refresh_secret_key
    )
    
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    
    # ✅ Проверяем тип токена (защита от token substitution attack)
    if payload.get("type") != token_type:
        raise ValueError(f"Expected {token_type} token, got {payload.get('type')}")
    
    return payload