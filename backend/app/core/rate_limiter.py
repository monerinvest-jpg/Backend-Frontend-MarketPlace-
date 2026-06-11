from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings
import logging
 
logger = logging.getLogger(__name__)
 
def _get_storage_uri() -> str:
    """Проверяем доступность Redis, иначе — критическая ошибка в production"""
    if not settings.redis_url:
        if settings.app_env == "production":
            raise RuntimeError(
                "REDIS_URL обязателен в production для distributed rate limiting!"
            )
        logger.warning("Redis не настроен, rate limiter использует memory://")
        return "memory://"
    return settings.redis_url
 
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_get_storage_uri(),
    headers_enabled=True,
    # ✅ Дополнительные заголовки: X-RateLimit-Limit, X-RateLimit-Remaining
    strategy="fixed-window",
)

# Использование в роутерах:
#
# @router.post("/login")
# @limiter.limit("5/minute")           # 5 попыток в минуту
# async def login(request: Request, ...):
#     ...
#
# @router.post("/register")
# @limiter.limit("5/minute")
# async def register(request: Request, ...):
#     ...
#
# @router.get("/products")
# @limiter.limit("60/minute")          # Менее строгий лимит
# async def list_products(request: Request, ...):
#     ...