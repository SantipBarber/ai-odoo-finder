# AI-OdooFinder MCP Server Dockerfile
# Runs the MCP server in HTTP mode for remote clients

FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Install dependencies
RUN uv sync --frozen --no-dev

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Environment defaults
ENV MCP_TRANSPORT=http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8080 \
    MCP_PATH=/mcp \
    AI_ODOOFINDER_API_URL=http://api:8989 \
    AI_ODOOFINDER_API_TIMEOUT=60

# Expose port
EXPOSE 8080

# Health check endpoint (FastMCP doesn't have one by default, so we check if port is open)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run MCP server in HTTP mode
CMD ["uv", "run", "ai-odoofinder-mcp", "--http"]
