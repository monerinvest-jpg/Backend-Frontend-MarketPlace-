# backend/app/core/db.py — ИСПРАВЛЕННАЯ ВЕРСИЯ

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine
)
from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    # ✅ Пинг перед выдачей соединения из пула
    pool_pre_ping=True,
    # ✅ Настройка пула
    pool_size=settings.db_pool_min,          # минимум соединений (5)
    max_overflow=settings.db_pool_max - settings.db_pool_min,  # доп. соединения
    pool_timeout=30,                          # ждать соединение 30 сек
    pool_recycle=3600,                        # переоткрывать соединения каждый час
    # ✅ Эхо только в development
    echo=settings.app_env == "development",
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,        # ✅ Явное управление flush
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()    # ✅ Авто-коммит при успехе
        except Exception:
            await session.rollback()  # ✅ Авто-откат при ошибке
            raise