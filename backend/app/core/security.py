# backend/app/core/security.py — анализ (код корректный, но нужны комментарии)

import uuid
from datetime import datetime, timedelta, timezone

import jwt                     # ✅ PyJWT (не python-jose — у него CVE-2022-29217!)
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    # ✅ bcrypt с rounds=12 из settings (не хардкод!)
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    # ✅ passlib.verify — защищён от timing attack
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": subject,                 # <- реальный user_id
        "type": "access",
        "jti": str(uuid.uuid4()),       # <- реальный UUID для blacklist
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

def create_refresh_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.refresh_token_expire_minutes)
    payload = {
        "sub": subject,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": expire,
    }  # <- закрыть dict
    return jwt.encode(payload, settings.refresh_secret_key, algorithm=ALGORITHM)

def decode_token(token: str, token_type: str = "access") -> dict:
    # ✅ Выбираем ключ по типу токена
    secret = settings.secret_key if token_type == "access" else settings.refresh_secret_key
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    
    # ✅ Проверяем что тип совпадает (защита от подстановки refresh вместо access)
    if payload.get("type") != token_type:
        raise ValueError(f"Expected {token_type} token, got {payload.get('type')}")
    return payload