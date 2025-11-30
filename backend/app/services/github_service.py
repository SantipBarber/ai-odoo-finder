import ast
import base64
from typing import Any, Dict, List, Optional

import requests

from ..config import get_settings

settings = get_settings()


def _safe_ast_eval(node: ast.AST) -> Any:
    """Safely evaluate AST nodes allowing only literal data structures."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [_safe_ast_eval(elt) for elt in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_safe_ast_eval(elt) for elt in node.elts)
    if isinstance(node, ast.Dict):
        return {
            _safe_ast_eval(key): _safe_ast_eval(value) for key, value in zip(node.keys, node.values)
        }
    if isinstance(node, ast.Set):
        return {_safe_ast_eval(elt) for elt in node.elts}
    if isinstance(node, ast.NameConstant):  # Py<3.8 compatibility
        return node.value
    if isinstance(node, ast.Name):
        if node.id in {"True", "False", "None"}:
            return eval(node.id)  # noqa: PGH001
        raise ValueError(f"Name not allowed in manifest: {node.id}")
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "_":
            if node.args:
                return _safe_ast_eval(node.args[0])
        raise ValueError("Function calls not allowed in manifest")
    raise ValueError(f"Unsupported node type: {type(node).__name__}")


class GitHubService:
    def __init__(self):
        self.token = settings.gh_token
        self.headers = {"Authorization": f"token {self.token}"}
        self.base_url = "https://api.github.com"

    def get_repo_metadata(self, repo_name: str) -> Dict:
        """Get repository metadata (stars, issues, last update)."""
        url = f"{self.base_url}/repos/OCA/{repo_name}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        data = response.json()

        return {
            "stars": data.get("stargazers_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "last_push": data.get("pushed_at"),
            "url": data.get("html_url"),
        }

    def list_versions(self, repo_name: str) -> List[str]:
        """List available Odoo versions (branches)."""
        url = f"{self.base_url}/repos/OCA/{repo_name}/branches"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        branches = response.json()

        # Filtrar solo versiones de Odoo
        odoo_versions = [
            b["name"] for b in branches if b["name"] in ["14.0", "15.0", "16.0", "17.0", "18.0"]
        ]

        return sorted(odoo_versions)

    def get_all_oca_repos(self, min_stars: int = 0) -> List[str]:
        """Get all active repositories from OCA organization."""
        all_repos = []
        page = 1
        per_page = 100

        print("Discovering OCA repositories...")

        while True:
            url = f"{self.base_url}/orgs/OCA/repos"
            params = {"page": page, "per_page": per_page, "type": "public", "sort": "updated"}

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            repos = response.json()

            if not repos:
                break

            for repo in repos:
                if repo.get("archived", False):
                    continue
                if repo.get("fork", False):
                    continue

                stars = repo.get("stargazers_count", 0)
                if stars < min_stars:
                    continue

                repo_name = repo["name"]
                infrastructure_repos = [
                    "maintainer-tools",
                    "maintainer-quality-tools",
                    "odoo-pre-commit-hooks",
                    "pylint-odoo",
                    "github-organization-project",
                    "oca-custom",
                    "OpenUpgrade",
                    "runbot-addons",
                    "odoo-community.org",
                    "OCB",
                ]

                if repo_name in infrastructure_repos:
                    continue

                all_repos.append(repo_name)

            print(f"   Page {page}: {len(repos)} repos ({len(all_repos)} valid accumulated)")
            page += 1

            if len(all_repos) >= 500:
                print("   Reached 500 repos limit")
                break

        print(f"Found {len(all_repos)} active OCA repositories\n")
        return all_repos

    def find_manifests(self, repo_name: str, version: str) -> List[str]:
        """Find all __manifest__.py files in a repo/version."""
        url = f"{self.base_url}/repos/OCA/{repo_name}/git/trees/{version}?recursive=1"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return []

        tree = response.json().get("tree", [])

        manifests = [item["path"] for item in tree if item["path"].endswith("__manifest__.py")]

        return manifests

    def get_manifest_content(
        self, repo_name: str, version: str, manifest_path: str
    ) -> Optional[Dict]:
        """Get and parse __manifest__.py content."""
        url = f"{self.base_url}/repos/OCA/{repo_name}/contents/{manifest_path}?ref={version}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return None

        data = response.json()

        content = base64.b64decode(data["content"]).decode("utf-8")

        try:
            tree = ast.parse(content)

            for node in tree.body:
                if isinstance(node, ast.Assign):
                    try:
                        return _safe_ast_eval(node.value)
                    except Exception:
                        continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    try:
                        return _safe_ast_eval(node)
                    except Exception:
                        continue
        except Exception as e:
            print(f"Error parsing {manifest_path}: {e}")
            return None

        return None

    def get_readme_content(self, repo_name: str, version: str, module_path: str) -> Optional[str]:
        """Get README content for a module."""
        module_dir = (
            module_path.rsplit("/", 1)[0]
            if "/" in module_path
            else module_path.replace("__manifest__.py", "")
        )

        readme_names = ["README.md", "README.rst", "README.MD", "README.RST", "readme.md"]

        for readme_name in readme_names:
            readme_path = f"{module_dir}/{readme_name}"
            url = f"{self.base_url}/repos/OCA/{repo_name}/contents/{readme_path}?ref={version}"

            try:
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                    return content
            except Exception:
                continue

        return None


_github_service = None


def get_github_service() -> GitHubService:
    global _github_service
    if _github_service is None:
        _github_service = GitHubService()
    return _github_service
