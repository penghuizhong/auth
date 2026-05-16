from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from models.base import CoreBase, TimestampMixin
from models.user import User


class ChatSession(CoreBase, TimestampMixin, table=True):
    __tablename__ = "core_chat_sessions"

    thread_id: UUID = Field(index=True, unique=True)
    user_id: UUID = Field(foreign_key="core_users.id", index=True)
    title: str | None = Field(default=None, max_length=255)
    is_deleted: bool = Field(default=False)

    user: Optional["User"] = Relationship()
