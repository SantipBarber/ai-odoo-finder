# scripts/explore_oca.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def list_oca_repos():
    """Listar repositorios de OCA"""
    print("\n📚 Explorando repositorios de OCA...")
    
    url = "https://api.github.com/orgs/OCA/repos"
    repos = []
    page = 1
    
    while len(repos) < 100:  # Máximo 100 repos
        response = requests.get(
            f"{url}?page={page}&per_page=100",
            headers=HEADERS
        )
        data = response.json()
        
        if not data:
            break
            
        repos.extend(data)
        page += 1
    
    print(f"✅ Encontrados {len(repos)} repositorios")
    
    # Filtrar repos relevantes (con módulos Odoo)
    relevant = [r for r in repos if not any(x in r['name'].lower() 
                for x in ['odoo', 'template', 'tools', 'maintainer'])]
    
    print(f"📦 Repositorios con módulos: {len(relevant)}")
    
    # Top 10 por estrellas
    top_repos = sorted(relevant, key=lambda x: x['stargazers_count'], reverse=True)[:10]
    
    print("\n⭐ Top 10 repositorios:")
    for i, repo in enumerate(top_repos, 1):
        print(f"{i}. {repo['name']:30} ⭐ {repo['stargazers_count']:4} stars")
    
    return [r['name'] for r in top_repos[:5]]  # Devolver top 5

def get_repo_branches(repo_name):
    """Obtener branches de un repo"""
    url = f"https://api.github.com/repos/OCA/{repo_name}/branches"
    response = requests.get(url, headers=HEADERS)
    branches = response.json()
    
    # Filtrar solo versiones de Odoo
    odoo_versions = [b['name'] for b in branches if b['name'] in 
                     ['14.0', '15.0', '16.0', '17.0', '18.0']]
    
    return odoo_versions

def find_manifests(repo_name, version):
    """Encontrar manifests en un repo/version"""
    url = f"https://api.github.com/repos/OCA/{repo_name}/git/trees/{version}?recursive=1"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return []
    
    tree = response.json().get('tree', [])
    
    # Buscar __manifest__.py
    manifests = [item['path'] for item in tree 
                 if item['path'].endswith('__manifest__.py')]
    
    return manifests

def main():
    print("="*60)
    print("🔍 EXPLORACIÓN DE OCA")
    print("="*60)
    
    # 1. Listar repos
    top_repos = list_oca_repos()
    
    # 2. Explorar primer repo
    test_repo = top_repos[0]
    print(f"\n📂 Explorando '{test_repo}'...")
    
    versions = get_repo_branches(test_repo)
    print(f"   Versiones disponibles: {versions}")
    
    if versions:
        test_version = versions[-1]  # Última versión
        print(f"\n🔍 Buscando módulos en {test_version}...")
        manifests = find_manifests(test_repo, test_version)
        print(f"   ✅ Encontrados {len(manifests)} módulos")
        
        if manifests:
            print(f"\n   Ejemplos:")
            for manifest in manifests[:5]:
                module_name = manifest.split('/')[0]
                print(f"   - {module_name}")
    
    print("\n" + "="*60)
    print("✅ Exploración completada")
    print("="*60)

if __name__ == "__main__":
    main()