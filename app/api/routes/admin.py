from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.document import Document, DocumentStatus
from app.schemas.documents import DocumentRead, IndexingJobRead
from app.workers.tasks import index_document_task

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/documents", response_model=list[DocumentRead])
async def list_documents(db: AsyncSession = Depends(get_db)) -> list[DocumentRead]:
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return list(result.scalars().all())


@router.get("/indexing-jobs", response_model=list[IndexingJobRead])
async def list_indexing_jobs(db: AsyncSession = Depends(get_db)) -> list[IndexingJobRead]:
    result = await db.execute(
        select(Document)
        .where(Document.status.in_([DocumentStatus.uploaded, DocumentStatus.indexing, DocumentStatus.failed]))
        .order_by(Document.updated_at.desc())
    )
    docs = result.scalars().all()
    return [
        IndexingJobRead(
            document_id=doc.id,
            filename=doc.filename,
            status=doc.status,
            celery_task_id=doc.celery_task_id,
            chunk_count=doc.chunk_count,
            error_message=doc.error_message,
            updated_at=doc.updated_at,
        )
        for doc in docs
    ]


@router.post("/documents/{document_id}/reindex", response_model=DocumentRead, status_code=status.HTTP_202_ACCEPTED)
async def reindex_document(document_id: UUID, db: AsyncSession = Depends(get_db)) -> DocumentRead:
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    document.status = DocumentStatus.indexing
    document.error_message = None
    document.chunk_count = 0
    async_result = index_document_task.delay(str(document.id))
    document.celery_task_id = async_result.id
    await db.commit()
    await db.refresh(document)
    return document
