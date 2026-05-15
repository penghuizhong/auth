from sqlmodel import Session, SQLModel, create_engine

from core.config import settings

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
        )
    return _engine


def create_db_and_tables():
    """开发环境自动建表（生产使用 Alembic）"""
    SQLModel.metadata.create_all(get_engine())


def get_session():
    with Session(get_engine()) as session:
        yield session
