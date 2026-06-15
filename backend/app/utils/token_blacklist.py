# backend/app/utils/token_blacklist.py — SINGLETON Redis клиент

import redis.asyncio as aioredis
from app.core.config import settings

# ✅ Singleton на уровне модуля — один пул соединений для всего приложения
_redis_pool: aioredis.Redis | None = None


async def get_redis_client() -> aioredis.Redis:
    """Получить или создать singleton Redis-клиент с пулом соединений"""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,    # ✅ Пул до 20 соединений
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
    return _redis_pool


async def close_redis_client() -> None:
    """Закрыть пул при shutdown приложения"""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None


class TokenBlacklist:
    """Redis-based управление JWT токенами (использует общий пул)"""

    async def _r(self) -> aioredis.Redis:
        return await get_redis_client()   # ✅ Переиспользует singleton!

    # ─── Refresh Tokens ─────────────────────────────────────────────

    async def store_refresh_token(self, user_id: str, token: str) -> None:
        r = await self._r()
        await r.setex(
            f"refresh:{user_id}",
            settings.redis_refresh_token_ttl,   # 7 дней
            token,
        )

    async def get_refresh_token(self, user_id: str) -> str | None:
        r = await self._r()
        return await r.get(f"refresh:{user_id}")

    async def revoke_refresh_token(self, user_id: str) -> None:
        r = await self._r()
        await r.delete(f"refresh:{user_id}")

    # ─── Access Token Blacklist ──────────────────────────────────────

    async def revoke_access_token(self, jti: str, ttl_seconds: int = 900) -> None:
        """Добавить access token в blacklist до истечения срока"""
        r = await self._r()
        await r.setex(f"blacklist:{jti}", ttl_seconds, "revoked")

    async def is_access_token_revoked(self, jti: str) -> bool:
        """Проверить находится ли токен в blacklist"""
        r = await self._r()
        return await r.exists(f"blacklist:{jti}") > 0


# ─── В backend/app/main.py добавить в lifespan: ─────────────────────
# from app.utils.token_blacklist import close_redis_client
#
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await _seed_settings()
#     yield
#     await close_redis_client()   # ✅ Закрываем пул при shutdown