#!/bin/bash
# Script de monitoreo del ETL

echo "═══════════════════════════════════════════════════════════════"
echo "📊 Monitor ETL - AI-OdooFinder"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Verificar si existe checkpoint
if [ -f "scripts/etl_checkpoint.json" ]; then
    echo "📌 Último checkpoint:"
    cat scripts/etl_checkpoint.json | python3 -m json.tool
    echo ""
fi

# Estadísticas de base de datos
echo "📦 Estadísticas de Base de Datos:"
uv run python scripts/check_db.py

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "💡 Comandos útiles:"
echo "   watch -n 30 ./scripts/monitor_etl.sh  # Refrescar cada 30s"
echo "   tail -f etl_checkpoint.json            # Ver checkpoints en tiempo real"
echo "═══════════════════════════════════════════════════════════════"
