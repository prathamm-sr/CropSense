"""
routers/predict.py
------------------
POST /predict
  - Validates input via Pydantic
  - Forwards request to ML microservice (Phase 2) via httpx
  - Logs result to PostgreSQL
  - Returns enriched response with DB id + timestamp

POST /predict/batch
  - Same flow for up to 50 items
"""

from __future__ import annotations

import logging
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.dependencies import get_db
from backend.models import PredictionLog
from backend.schemas import (
    CropPrediction,
    PredictRequest,
    PredictResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["Predictions"])

DBDep = Annotated[AsyncSession, Depends(get_db)]


async def _call_ml_service(features: dict, top_k: int) -> dict:
    """Forward prediction request to the ML microservice and return raw JSON."""
    payload = {"features": features, "top_k": top_k}
    async with httpx.AsyncClient(timeout=settings.ml_timeout) as client:
        try:
            resp = await client.post(f"{settings.ml_service_url}/predict", json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"ML service unreachable at {settings.ml_service_url}. Is it running?",
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"ML service returned {e.response.status_code}: {e.response.text}",
            )


def _build_log(features: dict, ml_result: dict) -> PredictionLog:
    return PredictionLog(
        n=features["N"],
        p=features["P"],
        k=features["K"],
        temperature=features["temperature"],
        humidity=features["humidity"],
        ph=features["ph"],
        rainfall=features["rainfall"],
        top_crop=ml_result["top_crop"],
        confidence=ml_result["confidence"],
        top_k=ml_result["top_k"],
        model_used=ml_result["model_used"],
    )


def _build_response(log: PredictionLog, ml_result: dict) -> PredictResponse:
    return PredictResponse(
        id=log.id,
        top_crop=log.top_crop,
        confidence=log.confidence,
        top_k=[CropPrediction(**item) for item in ml_result["top_k"]],
        model_used=log.model_used,
        input_features=ml_result["input_features"],
        created_at=log.created_at,
    )


@router.post(
    "",
    response_model=PredictResponse,
    summary="Predict crop",
    description=(
        "Forwards soil parameters to the ML microservice, "
        "persists the prediction to PostgreSQL, and returns the result."
    ),
)
async def predict(request: PredictRequest, db: DBDep) -> PredictResponse:
    features = request.features.model_dump()
    ml_result = await _call_ml_service(features, request.top_k)

    log = _build_log(features, ml_result)
    db.add(log)
    await db.flush()   # populate log.id + log.created_at before building response

    logger.info("Logged prediction %s → %s (%.1f%%)", log.id, log.top_crop, log.confidence * 100)
    return _build_response(log, ml_result)


@router.post(
    "/batch",
    response_model=list[PredictResponse],
    summary="Batch predict",
    description="Run up to 50 predictions. Each is logged individually.",
)
async def predict_batch(requests: list[PredictRequest], db: DBDep) -> list[PredictResponse]:
    if len(requests) > 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Batch size limit is 50.",
        )

    responses = []
    for req in requests:
        features = req.features.model_dump()
        ml_result = await _call_ml_service(features, req.top_k)
        log = _build_log(features, ml_result)
        db.add(log)
        await db.flush()
        responses.append(_build_response(log, ml_result))

    return responses