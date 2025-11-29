#!/usr/bin/env python3
"""
Script de exploración de contenido en repositorios OCA GitHub.
Objetivo: Ver qué contenido útil hay disponible para extraer.
"""

import sys
import os
import requests
from typing import Optional, Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.config import get_settings
from backend.app.database import SessionLocal
from backend.app.models import OdooModule

settings = get_settings()


def get_github_headers() -> Dict:
    """Headers para GitHub API con autenticación."""
    return {
        "Authorization": f"token {settings.gh_token}",
        "Accept": "application/vnd.github.v3+json"
    }


def build_module_url(repo_name: str, version: str, technical_name: str) -> str:
    """Construye URL del módulo en GitHub."""
    return f"https://github.com/OCA/{repo_name}/tree/{version}/{technical_name}"


def build_api_url(repo_name: str, version: str, technical_name: str) -> str:
    """Construye URL de la API de GitHub para listar contenido."""
    return f"https://api.github.com/repos/OCA/{repo_name}/contents/{technical_name}?ref={version}"


def build_raw_url(repo_name: str, version: str, path: str) -> str:
    """Construye URL para contenido raw."""
    return f"https://raw.githubusercontent.com/OCA/{repo_name}/{version}/{path}"


def list_module_contents(repo_name: str, version: str, technical_name: str) -> Optional[List[Dict]]:
    """Lista el contenido de un módulo usando GitHub API."""
    url = build_api_url(repo_name, version, technical_name)

    try:
        response = requests.get(url, headers=get_github_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ Error HTTP: {e}")
        return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def get_raw_content(repo_name: str, version: str, path: str) -> Optional[str]:
    """Descarga contenido raw de un archivo."""
    url = build_raw_url(repo_name, version, path)

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  ❌ Error descargando {path}: {e}")
        return None


def explore_module(module: Dict) -> Dict:
    """
    Explora un módulo y retorna información sobre su contenido.
    """
    repo_name = module['repo_name']
    version = module['version']
    technical_name = module['technical_name']

    result = {
        'technical_name': technical_name,
        'url': build_module_url(repo_name, version, technical_name),
        'files': [],
        'interesting_files': [],
        'readme_preview': None,
        'has_html_description': False,
        'has_models': False,
    }

    # Listar contenido del directorio raíz
    contents = list_module_contents(repo_name, version, technical_name)

    if not contents:
        return result

    # Analizar archivos encontrados
    for item in contents:
        file_info = {
            'name': item['name'],
            'type': item['type'],
            'size': item.get('size', 0),
            'path': item['path']
        }
        result['files'].append(file_info)

        # Archivos interesantes
        if item['name'] in ['README.rst', 'README.md', '__manifest__.py']:
            result['interesting_files'].append(file_info)

        # Buscar en subdirectorios
        if item['type'] == 'dir':
            if item['name'] == 'static':
                result['has_html_description'] = True  # Potencialmente
            elif item['name'] == 'models':
                result['has_models'] = True

    # Descargar README para preview
    readme_file = next((f for f in result['files'] if f['name'] in ['README.rst', 'README.md']), None)
    if readme_file:
        content = get_raw_content(repo_name, version, readme_file['path'])
        if content:
            result['readme_preview'] = content[:2000]

    # Buscar static/description/index.html
    static_contents = list_module_contents(repo_name, version, f"{technical_name}/static/description")
    if static_contents:
        for item in static_contents:
            if item['name'] == 'index.html':
                result['has_html_description'] = True
                html_content = get_raw_content(repo_name, version, item['path'])
                if html_content:
                    result['html_description_preview'] = html_content[:1500]
                break

    return result


def get_sample_modules(db, limit: int = 5) -> List[Dict]:
    """Obtiene módulos de ejemplo para explorar."""

    # Módulos específicos interesantes
    test_names = [
        ('l10n_es_aeat_mod303', '16.0'),
        ('l10n_es_facturae', '16.0'),
        ('account_banking_sepa_credit_transfer', '16.0'),
        ('dms', '16.0'),
        ('sale_subscription', '16.0'),
    ]

    modules = []
    for name, version in test_names[:limit]:
        mod = db.query(OdooModule).filter(
            OdooModule.technical_name == name,
            OdooModule.version == version
        ).first()

        if mod:
            modules.append({
                'technical_name': mod.technical_name,
                'name': mod.name,
                'version': mod.version,
                'repo_name': mod.repo_name,
                'readme_in_db': len(mod.readme) if mod.readme else 0,
            })

    return modules


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    print("=" * 80)
    print("EXPLORACIÓN DE CONTENIDO OCA GITHUB")
    print("=" * 80)

    db = SessionLocal()

    try:
        modules = get_sample_modules(db, limit)
        print(f"\n📦 Explorando {len(modules)} módulos...\n")

        for i, mod in enumerate(modules, 1):
            print(f"\n{'='*80}")
            print(f"[{i}/{len(modules)}] {mod['technical_name']} (v{mod['version']})")
            print(f"{'='*80}")

            result = explore_module(mod)

            print(f"\n🔗 URL: {result['url']}")
            print(f"\n📁 Archivos encontrados ({len(result['files'])}):")

            for f in result['files']:
                icon = "📁" if f['type'] == 'dir' else "📄"
                size = f"({f['size']} bytes)" if f['size'] > 0 else ""
                print(f"   {icon} {f['name']} {size}")

            print(f"\n📊 Análisis:")
            print(f"   - README en BD: {mod['readme_in_db']} chars")
            print(f"   - Tiene models/: {'✅' if result['has_models'] else '❌'}")
            print(f"   - Tiene static/description/index.html: {'✅' if result.get('html_description_preview') else '❌'}")

            if result.get('readme_preview'):
                print(f"\n📝 README preview (primeros 500 chars):")
                print("-" * 40)
                print(result['readme_preview'][:500])
                print("-" * 40)

            if result.get('html_description_preview'):
                print(f"\n🌐 HTML Description preview (primeros 500 chars):")
                print("-" * 40)
                print(result['html_description_preview'][:500])
                print("-" * 40)

    finally:
        db.close()

    print("\n" + "=" * 80)
    print("✅ Exploración completada")
    print("=" * 80)


if __name__ == "__main__":
    main()