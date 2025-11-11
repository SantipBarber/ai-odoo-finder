# scripts/test_apis.py
import os
import sys
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_github():
    """Test GitHub API"""
    print("\n🔍 Testing GitHub API...")
    token = os.getenv("GITHUB_TOKEN")
    
    response = requests.get(
        "https://api.github.com/repos/OCA/server-tools",
        headers={"Authorization": f"token {token}"}
    )
    
    if response.status_code == 200:
        print("✅ GitHub API: OK")
        data = response.json()
        print(f"   📦 Repo: {data['name']}")
        print(f"   ⭐ Stars: {data['stargazers_count']}")
        return True
    else:
        print(f"❌ GitHub API: Error {response.status_code}")
        return False

def test_openrouter():
    """Test OpenRouter API"""
    print("\n🔍 Testing OpenRouter API...")
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek/deepseek-v3.1-terminus",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 10
        }
    )
    
    if response.status_code == 200:
        print("✅ OpenRouter API: OK")
        return True
    else:
        print(f"❌ OpenRouter API: Error {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_neon():
    """Test Neon Database"""
    print("\n🔍 Testing Neon Database...")
    db_url = os.getenv("DATABASE_URL")
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Verificar pgVector
        cursor.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
        result = cursor.fetchone()
        
        if result:
            print("✅ Neon DB: OK")
            print(f"   📊 pgVector version: {result[1]}")
            conn.close()
            return True
        else:
            print("❌ pgVector no está instalado")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Neon DB: Error - {e}")
        return False

def main():
    print("="*60)
    print("🧪 VALIDACIÓN DE APIs - AI-OdooFinder")
    print("="*60)
    
    results = []
    results.append(("GitHub", test_github()))
    results.append(("OpenRouter", test_openrouter()))
    results.append(("Neon DB", test_neon()))
    
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    all_ok = all(r[1] for r in results)
    
    if all_ok:
        print("\n🎉 ¡TODO LISTO! Puedes continuar con el desarrollo.")
    else:
        print("\n⚠️  Hay errores. Revisa las configuraciones.")
        sys.exit(1)

if __name__ == "__main__":
    main()