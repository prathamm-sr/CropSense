"""
main.py
-------
FastAPI application factory for the CropSense ML microservice.

Run locally:
    uvicorn app.main:app --reload --port 8000

Environment variables:
    PORT          — port to bind (default 8000, used by Dockerfile)
    LOG_LEVEL     — uvicorn log level (default "info")
    CORS_ORIGINS  — comma-separated allowed origins (default "*" for dev)
"""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.dependencies import lifespan
from app.routers import health, predict

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="CropSense ML API",
        description=(
            "Precision agriculture — recommend the optimal crop based on soil and climate parameters. "
            "Trained on 2,200 samples across 22 crop classes using an ensemble of 5 classifiers."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    raw_origins = os.getenv("CORS_ORIGINS", "*")
    origins = [o.strip() for o in raw_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Prometheus metrics ────────────────────────────────────────────────────
    # Exposes /metrics endpoint — Prometheus scrapes this
    Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=["/metrics", "/health", "/ready"],
    ).instrument(app).expose(app)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(predict.router)

    # ── Root ──────────────────────────────────────────────────────────────────
    @app.get("/", include_in_schema=False)
    def root():
        return {
            "service": "cropsense-ml",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics",
        }

    # ── Global exception handler ──────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def unhandled_exception(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)},
        )

    return app


app = create_app()