"""
MCP Tools para AI-OdooFinder

Define los tools MCP que permiten a Claude buscar módulos de Odoo
usando el servidor de búsqueda semántica.
"""

import logging
from typing import Optional, Annotated
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from sqlalchemy.orm import Session

from .database import get_db
from .services.search_service import get_search_service
from .core.logging import get_logger

logger = get_logger(__name__)

# Crear instancia de FastMCP
mcp = FastMCP("AI-OdooFinder 🔍")


@mcp.tool()
async def search_odoo_modules(
    query: Annotated[str, "Description of the desired functionality in natural language"],
    version: Annotated[str, "Odoo version (12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, or 19.0)"],
    dependencies: Annotated[Optional[list[str]], "Optional list of required module dependencies"] = None,
    limit: Annotated[int, "Maximum number of results (default: 5, max: 20)"] = 5,
) -> str:
    """
    Search for Odoo modules using AI-powered semantic search.

    This tool searches through 2,500+ OCA (Odoo Community Association) modules
    indexed from GitHub, using hybrid search (semantic + filters) to find the
    most relevant modules for your needs.

    Examples:
    - query="recurring payments and subscriptions", version="17.0"
    - query="inventory management with barcodes", version="16.0", dependencies=["stock"]
    - query="separate B2B and B2C sales workflows", version="16.0"

    Returns:
    A formatted list of matching modules with their technical details,
    GitHub links, and relevance scores.
    """
    try:
        # Validaciones
        if not query or not query.strip():
            return "❌ Error: Query cannot be empty"

        if version not in ["12.0", "13.0", "14.0", "15.0", "16.0", "17.0", "18.0", "19.0"]:
            return f"❌ Error: Invalid version '{version}'. Use: 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, or 19.0"

        if limit < 1 or limit > 20:
            limit = min(max(1, limit), 20)

        logger.info(f"MCP search: query='{query[:50]}...', version={version}, limit={limit}")

        # Obtener DB session
        db: Session = next(get_db())

        try:
            # Llamar al servicio de búsqueda directamente (NO HTTP)
            search_service = get_search_service(db)
            results = search_service.search(
                query=query,
                version=version,
                dependencies=dependencies,
                limit=limit,
                min_score=0
            )

            if not results:
                return f"🔍 No modules found for query '{query}' in Odoo {version}\n\nTry:\n- Broadening your search terms\n- Checking a different Odoo version\n- Removing dependency filters"

            # Formatear resultados para Claude
            formatted_output = _format_results_for_claude(results, query, version)
            return formatted_output

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in MCP search: {e}", exc_info=True)
        return f"❌ Error searching modules: {str(e)}\n\nPlease try again or contact support if the error persists."


def _format_results_for_claude(results: list[dict], query: str, version: str) -> str:
    """
    Formatea los resultados de búsqueda de manera amigable para Claude.
    """
    output = []
    output.append(f"# 🎯 Found {len(results)} Odoo modules for '{query}' (v{version})\n")

    for i, module in enumerate(results, 1):
        score = module.get("score", 0)

        # Emoji según score
        emoji = "🌟" if score >= 85 else "⭐" if score >= 70 else "✓"

        output.append(f"## {emoji} {i}. {module['name']}")
        output.append(f"**Technical Name:** `{module['technical_name']}`")
        output.append(f"**Score:** {score}/100 (relevance)")

        if module.get('summary'):
            output.append(f"**Summary:** {module['summary']}")

        if module.get('description'):
            output.append(f"**Description:** {module['description']}")

        # Metadatos importantes
        output.append(f"**Repository:** [{module['repo_name']}]({module['repo_url']})")
        output.append(f"**GitHub Stars:** ⭐ {module['github_stars']}")

        if module.get('depends'):
            deps = ', '.join(f"`{d}`" for d in module['depends'][:5])
            if len(module['depends']) > 5:
                deps += f" (+{len(module['depends'])-5} more)"
            output.append(f"**Dependencies:** {deps}")

        output.append(f"**License:** {module['license']}")
        output.append(f"**Author:** {module['author']}")

        if module.get('last_commit_date'):
            output.append(f"**Last Update:** {module['last_commit_date'][:10]}")

        # Link directo al módulo en GitHub
        repo_url = module['repo_url']
        module_path = module['module_path'].replace('/__manifest__.py', '')
        github_link = f"{repo_url}/tree/{version}/{module_path}"
        output.append(f"**View on GitHub:** {github_link}")

        output.append("")  # Línea en blanco entre módulos

    # Footer con tips
    output.append("---")
    output.append("💡 **Tips:**")
    output.append("- Higher scores indicate better relevance to your query")
    output.append("- Check dependencies before installation")
    output.append("- Review GitHub stars and last update date for quality indicators")
    output.append("- Visit the GitHub link to see full documentation")

    return "\n".join(output)


# Exportar la instancia MCP
__all__ = ["mcp"]
