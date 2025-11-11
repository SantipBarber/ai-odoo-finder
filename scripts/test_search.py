import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.database import SessionLocal
from backend.app.services.search_service import get_search_service


def test_search():
    db = SessionLocal()
    search = get_search_service(db)

    # Test 1: Búsqueda simple
    print("=" * 70)
    print("🔍 TEST 1: Búsqueda simple")
    print("=" * 70)
    print("Query: 'sales subscriptions and recurring invoices'")
    print("Version: 17.0\n")

    results = search.search(
        query="sales subscriptions and recurring invoices",
        version="17.0",
        limit=5,
    )

    for i, module in enumerate(results, 1):
        print(f"{i}. {module['name']} ({module['technical_name']})")
        print(f"   Score: {module['score']}/100")
        print(f"   ⭐ {module['github_stars']} stars")
        print(f"   📝 {module['summary']}")
        print()

    # Test 2: Con dependencias
    print("=" * 70)
    print("🔍 TEST 2: Con dependencias")
    print("=" * 70)
    print("Query: 'inventory management'")
    print("Version: 17.0")
    print("Dependencies: ['stock']\n")

    results = search.search(
        query="inventory management",
        version="17.0",
        dependencies=["stock"],
        limit=5,
    )

    for i, module in enumerate(results, 1):
        print(f"{i}. {module['name']}")
        print(f"   Score: {module['score']}/100")
        print(f"   Depends: {', '.join(module['depends'][:5])}")
        print()

    # Test 3: Búsqueda con filtro de score mínimo
    print("=" * 70)
    print("🔍 TEST 3: Con score mínimo")
    print("=" * 70)
    print("Query: 'payment processing'")
    print("Version: 17.0")
    print("Min Score: 50\n")

    results = search.search(
        query="payment processing",
        version="17.0",
        limit=5,
        min_score=50,
    )

    if results:
        for i, module in enumerate(results, 1):
            print(f"{i}. {module['name']} ({module['technical_name']})")
            print(f"   Score: {module['score']}/100")
            print(f"   Distance: {module['distance']}")
            print(f"   📝 {module['summary']}")
            print()
    else:
        print("❌ No se encontraron resultados con score >= 50\n")

    # Test 4: Versión diferente
    print("=" * 70)
    print("🔍 TEST 4: Otra versión")
    print("=" * 70)
    print("Query: 'reporting and analytics'")
    print("Version: 16.0\n")

    results = search.search(
        query="reporting and analytics",
        version="16.0",
        limit=3,
    )

    for i, module in enumerate(results, 1):
        print(f"{i}. {module['name']} ({module['technical_name']})")
        print(f"   Version: {module['version']}")
        print(f"   Score: {module['score']}/100")
        print(f"   📝 {module['summary']}")
        print()

    db.close()
    print("=" * 70)
    print("✅ Tests completados")
    print("=" * 70)


if __name__ == "__main__":
    test_search()

