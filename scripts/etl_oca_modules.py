import os
import sys
from datetime import datetime
from typing import Dict, List

# Añadir backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.database import SessionLocal
from backend.app.models import OdooModule
from backend.app.services.embedding_service import get_embedding_service
from backend.app.services.github_service import get_github_service

# Servicios
github = get_github_service()
embedding = get_embedding_service()

# Configuración
TARGET_REPOS: List[str] = [
    "web",
    "server-tools",
    "account-financial-tools",
    "sale-workflow",
    "purchase-workflow",
]

ODOO_VERSIONS: List[str] = ["16.0", "17.0", "18.0"]


def process_module(
    db,
    repo_name: str,
    version: str,
    manifest_path: str,
    repo_metadata: Dict,
) -> None:
    """
    Procesar un módulo individual.

    Args:
        db: Sesión de base de datos
        repo_name: Nombre del repositorio
        version: Versión de Odoo
        manifest_path: Path al __manifest__.py
        repo_metadata: Metadata del repositorio (stars, issues, etc)
    """

    # Extraer nombre técnico del módulo
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
        return

    # Obtener manifest
    print(f"    📄 {technical_name}...", end=" ")
    manifest = github.get_manifest_content(repo_name, version, manifest_path)

    if not manifest:
        print("❌ No se pudo parsear")
        return

    # Preparar texto para embedding
    name = manifest.get("name", technical_name)
    summary = manifest.get("summary", "")
    description = manifest.get("description", "")

    # Combinar textos relevantes
    text_for_embedding = f"{name}. {summary}. {description}"

    # Generar embedding
    try:
        emb = embedding.get_embedding(text_for_embedding)
    except Exception as e:
        print(f"❌ Error en embedding: {e}")
        return

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


def main() -> None:
    """Pipeline ETL principal"""
    print("=" * 70)
    print("🚀 ETL - AI-OdooFinder")
    print("=" * 70)

    db = SessionLocal()
    total_modules = 0

    try:
        for repo_name in TARGET_REPOS:
            print(f"\n📂 Repositorio: {repo_name}")
            print("-" * 70)

            # Obtener metadata del repo
            try:
                repo_metadata = github.get_repo_metadata(repo_name)
                print(f"   ⭐ Stars: {repo_metadata['stars']}")
            except Exception as e:
                print(f"   ❌ Error obteniendo metadata: {e}")
                continue

            for version in ODOO_VERSIONS:
                print(f"\n   📖 Versión: {version}")

                try:
                    # Buscar manifests
                    manifests = github.find_manifests(repo_name, version)

                    if not manifests:
                        print("      ⚠️  No se encontraron módulos")
                        continue

                    print(f"      📦 Encontrados: {len(manifests)} módulos")

                    # Procesar cada módulo
                    for manifest_path in manifests:
                        try:
                            process_module(
                                db, repo_name, version, manifest_path, repo_metadata
                            )
                            total_modules += 1
                        except Exception as e:
                            print(f"      ❌ Error procesando {manifest_path}: {e}")
                            continue

                except Exception as e:
                    print(f"      ❌ Error en versión {version}: {e}")
                    continue

        # Resumen final
        print("\n" + "=" * 70)
        print("✅ ETL COMPLETADO")
        print("=" * 70)

        # Estadísticas
        total_db = db.query(OdooModule).count()
        by_version: Dict[str, int] = {}
        for v in ODOO_VERSIONS:
            count = db.query(OdooModule).filter(OdooModule.version == v).count()
            by_version[v] = count

        print("\n📊 ESTADÍSTICAS:")
        print(f"   Total módulos en DB: {total_db}")
        for version, count in by_version.items():
            print(f"   - Odoo {version}: {count} módulos")

        print("\n🎉 ¡Listo para búsquedas!")

    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
