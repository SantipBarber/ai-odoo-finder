import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Añadir backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.exc import DBAPIError, OperationalError

from backend.app.database import SessionLocal
from backend.app.models import OdooModule
from backend.app.services.embedding_service import get_embedding_service
from backend.app.services.enrichment_service import get_enrichment_service
from backend.app.services.github_service import get_github_service

# Servicios
github = get_github_service()
embedding = get_embedding_service()
enrichment = get_enrichment_service()

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# AUTO-DESCUBRIMIENTO: Si True, ignora TARGET_REPOS y obtiene TODOS los repos de OCA
AUTO_DISCOVER_REPOS = False  # TEMP: False para prueba

# Filtro de calidad (solo si AUTO_DISCOVER_REPOS=True)
MIN_STARS = 0  # Mínimo de estrellas en GitHub

# Lista manual (solo si AUTO_DISCOVER_REPOS=False)
TARGET_REPOS: List[str] = [
    "l10n-canada",  # TEMP: Repo NO indexado para probar enrichment
]

# Versiones de Odoo a procesar
ODOO_VERSIONS: List[str] = ["18.0"]  # TEMP: Solo 18.0 para prueba

# Sistema de checkpoints
CHECKPOINT_FILE = Path(__file__).parent / "etl_checkpoint.json"
ENABLE_CHECKPOINTS = True

# Rate limiting (segundos entre requests a GitHub)
RATE_LIMIT_DELAY = 0.5

# Enrichment con IA
ENABLE_ENRICHMENT = True  # Si False, solo usa fallback heurístico

# Reintentos para errores de BD
MAX_DB_RETRIES = 3
DB_RETRY_DELAY = 5  # segundos

# ============================================================================
# FUNCIONES DE RECONEXIÓN Y RETRY
# ============================================================================


def reconnect_db(db) -> SessionLocal:
    """Reconectar a la base de datos si la conexión se perdió"""
    try:
        db.close()
        print("   🔄 Reconectando a la base de datos...")
        sys.stdout.flush()
        time.sleep(2)
        new_db = SessionLocal()
        print("   ✅ Reconexión exitosa")
        sys.stdout.flush()
        return new_db
    except Exception as e:
        print(f"   ❌ Error en reconexión: {e}")
        sys.stdout.flush()
        raise


def is_connection_error(error: Exception) -> bool:
    """Detectar si es un error de conexión que requiere reconexión"""
    error_msg = str(error).lower()
    connection_errors = [
        "server closed the connection",
        "connection already closed",
        "connection was closed",
        "broken pipe",
        "can't reconnect",
        "lost connection",
        "connection refused",
    ]
    return any(err in error_msg for err in connection_errors)


def db_operation_with_retry(operation, max_retries=MAX_DB_RETRIES):
    """
    Ejecutar operación de BD con reintentos automáticos.

    Args:
        operation: Función lambda que ejecuta la operación
        max_retries: Número máximo de reintentos

    Returns:
        Resultado de la operación
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            return operation()
        except (OperationalError, DBAPIError) as e:
            last_error = e

            if is_connection_error(e):
                wait_time = DB_RETRY_DELAY * (attempt + 1)
                print(f"   ⚠️  Error de conexión (intento {attempt + 1}/{max_retries})")
                print(f"   ⏳ Esperando {wait_time}s antes de reintentar...")
                sys.stdout.flush()
                time.sleep(wait_time)
                continue
            else:
                # No es error de conexión, no reintentar
                raise
        except Exception as e:
            # Otros errores no relacionados con BD
            raise

    # Si llegamos aquí, agotamos los reintentos
    raise last_error


# ============================================================================
# FUNCIONES DE OPTIMIZACIÓN - DETECTAR REPOS YA INDEXADOS
# ============================================================================


def get_fully_indexed_repos(db) -> set:
    """
    Obtener repos que ya tienen módulos indexados para TODAS las versiones.
    Esto permite saltar repos completos sin hacer requests a GitHub.
    """
    try:
        from sqlalchemy import func

        # Obtener repos únicos que ya tienen módulos en BD
        result = db.query(OdooModule.repo_name).distinct().all()
        indexed_repos = {r[0] for r in result}

        print(f"📦 Repos ya indexados en BD: {len(indexed_repos)}")
        sys.stdout.flush()

        return indexed_repos
    except Exception as e:
        print(f"⚠️  Error obteniendo repos indexados: {e}")
        sys.stdout.flush()
        return set()


def repo_version_has_modules(db, repo_name: str, version: str) -> bool:
    """Verificar si un repo+versión específico ya tiene módulos en BD"""
    try:
        count = (
            db.query(OdooModule)
            .filter(OdooModule.repo_name == repo_name, OdooModule.version == version)
            .count()
        )
        return count > 0
    except Exception:
        return False


# ============================================================================
# FUNCIONES DE CHECKPOINT
# ============================================================================


def save_checkpoint(
    repo_name: str,
    version: str,
    modules_processed: int,
    repo_idx: int = 0,
    repos_list: List[str] = None,
) -> None:
    """Guardar progreso del ETL"""
    if not ENABLE_CHECKPOINTS:
        return

    # Cargar checkpoint existente para preservar repos_list si no se provee
    existing_repos_list = None
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                existing = json.load(f)
                existing_repos_list = existing.get("repos_list")
        except Exception:
            pass

    checkpoint = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "last_repo": repo_name,
        "last_repo_idx": repo_idx,  # Guardar índice en lugar de solo nombre
        "last_version": version,
        "modules_processed": modules_processed,
        "repos_list": repos_list
        if repos_list is not None
        else existing_repos_list,  # Preservar lista de repos
    }

    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=2)


def load_checkpoint() -> Optional[Dict]:
    """Cargar último checkpoint guardado"""
    if not ENABLE_CHECKPOINTS or not CHECKPOINT_FILE.exists():
        return None

    try:
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Error cargando checkpoint: {e}")
        return None


def clear_checkpoint() -> None:
    """Limpiar checkpoint al finalizar ETL"""
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()


def should_skip(repo_idx: int, repo_name: str, version: str, checkpoint: Optional[Dict]) -> bool:
    """Determinar si debemos saltar un repo/versión basado en checkpoint"""
    if not checkpoint:
        return False

    last_repo_idx = checkpoint.get("last_repo_idx", 0)
    last_repo = checkpoint.get("last_repo")
    last_version = checkpoint.get("last_version")

    # Comparar por ÍNDICE no por nombre alfabético
    if repo_idx < last_repo_idx:
        return True
    if repo_idx == last_repo_idx and repo_name == last_repo and version <= last_version:
        return True

    return False


def process_module(
    db,
    repo_name: str,
    version: str,
    manifest_path: str,
    repo_metadata: Dict,
) -> tuple[bool, Optional[SessionLocal]]:
    """
    Procesar un módulo individual con reconexión automática.

    Args:
        db: Sesión de base de datos
        repo_name: Nombre del repositorio
        version: Versión de Odoo
        manifest_path: Path al __manifest__.py
        repo_metadata: Metadata del repositorio (stars, issues, etc)

    Returns:
        Tupla (éxito, nueva_sesión_db_si_reconectó)
    """

    # Extraer nombre técnico del módulo
    technical_name = manifest_path.split("/")[0]

    try:
        # Verificar si ya existe (con retry automático)
        def check_existing():
            return (
                db.query(OdooModule)
                .filter(
                    OdooModule.technical_name == technical_name,
                    OdooModule.version == version,
                    OdooModule.repo_name == repo_name,
                )
                .first()
            )

        existing = db_operation_with_retry(check_existing)

        if existing:
            print(f"    ⏭️  {technical_name} ya existe, saltando...")
            sys.stdout.flush()
            return (True, None)

    except (OperationalError, DBAPIError) as e:
        if is_connection_error(e):
            # Reconectar y reintentar
            print(f"    🔄 Reconexión necesaria para {technical_name}...")
            sys.stdout.flush()
            db = reconnect_db(db)
            # Intentar verificar existencia nuevamente
            try:
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
                    return (True, db)
            except Exception:
                print(f"    ❌ Error verificando existencia de {technical_name}")
                sys.stdout.flush()
                return (False, db)

    # Obtener manifest
    print(f"    📄 {technical_name}...", end=" ")
    sys.stdout.flush()

    manifest = github.get_manifest_content(repo_name, version, manifest_path)

    if not manifest:
        print("❌ No se pudo parsear")
        sys.stdout.flush()
        return (False, None)

    # Obtener README (si existe)
    readme_content = github.get_readme_content(repo_name, version, manifest_path)

    # Preparar datos del módulo
    name = manifest.get("name", technical_name)
    summary = manifest.get("summary", "")
    description = manifest.get("description", "")
    depends = manifest.get("depends", [])

    # =========================================================================
    # ENRICHMENT: Generar descripción IA, tags y keywords ANTES del embedding
    # =========================================================================
    enrichment_data = None
    if ENABLE_ENRICHMENT:
        print("🤖", end=" ")
        sys.stdout.flush()
        enrichment_data = enrichment.enrich_module(
            technical_name=technical_name,
            name=name,
            summary=summary,
            description=description,
            readme=readme_content[:1500] if readme_content else None,
            depends=depends,
            repo_name=repo_name,
        )

    # Fallback si enrichment falló o está deshabilitado
    if not enrichment_data or not enrichment_data.get("ai_description"):
        enrichment_data = enrichment.generate_fallback_enrichment(
            technical_name=technical_name,
            name=name,
            summary=summary,
            depends=depends,
        )

    # =========================================================================
    # EMBEDDING: Incluir contenido enriquecido para mejor búsqueda semántica
    # =========================================================================
    text_parts = [name, summary, description]

    # Añadir descripción IA si existe (mejora significativamente la búsqueda)
    if enrichment_data.get("ai_description"):
        text_parts.append(enrichment_data["ai_description"])

    # Añadir keywords
    if enrichment_data.get("keywords"):
        text_parts.append(" ".join(enrichment_data["keywords"]))

    # Añadir README preview
    if readme_content:
        readme_preview = readme_content[:1500]
        text_parts.append(readme_preview)

    text_for_embedding = ". ".join(filter(None, text_parts))

    # Generar embedding con reintentos
    emb = None
    for attempt in range(3):
        try:
            emb = embedding.get_embedding(text_for_embedding)
            break
        except Exception as e:
            if attempt < 2:
                wait_time = 2 * (attempt + 1)
                print(f"⚠️ Error embedding (intento {attempt + 1}/3), esperando {wait_time}s...")
                sys.stdout.flush()
                time.sleep(wait_time)
            else:
                print(f"❌ Error en embedding: {e}")
                sys.stdout.flush()
                # Hacer rollback y reconectar para limpiar sesión
                try:
                    db.rollback()
                except Exception:
                    pass
                # Reconectar para evitar sesión corrupta
                try:
                    print(f"    🔄 Reconectando tras fallo de embedding...")
                    sys.stdout.flush()
                    db = reconnect_db(db)
                    return (False, db)  # Devolver nueva sesión limpia
                except Exception as reconnect_err:
                    print(f"    ❌ Error en reconexión: {reconnect_err}")
                    sys.stdout.flush()
                    return (False, None)

    # Crear módulo con todos los campos incluyendo enrichment
    module = OdooModule(
        technical_name=technical_name,
        name=name,
        version=version,
        depends=depends,
        author=manifest.get("author", ""),
        license=manifest.get("license", "AGPL-3"),
        summary=summary,
        description=description,
        readme=readme_content,  # Guardar README completo
        repo_name=repo_name,
        repo_url=f"https://github.com/OCA/{repo_name}",
        module_path=manifest_path,
        embedding=emb,
        github_stars=repo_metadata["stars"],
        github_issues_open=repo_metadata["open_issues"],
        last_commit_date=datetime.fromisoformat(repo_metadata["last_push"].replace("Z", "+00:00")),
        # Enrichment fields
        ai_description=enrichment_data.get("ai_description"),
        functional_tags=enrichment_data.get("functional_tags", []),
        keywords=enrichment_data.get("keywords", []),
        enriched_at=datetime.now(timezone.utc) if enrichment_data.get("ai_description") else None,
        enrichment_version="v2.0-grok4fast" if enrichment_data.get("ai_description") else None,
    )

    # Insertar con retry automático
    try:

        def insert_module():
            db.add(module)
            db.commit()

        db_operation_with_retry(insert_module)
        print("✅")
        sys.stdout.flush()

    except (OperationalError, DBAPIError) as e:
        if is_connection_error(e):
            # Reconectar y reintentar una vez más
            print(f"    🔄 Reconexión necesaria para insertar {technical_name}...")
            sys.stdout.flush()
            db = reconnect_db(db)

            try:
                db.add(module)
                db.commit()
                print("✅")
                sys.stdout.flush()
                return (True, db)
            except Exception as retry_err:
                print(f"    ❌ Error en reintento: {retry_err}")
                sys.stdout.flush()
                db.rollback()
                return (False, db)
        else:
            print(f"    ❌ Error de BD: {e}")
            sys.stdout.flush()
            db.rollback()
            return (False, None)

    # Rate limiting
    time.sleep(RATE_LIMIT_DELAY)

    return (True, None)


def main() -> None:
    """Pipeline ETL principal con auto-descubrimiento y checkpoints"""
    print("=" * 80)
    print("🚀 ETL - AI-OdooFinder (Enhanced)")
    print("=" * 80)

    # Inicialización
    db = SessionLocal()
    start_time = time.time()
    stats = {
        "total_repos": 0,
        "total_modules_processed": 0,
        "total_modules_success": 0,
        "total_modules_skipped": 0,
        "total_modules_failed": 0,
        "repos_processed": [],
        "repos_failed": [],
    }

    try:
        # Cargar checkpoint si existe
        checkpoint = load_checkpoint()
        if checkpoint:
            print(f"\n📌 Checkpoint encontrado: {checkpoint['timestamp']}")
            print(f"   Última posición: {checkpoint['last_repo']} @ {checkpoint['last_version']}")
            print(f"   Módulos procesados: {checkpoint['modules_processed']}")
            print("   🔄 Resumiendo desde última posición...\n")
            sys.stdout.flush()

        # Obtener lista de repositorios (usar checkpoint si existe para mantener orden)
        if checkpoint and checkpoint.get("repos_list"):
            print(f"\n♻️  Usando lista de repos del checkpoint (orden consistente)")
            sys.stdout.flush()
            repos_to_process = checkpoint["repos_list"]
        elif AUTO_DISCOVER_REPOS:
            print(f"\n🔍 Modo: AUTO-DESCUBRIMIENTO (min_stars={MIN_STARS})")
            sys.stdout.flush()
            repos_to_process = github.get_all_oca_repos(min_stars=MIN_STARS)
        else:
            print(f"\n📋 Modo: LISTA MANUAL ({len(TARGET_REPOS)} repos)")
            sys.stdout.flush()
            repos_to_process = TARGET_REPOS

        stats["total_repos"] = len(repos_to_process)
        print(f"📊 Total de repositorios a procesar: {len(repos_to_process)}")
        print("=" * 80)
        sys.stdout.flush()

        # OPTIMIZACIÓN: Obtener repos ya indexados para saltarlos
        indexed_repos = get_fully_indexed_repos(db)
        repos_to_skip = len([r for r in repos_to_process if r in indexed_repos])
        repos_new = len(repos_to_process) - repos_to_skip
        print(f"⏭️  Repos a saltar (ya indexados): {repos_to_skip}")
        print(f"🆕 Repos nuevos a procesar: {repos_new}")
        print("=" * 80)
        sys.stdout.flush()

        # Procesar cada repositorio
        for repo_idx, repo_name in enumerate(repos_to_process, 1):
            # OPTIMIZACIÓN: Saltar repos completamente indexados
            if repo_name in indexed_repos:
                print(
                    f"\n⏭️  [{repo_idx}/{len(repos_to_process)}] {repo_name} - Ya indexado, saltando..."
                )
                sys.stdout.flush()
                stats["repos_processed"].append(repo_name)
                # Guardar checkpoint para no perder progreso
                save_checkpoint(
                    repo_name, ODOO_VERSIONS[-1], stats["total_modules_processed"], repo_idx, None
                )
                continue

            print(f"\n{'=' * 80}")
            print(f"📂 [{repo_idx}/{len(repos_to_process)}] Repositorio: {repo_name}")
            print(f"{'=' * 80}")
            sys.stdout.flush()

            # Obtener metadata del repo
            try:
                repo_metadata = github.get_repo_metadata(repo_name)
                print(
                    f"   ⭐ Stars: {repo_metadata['stars']} | Issues: {repo_metadata['open_issues']}"
                )
                sys.stdout.flush()
            except Exception as e:
                print(f"   ❌ Error obteniendo metadata: {e}")
                sys.stdout.flush()
                stats["repos_failed"].append(repo_name)
                continue

            repo_has_modules = False

            # Procesar cada versión de Odoo
            for version in ODOO_VERSIONS:
                # Verificar si debemos saltar (checkpoint)
                if should_skip(repo_idx, repo_name, version, checkpoint):
                    print(f"   ⏩ Saltando {version} (ya procesado)")
                    sys.stdout.flush()
                    continue

                print(f"\n   📖 Versión: {version}")
                sys.stdout.flush()

                try:
                    # Buscar manifests
                    manifests = github.find_manifests(repo_name, version)

                    if not manifests:
                        print("      ⚠️  No se encontraron módulos")
                        sys.stdout.flush()
                        continue

                    print(f"      📦 Encontrados: {len(manifests)} módulos")
                    sys.stdout.flush()

                    # Procesar cada módulo
                    for manifest_path in manifests:
                        stats["total_modules_processed"] += 1

                        try:
                            success, new_db = process_module(
                                db, repo_name, version, manifest_path, repo_metadata
                            )

                            # Si hubo reconexión, actualizar la sesión
                            if new_db is not None:
                                db = new_db

                            if success:
                                stats["total_modules_success"] += 1
                                repo_has_modules = True
                            else:
                                stats["total_modules_failed"] += 1

                        except (OperationalError, DBAPIError) as e:
                            if is_connection_error(e):
                                print(f"      🔄 Error de conexión, reconectando...")
                                sys.stdout.flush()
                                try:
                                    db = reconnect_db(db)
                                    print(f"      ✅ Reconexión exitosa, continuando...")
                                    sys.stdout.flush()
                                except Exception as reconnect_err:
                                    print(f"      ❌ Error crítico de reconexión: {reconnect_err}")
                                    sys.stdout.flush()
                                    stats["total_modules_failed"] += 1
                                    continue
                            else:
                                print(f"      ❌ Error de BD procesando {manifest_path}: {e}")
                                sys.stdout.flush()
                                stats["total_modules_failed"] += 1
                                db.rollback()
                                continue

                        except Exception as e:
                            print(f"      ❌ Error procesando {manifest_path}: {e}")
                            sys.stdout.flush()
                            stats["total_modules_failed"] += 1
                            continue

                    # Guardar checkpoint después de cada versión (con retry)
                    try:
                        # Solo pasar repos_list en el primer checkpoint
                        repos_list_to_save = (
                            repos_to_process
                            if repo_idx == 1 and version == ODOO_VERSIONS[0]
                            else None
                        )
                        save_checkpoint(
                            repo_name,
                            version,
                            stats["total_modules_processed"],
                            repo_idx,
                            repos_list_to_save,
                        )
                    except Exception as e:
                        print(f"      ⚠️  Error guardando checkpoint: {e}")
                        sys.stdout.flush()

                except Exception as e:
                    print(f"      ❌ Error en versión {version}: {e}")
                    sys.stdout.flush()
                    continue

            if repo_has_modules:
                stats["repos_processed"].append(repo_name)

        # Limpiar checkpoint al finalizar
        clear_checkpoint()

        # Resumen final
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 80)
        print("✅ ETL COMPLETADO")
        print("=" * 80)

        # Estadísticas de ejecución
        print("\n📊 ESTADÍSTICAS DE EJECUCIÓN:")
        print(f"   ⏱️  Tiempo total: {elapsed_time / 60:.1f} minutos")
        print(f"   📂 Repos procesados: {len(stats['repos_processed'])}/{stats['total_repos']}")
        print(f"   📦 Módulos encontrados: {stats['total_modules_processed']}")
        print(f"   ✅ Módulos añadidos: {stats['total_modules_success']}")
        print(f"   ⏭️  Módulos ya existentes: {stats['total_modules_skipped']}")
        print(f"   ❌ Módulos con error: {stats['total_modules_failed']}")

        # Estadísticas de base de datos
        print("\n📊 ESTADÍSTICAS DE BASE DE DATOS:")
        total_db = db.query(OdooModule).count()
        print(f"   Total módulos en DB: {total_db}")

        by_version: Dict[str, int] = {}
        for v in ODOO_VERSIONS:
            count = db.query(OdooModule).filter(OdooModule.version == v).count()
            by_version[v] = count

        for version, count in by_version.items():
            print(f"   - Odoo {version}: {count} módulos")

        # Módulos con README
        with_readme = db.query(OdooModule).filter(OdooModule.readme.isnot(None)).count()
        readme_percentage = (with_readme / total_db * 100) if total_db > 0 else 0
        print(f"\n   📄 Módulos con README: {with_readme} ({readme_percentage:.1f}%)")

        # Módulos con enrichment IA
        with_enrichment = db.query(OdooModule).filter(OdooModule.ai_description.isnot(None)).count()
        enrichment_percentage = (with_enrichment / total_db * 100) if total_db > 0 else 0
        print(f"   🤖 Módulos con AI enrichment: {with_enrichment} ({enrichment_percentage:.1f}%)")

        print("\n🎉 ¡Listo para búsquedas!")
        sys.stdout.flush()

    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        print(f"💾 Checkpoint guardado. Ejecuta nuevamente para continuar.")
        sys.stdout.flush()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.stdout.flush()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
