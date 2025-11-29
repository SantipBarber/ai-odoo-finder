#!/usr/bin/env python3
"""
Get modules that need keyword re-enrichment.
Used by /reenrich-keywords slash command.

Identifies modules where keywords are poor/technical instead of functional.
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.database import SessionLocal
from backend.app.models import OdooModule
from sqlalchemy import text

# Checkpoint file for tracking progress
CHECKPOINT_FILE = os.path.join(os.path.dirname(__file__), ".reenrich_checkpoint.json")


def load_checkpoint() -> set:
    """Load processed IDs from checkpoint."""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE) as f:
                data = json.load(f)
                return set(data.get("processed_ids", []))
        except Exception:
            pass
    return set()


def get_modules_for_reenrich(limit: int = 20) -> list:
    """
    Get modules that have poor keywords (technical instead of functional).

    Criteria for "poor" keywords:
    - Keywords contain the module's technical_name
    - Keywords contain common technical terms (odoo, erp, base, etc.)
    - Very few keywords (< 4)
    """
    db = SessionLocal()
    processed_ids = load_checkpoint()

    try:
        # Get modules where keywords look technical
        sql = text("""
            WITH keyword_analysis AS (
                SELECT
                    id,
                    technical_name,
                    name,
                    version,
                    summary,
                    LEFT(readme, 800) as readme_preview,
                    depends,
                    keywords,
                    ai_description,
                    functional_tags,
                    -- Check if keywords contain technical patterns
                    EXISTS (
                        SELECT 1 FROM unnest(keywords) k
                        WHERE lower(k) = lower(technical_name)
                           OR lower(k) = replace(lower(technical_name), '_', '-')
                           OR lower(k) IN ('odoo', 'erp', 'business', 'module', 'base')
                    ) as has_technical_keywords,
                    -- Check keyword count
                    COALESCE(array_length(keywords, 1), 0) as keyword_count
                FROM odoo_modules
                WHERE enriched_at IS NOT NULL
                  AND keywords IS NOT NULL
            )
            SELECT id, technical_name, name, version, summary, readme_preview,
                   depends, keywords, ai_description, functional_tags
            FROM keyword_analysis
            WHERE has_technical_keywords = true
               OR keyword_count < 4
            ORDER BY
                -- Prioritize more popular modules
                (SELECT github_stars FROM odoo_modules WHERE odoo_modules.id = keyword_analysis.id) DESC NULLS LAST,
                id
            LIMIT :limit_plus
        """)

        # Get extra to account for already processed
        rows = db.execute(sql, {"limit_plus": limit + len(processed_ids)}).fetchall()

        modules = []
        for row in rows:
            # Skip already processed
            if row.id in processed_ids:
                continue

            if len(modules) >= limit:
                break

            modules.append({
                "id": row.id,
                "technical_name": row.technical_name,
                "name": row.name,
                "version": row.version,
                "summary": row.summary or "",
                "readme_preview": row.readme_preview or "",
                "depends": row.depends or [],
                "current_keywords": row.keywords or [],
                "ai_description": row.ai_description or "",
                "functional_tags": row.functional_tags or []
            })

        return modules

    finally:
        db.close()


def get_reenrich_stats():
    """Get statistics about re-enrichment progress."""
    db = SessionLocal()
    processed_ids = load_checkpoint()

    try:
        # Count modules with poor keywords
        sql = text("""
            SELECT COUNT(*)
            FROM odoo_modules
            WHERE enriched_at IS NOT NULL
              AND keywords IS NOT NULL
              AND (
                  EXISTS (
                      SELECT 1 FROM unnest(keywords) k
                      WHERE lower(k) = lower(technical_name)
                         OR lower(k) = replace(lower(technical_name), '_', '-')
                         OR lower(k) IN ('odoo', 'erp', 'business', 'module', 'base')
                  )
                  OR COALESCE(array_length(keywords, 1), 0) < 4
              )
        """)
        total_poor = db.execute(sql).scalar()

        # Count total enriched
        total_enriched = db.query(OdooModule).filter(
            OdooModule.enriched_at.isnot(None)
        ).count()

        # Count re-enriched (v2.0)
        reenriched = db.query(OdooModule).filter(
            OdooModule.enrichment_version == "v2.0"
        ).count()

        return {
            "total_enriched": total_enriched,
            "with_poor_keywords": total_poor,
            "already_processed": len(processed_ids),
            "remaining": total_poor - len(processed_ids),
            "reenriched_v2": reenriched,
            "progress_percent": round((len(processed_ids) / total_poor) * 100, 1) if total_poor > 0 else 0
        }
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Get modules for keyword re-enrichment")
    parser.add_argument("--limit", type=int, default=20, help="Number of modules to get")
    parser.add_argument("--stats", action="store_true", help="Show re-enrichment statistics")
    parser.add_argument("--clear", action="store_true", help="Clear checkpoint to start fresh")

    args = parser.parse_args()

    if args.clear:
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
            print("✅ Checkpoint cleared")
        else:
            print("ℹ️ No checkpoint to clear")
        return

    if args.stats:
        stats = get_reenrich_stats()
        print("\n📊 RE-ENRICHMENT PROGRESS")
        print("=" * 40)
        print(f"Total enriched modules:  {stats['total_enriched']:,}")
        print(f"With poor keywords:      {stats['with_poor_keywords']:,}")
        print(f"Already processed:       {stats['already_processed']:,}")
        print(f"Remaining:               {stats['remaining']:,}")
        print(f"Re-enriched (v2.0):      {stats['reenriched_v2']:,}")
        print(f"Progress:                {stats['progress_percent']}%")
        print("=" * 40)
    else:
        modules = get_modules_for_reenrich(limit=args.limit)

        if not modules:
            print("✅ No modules need keyword re-enrichment!")
            return

        print(f"\n📦 Found {len(modules)} modules needing keyword improvement:\n")
        print(json.dumps(modules, indent=2, ensure_ascii=False))

        # Also show stats
        stats = get_reenrich_stats()
        print(f"\n📊 Progress: {stats['already_processed']:,}/{stats['with_poor_keywords']:,} ({stats['progress_percent']}%)")


if __name__ == "__main__":
    main()