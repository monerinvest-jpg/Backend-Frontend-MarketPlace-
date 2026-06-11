from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app_name: str = "Marketplace API"
    app_env: str = "development"
    
    # ✅ Раздельные секреты для access и refresh токенов
    # ⛔ БЫЛО: secret_key: str = Field(default="change-me")
    secret_key: str = Field(min_length=32)           # JWT access token secret
    refresh_secret_key: str = Field(min_length=32)   # JWT refresh token secret
    
    access_token_expire_minutes: int = 15    # ✅ Было 30, теперь 15
    refresh_token_expire_minutes: int = 10080  # ✅ 7 дней (было 30 дней!)

    # ✅ PostgreSQL (не MySQL!)
    database_url: str = Field(
        default="postgresql+asyncpg://user:pass@localhost:5432/marketplace_db"
    )
    
    # ✅ Не хранить отдельно host/port/user/pass — только URL из env
    db_pool_max: int = 20
    db_pool_min: int = 5

    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_refresh_token_ttl: int = 604800  # 7 дней в секундах

    # ✅ YooKassa и CDEK — только из env, НИКОГДА не в БД!
    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""
    yookassa_webhook_secret: str = ""    # ✅ Для верификации webhook

    cdek_client_id: str = ""
    cdek_client_secret: str = ""
    cdek_api_url: str = "https://api.cdek.ru/v2"

    frontend_url: str = "http://localhost:3000"
    allowed_origins: list[str] = ["http://localhost:3000"]

    bcrypt_rounds: int = 12
    max_file_size: int = 5 * 1024 * 1024  # 5MB
    
    # Rate limiting
    rate_limit_window_ms: int = 900000
    rate_limit_max_requests: int = 100
    auth_rate_limit_max: int = 5

    @field_validator("app_env")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v
    
    @field_validator("secret_key", "refresh_secret_key")
    @classmethod
    def validate_secrets(cls, v: str) -> str:
        if v in ("change-me", "secret", "password", ""):
            raise ValueError("Используйте криптографически стойкий секрет!")
        return v


settings = Settings()