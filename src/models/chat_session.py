import os
from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from models.base import CoreBase, TimestampMixin, get_core_table_name
from models.user import User


class ChatSession(CoreBase, TimestampMixin, table=True):
    __tablename__ = os.environ.get("CHAT_SESSION_TABLE_NAME", "chat_sessions")


    thread_id: UUID = Field(index=True, unique=True)
    # 使用动态外键引用，确保前缀一致
    user_id: UUID = Field(foreign_key=get_core_table_name("users") + ".id", index=True)
    title: str | None = Field(default=None, max_length=255)
    is_deleted: bool = Field(default=False)

    user: Optional["User"] = Relationship()
