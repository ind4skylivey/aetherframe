"""Application configuration and settings loader."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    environment: str = Field(default="development", env="ENVIRONMENT")

    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="aether", env="POSTGRES_USER")
    postgres_password: str = Field(default="changeme", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="aetherdb", env="POSTGRES_DB")

    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")

    minio_endpoint: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="changeme", env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="changeme", env="MINIO_SECRET_KEY")
    minio_use_ssl: bool = Field(default=False, env="MINIO_USE_SSL")
    minio_bucket: str = Field(default="aether-artifacts", env="MINIO_BUCKET")

    db_url: str | None = Field(default=None, validation_alias=AliasChoices("AETHERFRAME_DB_URL", "DB_URL"))
    api_host: str = Field(default="0.0.0.0", env="AETHERFRAME_API_HOST")
    api_port: int = Field(default=8000, env="AETHERFRAME_API_PORT")

    worker_concurrency: int = Field(default=2, env="AETHERFRAME_WORKER_CONCURRENCY")

    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"],
        env="AETHERFRAME_CORS_ORIGINS",
    )

    license_enforce: bool = Field(default=False, env="AETHERFRAME_LICENSE_ENFORCE")


@lru_cache()
def get_settings() -> Settings:
    """Cached settings loader."""
    return Settings()
