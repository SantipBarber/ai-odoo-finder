#!/usr/bin/env python3
"""
Script para verificar el contenido de la base de datos
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.database import SessionLocal
from backend.app.models import OdooModule
from sqlalchemy import func


def main():
    db = SessionLocal()

    print("=" * 80)
    print("📊 ESTADÍSTICAS DE BASE DE DATOS")
    print("=" * 80)

    # Total de módulos
    total = db.query(OdooModule).count()
    print(f"\n📦 Total módulos: {total}")

    # Por versión
    print("\n📖 Por versión:")
    versions = ["12.0", "13.0", "14.0", "15.0", "16.0", "17.0", "18.0", "19.0"]
    for version in versions:
        count = db.query(OdooModule).filter(OdooModule.version == version).count()
        print(f"   - Odoo {version}: {count} módulos")

    # Por repositorio (top 10)
    print("\n📂 Top 10 repositorios:")
    repo_counts = (
        db.query(OdooModule.repo_name, func.count(OdooModule.id))
        .group_by(OdooModule.repo_name)
        .order_by(func.count(OdooModule.id).desc())
        .limit(10)
        .all()
    )

    for repo_name, count in repo_counts:
        print(f"   - {repo_name}: {count} módulos")

    # Módulos con README
    with_readme = db.query(OdooModule).filter(OdooModule.readme.isnot(None)).count()
    readme_pct = (with_readme / total * 100) if total > 0 else 0
    print(f"\n📄 Módulos con README: {with_readme} ({readme_pct:.1f}%)")

    # Verificar nuevos repos de prueba
    print("\n🧪 Repos de prueba añadidos:")
    test_repos = ["manufacture", "stock-logistics-warehouse"]
    for repo in test_repos:
        count = db.query(OdooModule).filter(OdooModule.repo_name == repo).count()
        print(f"   - {repo}: {count} módulos")

        if count > 0:
            # Mostrar algunos ejemplos
            samples = (
                db.query(OdooModule.technical_name, OdooModule.version)
                .filter(OdooModule.repo_name == repo)
                .limit(3)
                .all()
            )
            for tech_name, version in samples:
                print(f"      • {tech_name} (v{version})")

    print("\n" + "=" * 80)
    db.close()


if __name__ == "__main__":
    main()
