"""
routers/predict.py
------------------
POST /predict         — single prediction
POST /predict/batch   — batch predictions (up to 100)
GET  /predict/crops   — list all supported crop classes
GET  /predict/features — feature metadata (ranges, descriptions)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.dependencies import PredictorDep
from app.schemas import (
    BatchPredictRequest,
    BatchPredictResponse,
    CropPrediction,
    ErrorDetail,
    PredictRequest,
    PredictResponse,
)
from ml.predict import FEATURE_RANGES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["Predictions"])


def _build_response(result) -> PredictResponse:
    """Convert ml.predict.PredictionResult → PredictResponse schema."""
    return PredictResponse(
        top_crop=result.top_crop,
        confidence=result.confidence,
        top_k=[CropPrediction(crop=item["crop"], probability=item["probability"])
               for item in result.top_k],
        model_used=result.model_used,
        input_features=result.input_features,
    )


@router.post(
    "",
    response_model=PredictResponse,
    responses={
        422: {"model": ErrorDetail, "description": "Validation error — invalid feature values"},
        503: {"model": ErrorDetail, "description": "Model not loaded"},
    },
    summary="Predict best crop",
    description=(
        "Given soil and climate parameters, returns the most suitable crop to grow "
        "along with confidence scores for the top-k candidates."
    ),
)
def predict(request: PredictRequest, predictor: PredictorDep) -> PredictResponse:
    features = request.features.model_dump()
    try:
        result = predictor.predict(features, top_k=request.top_k)
    except ValueError as e:
        logger.warning("Prediction input error: %s", e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected prediction error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    logger.info("Predicted: %s (%.2f%%)", result.top_crop, result.confidence * 100)
    return _build_response(result)


@router.post(
    "/batch",
    response_model=BatchPredictResponse,
    responses={
        422: {"model": ErrorDetail, "description": "Validation error"},
        503: {"model": ErrorDetail, "description": "Model not loaded"},
    },
    summary="Batch predict",
    description="Run up to 100 predictions in a single request. Items are processed sequentially.",
)
def predict_batch(request: BatchPredictRequest, predictor: PredictorDep) -> BatchPredictResponse:
    results = []
    errors = []

    for i, item in enumerate(request.items):
        features = item.features.model_dump()
        try:
            result = predictor.predict(features, top_k=item.top_k)
            results.append(_build_response(result))
        except ValueError as e:
            errors.append(f"Item {i}: {e}")
        except Exception as e:
            logger.exception("Batch item %d failed", i)
            errors.append(f"Item {i}: internal error — {e}")

    if errors and not results:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": errors},
        )

    return BatchPredictResponse(results=results, total=len(results))


@router.get(
    "/crops",
    response_model=list[str],
    summary="List supported crops",
    description="Returns the full list of crop classes the model was trained on.",
)
def list_crops(predictor: PredictorDep) -> list[str]:
    return predictor.class_names


@router.get(
    "/features",
    summary="Feature metadata",
    description="Returns name, description, and valid range for each input feature.",
)
def feature_metadata() -> dict:
    descriptions = {
        "N":           "Ratio of Nitrogen content in soil (kg/ha)",
        "P":           "Ratio of Phosphorous content in soil (kg/ha)",
        "K":           "Ratio of Potassium content in soil (kg/ha)",
        "temperature": "Ambient temperature in degree Celsius",
        "humidity":    "Relative humidity in %",
        "ph":          "pH value of the soil (acidity/alkalinity)",
        "rainfall":    "Annual rainfall in mm",
    }
    return {
        feat: {
            "description": descriptions[feat],
            "min": lo,
            "max": hi,
        }
        for feat, (lo, hi) in FEATURE_RANGES.items()
    }