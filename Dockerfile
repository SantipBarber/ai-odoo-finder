# AI-OdooFinder Docker Image
# Production build - minimal dependencies

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with pip
# Note: These are production-only deps (no torch/transformers needed)
RUN pip install --no-cache-dir \
    fastapi==0.115.6 \
    uvicorn[standard]==0.32.1 \
    sqlalchemy==2.0.36 \
    pgvector==0.3.6 \
    psycopg[binary]==3.2.3 \
    pydantic==2.10.3 \
    pydantic-settings==2.6.1 \
    httpx==0.28.1 \
    python-dotenv==1.1.0 \
    requests==2.32.3 \
    fastmcp==2.3.3

# Copy application code
COPY backend/ ./backend/

# Set environment variables
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose API port
EXPOSE 8989

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8989/').raise_for_status()" || exit 1

# Run the API server
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8989"]
