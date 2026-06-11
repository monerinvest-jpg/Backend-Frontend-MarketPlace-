import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import select

from app.api.router import api_router
from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.core.rate_limiter import limiter
from app.models.entities import Settings
import secure
from fastapi import Request
from fastapi.responses import Response

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при старте приложения"""
    await _seed_settings()
    logger.info("Application started")
    yield
    logger.info("Application shutdown")


async def _seed_settings() -> None:
    """✅ ИСПРАВЛЕНО: секреты YooKassa и CDEK НЕ записываются в БД!
    В БД только бизнес-настройки, которые можно изменять через /admin/settings"""
    defaults = {
        "global_commission_percent": "10",
        "referral_buyer_bonus_amount": "300",
        "referral_buyer_min_order_amount": "2500",
        "referral_seller_bonus_amount": "1500",
        "referral_bonus_max_discount_percent": "30",
        "enable_premoderation": "true",
        # ⛔ БЫЛО: yookassa_secret_key, cdek_client_secret — УБРАНЫ!
        # Читаем из settings напрямую при использовании, не храним в БД
    }
    async with AsyncSessionLocal() as session:
        for key, value in defaults.items():
            existing = await session.execute(
                select(Settings).where(Settings.key == key)
            )
            if not existing.scalar_one_or_none():
                session.add(Settings(key=key, value=value))
        await session.commit()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    # ✅ В production скрываем документацию
    docs_url="/api/docs" if settings.app_env != "production" else None,
    redoc_url="/api/redoc" if settings.app_env != "production" else None,
    # ✅ Не показываем стектрейсы в production
    debug=settings.app_env == "development",
)

# ✅ Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ✅ CORS: только разрешённые origins из конфига
# ⛔ БЫЛО: [settings.frontend_url, "http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,     # Из env переменной
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],  # Не ["*"]!
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    max_age=3600,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """✅ В production не раскрываем детали ошибки"""
    logger.exception(f"Unhandled exception: {exc}")
    if settings.app_env == "production":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
    # В development — полные детали
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


app.include_router(api_router)


@app.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok", "env": settings.app_env}

security_headers = secure.Secure(
    server=secure.Server().set(""),           # Скрыть Server header
    hsts=secure.StrictTransportSecurity()
        .max_age(31536000)
        .include_subdomains()
        .preload(),
    xfo=secure.XFrameOptions().deny(),
    content=secure.XContentTypeOptions(),
    referrer=secure.ReferrerPolicy().strict_origin_when_cross_origin(),
    permissions=secure.PermissionsPolicy(
        geolocation="()",
        microphone="()",
        camera="()",
    ),
    csp=secure.ContentSecurityPolicy()
        .default_src("'self'")
        .script_src("'self'")
        .style_src("'self'")
        .img_src("'self'", "data:")
        .connect_src("'self'"),
)

# ─── Middleware ──────────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    # ✅ Применяем security headers ко всем ответам
    await security_headers.set_headers_async(response)
    # ✅ Добавляем Request ID для трассировки
    response.headers["X-Request-ID"] = request.headers.get(
        "X-Request-ID", str(uuid.uuid4())[:8]
    )
    return response