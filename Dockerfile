# ── Stage 1: builder ─────────────────────────────────────────────────────────
# Install all dependencies into a clean venv.
# Keeping this separate means the final image doesn't carry pip/build tools.
FROM python:3.11.9-slim-bookworm AS builder

WORKDIR /build

# Install build deps for packages that compile C extensions (numpy, scikit-learn)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements-api.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11.9-slim-bookworm AS runtime

LABEL org.opencontainers.image.title="CropSense ML API"
LABEL org.opencontainers.image.description="Precision agriculture crop recommendation microservice"
LABEL org.opencontainers.image.version="1.0.0"

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY ml/         ./ml/
COPY app/        ./app/
COPY models/     ./models/
COPY outputs/    ./outputs/

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (override with PORT env var at runtime if needed)
ENV PORT=8000
EXPOSE $PORT

# Health check — Docker uses this to mark container healthy/unhealthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]