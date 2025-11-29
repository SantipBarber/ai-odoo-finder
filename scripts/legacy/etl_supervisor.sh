#!/bin/bash

# ETL Supervisor - Ejecuta ETL una vez al día, reinicia solo si hay errores
# Uso: ./scripts/etl_supervisor.sh
#
# Comportamiento:
# - Si el ETL completa exitosamente → termina (no reinicia hasta mañana)
# - Si hay error/timeout → reintenta hasta 10 veces
# - Guarda marca de "completado hoy" para evitar re-ejecuciones

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ETL_SCRIPT="$SCRIPT_DIR/etl_oca_modules.py"
LOG_FILE="$SCRIPT_DIR/etl_supervisor.log"
CHECKPOINT_FILE="$SCRIPT_DIR/etl_checkpoint.json"
COMPLETION_MARKER="$SCRIPT_DIR/.etl_completed_$(date +%Y%m%d)"

# Limpiar markers antiguos (de días anteriores)
find "$SCRIPT_DIR" -name ".etl_completed_*" -mtime +1 -delete 2>/dev/null || true

# Verificar si ya completó HOY
if [ -f "$COMPLETION_MARKER" ]; then
    echo "✅ ETL ya completó hoy ($(date +%Y-%m-%d)). Nada que hacer." | tee -a "$LOG_FILE"
    exit 0
fi

echo "========================================" | tee -a "$LOG_FILE"
echo "ETL Supervisor iniciado: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Configuración
max_attempts=10          # Máximo reintentos por errores
max_runtime=3600         # 1 hora máximo por intento (repos nuevos pueden tardar)
attempt=1

while [ $attempt -le $max_attempts ]; do
    # Mostrar progreso actual si hay checkpoint
    if [ -f "$CHECKPOINT_FILE" ]; then
        current_repo=$(jq -r '.last_repo // "inicio"' "$CHECKPOINT_FILE" 2>/dev/null || echo "?")
        current_idx=$(jq -r '.last_repo_idx // 0' "$CHECKPOINT_FILE" 2>/dev/null || echo "0")
        echo "📊 Checkpoint: repo $current_idx ($current_repo)" | tee -a "$LOG_FILE"
    fi

    echo "🚀 Intento #$attempt/$max_attempts: Ejecutando ETL... ($(date))" | tee -a "$LOG_FILE"

    # Ejecutar ETL con timeout
    set +e  # No salir en error para capturar exit code
    timeout $max_runtime uv run python "$ETL_SCRIPT" 2>&1 | tee -a "$LOG_FILE"
    exit_code=${PIPESTATUS[0]}
    set -e

    # Verificar resultado
    if [ $exit_code -eq 0 ]; then
        # ETL completó exitosamente
        echo "" | tee -a "$LOG_FILE"
        echo "✅ ETL COMPLETADO EXITOSAMENTE" | tee -a "$LOG_FILE"
        echo "📅 Fecha: $(date)" | tee -a "$LOG_FILE"

        # Crear marker de completado para hoy
        touch "$COMPLETION_MARKER"

        # Limpiar checkpoint (ya no necesario)
        rm -f "$CHECKPOINT_FILE"

        echo "========================================" | tee -a "$LOG_FILE"
        echo "ETL Supervisor finalizado: $(date)" | tee -a "$LOG_FILE"
        echo "Intentos utilizados: $attempt" | tee -a "$LOG_FILE"
        echo "========================================" | tee -a "$LOG_FILE"
        exit 0

    elif [ $exit_code -eq 124 ]; then
        # Timeout
        echo "⏱️  Timeout después de $((max_runtime/60)) minutos" | tee -a "$LOG_FILE"

    else
        # Otro error
        echo "⚠️  ETL terminó con código $exit_code" | tee -a "$LOG_FILE"
    fi

    # Incrementar intento y esperar antes de reintentar
    attempt=$((attempt + 1))

    if [ $attempt -le $max_attempts ]; then
        wait_time=$((30 * attempt))  # Backoff exponencial: 30s, 60s, 90s...
        echo "⏳ Esperando ${wait_time}s antes de reintentar..." | tee -a "$LOG_FILE"
        sleep $wait_time
    fi
done

# Si llegamos aquí, agotamos los intentos
echo "" | tee -a "$LOG_FILE"
echo "❌ ERROR: ETL falló después de $max_attempts intentos" | tee -a "$LOG_FILE"
echo "📅 Fecha: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
exit 1
