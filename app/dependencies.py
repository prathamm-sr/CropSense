"""
dependencies.py
---------------
Manages the Predictor as a process-wide singleton.
Loaded once at startup via FastAPI lifespan, injected into routes via Depends().

Why singleton: model files are ~50-200MB. Loading per-request would be
catastrophic. One load at startup, shared across all async workers.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from ml.predict import Predictor

# ── Global state ──────────────────────────────────────────────────────────────

_predictor: Predictor | None = None
_start_time: float = 0.0


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, release on shutdown."""
    global _predictor, _start_time
    print("[lifespan] Loading model...")
    try:
        _predictor = Predictor()
        _start_time = time.monotonic()
        print(f"[lifespan] Model ready: {_predictor.model_name}")
    except Exception as e:
        print(f"[lifespan] WARNING: Model failed to load — {e}")
        print("[lifespan] Server starting anyway; /predict will return 503 until model is available.")
        _predictor = None
        _start_time = time.monotonic()

    yield  # app is running

    print("[lifespan] Shutting down.")
    _predictor = None


# ── Dependency functions ──────────────────────────────────────────────────────

def get_predictor() -> Predictor:
    """
    FastAPI dependency. Raises 503 if model is not loaded.
    Usage: predictor: Annotated[Predictor, Depends(get_predictor)]
    """
    if _predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Check server logs.",
        )
    return _predictor


def get_uptime() -> float:
    return time.monotonic() - _start_time


def is_model_loaded() -> bool:
    return _predictor is not None


def get_model_name() -> str | None:
    return _predictor.model_name if _predictor else None


# ── Type alias for cleaner route signatures ───────────────────────────────────

PredictorDep = Annotated[Predictor, Depends(get_predictor)]