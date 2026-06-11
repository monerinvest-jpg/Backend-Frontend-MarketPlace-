from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CraftBridge API"
    app_env: str = "development"
    secret_key: str = Field(default="change-me", min_length=8)
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 30

    mysql_host: str = "mysql"
    mysql_port: int = 3306
    mysql_user: str = "market"
    mysql_password: str = "market"
    mysql_database: str = "marketplace"

    redis_url: str = "redis://redis:6379/0"

    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""
    yookassa_webhook_secret: str = ""

    cdek_client_id: str = ""
    cdek_client_secret: str = ""

    frontend_url: str = "http://localhost:3000"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+asyncmy://{self.mysql_user}:{self.mysql_password}@"
            f"{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


settings = Settings()
