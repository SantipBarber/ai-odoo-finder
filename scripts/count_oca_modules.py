"""
Cuenta los módulos OCA disponibles en GitHub sin indexar nada.

Usa las mismas funciones de descubrimiento que el ETL (get_all_oca_repos y
find_manifests), pero no toca la base de datos ni llama a OpenRouter. Solo
necesita GH_TOKEN (variable de entorno o .env).

Cuenta dos cifras por versión:
  - modules: manifiestos de primer nivel (<modulo>/__manifest__.py), es decir,
    módulos instalables desde el repo.
  - etl_manifests: todos los __manifest__.py a cualquier profundidad, que es lo
    que procesaría el ETL.

Uso:
    python scripts/count_oca_modules.py
    python scripts/count_oca_modules.py --versions 17.0 18.0 --repos web sale-workflow
    python scripts/count_oca_modules.py --stats-url http://localhost:8989/stats
    python scripts/count_oca_modules.py --output conteo.json
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.services.github_service import GitHubService

# Mismas versiones que procesa el ETL (scripts/etl_oca_modules.py)
ODOO_VERSIONS: List[str] = ["12.0", "13.0", "14.0", "15.0", "16.0", "17.0", "18.0", "19.0"]

# Peticiones simultáneas a la API de GitHub
MAX_WORKERS = 8


def load_gh_token() -> str:
    """GH_TOKEN del entorno o, si no está, del .env de la raíz del repo."""
    token = os.environ.get("GH_TOKEN")
    if token:
        return token

    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() == "GH_TOKEN":
                return value.strip().strip("\"'")

    sys.exit("Falta GH_TOKEN (variable de entorno o .env)")


def check_token(github: GitHubService) -> None:
    """find_manifests devuelve [] ante cualquier error: sin esta comprobación, un
    token caducado daría un conteo de 0 en lugar de un error."""
    response = requests.get(f"{github.base_url}/rate_limit", headers=github.headers, timeout=30)
    if response.status_code != 200:
        sys.exit(f"GH_TOKEN rechazado por GitHub (HTTP {response.status_code})")
    remaining = response.json()["resources"]["core"]["remaining"]
    print(f"Peticiones disponibles a la API de GitHub: {remaining}", file=sys.stderr)


def count_repo_version(github: GitHubService, repo: str, version: str) -> Dict:
    manifests = github.find_manifests(repo, version)
    top_level = [path for path in manifests if path.count("/") == 1]
    return {
        "repo": repo,
        "version": version,
        "modules": len(top_level),
        "etl_manifests": len(manifests),
    }


def fetch_stats(url: str) -> Optional[Dict]:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"No se pudo leer {url}: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0].strip())
    parser.add_argument("--versions", nargs="+", default=ODOO_VERSIONS)
    parser.add_argument("--repos", nargs="+", help="Repos concretos (por defecto, todos)")
    parser.add_argument("--stats-url", help="URL de /stats del backend para comparar")
    parser.add_argument("--output", help="Guardar el resultado completo en un JSON")
    args = parser.parse_args()

    github = GitHubService(token=load_gh_token())
    check_token(github)
    repos = args.repos or github.get_all_oca_repos()

    tasks = [(repo, version) for repo in repos for version in args.versions]
    print(f"Contando {len(tasks)} combinaciones repo/versión...", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        rows = list(pool.map(lambda t: count_repo_version(github, *t), tasks))

    rows = [row for row in rows if row["etl_manifests"]]

    by_version = {}
    for version in args.versions:
        version_rows = [row for row in rows if row["version"] == version]
        by_version[version] = {
            "modules": sum(row["modules"] for row in version_rows),
            "etl_manifests": sum(row["etl_manifests"] for row in version_rows),
            "repos": len(version_rows),
        }

    by_repo: Dict[str, int] = {}
    for row in rows:
        by_repo[row["repo"]] = by_repo.get(row["repo"], 0) + row["modules"]

    result = {
        "counted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repos_scanned": len(repos),
        "repos_with_modules": len(by_repo),
        "total_modules": sum(v["modules"] for v in by_version.values()),
        "total_etl_manifests": sum(v["etl_manifests"] for v in by_version.values()),
        "by_version": by_version,
        "by_repo": dict(sorted(by_repo.items(), key=lambda item: -item[1])),
    }

    stats = fetch_stats(args.stats_url) if args.stats_url else None
    if stats:
        result["indexed"] = stats

    print(f"\nRepos OCA analizados: {result['repos_scanned']}")
    print(f"Repos con módulos:    {result['repos_with_modules']}\n")
    header = f"{'Versión':<8} {'Módulos':>8} {'Manifiestos ETL':>16} {'Repos':>6}"
    if stats:
        header += f" {'Indexados':>10}"
    print(header)
    for version, counts in by_version.items():
        line = f"{version:<8} {counts['modules']:>8} {counts['etl_manifests']:>16}"
        line += f" {counts['repos']:>6}"
        if stats:
            line += f" {stats.get('by_version', {}).get(version, 0):>10}"
        print(line)
    total = f"{'Total':<8} {result['total_modules']:>8} {result['total_etl_manifests']:>16}"
    if stats:
        total += f" {'':>6} {stats.get('total_modules', 0):>10}"
    print(total)

    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\nResultado guardado en {args.output}")


if __name__ == "__main__":
    main()
