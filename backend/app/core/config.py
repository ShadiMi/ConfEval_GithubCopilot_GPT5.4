from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ConfEval API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14
    database_url: str = "postgresql+psycopg://confeval:confeval@localhost:5432/confeval"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    google_client_id: str = ""
    google_client_secret: str = ""
    object_storage_endpoint: str = "http://localhost:9000"
    object_storage_bucket: str = "confeval"
    object_storage_access_key: str = "minioadmin"
    object_storage_secret_key: str = "minioadmin"
    local_upload_dir: str = str(Path(__file__).resolve().parents[2] / "uploads")
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
