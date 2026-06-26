from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.models.message import Message, MessageRole
from app.models.session import SupportSession
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> ChatResponse:
    if payload.session_id:
        session = await db.get(SupportSession, payload.session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found.")
    else:
        session = SupportSession(user_id=user_id, title=payload.message[:80])
        db.add(session)
        await db.flush()

    user_message = Message(session_id=session.id, role=MessageRole.user, content=payload.message)
    db.add(user_message)

    rag = RAGService()
    answer = await rag.answer(payload.message)

    assistant_message = Message(
        session_id=session.id,
        role=MessageRole.assistant,
        content=answer.answer,
        issue_type=answer.issue_type,
        confidence=answer.confidence,
        citations=[citation.model_dump(mode="json") for citation in answer.citations],
    )
    db.add(assistant_message)
    await db.commit()

    return ChatResponse(session_id=session.id, **answer.model_dump())
