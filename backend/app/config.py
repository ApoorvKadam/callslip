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

    # Answering. The same model and settings serve the agent and the single-pass baseline.
    anthropic_api_key: str = ""
    # Haiku 5.5 passed more evaluation runs than Sonnet 5.5 at about a tenth of the cost
    # (docs/evaluation.md); set ANSWER_MODEL=claude-sonnet-5-5 to use Sonnet instead.
    answer_model: str = "claude-haiku-5-5"
    answer_effort: str = "medium"
    top_k: int = 8
    history_turns: int = 3

    # Execution limits for one run (one question).
    run_deadline_s: float = 90.0
    finalize_reserve_s: float = 20.0
    llm_timeout_s: float = 60.0
    max_model_turns: int = 10
    max_tool_calls: int = 9
    tool_timeout_s: float = 8.0
    # Lets the evaluation inject tool failures. Off unless explicitly enabled.
    allow_fault_injection: bool = False
    # Send the session cookie only over HTTPS. Off for the local stack on plain HTTP; on behind TLS.
    cookie_secure: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
