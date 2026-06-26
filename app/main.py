from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import admin, chat, health, sessions, upload
from app.core.config import get_settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    if not settings.skip_startup_db:
        await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(upload.router)
    app.include_router(chat.router)
    app.include_router(sessions.router)
    app.include_router(admin.router)
    return app


app = create_app()
