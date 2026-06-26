import asyncio
from uuid import UUID

from app.db.session import AsyncSessionLocal
from app.models.document import Document, DocumentStatus
from app.services.chunking import split_text_into_chunks
from app.services.document_loader import load_document_text
from app.services.qdrant_store import QdrantVectorStore
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="index_document_task")
def index_document_task(self, document_id: str) -> dict:
    return asyncio.run(_index_document_async(document_id=document_id))


async def _index_document_async(document_id: str) -> dict:
    async with AsyncSessionLocal() as db:
        document = await db.get(Document, UUID(document_id))
        if document is None:
            return {"status": "failed", "reason": "document_not_found"}

        try:
            document.status = DocumentStatus.indexing
            document.error_message = None
            await db.commit()

            text = load_document_text(document.storage_path)
            if not text.strip():
                raise ValueError("No extractable text found in document.")

            docs = split_text_into_chunks(
                text,
                metadata={"document_id": str(document.id), "filename": document.filename},
            )
            chunks = [doc.page_content for doc in docs]

            vector_store = QdrantVectorStore()
            vector_store.upsert_chunks(
                document_id=str(document.id),
                filename=document.filename,
                chunks=chunks,
            )

            document.status = DocumentStatus.indexed
            document.chunk_count = len(chunks)
            document.error_message = None
            await db.commit()
            return {"status": "indexed", "document_id": document_id, "chunks": len(chunks)}

        except Exception as exc:
            document.status = DocumentStatus.failed
            document.error_message = f"{exc.__class__.__name__}: {exc}"
            await db.commit()
            return {"status": "failed", "document_id": document_id, "error": document.error_message}
