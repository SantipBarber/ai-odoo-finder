#!/usr/bin/env python3
"""
Analyze field statistics for embedding analysis.
Helps understand what content is available in the database.
"""

import sys

sys.path.insert(0, ".")

from sqlalchemy import text

from backend.app.database import SessionLocal


def main():
    db = SessionLocal()

    print("=" * 70)
    print("📊 ESTADÍSTICAS GLOBALES DE LONGITUD DE CAMPOS")
    print("=" * 70)

    stats = db.execute(
        text("""
        SELECT
            COUNT(*) as total,
            AVG(LENGTH(name)) as avg_name,
            AVG(LENGTH(summary)) as avg_summary,
            AVG(LENGTH(readme)) as avg_readme,
            AVG(CASE WHEN description IS NOT NULL AND description != '' THEN LENGTH(description) END) as avg_desc,
            AVG(LENGTH(ai_description)) as avg_ai_desc,
            COUNT(CASE WHEN summary IS NOT NULL AND summary != '' THEN 1 END) as has_summary,
            COUNT(CASE WHEN readme IS NOT NULL AND LENGTH(readme) > 100 THEN 1 END) as has_readme,
            COUNT(CASE WHEN description IS NOT NULL AND description != '' THEN 1 END) as has_desc,
            COUNT(CASE WHEN ai_description IS NOT NULL AND ai_description != '' THEN 1 END) as has_ai_desc
        FROM odoo_modules
    """)
    ).fetchone()

    total = stats[0]
    print(f"\nTotal módulos: {total}")
    print(f"\n📏 Longitud promedio de campos:")
    print(f"   - name:           {stats[1]:.0f} chars")
    print(f"   - summary:        {stats[2]:.0f} chars")
    print(f"   - readme:         {stats[3]:.0f} chars")
    if stats[4]:
        print(f"   - description:    {stats[4]:.0f} chars (solo los que tienen)")
    else:
        print(f"   - description:    N/A (ninguno tiene)")
    if stats[5]:
        print(f"   - ai_description: {stats[5]:.0f} chars")
    else:
        print(f"   - ai_description: N/A")

    print(f"\n📊 Cobertura de campos:")
    print(f"   - Con summary:        {stats[6]:>6} ({stats[6] / total * 100:.1f}%)")
    print(f"   - Con readme >100ch:  {stats[7]:>6} ({stats[7] / total * 100:.1f}%)")
    print(f"   - Con description:    {stats[8]:>6} ({stats[8] / total * 100:.1f}%)")
    print(f"   - Con ai_description: {stats[9]:>6} ({stats[9] / total * 100:.1f}%)")

    # Comparar readme vs description
    print("\n" + "=" * 70)
    print("📊 COMPARACIÓN README vs DESCRIPTION (limpia)")
    print("=" * 70)

    comparison = db.execute(
        text("""
        SELECT
            AVG(LENGTH(readme)) as avg_readme,
            AVG(LENGTH(description)) as avg_desc,
            AVG(LENGTH(readme) - LENGTH(description)) as avg_diff
        FROM odoo_modules
        WHERE description IS NOT NULL AND description != ''
          AND readme IS NOT NULL AND readme != ''
    """)
    ).fetchone()

    if comparison[0]:
        print(f"\nEn módulos que tienen ambos:")
        print(f"   - README promedio:      {comparison[0]:.0f} chars")
        print(f"   - description promedio: {comparison[1]:.0f} chars")
        print(
            f"   - Reducción:            {comparison[2]:.0f} chars ({comparison[2] / comparison[0] * 100:.0f}% menos ruido)"
        )

    # Ejemplo de contenido actual del embedding
    print("\n" + "=" * 70)
    print("📊 EJEMPLO: QUÉ CONTIENE EL EMBEDDING ACTUAL")
    print("=" * 70)

    sample = db.execute(
        text("""
        SELECT
            technical_name,
            name,
            summary,
            LEFT(readme, 500) as readme_preview,
            LEFT(description, 500) as desc_preview
        FROM odoo_modules
        WHERE description IS NOT NULL AND description != ''
          AND readme IS NOT NULL AND LENGTH(readme) > 500
        LIMIT 3
    """)
    ).fetchall()

    for row in sample:
        print(f"\n🔹 {row[0]}")
        print(f"   name: {row[1]}")
        print(f"   summary: {row[2]}")
        print(f"\n   README (primeros 300 chars - CON RUIDO):")
        print(f"   {row[3][:300]}...")
        print(f"\n   DESCRIPTION (limpia - primeros 300 chars):")
        print(f"   {row[4][:300]}...")

    # Qué se usó para generar el embedding
    print("\n" + "=" * 70)
    print("📊 CONTENIDO ACTUAL DEL EMBEDDING")
    print("=" * 70)
    print("""
El embedding se generó con (etl_oca_modules.py):

    text_for_embedding = ". ".join([
        name,              # ~30 chars
        summary,           # ~50 chars (solo 87% tienen)
        description,       # ❌ VACÍO en el ETL original
        readme[:2000]      # ~4500 chars pero con 85% RUIDO
    ])

PROBLEMA: El embedding captura principalmente ruido del README
(badges, imágenes, links, texto repetitivo de OCA...)
""")

    print("\n" + "=" * 70)
    print("📊 SI REGENERAMOS CON DESCRIPTION LIMPIA")
    print("=" * 70)
    print("""
Nuevo embedding sería:

    text_for_embedding = ". ".join([
        name,              # ~30 chars
        summary,           # ~50 chars
        description,       # ~500-1000 chars LIMPIOS y ÚTILES ✅
    ])

BENEFICIO: Embedding semántico de mejor calidad sin ruido
""")

    db.close()


if __name__ == "__main__":
    main()
