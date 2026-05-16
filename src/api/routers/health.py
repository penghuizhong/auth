from fastapi import APIRouter

from core.database import get_engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "degraded", "database": "disconnected"}
