"""
schemas.py
----------
Pydantic models for the main backend.
Intentionally mirrors app/schemas.py structure but is independent —
the backend owns its own contract with the frontend.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Shared ────────────────────────────────────────────────────────────────────

class SoilFeatures(BaseModel):
    N: float = Field(..., ge=0, le=140, examples=[90])
    P: float = Field(..., ge=5, le=145, examples=[42])
    K: float = Field(..., ge=5, le=205, examples=[43])
    temperature: float = Field(..., ge=8.0, le=44.0, examples=[20.87])
    humidity: float = Field(..., ge=14.0, le=100.0, examples=[82.0])
    ph: float = Field(..., ge=3.5, le=9.5, examples=[6.5])
    rainfall: float = Field(..., ge=20.0, le=300.0, examples=[202.9])

    model_config = {
        "json_schema_extra": {
            "example": {
                "N": 90, "P": 42, "K": 43,
                "temperature": 20.87, "humidity": 82.0,
                "ph": 6.5, "rainfall": 202.9,
            }
        }
    }


# ── Predict ───────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    features: SoilFeatures
    top_k: int = Field(default=5, ge=1, le=22)


class CropPrediction(BaseModel):
    crop: str
    probability: float


class PredictResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    id: uuid.UUID
    top_crop: str
    confidence: float
    top_k: list[CropPrediction]
    model_used: str
    input_features: dict[str, float]
    created_at: datetime


# ── History ───────────────────────────────────────────────────────────────────

class HistoryItem(BaseModel):
    model_config = {"from_attributes": True, "protected_namespaces": ()}
    id: uuid.UUID
    top_crop: str
    confidence: float
    top_k: list[CropPrediction]
    model_used: str
    input_features: dict[str, float]
    created_at: datetime


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
    page: int
    page_size: int


# ── Stats ─────────────────────────────────────────────────────────────────────

class CropCount(BaseModel):
    crop: str
    count: int


class StatsResponse(BaseModel):
    total_predictions: int
    top_crops: list[CropCount]
    avg_confidence: float