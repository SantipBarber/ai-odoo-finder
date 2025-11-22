#!/usr/bin/env python
"""
Script para validar que los expected_modules del benchmark existen en la BD.
"""
import json
import sys
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.database import SessionLocal


def main():
    """Valida expected_modules contra la base de datos."""
    print("="*80)
    print("Validación de Expected Modules - Benchmark Phase 1")
    print("="*80)

    # Load benchmark queries
    with open("tests/benchmark_queries.json") as f:
        data = json.load(f)

    # Extract all unique expected modules
    expected_modules = set()
    for query in data["benchmark_queries"]:
        expected_modules.update(query["expected_modules"])

    expected_modules = sorted(expected_modules)

    print(f"\n✓ Loaded {len(expected_modules)} unique expected modules from benchmark\n")

    # Query database
    db = SessionLocal()
    try:
        # Create SQL query to check which modules exist
        modules_list = ", ".join(f"'{m}'" for m in expected_modules)

        query = text(f"""
        WITH expected AS (
            SELECT unnest(ARRAY[{modules_list}]) AS module_name
        )
        SELECT
            e.module_name,
            om.technical_name,
            om.version,
            CASE
                WHEN om.technical_name IS NULL THEN '❌ NOT FOUND'
                ELSE '✅ EXISTS'
            END as status
        FROM expected e
        LEFT JOIN odoo_modules om ON e.module_name = om.technical_name
        ORDER BY status DESC, e.module_name;
        """)

        results = db.execute(query).fetchall()

        # Process results
        found = []
        not_found = []

        print("VALIDATION RESULTS:")
        print("-" * 80)

        for row in results:
            module_name, technical_name, version, status = row
            if technical_name:
                found.append(module_name)
                print(f"✅ {module_name:40} | Found in v{version}")
            else:
                not_found.append(module_name)
                print(f"❌ {module_name:40} | NOT FOUND")

        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total Expected Modules: {len(expected_modules)}")
        print(f"Found in Database:      {len(found)} ({len(found)/len(expected_modules)*100:.1f}%)")
        print(f"Not Found:              {len(not_found)} ({len(not_found)/len(expected_modules)*100:.1f}%)")

        if not_found:
            print(f"\n⚠️  WARNING: {len(not_found)} modules are missing from the database!")
            print("This explains the 0% precision in the benchmark results.")
            print("\nMissing modules:")
            for mod in not_found[:10]:
                print(f"  - {mod}")
            if len(not_found) > 10:
                print(f"  ... and {len(not_found) - 10} more")
        else:
            print("\n✅ All expected modules exist in the database!")

        print("="*80)

        return 0 if len(found) > len(expected_modules) * 0.5 else 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
