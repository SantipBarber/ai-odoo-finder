#!/usr/bin/env python3
"""
Find related modules for benchmark queries.
Helps identify valid alternative modules that should be included in the benchmark.
"""

import sys

sys.path.insert(0, ".")

from sqlalchemy import text

from backend.app.database import SessionLocal


def main():
    db = SessionLocal()

    # Para cada query problemática, buscar módulos relacionados válidos
    queries_to_check = [
        # Query 1: modelo 303 AEAT
        {"id": 1, "query": "modelo 303 IVA AEAT", "version": "16.0", "pattern": "%aeat_mod%"},
        # Query 3: facturae
        {"id": 3, "query": "facturae", "version": "16.0", "pattern": "%facturae%"},
        # Query 4: informes financieros
        {
            "id": 4,
            "query": "informes financieros",
            "version": "16.0",
            "pattern": "%financial_report%",
        },
        # Query 8: DMS
        {"id": 8, "query": "DMS", "version": "16.0", "pattern": "%dms%"},
        # Query 9: quality control
        {"id": 9, "query": "quality control", "version": "16.0", "pattern": "%quality%"},
        # Query 10: hr expense
        {"id": 10, "query": "hr expense", "version": "16.0", "pattern": "%hr_expense%"},
        # Query 11: subcontracting MRP
        {"id": 11, "query": "subcontracting", "version": "12.0", "pattern": "%subcontract%"},
        # Query 12: KPI mis_builder
        {"id": 12, "query": "mis_builder", "version": "16.0", "pattern": "%mis_%"},
    ]

    print("=" * 70)
    print("MÓDULOS RELACIONADOS PARA BENCHMARK")
    print("=" * 70)

    for q in queries_to_check:
        print(f"\n🔍 Query {q['id']}: {q['query']} (v{q['version']})")
        print("-" * 50)
        rows = db.execute(
            text("""
            SELECT technical_name, LEFT(description, 100) as desc
            FROM odoo_modules
            WHERE version = :version
              AND technical_name LIKE :pattern
            ORDER BY technical_name
            LIMIT 10
        """),
            {"version": q["version"], "pattern": q["pattern"]},
        ).fetchall()

        for r in rows:
            desc = r[1].replace("\n", " ")[:80] if r[1] else "No description"
            print(f"  - {r[0]}")
            print(f"    {desc}...")

    db.close()


if __name__ == "__main__":
    main()
