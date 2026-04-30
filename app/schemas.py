"""
schemas.py
----------
All Pydantic v2 request and response models for the CropSense API.
Keeping these in one file makes it trivial for the frontend / other services
to generate TypeScript types from a single source of truth.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


# ── Request ───────────────────────────────────────────────────────────────────

class SoilFeatures(BaseModel):
    """Soil and climate parameters for a single prediction request."""

    N: float = Field(
        ...,
        ge=0, le=140,
        description="Ratio of Nitrogen content in soil (kg/ha)",
        examples=[90],
    )
    P: float = Field(
        ...,
        ge=5, le=145,
        description="Ratio of Phosphorous content in soil (kg/ha)",
        examples=[42],
    )
    K: float = Field(
        ...,
        ge=5, le=205,
        description="Ratio of Potassium content in soil (kg/ha)",
        examples=[43],
    )
    temperature: float = Field(
        ...,
        ge=8.0, le=44.0,
        description="Temperature in degree Celsius",
        examples=[20.87],
    )
    humidity: float = Field(
        ...,
        ge=14.0, le=100.0,
        description="Relative humidity in %",
        examples=[82.0],
    )
    ph: float = Field(
        ...,
        ge=3.5, le=9.5,
        description="pH value of the soil",
        examples=[6.5],
    )
    rainfall: float = Field(
        ...,
        ge=20.0, le=300.0,
        description="Rainfall in mm",
        examples=[202.9],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "N": 90,
                "P": 42,
                "K": 43,
                "temperature": 20.87,
                "humidity": 82.0,
                "ph": 6.5,
                "rainfall": 202.9,
            }
        }
    }


class PredictRequest(BaseModel):
    features: SoilFeatures
    top_k: int = Field(default=5, ge=1, le=22, description="Number of top crops to return")
    model_name: str | None = Field(
        default=None,
        description="Override which saved model to use. Defaults to best model from training.",
    )


# ── Response ──────────────────────────────────────────────────────────────────

class CropPrediction(BaseModel):
    crop: str
    probability: float = Field(..., ge=0.0, le=1.0)


class PredictResponse(BaseModel):
    top_crop: str = Field(..., description="Most recommended crop")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Probability of top prediction")
    top_k: list[CropPrediction] = Field(..., description="Ranked list of crop predictions")
    model_used: str
    input_features: dict[str, float]


class BatchPredictRequest(BaseModel):
    items: list[PredictRequest] = Field(..., min_length=1, max_length=100)

    @model_validator(mode="after")
    def check_not_empty(self) -> BatchPredictRequest:
        if not self.items:
            raise ValueError("items list must not be empty")
        return self


class BatchPredictResponse(BaseModel):
    results: list[PredictResponse]
    total: int


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str | None
    uptime_seconds: float


class ReadyResponse(BaseModel):
    ready: bool


# ── Error ─────────────────────────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    error: str
    detail: str | None = None