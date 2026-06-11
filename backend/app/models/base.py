from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """✅ Миксин с временными метками для всех моделей"""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # ✅ ДОБАВЛЕНО: updated_at — обновляется автоматически при изменении
    # ⛔ БЫЛО: только created_at
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),           # ✅ Автообновление при UPDATE
        nullable=False,
    )