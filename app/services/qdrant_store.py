from dataclasses import dataclass
from uuid import uuid4

from qdrant_client import QdrantClient, models

from app.core.config import get_settings
from app.services.embeddings import get_embedding_service


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: str
    filename: str
    chunk_index: int
    text: str
    score: float


class QdrantVectorStore:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = QdrantClient(host=self.settings.qdrant_host, port=self.settings.qdrant_port)
        self.embeddings = get_embedding_service()

    def ensure_collection(self) -> None:
        collections = self.client.get_collections().collections
        existing = {collection.name for collection in collections}
        if self.settings.qdrant_collection not in existing:
            self.client.create_collection(
                collection_name=self.settings.qdrant_collection,
                vectors_config=models.VectorParams(
                    size=self.settings.embedding_dimension,
                    distance=models.Distance.COSINE,
                ),
            )

    def upsert_chunks(self, *, document_id: str, filename: str, chunks: list[str]) -> None:
        self.ensure_collection()
        vectors = self.embeddings.embed_documents(chunks)
        points = []
        for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
            points.append(
                models.PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload={
                        "document_id": document_id,
                        "filename": filename,
                        "chunk_index": index,
                        "text": chunk,
                    },
                )
            )
        if points:
            self.client.upsert(collection_name=self.settings.qdrant_collection, points=points)

    def search(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        self.ensure_collection()
        limit = top_k or self.settings.top_k
        query_vector = self.embeddings.embed_query(query)

        # qdrant-client has evolved over versions. Support both APIs so the project
        # is less brittle than the average tutorial fossil.
        if hasattr(self.client, "query_points"):
            response = self.client.query_points(
                collection_name=self.settings.qdrant_collection,
                query=query_vector,
                limit=limit,
                with_payload=True,
            )
            points = response.points
        else:  # pragma: no cover - older qdrant-client fallback
            points = self.client.search(
                collection_name=self.settings.qdrant_collection,
                query_vector=query_vector,
                limit=limit,
                with_payload=True,
            )

        chunks: list[RetrievedChunk] = []
        for point in points:
            payload = point.payload or {}
            chunks.append(
                RetrievedChunk(
                    document_id=str(payload.get("document_id", "unknown")),
                    filename=str(payload.get("filename", "unknown")),
                    chunk_index=int(payload.get("chunk_index", 0)),
                    text=str(payload.get("text", "")),
                    score=float(point.score or 0.0),
                )
            )
        return chunks
