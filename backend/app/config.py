"""All runtime settings, read once from the environment (see .env.example)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://rag:rag@localhost:5432/rag"
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"

    # Embeddings run locally; the model is baked into the image at this path.
    embed_model: str = "BAAI/bge-small-en-v1.5"
    embed_dim: int = 384
    embed_threads: int = 2
    embed_batch_size: int = 32
    fastembed_cache_path: str = "/opt/models"

    # Ingestion limits and worker behaviour.
    max_upload_mb: int = 25
    max_pages: int = 600
    chunk_tokens: int = 350
    chunk_overlap_tokens: int = 50
    worker_poll_seconds: float = 2.0
    lease_seconds: int = 300
    max_attempts: int = 3


@lru_cache
def get_settings() -> Settings:
    return Settings()
