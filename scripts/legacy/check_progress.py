#!/usr/bin/env python3
"""Script para monitorear el progreso del ETL"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Añadir backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.database import SessionLocal
from backend.app.models import OdooModule
from sqlalchemy import func, distinct

# Checkpoint
checkpoint_file = Path("scripts/etl_checkpoint.json")
checkpoint = None
if checkpoint_file.exists():
    with open(checkpoint_file) as f:
        checkpoint = json.load(f)

# Base de datos
db = SessionLocal()
total_modules = db.query(func.count(OdooModule.id)).scalar()
total_repos = db.query(func.count(distinct(OdooModule.repo_name))).scalar()
db.close()

print("=" * 70)
print("🚀 ESTADO DEL ETL - AI-OdooFinder")
print("=" * 70)

if checkpoint:
    idx = checkpoint['last_repo_idx']
    progress = idx / 244 * 100
    remaining = 244 - idx
    timestamp = datetime.fromisoformat(checkpoint['timestamp'])

    print(f"\n📊 PROGRESO:")
    print(f"   ├─ Repositorios: {idx}/244 ({progress:.1f}%)")
    print(f"   ├─ Restantes: {remaining} repos")
    print(f"   └─ Último: {checkpoint['last_repo']} @ {checkpoint['last_version']}")

    print(f"\n💾 BASE DE DATOS:")
    print(f"   ├─ Total módulos: {total_modules:,}")
    print(f"   └─ Repositorios únicos: {total_repos}")

    print(f"\n🕒 ÚLTIMA ACTUALIZACIÓN:")
    print(f"   └─ {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

    # Barra de progreso
    bar_width = 50
    filled = int(bar_width * idx / 244)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"\n[{bar}] {progress:.1f}%")

else:
    print("\n⚠️  Sin checkpoint (ETL completado o no iniciado)")
    print(f"\n💾 BASE DE DATOS:")
    print(f"   ├─ Total módulos: {total_modules:,}")
    print(f"   └─ Repositorios únicos: {total_repos}")

print("\n" + "=" * 70)
print("📝 Comandos útiles:")
print("   • Ver logs:     tail -f scripts/etl_supervisor.log")
print("   • Ver checkpoint: cat scripts/etl_checkpoint.json | jq")
print("   • Detener ETL:  pkill -f etl_supervisor.sh")
print("=" * 70)
