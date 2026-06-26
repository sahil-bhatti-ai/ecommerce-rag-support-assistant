from functools import lru_cache
from pathlib import Path
from uuid import UUID

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="E-commerce GenAI Support Automation Assistant", alias="APP_NAME")
    environment: str = Field(default="local", alias="ENVIRONMENT")

    database_url: str = Field(
        default="postgresql+asyncpg://support:support@postgres:5432/support_assistant",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    qdrant_host: str = Field(default="qdrant", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")
    qdrant_collection: str = Field(default="ecommerce_support_chunks", alias="QDRANT_COLLECTION")

    upload_dir: Path = Field(default=Path("/app/storage/uploads"), alias="UPLOAD_DIR")
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5", alias="EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=384, alias="EMBEDDING_DIMENSION")

    chunk_size: int = Field(default=900, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=120, alias="CHUNK_OVERLAP")
    top_k: int = Field(default=5, alias="TOP_K")
    min_confidence: float = Field(default=0.45, alias="MIN_CONFIDENCE")

    demo_user_id: UUID = Field(
        default=UUID("11111111-1111-1111-1111-111111111111"),
        alias="DEMO_USER_ID",
    )

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    skip_startup_db: bool = Field(default=False, alias="SKIP_STARTUP_DB")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
