# src/api/service.py
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api.routers.admin import setup_admin
from api.routers.auth import router as auth_router
from api.routers.chat_sessions import router as chat_sessions_router
from api.routers.health import router as health_router
from api.routers.users import router as users_router
from core.config import settings
from core.database import create_db_and_tables
from core.logging import setup_structured_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.is_dev():
        create_db_and_tables()
    yield


def create_app() -> FastAPI:
    setup_structured_logging(settings.LOG_LEVEL)

    app = FastAPI(
        title="方圆智版 Core",
        docs_url="/docs" if settings.SHOW_DOCS else None,
        redoc_url="/redoc" if settings.SHOW_DOCS else None,
        lifespan=lifespan,
    )

    allowed_origins = settings.cors_origins_list
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        max_age=600,
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    app.include_router(health_router)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(chat_sessions_router, prefix="/api/v1")

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.AUTH_SECRET.get_secret_value(),
        same_site="lax",
        https_only=not settings.is_dev(),
    )

    setup_admin(app)

    return app


app = create_app()
