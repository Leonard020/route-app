from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "local"
    DATABASE_URL: str = "postgresql+asyncpg://app:app@db:5432/route"
    SQL_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    JWT_SECRET: str = "change-me"
    ACCESS_TOKEN_TTL: int = 3600
    REFRESH_TOKEN_TTL: int = 60 * 60 * 24 * 30

    CORS_ORIGINS: list[str] = ["*"]

    REDIS_URL: str = "redis://redis:6379/0"

    ML_ENABLED: bool = False
    ML_BASE_URL: str = "http://ml:8100"
    ML_API_KEY: str = "dev-ml-key"


settings = Settings()