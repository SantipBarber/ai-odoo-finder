#!/bin/bash
# ============================================
# AI-OdooFinder: Migrate Data from Neon to Local PostgreSQL
# ============================================
#
# This script exports data from Neon and imports it to your local/server PostgreSQL.
#
# Prerequisites:
#   - pg_dump and psql installed
#   - Access to Neon database (connection string)
#   - Docker containers running (docker-compose up -d)
#
# Usage:
#   ./scripts/migrate_from_neon.sh
#
# Environment Variables (set in .env or export):
#   NEON_DATABASE_URL - Full Neon connection string
#   LOCAL_DATABASE_URL - Local PostgreSQL connection (default: from docker-compose)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}AI-OdooFinder: Neon to PostgreSQL Migration${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo -e "${GREEN}[OK]${NC} Loaded .env file"
fi

# Check required variables
if [ -z "$NEON_DATABASE_URL" ]; then
    echo -e "${RED}[ERROR]${NC} NEON_DATABASE_URL not set"
    echo "Please set it in .env or export it:"
    echo "  export NEON_DATABASE_URL='postgresql://user:pass@host/db?sslmode=require'"
    exit 1
fi

# Default local database URL (Docker)
LOCAL_DATABASE_URL="${LOCAL_DATABASE_URL:-postgresql://${POSTGRES_USER:-odoofinder}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB:-ai_odoofinder}}"

# Backup directory
BACKUP_DIR="./backups"
BACKUP_FILE="${BACKUP_DIR}/neon_backup_$(date +%Y%m%d_%H%M%S).sql"

mkdir -p "$BACKUP_DIR"

echo ""
echo -e "${YELLOW}Step 1: Exporting data from Neon...${NC}"
echo "  Source: Neon PostgreSQL"
echo "  Backup file: ${BACKUP_FILE}"
echo ""

# Export from Neon (data only, no schema since we use SQLAlchemy)
pg_dump "$NEON_DATABASE_URL" \
    --data-only \
    --no-owner \
    --no-privileges \
    --disable-triggers \
    --format=plain \
    > "$BACKUP_FILE"

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo -e "${GREEN}[OK]${NC} Backup created: ${BACKUP_FILE} (${BACKUP_SIZE})"

echo ""
echo -e "${YELLOW}Step 2: Checking Docker containers...${NC}"

if ! docker ps | grep -q "odoofinder-postgres"; then
    echo -e "${YELLOW}[WARN]${NC} PostgreSQL container not running. Starting..."
    docker-compose up -d db
    echo "Waiting for PostgreSQL to be ready..."
    sleep 10
fi

echo -e "${GREEN}[OK]${NC} PostgreSQL container is running"

echo ""
echo -e "${YELLOW}Step 3: Creating schema in local database...${NC}"

# Run the API once to create tables via SQLAlchemy
docker-compose run --rm api python -c "
from backend.app.database import engine
from backend.app.models import Base
Base.metadata.create_all(bind=engine)
print('Schema created successfully')
"

echo -e "${GREEN}[OK]${NC} Schema created"

echo ""
echo -e "${YELLOW}Step 4: Importing data to local PostgreSQL...${NC}"

# Import data
docker exec -i odoofinder-postgres psql \
    -U "${POSTGRES_USER:-odoofinder}" \
    -d "${POSTGRES_DB:-ai_odoofinder}" \
    < "$BACKUP_FILE"

echo -e "${GREEN}[OK]${NC} Data imported successfully"

echo ""
echo -e "${YELLOW}Step 5: Verifying migration...${NC}"

# Count records
RECORD_COUNT=$(docker exec odoofinder-postgres psql \
    -U "${POSTGRES_USER:-odoofinder}" \
    -d "${POSTGRES_DB:-ai_odoofinder}" \
    -t -c "SELECT COUNT(*) FROM odoo_modules;")

echo -e "${GREEN}[OK]${NC} Total modules migrated: ${RECORD_COUNT}"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Migration completed successfully!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Test the API: curl http://localhost:8989/"
echo "  2. Test search: curl 'http://localhost:8989/search?query=inventory&version=17.0'"
echo "  3. If everything works, you can cancel your Neon subscription"
echo ""
echo "Backup file saved at: ${BACKUP_FILE}"
echo "(Keep this backup until you verify everything works)"
