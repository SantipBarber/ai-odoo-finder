#!/bin/bash
# AI-OdooFinder - System Status
# This script shows the status of all services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== AI-OdooFinder: System Status ==="
echo "Timestamp: $(date)"
echo ""

cd "$PROJECT_DIR"

# Docker containers status
echo "--- Docker Containers ---"
docker compose ps
echo ""

# Health check
echo "--- API Health ---"
HEALTH=$(curl -s http://localhost:8989/health 2>/dev/null || echo '{"status":"unreachable"}')
echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
echo ""

# Database stats
echo "--- Database Stats ---"
STATS=$(curl -s http://localhost:8989/stats 2>/dev/null || echo '{"error":"unreachable"}')
echo "$STATS" | python3 -m json.tool 2>/dev/null || echo "$STATS"
echo ""

# Disk usage
echo "--- Disk Usage ---"
df -h / | tail -1
echo ""

# Docker disk usage
echo "--- Docker Disk Usage ---"
docker system df 2>/dev/null || echo "Unable to get Docker disk usage"
