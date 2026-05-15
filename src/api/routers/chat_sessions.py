from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api.deps import CurrentUser
from core.database import get_session
from models.chat_session import ChatSession
from schemas.chat_session import (
    ChatSessionCreateResponse,
    ChatSessionResponse,
    ChatSessionUpdateRequest,
)

router = APIRouter(prefix="/chat/sessions", tags=["chat-sessions"])


@router.post("", response_model=ChatSessionCreateResponse, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    thread_id = uuid4()
    chat_session = ChatSession(
        thread_id=thread_id,
        user_id=current_user.id,
        title=None,
    )
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)
    return chat_session


@router.get("", response_model=list[ChatSessionResponse])
def list_chat_sessions(
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    statement = (
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .where(ChatSession.is_deleted == False)  # noqa: E712
        .order_by(ChatSession.updated_at.desc())
    )
    return session.exec(statement).all()


@router.patch("/{thread_id}", response_model=ChatSessionResponse)
def update_chat_session(
    thread_id: UUID,
    request: ChatSessionUpdateRequest,
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    statement = (
        select(ChatSession)
        .where(ChatSession.thread_id == thread_id)
        .where(ChatSession.user_id == current_user.id)
        .where(ChatSession.is_deleted == False)  # noqa: E712
    )
    chat_session = session.exec(statement).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="会话不存在")

    chat_session.title = request.title
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)
    return chat_session


@router.delete("/{thread_id}")
def delete_chat_session(
    thread_id: UUID,
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    statement = (
        select(ChatSession)
        .where(ChatSession.thread_id == thread_id)
        .where(ChatSession.user_id == current_user.id)
        .where(ChatSession.is_deleted == False)  # noqa: E712
    )
    chat_session = session.exec(statement).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="会话不存在")

    chat_session.is_deleted = True
    session.add(chat_session)
    session.commit()
    return {"message": "已删除"}
