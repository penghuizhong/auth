from sqlmodel import Field

from models.base import CoreBase, TimestampMixin


class User(CoreBase, TimestampMixin, table=True):
    __tablename__ = "users"

    def __str__(self):
        return f"{self.nickname or '未命名'} ({self.email})"

    username: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    nickname: str | None = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)
