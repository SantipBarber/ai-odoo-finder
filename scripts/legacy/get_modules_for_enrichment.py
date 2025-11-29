#!/usr/bin/env python3
"""
Get modules that need enrichment from the database.
Used by /enrich slash command.
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.database import SessionLocal
from backend.app.models import OdooModule
from sqlalchemy import text


def get_modules_for_enrichment(limit: int = 20, version: str = None):
    """
    Get modules that haven't been enriched yet.
    Returns ONE entry per technical_name (not per version).

    Args:
        limit: Maximum number of modules to return
        version: Optional Odoo version filter (e.g., "16.0")

    Returns:
        List of modules needing enrichment (unique by technical_name)
    """
    db = SessionLocal()

    try:
        # Use raw SQL to get distinct technical_names with best version
        # Priority: latest version with most stars
        from sqlalchemy import text

        sql = text("""
            WITH ranked AS (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY technical_name
                        ORDER BY version DESC, github_stars DESC NULLS LAST
                    ) as rn
                FROM odoo_modules
                WHERE enriched_at IS NULL
            )
            SELECT id, technical_name, name, version, summary, description,
                   readme, depends, repo_name, github_stars
            FROM ranked
            WHERE rn = 1
            ORDER BY github_stars DESC NULLS LAST
            LIMIT :limit
        """)

        rows = db.execute(sql, {"limit": limit}).fetchall()

        # Convert to dict for JSON output
        modules = []
        for row in rows:
            modules.append({
                "id": row.id,
                "technical_name": row.technical_name,
                "name": row.name,
                "version": row.version,
                "summary": row.summary or "",
                "description": (row.description or "")[:500],  # Truncate for context
                "readme_preview": (row.readme or "")[:1000],   # Truncate for context
                "depends": row.depends or [],
                "repo_name": row.repo_name,
                "github_stars": row.github_stars
            })

        return modules

    finally:
        db.close()


def get_enrichment_stats():
    """Get statistics about enrichment progress."""
    db = SessionLocal()

    try:
        total = db.query(OdooModule).count()
        enriched = db.query(OdooModule).filter(
            OdooModule.enriched_at.isnot(None)
        ).count()
        remaining = total - enriched

        return {
            "total_modules": total,
            "enriched": enriched,
            "remaining": remaining,
            "progress_percent": round((enriched / total) * 100, 1) if total > 0 else 0
        }
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Get modules for enrichment")
    parser.add_argument("--limit", type=int, default=20, help="Number of modules to get")
    parser.add_argument("--version", type=str, help="Filter by Odoo version (e.g., 16.0)")
    parser.add_argument("--stats", action="store_true", help="Show enrichment statistics only")

    args = parser.parse_args()

    if args.stats:
        stats = get_enrichment_stats()
        print("\n📊 ENRICHMENT PROGRESS")
        print("=" * 40)
        print(f"Total modules:  {stats['total_modules']:,}")
        print(f"Enriched:       {stats['enriched']:,}")
        print(f"Remaining:      {stats['remaining']:,}")
        print(f"Progress:       {stats['progress_percent']}%")
        print("=" * 40)
    else:
        modules = get_modules_for_enrichment(limit=args.limit, version=args.version)

        if not modules:
            print("✅ No modules need enrichment!")
            return

        print(f"\n📦 Found {len(modules)} modules needing enrichment:\n")
        print(json.dumps(modules, indent=2, ensure_ascii=False))

        # Also show stats
        stats = get_enrichment_stats()
        print(f"\n📊 Progress: {stats['enriched']:,}/{stats['total_modules']:,} ({stats['progress_percent']}%)")


if __name__ == "__main__":
    main()
