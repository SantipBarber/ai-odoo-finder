import requests
import json

BASE_URL = "http://localhost:8989"

def test_health():
    print("\n" + "="*70)
    print("🏥 TEST: Health Check")
    print("="*70)

    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_search():
    print("\n" + "="*70)
    print("🔍 TEST: Search")
    print("="*70)

    params = {
        "query": "sales subscriptions and recurring invoices",
        "version": "17.0",
        "limit": 3
    }

    response = requests.post(f"{BASE_URL}/search", params=params)
    print(f"Status: {response.status_code}")

    data = response.json()
    print(f"\nQuery: {data['query']}")
    print(f"Version: {data['version']}")
    print(f"Total results: {data['total_results']}\n")

    for i, module in enumerate(data['results'], 1):
        print(f"{i}. {module['name']}")
        print(f"   Score: {module['score']}/100")
        print(f"   📦 {module['technical_name']}")
        print(f"   ⭐ {module['github_stars']} stars")

def test_module_detail():
    print("\n" + "="*70)
    print("📄 TEST: Module Detail")
    print("="*70)

    # Primero buscar un módulo para obtener su ID
    params = {"query": "sale subscription", "version": "17.0", "limit": 1}
    search_response = requests.post(f"{BASE_URL}/search", params=params)

    if search_response.json()['total_results'] > 0:
        module_id = search_response.json()['results'][0]['id']

        # Obtener detalle
        response = requests.get(f"{BASE_URL}/modules/{module_id}")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    else:
        print("⚠️  No se encontraron módulos para este test")

def test_stats():
    print("\n" + "="*70)
    print("📊 TEST: Statistics")
    print("="*70)

    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_search_with_dependencies():
    print("\n" + "="*70)
    print("🔍 TEST: Search with Dependencies")
    print("="*70)

    params = {
        "query": "inventory management",
        "version": "17.0",
        "dependencies": ["stock"],
        "limit": 3
    }

    response = requests.post(f"{BASE_URL}/search", params=params)
    print(f"Status: {response.status_code}")

    data = response.json()
    print(f"\nQuery: {data['query']}")
    print(f"Version: {data['version']}")
    print(f"Dependencies: {data['dependencies']}")
    print(f"Total results: {data['total_results']}\n")

    for i, module in enumerate(data['results'], 1):
        print(f"{i}. {module['name']}")
        print(f"   Score: {module['score']}/100")
        print(f"   Depends: {', '.join(module['depends'][:5])}")

if __name__ == "__main__":
    print("🧪 Testing AI-OdooFinder API")

    try:
        test_health()
        test_search()
        test_search_with_dependencies()
        test_module_detail()
        test_stats()

        print("\n" + "="*70)
        print("✅ Todos los tests completados")
        print("="*70)

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo: python scripts/run_server.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
