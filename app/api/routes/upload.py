from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.models.document import Document, DocumentStatus
from app.schemas.documents import DocumentUploadResponse
from app.utils.file_storage import save_upload_file, validate_upload_extension
from app.workers.tasks import index_document_task

router = APIRouter(tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> DocumentUploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    if not validate_upload_extension(Path(file.filename).suffix):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed: .txt, .md, .csv, .json, .pdf",
        )

    document = Document(
        user_id=user_id,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        storage_path="pending",
        status=DocumentStatus.uploaded,
    )
    db.add(document)
    await db.flush()

    storage_path = await save_upload_file(file=file, document_id=document.id)
    document.storage_path = str(storage_path)
    document.status = DocumentStatus.indexing
    await db.commit()
    await db.refresh(document)

    async_result = index_document_task.delay(str(document.id))
    document.celery_task_id = async_result.id
    await db.commit()

    return DocumentUploadResponse(
        document_id=document.id,
        filename=document.filename,
        status=document.status,
        celery_task_id=document.celery_task_id,
        message="Document accepted. Background indexing started.",
    )
