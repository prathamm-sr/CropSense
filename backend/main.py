"""
backend/main.py
---------------
Main backend FastAPI app.

Runs on port 8001 (ML microservice runs on 8000).
Connects to PostgreSQL on startup and creates tables if missing.

Run locally:
    uvicorn backend.main:app --reload --port 8001
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from backend.config import settings
from backend.database import init_db
from backend.routers import history, predict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to database and creating tables...")
    await init_db()
    logger.info("Database ready.")
    yield
    logger.info("Backend shutting down.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="CropSense Backend API",
        description=(
            "Main backend for CropSense. "
            "Accepts prediction requests, forwards to ML service, logs to PostgreSQL."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS
    origins = [o.strip() for o in settings.cors_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Prometheus
    Instrumentator(
        excluded_handlers=["/metrics", "/health"],
    ).instrument(app).expose(app)

    # Routers
    app.include_router(predict.router)
    app.include_router(history.router)

    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "service": "cropsense-backend"}

    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "service": "cropsense-backend",
            "version": "1.0.0",
            "docs": "/docs",
            "ml_service": settings.ml_service_url,
        }

    return app


app = create_app()