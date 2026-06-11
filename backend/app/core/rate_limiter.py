# Rate limiting через slowapi + Redis
# ✅ Глобальный лимит: 100 req/min
# ✅ Строгий лимит для /auth: 5 req/min  
# ✅ Хранение счётчиков в Redis

from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    # ✅ ИСПРАВЛЕНО: Redis — shared state между всеми воркерами
    storage_uri=settings.redis_url,   # ⛔ БЫЛО: "memory://"
    headers_enabled=True,
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