#!/usr/bin/env python3
"""Audit database columns for completeness."""

import os
import sys
from collections import defaultdict

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


def audit_columns():
    """Audit all columns in odoo_modules table."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return

    # Force psycopg3 driver
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    engine = create_engine(database_url)

    # Columns to audit (excluding id, created_at, updated_at)
    columns = [
        "technical_name",
        "name",
        "version",
        "depends",
        "author",
        "license",
        "summary",
        "description",
        "readme",
        "repo_name",
        "repo_url",
        "module_path",
        "github_stars",
        "github_issues_open",
        "last_commit_date",
        "embedding",
        "searchable_text",
        "ai_description",
        "functional_tags",
        "keywords",
        "enriched_at",
        "enrichment_version",
    ]

    with engine.connect() as conn:
        # Get total count
        result = conn.execute(text("SELECT COUNT(*) FROM odoo_modules"))
        total = result.scalar()
        print(f"Total modules: {total:,}\n")
        print("=" * 70)
        print(f"{'Column':<25} {'Non-null':>10} {'Null':>10} {'%Complete':>12}")
        print("=" * 70)

        stats = {}
        for col in columns:
            # Count non-null values
            if col in ["depends", "functional_tags", "keywords"]:
                # For array columns, also check for empty arrays
                query = text(f"""
                    SELECT
                        COUNT(*) FILTER (WHERE {col} IS NOT NULL AND array_length({col}, 1) > 0) as non_null,
                        COUNT(*) FILTER (WHERE {col} IS NULL OR array_length({col}, 1) IS NULL OR array_length({col}, 1) = 0) as null_count
                    FROM odoo_modules
                """)
            elif col == "embedding":
                query = text(f"""
                    SELECT
                        COUNT(*) FILTER (WHERE {col} IS NOT NULL) as non_null,
                        COUNT(*) FILTER (WHERE {col} IS NULL) as null_count
                    FROM odoo_modules
                """)
            elif col == "searchable_text":
                query = text(f"""
                    SELECT
                        COUNT(*) FILTER (WHERE {col} IS NOT NULL) as non_null,
                        COUNT(*) FILTER (WHERE {col} IS NULL) as null_count
                    FROM odoo_modules
                """)
            else:
                # For text/string columns, also check for empty strings
                query = text(f"""
                    SELECT
                        COUNT(*) FILTER (WHERE {col} IS NOT NULL AND {col}::text != '') as non_null,
                        COUNT(*) FILTER (WHERE {col} IS NULL OR {col}::text = '') as null_count
                    FROM odoo_modules
                """)

            result = conn.execute(query)
            row = result.fetchone()
            non_null = row[0]
            null_count = row[1]
            pct = (non_null / total * 100) if total > 0 else 0

            stats[col] = {"non_null": non_null, "null": null_count, "pct": pct}

            # Color coding based on completeness
            if pct == 100:
                status = "✓"
            elif pct >= 90:
                status = "○"
            elif pct > 0:
                status = "△"
            else:
                status = "✗"

            print(f"{col:<25} {non_null:>10,} {null_count:>10,} {pct:>10.1f}% {status}")

        print("=" * 70)

        # Summary by category
        print("\n\n📊 SUMMARY BY CATEGORY\n")

        categories = {
            "Core Identity": ["technical_name", "name", "version", "repo_name"],
            "Odoo Metadata": ["depends", "author", "license"],
            "Descriptions": ["summary", "description", "readme"],
            "GitHub Info": ["repo_url", "module_path", "github_stars", "github_issues_open", "last_commit_date"],
            "Search/Embedding": ["embedding", "searchable_text"],
            "AI Enrichment": ["ai_description", "functional_tags", "keywords", "enriched_at", "enrichment_version"],
        }

        for cat_name, cat_cols in categories.items():
            print(f"\n{cat_name}:")
            for col in cat_cols:
                s = stats[col]
                print(f"  {col:<22} {s['pct']:>6.1f}%  ({s['non_null']:,}/{total:,})")

        # Sample empty fields
        print("\n\n📋 SAMPLE ANALYSIS\n")

        # Check what modules are missing readme
        result = conn.execute(text("""
            SELECT technical_name, version, repo_name
            FROM odoo_modules
            WHERE readme IS NULL OR readme = ''
            LIMIT 5
        """))
        rows = result.fetchall()
        if rows:
            print("Modules without README (sample):")
            for row in rows:
                print(f"  - {row[0]} v{row[1]} ({row[2]})")

        # Check what modules are missing description
        result = conn.execute(text("""
            SELECT technical_name, version, summary
            FROM odoo_modules
            WHERE description IS NULL OR description = ''
            LIMIT 5
        """))
        rows = result.fetchall()
        if rows:
            print("\nModules without description (sample):")
            for row in rows:
                summary_preview = (row[2][:50] + "...") if row[2] and len(row[2]) > 50 else row[2]
                print(f"  - {row[0]} v{row[1]} (summary: {summary_preview})")

        # Check github_stars distribution
        result = conn.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE github_stars = 0) as zero_stars,
                COUNT(*) FILTER (WHERE github_stars > 0 AND github_stars <= 10) as low_stars,
                COUNT(*) FILTER (WHERE github_stars > 10 AND github_stars <= 100) as med_stars,
                COUNT(*) FILTER (WHERE github_stars > 100) as high_stars
            FROM odoo_modules
        """))
        row = result.fetchone()
        print(f"\nGitHub stars distribution:")
        print(f"  0 stars:     {row[0]:,}")
        print(f"  1-10 stars:  {row[1]:,}")
        print(f"  11-100 stars: {row[2]:,}")
        print(f"  100+ stars:  {row[3]:,}")

        # Enrichment quality check
        print("\n\n🤖 ENRICHMENT QUALITY CHECK\n")

        # AI description length distribution
        result = conn.execute(text("""
            SELECT
                AVG(LENGTH(ai_description)) as avg_len,
                MIN(LENGTH(ai_description)) as min_len,
                MAX(LENGTH(ai_description)) as max_len,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY LENGTH(ai_description)) as median_len
            FROM odoo_modules
            WHERE ai_description IS NOT NULL AND ai_description != ''
        """))
        row = result.fetchone()
        print(f"AI Description length:")
        print(f"  Avg: {row[0]:.0f} chars")
        print(f"  Min: {row[1]} chars")
        print(f"  Max: {row[2]} chars")
        print(f"  Median: {row[3]:.0f} chars")

        # Keywords count distribution
        result = conn.execute(text("""
            SELECT
                AVG(array_length(keywords, 1)) as avg_kw,
                MIN(array_length(keywords, 1)) as min_kw,
                MAX(array_length(keywords, 1)) as max_kw
            FROM odoo_modules
            WHERE keywords IS NOT NULL AND array_length(keywords, 1) > 0
        """))
        row = result.fetchone()
        print(f"\nKeywords per module:")
        print(f"  Avg: {row[0]:.1f}")
        print(f"  Min: {row[1]}")
        print(f"  Max: {row[2]}")

        # Functional tags distribution
        result = conn.execute(text("""
            SELECT unnest(functional_tags) as tag, COUNT(*) as cnt
            FROM odoo_modules
            WHERE functional_tags IS NOT NULL AND array_length(functional_tags, 1) > 0
            GROUP BY tag
            ORDER BY cnt DESC
            LIMIT 15
        """))
        rows = result.fetchall()
        print(f"\nTop functional tags:")
        for row in rows:
            print(f"  {row[0]:<25} {row[1]:,}")


if __name__ == "__main__":
    audit_columns()