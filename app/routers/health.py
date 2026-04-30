"""
routers/health.py
-----------------
/health  — liveness probe  (is the process alive?)
/ready   — readiness probe (is the model loaded and ready to serve?)

Docker / Kubernetes use these differently:
  liveness  → restart container if this fails
  readiness → stop sending traffic if this fails
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.dependencies import get_uptime, is_model_loaded, get_model_name
from app.schemas import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Returns 200 as long as the process is running, regardless of model state.",
)
def health():
    return HealthResponse(
        status="ok",
        model_loaded=is_model_loaded(),
        model_name=get_model_name(),
        uptime_seconds=round(get_uptime(), 2),
    )


@router.get(
    "/ready",
    response_model=ReadyResponse,
    summary="Readiness probe",
    description="Returns 200 only when model is loaded. Returns 503 otherwise.",
)
def ready():
    loaded = is_model_loaded()
    if not loaded:
        return JSONResponse(
            status_code=503,
            content={"ready": False},
        )
    return ReadyResponse(ready=True)