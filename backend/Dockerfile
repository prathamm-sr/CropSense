# Dockerfile.backend
# Multi-stage build for the Phase 3 main backend.

FROM python:3.11.9-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-backend.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements-backend.txt


FROM python:3.11.9-slim-bookworm AS runtime

WORKDIR /app

COPY --from=builder /install /usr/local

COPY backend/  ./backend/
COPY alembic/  ./alembic/
COPY alembic.ini .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV BACKEND_PORT=8001
EXPOSE $BACKEND_PORT

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${BACKEND_PORT}/health')"

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${BACKEND_PORT} --workers 1"]