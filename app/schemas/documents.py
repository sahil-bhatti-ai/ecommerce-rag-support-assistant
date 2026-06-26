from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    filename: str
    status: DocumentStatus
    celery_task_id: str | None
    message: str


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    content_type: str
    status: DocumentStatus
    chunk_count: int
    error_message: str | None
    celery_task_id: str | None
    created_at: datetime
    updated_at: datetime


class IndexingJobRead(BaseModel):
    document_id: UUID
    filename: str
    status: DocumentStatus
    celery_task_id: str | None
    chunk_count: int
    error_message: str | None
    updated_at: datetime
