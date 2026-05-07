from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import (
    affiliate_products,
    content,
    dashboard,
    drafts,
    fortune_templates,
    fortune_a8_offers,
    health,
    imports,
    knowledge,
    note_cta_templates,
    note_funnel_pages,
    persona_pains,
    publish,
    settings,
    threads_plan,
    threads_post_templates,
    typefully,
)


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

    app.include_router(health.router)
    app.include_router(dashboard.router)
    app.include_router(knowledge.router)
    app.include_router(affiliate_products.router)
    app.include_router(persona_pains.router)
    app.include_router(fortune_templates.router)
    app.include_router(note_funnel_pages.router)
    app.include_router(fortune_a8_offers.router)
    app.include_router(threads_post_templates.router)
    app.include_router(note_cta_templates.router)
    app.include_router(threads_plan.router)
    app.include_router(imports.router)
    app.include_router(content.router)
    app.include_router(drafts.router)
    app.include_router(publish.router)
    app.include_router(typefully.router)
    app.include_router(settings.router)
    return app


app = create_app()
