#!/bin/bash
# =============================================================================
# AI-OdooFinder - ETL Cron Script
# =============================================================================
# Este script ejecuta el ETL de módulos OCA de forma programada via cron.
#
# Instalación del cron job (ejecutar como root o con sudo):
#   crontab -e
#   # Añadir la siguiente línea para ejecutar a las 3 AM UTC diariamente:
#   0 3 * * * /opt/ai-odoo-finder/scripts/cron_etl.sh >> /var/log/ai-odoofinder-etl.log 2>&1
#
# Para ejecutar manualmente:
#   /opt/ai-odoo-finder/scripts/cron_etl.sh
# =============================================================================

set -e

# Configuración
PROJECT_DIR="/opt/ai-odoo-finder"
LOG_PREFIX="[AI-OdooFinder ETL]"
UV_BIN="$HOME/.local/bin/uv"

# Colores para output (solo si es terminal interactivo)
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    NC='\033[0m' # No Color
else
    GREEN=''
    RED=''
    YELLOW=''
    NC=''
fi

log_info() {
    echo -e "${GREEN}${LOG_PREFIX}${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}${LOG_PREFIX}${NC} $(date '+%Y-%m-%d %H:%M:%S') - WARNING: $1"
}

log_error() {
    echo -e "${RED}${LOG_PREFIX}${NC} $(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1"
}

# Verificar que el directorio del proyecto existe
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "Project directory not found: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# Verificar que uv está instalado
if [ ! -f "$UV_BIN" ]; then
    # Intentar encontrar uv en PATH
    UV_BIN=$(which uv 2>/dev/null || echo "")
    if [ -z "$UV_BIN" ]; then
        log_error "uv not found. Please install it: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
fi

# Cargar variables de entorno desde .env
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    log_info "Environment variables loaded from .env"
else
    log_warn ".env file not found, using existing environment variables"
fi

# Verificar que las variables necesarias están definidas
if [ -z "$DATABASE_URL" ]; then
    log_error "DATABASE_URL not defined"
    exit 1
fi

if [ -z "$OPENROUTER_API_KEY" ]; then
    log_warn "OPENROUTER_API_KEY not defined - AI enrichment will be skipped"
fi

# Verificar que PostgreSQL está accesible
log_info "Checking database connection..."
if ! docker exec odoofinder-postgres pg_isready -U odoofinder -q 2>/dev/null; then
    log_error "PostgreSQL is not ready. Is the container running?"
    log_info "Try: docker compose up -d db"
    exit 1
fi

log_info "=========================================="
log_info "Starting ETL process..."
log_info "=========================================="

START_TIME=$(date +%s)

# Ejecutar ETL
if $UV_BIN run python scripts/etl_oca_modules.py; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    DURATION_MIN=$((DURATION / 60))
    DURATION_SEC=$((DURATION % 60))

    log_info "=========================================="
    log_info "ETL completed successfully!"
    log_info "Duration: ${DURATION_MIN}m ${DURATION_SEC}s"
    log_info "=========================================="

    # Mostrar estadísticas de la base de datos
    log_info "Database statistics:"
    docker exec odoofinder-postgres psql -U odoofinder -d ai_odoofinder -c \
        "SELECT version, COUNT(*) as modules FROM odoo_modules GROUP BY version ORDER BY version;" \
        2>/dev/null || log_warn "Could not fetch statistics"

    exit 0
else
    log_error "=========================================="
    log_error "ETL failed! Check the logs above for details."
    log_error "=========================================="
    exit 1
fi
