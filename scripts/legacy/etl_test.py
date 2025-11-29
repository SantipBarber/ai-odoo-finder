#!/usr/bin/env python3
"""
Script de prueba del ETL mejorado
Procesa solo 2-3 repos nuevos para validar funcionalidad
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Añadir backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.database import SessionLocal
from backend.app.models import OdooModule
from backend.app.services.embedding_service import get_embedding_service
from backend.app.services.github_service import get_github_service

# Servicios
github = get_github_service()
embedding = get_embedding_service()

# ============================================================================
# CONFIGURACIÓN DE PRUEBA
# ============================================================================

# Repos de prueba (NUEVOS, no están en los 5 originales)
TEST_REPOS: List[str] = [
    "manufacture",              # MRP/Manufacturing
    "stock-logistics-warehouse", # Inventory/Logistics
]

# Solo versiones recientes para prueba rápida
TEST_VERSIONS: List[str] = ["16.0", "17.0"]

# Rate limiting
RATE_LIMIT_DELAY = 0.5


def process_module(
    db,
    repo_name: str,
    version: str,
    manifest_path: str,
    repo_metadata: Dict,
) -> bool:
    """Procesar un módulo individual (versión de prueba)"""

    technical_name = manifest_path.split("/")[0]

    # Verificar si ya existe
    existing = (
        db.query(OdooModule)
        .filter(
            OdooModule.technical_name == technical_name,
            OdooModule.version == version,
            OdooModule.repo_name == repo_name,
        )
        .first()
    )

    if existing:
        print(f"    ⏭️  {technical_name} ya existe, saltando...")
        sys.stdout.flush()
        return True

    # Obtener manifest
    print(f"    📄 {technical_name}...", end=" ")
    sys.stdout.flush()

    manifest = github.get_manifest_content(repo_name, version, manifest_path)

    if not manifest:
        print("❌ No se pudo parsear")
        sys.stdout.flush()
        return False

    # Obtener README
    readme_content = github.get_readme_content(repo_name, version, manifest_path)

    # Preparar texto para embedding
    name = manifest.get("name", technical_name)
    summary = manifest.get("summary", "")
    description = manifest.get("description", "")

    text_parts = [name, summary, description]
    if readme_content:
        readme_preview = readme_content[:2000]
        text_parts.append(readme_preview)

    text_for_embedding = ". ".join(filter(None, text_parts))

    # Generar embedding
    try:
        emb = embedding.get_embedding(text_for_embedding)
    except Exception as e:
        print(f"❌ Error en embedding: {e}")
        sys.stdout.flush()
        return False

    # Crear módulo
    module = OdooModule(
        technical_name=technical_name,
        name=name,
        version=version,
        depends=manifest.get("depends", []),
        author=manifest.get("author", ""),
        license=manifest.get("license", "AGPL-3"),
        summary=summary,
        description=description,
        readme=readme_content,
        repo_name=repo_name,
        repo_url=f"https://github.com/OCA/{repo_name}",
        module_path=manifest_path,
        embedding=emb,
        github_stars=repo_metadata["stars"],
        github_issues_open=repo_metadata["open_issues"],
        last_commit_date=datetime.fromisoformat(
            repo_metadata["last_push"].replace("Z", "+00:00")
        ),
    )

    db.add(module)
    db.commit()
    print("✅")
    sys.stdout.flush()

    # Rate limiting
    time.sleep(RATE_LIMIT_DELAY)

    return True


def main() -> None:
    """Pipeline de prueba"""
    print("=" * 80)
    print("🧪 ETL - PRUEBA (Test Run)")
    print("=" * 80)
    print(f"\n📋 Repos de prueba: {', '.join(TEST_REPOS)}")
    print(f"📖 Versiones: {', '.join(TEST_VERSIONS)}")
    print("=" * 80)

    db = SessionLocal()
    start_time = time.time()
    stats = {
        "total_modules_processed": 0,
        "total_modules_success": 0,
        "total_modules_failed": 0,
    }

    try:
        for repo_idx, repo_name in enumerate(TEST_REPOS, 1):
            print(f"\n{'='*80}")
            print(f"📂 [{repo_idx}/{len(TEST_REPOS)}] Repositorio: {repo_name}")
            print(f"{'='*80}")
            sys.stdout.flush()

            # Obtener metadata del repo
            try:
                repo_metadata = github.get_repo_metadata(repo_name)
                print(f"   ⭐ Stars: {repo_metadata['stars']} | Issues: {repo_metadata['open_issues']}")
                sys.stdout.flush()
            except Exception as e:
                print(f"   ❌ Error obteniendo metadata: {e}")
                sys.stdout.flush()
                continue

            # Procesar versiones
            for version in TEST_VERSIONS:
                print(f"\n   📖 Versión: {version}")
                sys.stdout.flush()

                try:
                    manifests = github.find_manifests(repo_name, version)

                    if not manifests:
                        print("      ⚠️  No se encontraron módulos")
                        sys.stdout.flush()
                        continue

                    print(f"      📦 Encontrados: {len(manifests)} módulos")
                    sys.stdout.flush()

                    # Procesar solo primeros 5 módulos (prueba rápida)
                    for manifest_path in manifests[:5]:
                        stats["total_modules_processed"] += 1

                        try:
                            success = process_module(
                                db, repo_name, version, manifest_path, repo_metadata
                            )

                            if success:
                                stats["total_modules_success"] += 1
                            else:
                                stats["total_modules_failed"] += 1

                        except Exception as e:
                            print(f"      ❌ Error procesando {manifest_path}: {e}")
                            sys.stdout.flush()
                            stats["total_modules_failed"] += 1

                    if len(manifests) > 5:
                        print(f"      ⏩ Saltando {len(manifests) - 5} módulos restantes (modo prueba)")
                        sys.stdout.flush()

                except Exception as e:
                    print(f"      ❌ Error en versión {version}: {e}")
                    sys.stdout.flush()

        # Resumen
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 80)
        print("✅ PRUEBA COMPLETADA")
        print("=" * 80)

        print("\n📊 ESTADÍSTICAS:")
        print(f"   ⏱️  Tiempo: {elapsed_time:.1f} segundos")
        print(f"   📦 Módulos procesados: {stats['total_modules_processed']}")
        print(f"   ✅ Éxitos: {stats['total_modules_success']}")
        print(f"   ❌ Fallos: {stats['total_modules_failed']}")

        print("\n🎉 ¡Prueba exitosa! El ETL está listo para ejecución completa.")
        sys.stdout.flush()

    except Exception as e:
        print(f"\n❌ Error en prueba: {e}")
        sys.stdout.flush()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
