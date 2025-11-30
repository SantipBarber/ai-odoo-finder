#!/bin/bash
# AI-OdooFinder - Start System
# This script starts all Docker services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== AI-OdooFinder: Starting System ==="
echo "Project directory: $PROJECT_DIR"
echo "Timestamp: $(date)"

cd "$PROJECT_DIR"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    exit 1
fi

# Pull latest changes (optional, comment out if not desired)
# echo "Pulling latest code..."
# git pull

# Start Docker services
echo "Starting Docker services..."
docker compose up -d

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Health check
echo "Running health check..."
HEALTH=$(curl -s http://localhost:8989/health 2>/dev/null || echo '{"status":"error"}')

if echo "$HEALTH" | grep -q '"status":"healthy"'; then
    echo "=== System started successfully ==="
    echo "Health: $HEALTH"
    docker compose ps
else
    echo "WARNING: Health check failed"
    echo "Response: $HEALTH"
    echo "Checking logs..."
    docker compose logs --tail 20
    exit 1
fi
