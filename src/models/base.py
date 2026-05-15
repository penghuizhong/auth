from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class CoreBase(SQLModel):
    """所有 core_* 表的基类，自动添加 core_ 表前缀"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "__tablename__") and not cls.__tablename__.startswith("core_"):
            cls.__tablename__ = f"core_{cls.__tablename__}"


class TimestampMixin(SQLModel):
    """时间戳 mixin"""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
