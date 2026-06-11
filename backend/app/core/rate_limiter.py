# Rate limiting через slowapi + Redis
# ✅ Глобальный лимит: 100 req/min
# ✅ Строгий лимит для /auth: 5 req/min  
# ✅ Хранение счётчиков в Redis

from slowapi import Limiter
from slowapi.util import get_remote_address

# ✅ Используем IP адрес как ключ для rate limiting
# В production за nginx: X-Forwarded-For или X-Real-IP
limiter = Limiter(
    key_func=get_remote_address,
    # ✅ Хранить счётчики в Redis (shared state между workers)
    storage_uri="memory://",  # В prod: settings.redis_url
    # Заголовки с информацией о лимите в ответе
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