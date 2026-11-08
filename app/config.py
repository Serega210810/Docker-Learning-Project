from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://app:app@db:5432/shortener"
    redis_url: str = "redis://redis:6379/0"
    base_url: str = "http://localhost:8000"
    short_code_length: int = 6

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()