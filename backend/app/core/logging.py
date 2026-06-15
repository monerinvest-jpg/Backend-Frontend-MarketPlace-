import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.config import settings

SENSITIVE_FIELDS = {"password", "token", "secret", "authorization", "cookie"}

class SanitizingFilter(logging.Filter):
    """Убирает чувствительные данные из логов"""
    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, 'msg') and isinstance(record.msg, dict):
            for key in SENSITIVE_FIELDS:
                if key in record.msg:
                    record.msg[key] = "***"
        return True

def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)

    if settings.app_env == "production":
        # ✅ JSON-формат для ELK/Grafana
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
    else:
        # Dev: читаемый формат
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

    handler.setFormatter(formatter)
    handler.addFilter(SanitizingFilter())

    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO if settings.app_env == "production" else logging.DEBUG)