import os
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def get_core_table_name(base_name: str) -> str:
    """获取带前缀的完整表名
    
    用于外键引用时确保表名前缀一致
    示例：get_core_table_name("users") -> "core_users"
    """
    prefix = os.environ.get("CORE_TABLE_PREFIX", "core_")
    return f"{prefix}{base_name}"


class CoreBase(SQLModel):
    """所有 core 服务表的基类，自动添加配置的表前缀（默认 core_）"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # 从环境变量读取表名前缀，默认为 'core_'
        # 这样 Alembic 和运行时都能正确获取
        prefix = os.environ.get("CORE_TABLE_PREFIX", "core_")
        if hasattr(cls, "__tablename__") and not cls.__tablename__.startswith(prefix):
            cls.__tablename__ = f"{prefix}{cls.__tablename__}"


class TimestampMixin(SQLModel):
    """时间戳 mixin"""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
