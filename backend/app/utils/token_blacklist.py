import redis.asyncio as aioredis
from app.core.config import settings


class TokenBlacklist:
    """Redis-based управление JWT токенами"""
    
    def __init__(self) -> None:
        self._redis = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

    # ─── Refresh Tokens ───────────────────────────────────────
    
    async def store_refresh_token(self, user_id: str, token: str) -> None:
        """Сохранить refresh token пользователя в Redis с TTL"""
        await self._redis.setex(
            f"refresh:{user_id}",
            settings.redis_refresh_token_ttl,   # 7 дней
            token,
        )

    async def get_refresh_token(self, user_id: str) -> str | None:
        """Получить текущий refresh token пользователя"""
        return await self._redis.get(f"refresh:{user_id}")

    async def revoke_refresh_token(self, user_id: str) -> None:
        """Отозвать refresh token (при logout или ротации)"""
        await self._redis.delete(f"refresh:{user_id}")

    # ─── Access Token Blacklist ───────────────────────────────
    
    async def revoke_access_token(self, jti: str, ttl_seconds: int = 900) -> None:
        """Добавить access token в blacklist до истечения его срока (15 мин)"""
        await self._redis.setex(
            f"blacklist:{jti}",
            ttl_seconds,   # TTL = оставшееся время жизни access token
            "revoked",
        )

    async def is_access_token_revoked(self, jti: str) -> bool:
        """Проверить находится ли токен в blacklist"""
        return await self._redis.exists(f"blacklist:{jti}") > 0
    
    async def close(self) -> None:
        await self._redis.aclose()