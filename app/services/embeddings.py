from functools import lru_cache

from fastembed import TextEmbedding

from app.core.config import get_settings


class EmbeddingService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = TextEmbedding(model_name=settings.embedding_model)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [embedding.tolist() for embedding in self.model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return next(self.model.query_embed(text)).tolist()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
