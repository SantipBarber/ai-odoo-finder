#!/bin/bash
# AI-OdooFinder - Stop System
# This script stops all Docker services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== AI-OdooFinder: Stopping System ==="
echo "Project directory: $PROJECT_DIR"
echo "Timestamp: $(date)"

cd "$PROJECT_DIR"

# Stop Docker services (just stop, don't remove)
echo "Stopping Docker services..."
docker compose stop

echo "=== System stopped successfully ==="
