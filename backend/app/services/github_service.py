import ast
import base64
from typing import Any, Dict, List, Optional

import requests

from ..config import get_settings

settings = get_settings()


def _safe_ast_eval(node: ast.AST) -> Any:
    """Evaluar nodos AST permitiendo solo estructuras de datos literales."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [_safe_ast_eval(elt) for elt in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_safe_ast_eval(elt) for elt in node.elts)
    if isinstance(node, ast.Dict):
        return {
            _safe_ast_eval(key): _safe_ast_eval(value)
            for key, value in zip(node.keys, node.values)
        }
    if isinstance(node, ast.Set):
        return {_safe_ast_eval(elt) for elt in node.elts}
    if isinstance(node, ast.NameConstant):  # Py<3.8 compatibility
        return node.value
    if isinstance(node, ast.Name):
        if node.id in {"True", "False", "None"}:
            return eval(node.id)  # noqa: PGH001
        raise ValueError(f"Nombre no permitido en manifest: {node.id}")
    if isinstance(node, ast.Call):
        # Soportar traducciones tipo _("texto")
        if isinstance(node.func, ast.Name) and node.func.id == "_":
            if node.args:
                return _safe_ast_eval(node.args[0])
        raise ValueError("Llamadas a funciones no permitidas en manifest")
    raise ValueError(f"Tipo de nodo no soportado: {type(node).__name__}")


class GitHubService:
    def __init__(self):
        self.token = settings.github_token
        self.headers = {"Authorization": f"token {self.token}"}
        self.base_url = "https://api.github.com"

    def get_repo_metadata(self, repo_name: str) -> Dict:
        """
        Obtener metadata de un repositorio.

        Args:
            repo_name: Nombre del repo (ej: "server-tools")

        Returns:
            Dict con stars, issues, última actualización
        """
        url = f"{self.base_url}/repos/OCA/{repo_name}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        data = response.json()

        return {
            "stars": data.get("stargazers_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "last_push": data.get("pushed_at"),
            "url": data.get("html_url")
        }

    def list_versions(self, repo_name: str) -> List[str]:
        """
        Listar versiones de Odoo disponibles (branches).

        Args:
            repo_name: Nombre del repo

        Returns:
            Lista de versiones (ej: ["16.0", "17.0", "18.0"])
        """
        url = f"{self.base_url}/repos/OCA/{repo_name}/branches"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        branches = response.json()

        # Filtrar solo versiones de Odoo
        odoo_versions = [
            b['name'] for b in branches
            if b['name'] in ['14.0', '15.0', '16.0', '17.0', '18.0']
        ]

        return sorted(odoo_versions)

    def find_manifests(self, repo_name: str, version: str) -> List[str]:
        """
        Encontrar todos los __manifest__.py en un repo/versión.

        Args:
            repo_name: Nombre del repo
            version: Versión de Odoo (ej: "17.0")

        Returns:
            Lista de paths a manifests (ej: ["module_name/__manifest__.py"])
        """
        url = f"{self.base_url}/repos/OCA/{repo_name}/git/trees/{version}?recursive=1"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return []

        tree = response.json().get('tree', [])

        manifests = [
            item['path'] for item in tree
            if item['path'].endswith('__manifest__.py')
        ]

        return manifests

    def get_manifest_content(self, repo_name: str, version: str, manifest_path: str) -> Optional[Dict]:
        """
        Obtener y parsear el contenido de un __manifest__.py

        Args:
            repo_name: Nombre del repo
            version: Versión de Odoo
            manifest_path: Path al manifest (ej: "module_name/__manifest__.py")

        Returns:
            Dict con el contenido del manifest parseado
        """
        url = f"{self.base_url}/repos/OCA/{repo_name}/contents/{manifest_path}?ref={version}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return None

        data = response.json()

        # Decodificar contenido (está en base64)
        content = base64.b64decode(data['content']).decode('utf-8')

        # Parsear el manifest (es código Python)
        try:
            tree = ast.parse(content)

            for node in tree.body:
                if isinstance(node, ast.Assign):
                    try:
                        return _safe_ast_eval(node.value)
                    except Exception:
                        continue

            # Fallback: primer dict literal encontrado
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    try:
                        return _safe_ast_eval(node)
                    except Exception:
                        continue
        except Exception as e:
            print(f"❌ Error parseando {manifest_path}: {e}")
            return None

        return None


# Singleton
_github_service = None


def get_github_service() -> GitHubService:
    global _github_service
    if _github_service is None:
        _github_service = GitHubService()
    return _github_service


