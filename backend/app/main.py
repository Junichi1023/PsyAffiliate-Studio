from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import content, dashboard, drafts, knowledge, products, settings
from .database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="PsyAffiliate Studio API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "PsyAffiliate Studio"}

    app.include_router(dashboard.router)
    app.include_router(knowledge.router)
    app.include_router(products.router)
    app.include_router(content.router)
    app.include_router(drafts.router)
    app.include_router(settings.router)
    return app


app = create_app()
