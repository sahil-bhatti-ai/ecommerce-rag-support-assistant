from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.models.message import Message
from app.models.session import SupportSession
from app.schemas.sessions import MessageRead, SessionCreate, SessionRead

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionRead)
async def create_session(
    payload: SessionCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> SupportSession:
    session = SupportSession(user_id=user_id, title=payload.title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("", response_model=list[SessionRead])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> list[SupportSession]:
    result = await db.execute(
        select(SupportSession)
        .where(SupportSession.user_id == user_id)
        .order_by(SupportSession.updated_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{session_id}/messages", response_model=list[MessageRead])
async def list_session_messages(session_id: UUID, db: AsyncSession = Depends(get_db)) -> list[Message]:
    session = await db.get(SupportSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    result = await db.execute(
        select(Message).where(Message.session_id == session_id).order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())
