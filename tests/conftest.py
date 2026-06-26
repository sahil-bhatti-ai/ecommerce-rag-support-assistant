import os

os.environ.setdefault("SKIP_STARTUP_DB", "true")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://support:support@localhost:5433/support_assistant")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("QDRANT_HOST", "localhost")
