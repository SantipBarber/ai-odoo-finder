#!/usr/bin/env python3
"""
Extract clean descriptions from OCA GitHub repositories.

This script:
1. Queries modules without description from the database
2. Extracts clean descriptions using fallback strategy:
   - readme/DESCRIPTION.rst (cleanest)
   - README.rst (cleaned)
   - README.md (cleaned)
3. Updates the description column in the database
4. Handles GitHub rate limits by waiting when needed

Usage:
    uv run python scripts/extract_clean_descriptions.py [--batch-size N] [--dry-run]
"""

import argparse
import sys
import time
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, ".")

from sqlalchemy import text

from backend.app.database import SessionLocal
from backend.app.services.content_extraction_service import (
    ContentExtractionService,
    RateLimitError,
    get_content_extraction_service,
)


def get_modules_without_description(db, limit: int = None) -> list:
    """Get all modules that don't have a description yet."""
    query = """
        SELECT id, technical_name, version, repo_name
        FROM odoo_modules
        WHERE description IS NULL OR description = ''
        ORDER BY repo_name, version, technical_name
    """
    if limit:
        query += f" LIMIT {limit}"

    result = db.execute(text(query)).fetchall()
    return [
        {
            "id": row[0],
            "technical_name": row[1],
            "version": row[2],
            "repo_name": row[3],
        }
        for row in result
    ]


def update_module_description(db, module_id: int, description: str) -> bool:
    """Update the description column for a module."""
    try:
        db.execute(
            text(
                """
                UPDATE odoo_modules
                SET description = :description, updated_at = :updated_at
                WHERE id = :id
                """
            ),
            {
                "id": module_id,
                "description": description,
                "updated_at": datetime.now(timezone.utc),
            },
        )
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"    ❌ Error updating DB: {e}")
        return False


def wait_for_rate_limit_reset(reset_time: int) -> None:
    """Wait until rate limit resets."""
    now = time.time()
    wait_seconds = max(0, reset_time - now) + 5  # Add 5 seconds buffer

    if wait_seconds > 0:
        reset_datetime = datetime.fromtimestamp(reset_time)
        print(f"\n⏳ Rate limit exceeded. Waiting until {reset_datetime}...")
        print(f"   Sleeping for {wait_seconds:.0f} seconds...")

        # Show countdown every 30 seconds
        remaining = wait_seconds
        while remaining > 0:
            sleep_time = min(30, remaining)
            time.sleep(sleep_time)
            remaining -= sleep_time
            if remaining > 0:
                print(f"   {remaining:.0f} seconds remaining...")

        print("   ✅ Rate limit reset, resuming...\n")


def print_stats(stats: dict, elapsed: float) -> None:
    """Print extraction statistics."""
    total = stats["processed"]
    rate = total / elapsed * 60 if elapsed > 0 else 0

    print("\n" + "=" * 70)
    print("📊 EXTRACTION STATISTICS")
    print("=" * 70)
    print(f"\n⏱️  Time elapsed: {elapsed:.1f} seconds ({elapsed / 60:.1f} minutes)")
    print(f"📦 Modules processed: {total}")
    print(f"⚡ Rate: {rate:.1f} modules/minute")
    print(f"\n✅ Successful extractions: {stats['success']}")
    print(f"❌ No description found: {stats['no_description']}")
    print(f"⚠️  Errors: {stats['errors']}")

    print("\n📁 By source:")
    for source, count in sorted(stats["by_source"].items()):
        pct = count / total * 100 if total > 0 else 0
        print(f"   - {source}: {count} ({pct:.1f}%)")

    if stats["success"] > 0:
        success_rate = stats["success"] / total * 100
        print(f"\n🎯 Success rate: {success_rate:.1f}%")

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Extract clean descriptions from OCA GitHub repositories"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Limit number of modules to process (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't update database, just show what would be done",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output for each module",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("🚀 OCA MODULE DESCRIPTION EXTRACTION")
    print("=" * 70)
    print(f"📅 Started at: {datetime.now()}")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No database updates will be made")
    print()

    # Initialize services
    db = SessionLocal()
    extractor = get_content_extraction_service()

    # Check rate limit status
    rate_status = extractor.get_rate_limit_status()
    print(f"📡 GitHub API Rate Limit Status:")
    print(f"   - Limit: {rate_status['limit']}")
    print(f"   - Remaining: {rate_status['remaining']}")
    print(f"   - Resets at: {rate_status.get('reset_datetime', 'unknown')}")
    print()

    # Get modules without description
    print("🔍 Querying modules without description...")
    modules = get_modules_without_description(db, limit=args.batch_size)
    total_modules = len(modules)
    print(f"   Found {total_modules} modules to process\n")

    if total_modules == 0:
        print("✅ All modules already have descriptions!")
        db.close()
        return

    # Statistics
    stats = {
        "processed": 0,
        "success": 0,
        "no_description": 0,
        "errors": 0,
        "by_source": {},
    }

    start_time = time.time()
    current_repo = None

    try:
        for i, module in enumerate(modules, 1):
            module_id = module["id"]
            technical_name = module["technical_name"]
            version = module["version"]
            repo_name = module["repo_name"]

            # Show repo header when it changes
            if repo_name != current_repo:
                current_repo = repo_name
                print(f"\n📂 Repository: {repo_name}")

            # Progress indicator
            progress = f"[{i}/{total_modules}]"
            print(f"  {progress} {technical_name} (v{version})...", end=" ", flush=True)

            try:
                # Extract description
                description, source = extractor.get_clean_description(
                    repo_name, version, technical_name
                )

                # Update statistics
                stats["processed"] += 1
                stats["by_source"][source] = stats["by_source"].get(source, 0) + 1

                if description:
                    # Update database
                    if not args.dry_run:
                        if update_module_description(db, module_id, description):
                            stats["success"] += 1
                            desc_preview = (
                                description[:60] + "..." if len(description) > 60 else description
                            )
                            desc_preview = desc_preview.replace("\n", " ")
                            print(f"✅ [{source}] {len(description)} chars")
                            if args.verbose:
                                print(f"      Preview: {desc_preview}")
                        else:
                            stats["errors"] += 1
                    else:
                        stats["success"] += 1
                        print(f"✅ [{source}] {len(description)} chars (dry-run)")
                else:
                    stats["no_description"] += 1
                    print(f"⚠️  No description found")

            except RateLimitError as e:
                # Wait for rate limit reset
                wait_for_rate_limit_reset(e.reset_time)
                # Retry this module
                i -= 1
                continue

            except Exception as e:
                stats["processed"] += 1
                stats["errors"] += 1
                stats["by_source"]["error"] = stats["by_source"].get("error", 0) + 1
                print(f"❌ Error: {e}")

            # Show progress every 100 modules
            if i % 100 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed * 60 if elapsed > 0 else 0
                remaining = (total_modules - i) / rate if rate > 0 else 0
                print(f"\n📈 Progress: {i}/{total_modules} ({i / total_modules * 100:.1f}%)")
                print(f"   Rate: {rate:.1f} modules/min")
                print(f"   ETA: {remaining:.1f} minutes\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        elapsed = time.time() - start_time
        print_stats(stats, elapsed)
        db.close()

    print(f"\n📅 Finished at: {datetime.now()}")


if __name__ == "__main__":
    main()
