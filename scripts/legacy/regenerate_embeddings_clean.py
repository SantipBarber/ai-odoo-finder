#!/usr/bin/env python3
"""
Regenerate embeddings using clean description (without readme noise).

This script regenerates embeddings for modules that have a clean description,
using only: name + summary + description

This produces much better semantic embeddings because:
- description has ~859 chars of useful content (vs 4100 chars of readme noise)
- 80% reduction in noise
- Better semantic understanding of module functionality

Usage:
    uv run python scripts/regenerate_embeddings_clean.py
    uv run python scripts/regenerate_embeddings_clean.py --batch-size 50
    uv run python scripts/regenerate_embeddings_clean.py --dry-run
    uv run python scripts/regenerate_embeddings_clean.py --reset  # Start from scratch

Run with caffeinate to prevent sleep:
    caffeinate -i uv run python scripts/regenerate_embeddings_clean.py
"""

import argparse
import json
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text as sql_text

from backend.app.database import SessionLocal
from backend.app.services.embedding_service import get_embedding_service

# ============================================================================
# CONFIGURATION
# ============================================================================

CHECKPOINT_FILE = Path(__file__).parent / ".embedding_clean_checkpoint.json"
LOG_FILE = Path(__file__).parent / "embedding_clean_regeneration.log"
BATCH_SIZE = 20
COMMIT_EVERY = 5
RATE_LIMIT_DELAY = 0.3  # seconds between requests
MAX_RETRIES = 5
BACKOFF_BASE = 2
MAX_TEXT_LENGTH = 4000  # Much smaller now - no readme noise

# Graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle interrupt signals."""
    global shutdown_requested
    print("\n⚠️  Shutdown requested, finishing current batch...")
    shutdown_requested = True


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# ============================================================================
# LOGGING
# ============================================================================


def log(message: str, level: str = "INFO"):
    """Log to file and console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    print(log_line)
    sys.stdout.flush()

    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")


# ============================================================================
# CHECKPOINT MANAGEMENT
# ============================================================================


def load_checkpoint() -> dict:
    """Load checkpoint from file."""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_id": 0, "processed": 0, "errors": 0, "started_at": None}


def save_checkpoint(checkpoint: dict):
    """Save checkpoint to file."""
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=2, default=str)


def reset_checkpoint():
    """Reset checkpoint file."""
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
    log("Checkpoint reset")


# ============================================================================
# TEXT BUILDING - CLEAN VERSION (NO README NOISE)
# ============================================================================


def build_clean_text_for_embedding(module_data: dict) -> str:
    """
    Build text for embedding using ONLY clean content.

    Fields included (in order of importance):
    1. name - module name
    2. summary - short summary
    3. description - CLEAN description from GitHub (the new field!)

    NO README - that's the whole point of this script!
    """
    parts = []

    # Name (always present)
    if module_data.get("name"):
        parts.append(module_data["name"])

    # Summary (75% have it)
    if module_data.get("summary"):
        parts.append(module_data["summary"])

    # Clean description - THIS IS THE KEY IMPROVEMENT
    if module_data.get("description"):
        parts.append(module_data["description"])

    # Join with separator
    text = ". ".join(filter(None, parts))

    # Truncate if too long (shouldn't happen with clean content)
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]

    return text


# ============================================================================
# EMBEDDING GENERATION
# ============================================================================


def generate_embedding_with_retry(
    embedding_service, text: str, module_name: str
) -> Optional[List[float]]:
    """Generate embedding with retries and exponential backoff."""

    for attempt in range(MAX_RETRIES):
        try:
            embedding = embedding_service.get_embedding(text)
            return embedding

        except Exception as e:
            error_str = str(e)

            # Rate limit - wait longer
            if "429" in error_str or "rate" in error_str.lower():
                wait_time = BACKOFF_BASE * (2**attempt) * 2
                log(
                    f"Rate limit for {module_name}, waiting {wait_time}s "
                    f"(attempt {attempt + 1}/{MAX_RETRIES})",
                    "WARN",
                )
                time.sleep(wait_time)
                continue

            # Other errors
            if attempt < MAX_RETRIES - 1:
                wait_time = BACKOFF_BASE * (2**attempt)
                log(
                    f"Error for {module_name}: {error_str}, retrying in {wait_time}s "
                    f"(attempt {attempt + 1}/{MAX_RETRIES})",
                    "WARN",
                )
                time.sleep(wait_time)
            else:
                log(
                    f"Permanent error for {module_name} after {MAX_RETRIES} attempts: {error_str}",
                    "ERROR",
                )
                return None

    return None


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================


def get_modules_with_description(db, last_id: int, batch_size: int) -> List[dict]:
    """Get modules that have clean description filled."""
    result = db.execute(
        sql_text("""
            SELECT id, technical_name, name, summary, description
            FROM odoo_modules
            WHERE id > :last_id
              AND description IS NOT NULL
              AND description != ''
            ORDER BY id
            LIMIT :limit
        """),
        {"last_id": last_id, "limit": batch_size},
    ).fetchall()

    return [
        {
            "id": row[0],
            "technical_name": row[1],
            "name": row[2],
            "summary": row[3],
            "description": row[4],
        }
        for row in result
    ]


def update_embedding(db, module_id: int, embedding: List[float]) -> bool:
    """Update embedding for a module using raw psycopg cursor."""
    try:
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        # Use raw psycopg connection to avoid SQLAlchemy parameter issues with ::vector
        raw_conn = db.connection().connection
        cursor = raw_conn.cursor()

        cursor.execute(
            """
            UPDATE odoo_modules
            SET embedding = %s::vector,
                updated_at = %s
            WHERE id = %s
            """,
            (embedding_str, datetime.now(timezone.utc), module_id),
        )
        cursor.close()
        return True
    except Exception as e:
        log(f"Error updating embedding for module {module_id}: {e}", "ERROR")
        return False


def get_total_with_description(db) -> int:
    """Get total count of modules with description."""
    result = db.execute(
        sql_text("""
            SELECT COUNT(*) FROM odoo_modules
            WHERE description IS NOT NULL AND description != ''
        """)
    ).scalar()
    return result or 0


# ============================================================================
# MAIN PROCESSING
# ============================================================================


def process_batch(
    db, modules: List[dict], embedding_service, checkpoint: dict, dry_run: bool
) -> tuple:
    """Process a batch of modules."""
    success = 0
    errors = 0
    commit_counter = 0

    for module in modules:
        if shutdown_requested:
            break

        module_id = module["id"]
        technical_name = module["technical_name"]

        # Build clean text
        text = build_clean_text_for_embedding(module)
        text_len = len(text)

        if dry_run:
            log(f"[DRY-RUN] {technical_name}: {text_len} chars")
            success += 1
            checkpoint["last_id"] = module_id
            continue

        # Generate embedding
        embedding = generate_embedding_with_retry(embedding_service, text, technical_name)

        if embedding:
            # Update database
            if update_embedding(db, module_id, embedding):
                success += 1
                commit_counter += 1
                log(f"✅ {technical_name}: {text_len} chars → embedding updated")
            else:
                errors += 1
                log(f"❌ {technical_name}: DB update failed", "ERROR")
        else:
            errors += 1
            log(f"❌ {technical_name}: Embedding generation failed", "ERROR")

        # Update checkpoint
        checkpoint["last_id"] = module_id
        checkpoint["processed"] += 1
        if errors > 0:
            checkpoint["errors"] = checkpoint.get("errors", 0) + 1

        # Commit periodically to avoid timeouts
        if commit_counter >= COMMIT_EVERY:
            db.commit()
            save_checkpoint(checkpoint)
            commit_counter = 0

        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)

    # Final commit for batch
    if not dry_run:
        db.commit()
        save_checkpoint(checkpoint)

    return success, errors


def run_regeneration(batch_size: int, dry_run: bool, reset: bool):
    """Main regeneration loop."""
    global shutdown_requested

    # Reset checkpoint if requested
    if reset:
        reset_checkpoint()

    # Load checkpoint
    checkpoint = load_checkpoint()
    if checkpoint.get("started_at") is None:
        checkpoint["started_at"] = datetime.now().isoformat()

    log("=" * 70)
    log("🚀 EMBEDDING REGENERATION (CLEAN DESCRIPTION)")
    log("=" * 70)
    log(f"Batch size: {batch_size}")
    log(f"Dry run: {dry_run}")
    log(f"Checkpoint: last_id={checkpoint['last_id']}, processed={checkpoint['processed']}")

    # Initialize services
    db = SessionLocal()
    embedding_service = get_embedding_service()

    try:
        # Get total count
        total = get_total_with_description(db)
        log(f"Total modules with description: {total}")

        if checkpoint["last_id"] > 0:
            # Count remaining
            remaining = db.execute(
                sql_text("""
                    SELECT COUNT(*) FROM odoo_modules
                    WHERE id > :last_id
                      AND description IS NOT NULL
                      AND description != ''
                """),
                {"last_id": checkpoint["last_id"]},
            ).scalar()
            log(f"Remaining to process: {remaining}")
        else:
            remaining = total

        if remaining == 0:
            log("✅ All modules already processed!")
            return

        # Estimate time
        rate_per_min = 60 / (RATE_LIMIT_DELAY + 0.5)  # Approximate
        eta_minutes = remaining / rate_per_min
        log(f"Estimated time: {eta_minutes:.0f} minutes ({eta_minutes / 60:.1f} hours)")

        start_time = time.time()
        total_success = 0
        total_errors = 0
        batch_num = 0

        # Main loop
        while not shutdown_requested:
            # Get next batch
            modules = get_modules_with_description(db, checkpoint["last_id"], batch_size)

            if not modules:
                log("✅ No more modules to process")
                break

            batch_num += 1
            log(
                f"\n📦 Batch {batch_num}: {len(modules)} modules (starting from id {checkpoint['last_id']})"
            )

            # Process batch
            success, errors = process_batch(db, modules, embedding_service, checkpoint, dry_run)
            total_success += success
            total_errors += errors

            # Progress report
            elapsed = time.time() - start_time
            rate = total_success / elapsed * 60 if elapsed > 0 else 0
            processed_total = checkpoint["processed"]

            log(f"   Batch complete: {success} ✅, {errors} ❌")
            log(
                f"   Total progress: {processed_total}/{total} ({processed_total / total * 100:.1f}%)"
            )
            log(f"   Rate: {rate:.1f} modules/min")

            if total_success > 0 and not dry_run:
                eta_remaining = (total - processed_total) / rate if rate > 0 else 0
                log(f"   ETA: {eta_remaining:.0f} minutes")

    except Exception as e:
        log(f"Fatal error: {e}", "ERROR")
        import traceback

        traceback.print_exc()

    finally:
        # Final stats
        elapsed = time.time() - start_time
        log("\n" + "=" * 70)
        log("📊 FINAL STATISTICS")
        log("=" * 70)
        log(f"Time elapsed: {elapsed / 60:.1f} minutes")
        log(f"Total processed: {checkpoint['processed']}")
        log(f"Success: {total_success}")
        log(f"Errors: {total_errors}")
        log(f"Last ID: {checkpoint['last_id']}")

        if shutdown_requested:
            log("\n⚠️  Process interrupted - can resume with same command")

        save_checkpoint(checkpoint)
        db.close()


# ============================================================================
# ENTRY POINT
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate embeddings using clean description (no readme noise)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help=f"Modules per batch (default: {BATCH_SIZE})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't update database, just show what would be done",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset checkpoint and start from beginning",
    )

    args = parser.parse_args()

    run_regeneration(
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        reset=args.reset,
    )


if __name__ == "__main__":
    main()
