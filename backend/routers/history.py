"""
routers/history.py
------------------
GET /history          — paginated prediction history
GET /history/stats    — aggregate stats (total, top crops, avg confidence)
GET /history/{id}     — single prediction by UUID
DELETE /history/{id}  — delete a prediction log
"""

from __future__ import annotations

import uuid
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_db
from backend.models import PredictionLog
from backend.schemas import (
    CropCount,
    HistoryItem,
    HistoryResponse,
    StatsResponse,
    CropPrediction,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/history", tags=["History"])

DBDep = Annotated[AsyncSession, Depends(get_db)]


def _log_to_item(log: PredictionLog) -> HistoryItem:
    return HistoryItem(
        id=log.id,
        top_crop=log.top_crop,
        confidence=log.confidence,
        top_k=[CropPrediction(**item) for item in log.top_k],
        model_used=log.model_used,
        input_features={
            "N": log.n, "P": log.p, "K": log.k,
            "temperature": log.temperature,
            "humidity": log.humidity,
            "ph": log.ph,
            "rainfall": log.rainfall,
        },
        created_at=log.created_at,
    )


@router.get(
    "",
    response_model=HistoryResponse,
    summary="Prediction history",
    description="Returns paginated prediction logs, newest first.",
)
async def get_history(
    db: DBDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    crop: str | None = Query(default=None, description="Filter by crop name"),
) -> HistoryResponse:
    offset = (page - 1) * page_size

    # Count query
    count_q = select(func.count()).select_from(PredictionLog)
    if crop:
        count_q = count_q.where(PredictionLog.top_crop == crop)
    total = (await db.execute(count_q)).scalar_one()

    # Data query
    data_q = select(PredictionLog).order_by(PredictionLog.created_at.desc())
    if crop:
        data_q = data_q.where(PredictionLog.top_crop == crop)
    data_q = data_q.offset(offset).limit(page_size)

    logs = (await db.execute(data_q)).scalars().all()

    return HistoryResponse(
        items=[_log_to_item(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Prediction statistics",
    description="Aggregate stats: total predictions, top 10 crops, average confidence.",
)
async def get_stats(db: DBDep) -> StatsResponse:
    total = (await db.execute(select(func.count()).select_from(PredictionLog))).scalar_one()

    avg_conf = (
        await db.execute(select(func.avg(PredictionLog.confidence)))
    ).scalar_one() or 0.0

    top_crops_q = (
        select(PredictionLog.top_crop, func.count().label("cnt"))
        .group_by(PredictionLog.top_crop)
        .order_by(func.count().desc())
        .limit(10)
    )
    top_crops = [
        CropCount(crop=row.top_crop, count=row.cnt)
        for row in (await db.execute(top_crops_q)).all()
    ]

    return StatsResponse(
        total_predictions=total,
        top_crops=top_crops,
        avg_confidence=round(float(avg_conf), 4),
    )


@router.get(
    "/{prediction_id}",
    response_model=HistoryItem,
    summary="Get prediction by ID",
)
async def get_prediction(prediction_id: uuid.UUID, db: DBDep) -> HistoryItem:
    log = await db.get(PredictionLog, prediction_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found.")
    return _log_to_item(log)


@router.delete(
    "/{prediction_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete prediction log",
)
async def delete_prediction(prediction_id: uuid.UUID, db: DBDep) -> dict:
    log = await db.get(PredictionLog, prediction_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found.")
    await db.delete(log)
    return {"deleted": str(prediction_id)}