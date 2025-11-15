from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str

    # APIs
    openrouter_api_key: str
    gh_token: str

    # App
    environment: str = "development"
    log_level: str = "INFO"

    # Embedding
    embedding_model: str = "qwen/qwen3-embedding-4b"
    embedding_dimensions: int = 2560


@lru_cache()
def get_settings():
    return Settings()


