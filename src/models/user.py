from typing import Optional
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from models.base import CoreBase, TimestampMixin


class User(CoreBase, TimestampMixin, table=True):
    __tablename__ = "core_users"
    
    def __str__(self):
        # 让它在下拉框里显示：昵称 (邮箱)
        return f"{self.nickname or '未命名'} ({self.email})"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    nickname: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)
