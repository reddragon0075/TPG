"""
TPG Backend Configuration

Loads settings from environment variables with sensible defaults.
All secrets MUST come from environment — never hardcoded.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """TPG application settings."""

    # ─── Application ───────────────────────────────────────────
    app_name: str = "TPG — The Product Guy"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # ─── Database ──────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/tpg",
        description="Async PostgreSQL connection string",
    )
    database_echo: bool = False

    # ─── OpenAI ────────────────────────────────────────────────
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key for GPT-4o reasoning",
    )
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # ─── Redis ─────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ─── Security ──────────────────────────────────────────────
    api_key: str = Field(
        default="",
        description="API key for authenticating ChatGPT Actions",
    )
    cors_origins: list[str] = ["https://chat.openai.com", "https://chatgpt.com"]

    # ─── Limits ────────────────────────────────────────────────
    max_memory_results: int = 50
    max_entity_name_length: int = 500
    embedding_dimensions: int = 1536

    model_config = {
        "env_file": ("backend/.env", ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
