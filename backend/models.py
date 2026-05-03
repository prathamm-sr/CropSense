"""
models.py
---------
SQLAlchemy ORM table definitions.

Tables:
  prediction_logs  — every prediction request + result
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    # ── Primary key ───────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── Input features ────────────────────────────────────────────────────────
    n: Mapped[float] = mapped_column(Float, nullable=False)
    p: Mapped[float] = mapped_column(Float, nullable=False)
    k: Mapped[float] = mapped_column(Float, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    ph: Mapped[float] = mapped_column(Float, nullable=False)
    rainfall: Mapped[float] = mapped_column(Float, nullable=False)

    # ── Prediction output ─────────────────────────────────────────────────────
    top_crop: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    top_k: Mapped[dict] = mapped_column(JSONB, nullable=False)   # full ranked list
    model_used: Mapped[str] = mapped_column(String(64), nullable=False)

    # ── Request metadata ──────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, index=True
    )

    # ── Indexes ───────────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_pred_logs_crop_created", "top_crop", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<PredictionLog id={self.id} crop={self.top_crop} conf={self.confidence:.2f}>"