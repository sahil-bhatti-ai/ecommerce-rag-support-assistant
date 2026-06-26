from fastapi import APIRouter
from qdrant_client import QdrantClient
from redis import Redis
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    settings = get_settings()
    checks: dict[str, str] = {"api": "ok"}

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # pragma: no cover - depends on local infra
        checks["database"] = f"error: {exc.__class__.__name__}"

    try:
        redis = Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)
        redis.ping()
        checks["redis"] = "ok"
    except Exception as exc:  # pragma: no cover - depends on local infra
        checks["redis"] = f"error: {exc.__class__.__name__}"

    try:
        client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port, timeout=1)
        client.get_collections()
        checks["qdrant"] = "ok"
    except Exception as exc:  # pragma: no cover - depends on local infra
        checks["qdrant"] = f"error: {exc.__class__.__name__}"

    status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
    return {"status": status, **checks}
