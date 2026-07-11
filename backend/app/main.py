"""
JARVIS Command Center - Zentrales FastAPI-Backend.

Start (Entwicklung):
    cd backend
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env  # und Keys eintragen
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Start (Produktiv, im lokalen Netz für das Handy erreichbar):
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import get_settings
from app.routers import chat, telemetry, search, satellites

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info(f"{settings.APP_NAME} startet im '{settings.ENV}'-Modus ...")
    yield
    logger.info("JARVIS Backend wird heruntergefahren.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Zentrales KI-Gehirn für das JARVIS Command Center (Android)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router registrieren
app.include_router(chat.router)
app.include_router(telemetry.router)
app.include_router(search.router)
app.include_router(satellites.router)


@app.get("/", tags=["System"])
async def root() -> dict:
    return {
        "system": settings.APP_NAME,
        "status": "online",
        "endpoints": {
            "chat": "/api/chat/command",
            "telemetry_ingest": "/api/telemetry/ingest",
            "telemetry_ws": "/ws/telemetry",
            "search": "/api/search/query",
            "satellites_ws": "/ws/satellites",
            "docs": "/docs",
        },
    }


@app.get("/health", tags=["System"])
async def health() -> dict:
    return {"status": "ok"}
