from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExpenseTrackerSettings(BaseSettings):
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/pricegenius",
        alias="DATABASE_URL",
    )
    jwt_secret_key: str = Field(default="change-me-in-production", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    storage_backend: str = Field(default="local", alias="STORAGE_BACKEND")
    local_storage_path: str = Field(default="storage", alias="LOCAL_STORAGE_PATH")
    s3_endpoint_url: str | None = Field(default=None, alias="S3_ENDPOINT_URL")
    s3_bucket_name: str | None = Field(default=None, alias="S3_BUCKET_NAME")
    s3_access_key_id: str | None = Field(default=None, alias="S3_ACCESS_KEY_ID")
    s3_secret_access_key: str | None = Field(default=None, alias="S3_SECRET_ACCESS_KEY")
    email_provider: str = Field(default="noop", alias="EMAIL_PROVIDER")
    app_base_url: str = Field(default="http://localhost:8000", alias="APP_BASE_URL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> ExpenseTrackerSettings:
    return ExpenseTrackerSettings()
