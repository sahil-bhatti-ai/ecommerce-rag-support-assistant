from uuid import UUID

from app.core.config import get_settings


def get_current_user_id() -> UUID:
    """Demo user dependency.

    Real systems should replace this with JWT/session authentication. This project
    keeps auth intentionally tiny so the backend/RAG architecture remains visible.
    """
    return get_settings().demo_user_id
