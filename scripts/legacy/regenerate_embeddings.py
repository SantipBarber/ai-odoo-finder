#!/usr/bin/env python3
"""
Script para regenerar embeddings incluyendo campos de enrichment.

Características:
- Checkpointing: guarda progreso y puede resumir
- Rate limiting: respeta límites de API
- Reintentos automáticos con backoff exponencial
- Manejo robusto de errores
- Logging detallado
- Puede correr desatendido durante la noche

Uso:
    python scripts/regenerate_embeddings.py
    python scripts/regenerate_embeddings.py --batch-size 50
    python scripts/regenerate_embeddings.py --reset  # Empezar desde cero
"""

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Tuple

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text as sql_text
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, engine
from backend.app.models import OdooModule
from backend.app.services.embedding_service import get_embedding_service

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

CHECKPOINT_FILE = Path(__file__).parent / ".embedding_checkpoint.json"
LOG_FILE = Path(__file__).parent / "embedding_regeneration.log"
BATCH_SIZE = 20  # Reducido para Neon (commits más frecuentes)
COMMIT_EVERY = 5  # Commit cada N módulos para evitar timeout SSL
RATE_LIMIT_DELAY = 0.5  # segundos entre requests
MAX_RETRIES = 5
BACKOFF_BASE = 2  # segundos base para backoff exponencial
MAX_TEXT_LENGTH = 8000  # límite de caracteres para el texto

# Control de señales para shutdown graceful
shutdown_requested = False


def signal_handler(signum, frame):
    """Maneja señales de interrupción."""
    global shutdown_requested
    print("\n⚠️  Shutdown solicitado, terminando batch actual...")
    shutdown_requested = True


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# ============================================================================
# LOGGING
# ============================================================================

def log(message: str, level: str = "INFO"):
    """Log a archivo y consola."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    sys.stdout.flush()

    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")


# ============================================================================
# CHECKPOINT
# ============================================================================

def load_checkpoint() -> dict:
    """Carga checkpoint si existe."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {
        "last_processed_id": 0,
        "total_processed": 0,
        "total_errors": 0,
        "started_at": None,
        "last_update": None
    }


def save_checkpoint(checkpoint: dict):
    """Guarda checkpoint."""
    checkpoint["last_update"] = datetime.now().isoformat()
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=2)


def reset_checkpoint():
    """Elimina checkpoint para empezar desde cero."""
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
    log("Checkpoint eliminado, empezando desde cero", "INFO")


# ============================================================================
# EMBEDDING GENERATION
# ============================================================================

def build_text_for_embedding(module: OdooModule) -> str:
    """
    Construye el texto para generar embedding incluyendo enrichment.

    Campos incluidos (en orden de importancia):
    1. name - nombre del módulo
    2. summary - resumen corto
    3. ai_description - descripción generada por AI (NUEVO)
    4. keywords - palabras clave (NUEVO)
    5. description - descripción original
    6. readme - contenido README (truncado)
    """
    parts = []

    # Nombre y summary (siempre presentes)
    if module.name:
        parts.append(module.name)
    if module.summary:
        parts.append(module.summary)

    # AI description (enrichment) - muy importante
    if module.ai_description:
        parts.append(module.ai_description)

    # Keywords (enrichment) - unir como texto
    if module.keywords:
        parts.append(" ".join(module.keywords))

    # Functional tags (enrichment)
    if module.functional_tags:
        parts.append(" ".join(module.functional_tags))

    # Description original
    if module.description:
        # Limitar descripción a 1500 chars
        parts.append(module.description[:1500])

    # README (truncado)
    if module.readme:
        # Limitar README a 2000 chars
        parts.append(module.readme[:2000])

    # Unir todo
    text = ". ".join(filter(None, parts))

    # Truncar si es muy largo
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]

    return text


def generate_embedding_with_retry(
    embedding_service,
    text: str,
    module_name: str
) -> Optional[List[float]]:
    """Genera embedding con reintentos y backoff exponencial."""

    for attempt in range(MAX_RETRIES):
        try:
            embedding = embedding_service.get_embedding(text)
            return embedding

        except Exception as e:
            error_str = str(e)

            # Rate limit - esperar más
            if "429" in error_str or "rate" in error_str.lower():
                wait_time = BACKOFF_BASE * (2 ** attempt) * 2  # Más tiempo para rate limit
                log(f"Rate limit para {module_name}, esperando {wait_time}s (intento {attempt + 1}/{MAX_RETRIES})", "WARN")
                time.sleep(wait_time)
                continue

            # Otros errores
            if attempt < MAX_RETRIES - 1:
                wait_time = BACKOFF_BASE * (2 ** attempt)
                log(f"Error para {module_name}: {error_str}, reintentando en {wait_time}s (intento {attempt + 1}/{MAX_RETRIES})", "WARN")
                time.sleep(wait_time)
            else:
                log(f"Error permanente para {module_name} después de {MAX_RETRIES} intentos: {error_str}", "ERROR")
                return None

    return None


# ============================================================================
# MAIN PROCESSING
# ============================================================================

def get_modules_to_process(db, last_id: int, batch_size: int) -> List[OdooModule]:
    """Obtiene el siguiente batch de módulos a procesar."""
    return db.query(OdooModule).filter(
        OdooModule.id > last_id
    ).order_by(OdooModule.id).limit(batch_size).all()


def extract_module_data(module: OdooModule) -> dict:
    """Extrae datos del módulo para evitar problemas de sesión."""
    return {
        "id": module.id,
        "technical_name": module.technical_name,
        "name": module.name,
        "summary": module.summary,
        "ai_description": module.ai_description,
        "keywords": module.keywords,
        "functional_tags": module.functional_tags,
        "description": module.description,
        "readme": module.readme,
    }


def build_text_from_data(data: dict) -> str:
    """Construye texto para embedding desde datos extraídos."""
    parts = []

    if data["name"]:
        parts.append(data["name"])
    if data["summary"]:
        parts.append(data["summary"])
    if data["ai_description"]:
        parts.append(data["ai_description"])
    if data["keywords"]:
        parts.append(" ".join(data["keywords"]))
    if data["functional_tags"]:
        parts.append(" ".join(data["functional_tags"]))
    if data["description"]:
        parts.append(data["description"][:1500])
    if data["readme"]:
        parts.append(data["readme"][:2000])

    text = ". ".join(filter(None, parts))
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]
    return text


def process_batch(
    db,
    modules: List[OdooModule],
    embedding_service,
    checkpoint: dict
) -> Tuple[int, int, Session]:
    """
    Procesa un batch de módulos con commits frecuentes para Neon.

    Returns:
        (processed_count, error_count, db_session)
    """
    # Extraer datos de módulos ANTES de procesar (evita problemas de sesión)
    modules_data = [extract_module_data(m) for m in modules]

    processed = 0
    errors = 0
    pending_commits = 0

    for data in modules_data:
        if shutdown_requested:
            log("Shutdown solicitado, guardando progreso...", "WARN")
            break

        module_id = data["id"]
        technical_name = data["technical_name"]

        try:
            # Construir texto desde datos extraídos
            text = build_text_from_data(data)

            if not text or len(text.strip()) < 10:
                log(f"Texto vacío para {technical_name}, saltando", "WARN")
                errors += 1
                continue

            # Generar embedding
            embedding = generate_embedding_with_retry(
                embedding_service,
                text,
                technical_name
            )

            if embedding is None:
                errors += 1
                continue

            # Actualizar en BD usando SQL directo
            try:
                db.execute(
                    sql_text("""
                        UPDATE odoo_modules
                        SET embedding = :embedding, updated_at = :updated_at
                        WHERE id = :id
                    """),
                    {
                        "embedding": str(embedding),
                        "updated_at": datetime.utcnow(),
                        "id": module_id
                    }
                )
                pending_commits += 1
                processed += 1
                checkpoint["last_processed_id"] = module_id
                checkpoint["total_processed"] += 1

            except Exception as db_error:
                log(f"Error DB para {technical_name}: {db_error}", "ERROR")
                errors += 1
                # Reconectar si hay error de conexión
                if "SSL" in str(db_error) or "closed" in str(db_error).lower():
                    log("Reconectando a BD tras error SSL...", "WARN")
                    try:
                        db.close()
                    except:
                        pass
                    db = SessionLocal()
                    pending_commits = 0
                continue

            # Commit cada COMMIT_EVERY módulos para evitar timeout SSL de Neon
            if pending_commits >= COMMIT_EVERY:
                try:
                    db.commit()
                    pending_commits = 0
                except Exception as commit_error:
                    log(f"Error en commit parcial: {commit_error}", "ERROR")
                    # Reconectar
                    try:
                        db.rollback()
                        db.close()
                    except:
                        pass
                    db = SessionLocal()
                    pending_commits = 0

            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)

        except Exception as e:
            log(f"Error procesando {technical_name}: {e}", "ERROR")
            errors += 1
            checkpoint["total_errors"] += 1

    # Commit final de lo pendiente
    if pending_commits > 0:
        try:
            db.commit()
        except Exception as e:
            log(f"Error en commit final: {e}", "ERROR")
            try:
                db.rollback()
            except:
                pass

    return processed, errors, db


def run_regeneration(batch_size: int = BATCH_SIZE, reset: bool = False):
    """Ejecuta la regeneración de embeddings."""

    log("=" * 60, "INFO")
    log("REGENERACIÓN DE EMBEDDINGS CON ENRICHMENT", "INFO")
    log("=" * 60, "INFO")

    # Cargar o resetear checkpoint
    if reset:
        reset_checkpoint()

    checkpoint = load_checkpoint()

    if checkpoint["started_at"] is None:
        checkpoint["started_at"] = datetime.now().isoformat()

    # Contar total de módulos
    db = SessionLocal()
    total_modules = db.query(OdooModule).count()
    remaining = db.query(OdooModule).filter(
        OdooModule.id > checkpoint["last_processed_id"]
    ).count()

    log(f"Total módulos: {total_modules:,}", "INFO")
    log(f"Ya procesados: {checkpoint['total_processed']:,}", "INFO")
    log(f"Pendientes: {remaining:,}", "INFO")
    log(f"Batch size: {batch_size}", "INFO")
    log(f"Rate limit: {RATE_LIMIT_DELAY}s entre requests", "INFO")

    # Estimar tiempo
    estimated_seconds = remaining * (RATE_LIMIT_DELAY + 0.5)  # 0.5s por request aprox
    estimated_hours = estimated_seconds / 3600
    log(f"Tiempo estimado: {estimated_hours:.1f} horas", "INFO")
    log("=" * 60, "INFO")

    # Obtener servicio de embeddings
    embedding_service = get_embedding_service()

    # Procesar en batches
    batch_num = 0
    total_processed = 0
    total_errors = 0
    start_time = time.time()

    try:
        while not shutdown_requested:
            # Obtener batch
            modules = get_modules_to_process(
                db,
                checkpoint["last_processed_id"],
                batch_size
            )

            if not modules:
                log("No hay más módulos por procesar", "INFO")
                break

            batch_num += 1
            batch_start = time.time()

            log(f"Batch {batch_num}: procesando {len(modules)} módulos (IDs {modules[0].id}-{modules[-1].id})...", "INFO")

            # Procesar batch (devuelve nueva sesión si hubo reconexión)
            processed, errors, db = process_batch(db, modules, embedding_service, checkpoint)

            total_processed += processed
            total_errors += errors

            # Guardar checkpoint
            save_checkpoint(checkpoint)

            # Stats
            batch_time = time.time() - batch_start
            elapsed = time.time() - start_time
            rate = total_processed / elapsed if elapsed > 0 else 0

            remaining_count = db.query(OdooModule).filter(
                OdooModule.id > checkpoint["last_processed_id"]
            ).count()

            eta_seconds = remaining_count / rate if rate > 0 else 0
            eta = timedelta(seconds=int(eta_seconds))

            log(f"  ✓ Batch {batch_num} completado: {processed} ok, {errors} errores | "
                f"Total: {total_processed:,} | Pendientes: {remaining_count:,} | "
                f"Rate: {rate:.1f}/s | ETA: {eta}", "INFO")

            # Reconectar BD periódicamente para evitar timeouts
            if batch_num % 10 == 0:
                log("Reconectando a BD...", "DEBUG")
                db.close()
                db = SessionLocal()

    except Exception as e:
        log(f"Error fatal: {e}", "ERROR")
        import traceback
        traceback.print_exc()

    finally:
        # Guardar checkpoint final
        save_checkpoint(checkpoint)
        db.close()

        # Resumen final
        elapsed = time.time() - start_time
        log("=" * 60, "INFO")
        log("RESUMEN FINAL", "INFO")
        log("=" * 60, "INFO")
        log(f"Tiempo total: {timedelta(seconds=int(elapsed))}", "INFO")
        log(f"Módulos procesados: {total_processed:,}", "INFO")
        log(f"Errores: {total_errors:,}", "INFO")
        log(f"Último ID procesado: {checkpoint['last_processed_id']}", "INFO")

        if shutdown_requested:
            log("Proceso interrumpido. Ejecutar de nuevo para continuar.", "WARN")
        else:
            log("✅ Regeneración completada!", "INFO")


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Regenera embeddings incluyendo campos de enrichment"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help=f"Tamaño del batch (default: {BATCH_SIZE})"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Empezar desde cero (eliminar checkpoint)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Mostrar estado actual y salir"
    )

    args = parser.parse_args()

    if args.status:
        checkpoint = load_checkpoint()
        print("\n📊 Estado de regeneración de embeddings:")
        print(f"   Último ID procesado: {checkpoint['last_processed_id']}")
        print(f"   Total procesados: {checkpoint['total_processed']:,}")
        print(f"   Total errores: {checkpoint['total_errors']:,}")
        print(f"   Iniciado: {checkpoint['started_at']}")
        print(f"   Última actualización: {checkpoint['last_update']}")

        # Contar pendientes
        db = SessionLocal()
        remaining = db.query(OdooModule).filter(
            OdooModule.id > checkpoint["last_processed_id"]
        ).count()
        db.close()
        print(f"   Pendientes: {remaining:,}")
        return 0

    run_regeneration(
        batch_size=args.batch_size,
        reset=args.reset
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())