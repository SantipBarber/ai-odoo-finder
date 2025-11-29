#!/bin/bash
# ============================================================================
# Supervisor para regeneración de embeddings
#
# Ejecuta el script de regeneración y lo relanza automáticamente si falla.
# Diseñado para correr durante la noche sin supervisión.
#
# Uso:
#   ./scripts/embedding_supervisor.sh
#   nohup ./scripts/embedding_supervisor.sh > embedding_supervisor.log 2>&1 &
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$SCRIPT_DIR/embedding_supervisor.log"
PID_FILE="$SCRIPT_DIR/.embedding_supervisor.pid"

# Configuración
MAX_RETRIES=100          # Máximo de reinicios
RETRY_DELAY=60           # Segundos entre reintentos
HEALTH_CHECK_INTERVAL=300  # Cada 5 minutos verificar progreso

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cleanup() {
    log "${YELLOW}Supervisor detenido${NC}"
    rm -f "$PID_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Verificar si ya hay un supervisor corriendo
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        log "${RED}ERROR: Supervisor ya está corriendo (PID: $OLD_PID)${NC}"
        log "Para detenerlo: kill $OLD_PID"
        exit 1
    fi
fi

# Guardar PID
echo $$ > "$PID_FILE"

log "============================================================"
log "${GREEN}EMBEDDING REGENERATION SUPERVISOR${NC}"
log "============================================================"
log "Proyecto: $PROJECT_DIR"
log "Log: $LOG_FILE"
log "PID: $$"
log "Max retries: $MAX_RETRIES"
log "============================================================"

cd "$PROJECT_DIR"

retry_count=0
last_processed=0

while [ $retry_count -lt $MAX_RETRIES ]; do
    log "${GREEN}Iniciando regeneración de embeddings (intento $((retry_count + 1))/$MAX_RETRIES)${NC}"

    # Ejecutar el script
    if uv run python scripts/regenerate_embeddings.py --batch-size 100; then
        log "${GREEN}✅ Regeneración completada exitosamente${NC}"
        break
    else
        exit_code=$?
        log "${RED}Script terminó con código $exit_code${NC}"

        # Verificar si hubo progreso
        if [ -f "$SCRIPT_DIR/.embedding_checkpoint.json" ]; then
            current_processed=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/.embedding_checkpoint.json'))['total_processed'])" 2>/dev/null || echo "0")

            if [ "$current_processed" -gt "$last_processed" ]; then
                log "${YELLOW}Progreso detectado: $last_processed -> $current_processed${NC}"
                last_processed=$current_processed
                retry_count=0  # Resetear contador si hubo progreso
            fi
        fi

        retry_count=$((retry_count + 1))

        if [ $retry_count -lt $MAX_RETRIES ]; then
            log "${YELLOW}Esperando ${RETRY_DELAY}s antes de reintentar...${NC}"
            sleep $RETRY_DELAY
        fi
    fi
done

if [ $retry_count -ge $MAX_RETRIES ]; then
    log "${RED}❌ Máximo de reintentos alcanzado${NC}"

    # Enviar notificación (opcional - descomentar si tienes configurado)
    # curl -X POST "https://api.pushover.net/1/messages.json" \
    #     -d "token=YOUR_TOKEN" \
    #     -d "user=YOUR_USER" \
    #     -d "message=Embedding regeneration failed after $MAX_RETRIES retries"
fi

# Mostrar resumen final
log "============================================================"
log "RESUMEN FINAL"
log "============================================================"

if [ -f "$SCRIPT_DIR/.embedding_checkpoint.json" ]; then
    uv run python scripts/regenerate_embeddings.py --status
fi

cleanup