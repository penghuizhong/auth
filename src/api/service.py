# src/api/service.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api.routers.auth import router as auth_router
from api.routers.chat_sessions import router as chat_sessions_router
from api.routers.users import router as users_router
from api.routers.admin import setup_admin

from core.config import settings
from core.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title="方圆智版 Core",
        docs_url="/docs" if settings.SHOW_DOCS else None,
        redoc_url="/redoc" if settings.SHOW_DOCS else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(chat_sessions_router, prefix="/api/v1")

    app.add_middleware(
        SessionMiddleware, 
        secret_key=settings.AUTH_SECRET.get_secret_value()
    )

    # 挂载 SQLAdmin
    setup_admin(app)

    return app

# 实例化全局 app 供 Uvicorn 调度
app = create_app()