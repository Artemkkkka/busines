from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Business Management"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "CHANGE_ME"
    CORS_ORIGINS: List[str] = ["*"]

    POSTGRES_USER: str = "app"
    POSTGRES_PASSWORD: str = "app_pass"
    POSTGRES_DB: str = "app_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
