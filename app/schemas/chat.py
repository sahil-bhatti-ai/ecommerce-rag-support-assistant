from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: UUID | None = None
    message: str = Field(min_length=1, max_length=5000)


class Citation(BaseModel):
    document_id: UUID | str
    filename: str
    chunk_index: int
    score: float
    text_preview: str


class ChatResponse(BaseModel):
    session_id: UUID
    answer: str
    issue_type: str
    customer_issue_summary: str
    resolution_steps: list[str]
    confidence: float
    grounded: bool
    citations: list[Citation]
    fallback_reason: str | None = None
