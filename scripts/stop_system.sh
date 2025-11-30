#!/bin/bash
# AI-OdooFinder - Stop System
# This script stops all Docker services and cleans up

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== AI-OdooFinder: Stopping System ==="
echo "Project directory: $PROJECT_DIR"
echo "Timestamp: $(date)"

cd "$PROJECT_DIR"

# Stop Docker services
echo "Stopping Docker services..."
docker compose down

# Optional: Clean up dangling images/containers
echo "Cleaning up orphaned containers..."
docker container prune -f 2>/dev/null || true

echo "=== System stopped successfully ==="
