"""
AI-OdooFinder MCP Server

MCP (Model Context Protocol) server that enables LLMs to search Odoo modules
in the OCA ecosystem using hybrid search (semantic + full-text).
Supports both STDIO (local) and HTTP (remote) transport.
"""

import logging
import os
import sys
from typing import Annotated, Optional

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

# Log to stderr (stdout is for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("ai-odoofinder-mcp")

API_BASE_URL = os.getenv("AI_ODOOFINDER_API_URL", "http://localhost:8989")
API_TIMEOUT = int(os.getenv("AI_ODOOFINDER_API_TIMEOUT", "60"))

mcp = FastMCP("AI-OdooFinder")


QUERY_DESCRIPTION = """
Search query for Odoo OCA modules.

⚠️ IMPORTANT - INTELLIGENT SEARCH FLOW:

═══════════════════════════════════════════════════════════════
STEP 1: DO YOU NEED CLARIFICATION?
═══════════════════════════════════════════════════════════════

ASK FOR CLARIFICATION if the query is:
• Generic: "invoicing", "inventory", "CRM"
  → Ask: Country? Specific functionality? Odoo version?
• Ambiguous: "document management"
  → Ask: Full DMS? Just attachments? With OCR?
• No clear version
  → Ask: What Odoo version do you use?
• Localization without country: "electronic invoice", "taxes"
  → Ask: For which country?

DO NOT ASK for clarification if:
• Specific query: "AEAT model 303 Spain 16.0"
• Technical name: "l10n_es_facturae"
• Complete context: "DMS to manage PDFs in Odoo 17"

═══════════════════════════════════════════════════════════════
STEP 2: BUILD THE QUERY
═══════════════════════════════════════════════════════════════

🚨 CRITICAL RULE FOR LOCALIZATIONS:
If the user searches for functionality for a SPECIFIC COUNTRY,
USE A SHORT QUERY with the l10n_XX_ prefix as the main term.

LOCALIZATION QUERY EXAMPLES:
• Spain + electronic invoice → "l10n_es_facturae facturae"
• Spain + AEAT taxes        → "l10n_es_aeat modelo"
• Spain + TicketBAI         → "l10n_es_ticketbai"
• Mexico + CFDI invoice     → "l10n_mx_edi cfdi"
• Argentina + AFIP invoice  → "l10n_ar_afipws factura"
• Colombia + DIAN invoice   → "l10n_co_edi dian"
• Chile + SII invoice       → "l10n_cl_dte sii"
• France + Chorus           → "l10n_fr_chorus facturx"
• Italy + fattura           → "l10n_it_fatturapa sdi"

⚠️ For localizations: query of 2-4 words maximum
⚠️ The l10n_XX_ prefix is MORE IMPORTANT than synonyms

═══════════════════════════════════════════════════════════════
FOR NON-LOCALIZATION SEARCHES:
═══════════════════════════════════════════════════════════════

Add English/Spanish synonyms (maximum 15-20 words):
• "inventario" → "inventory stock warehouse management"
• "ventas" → "sale sales quotation order"
• "compras" → "purchase procurement vendor"
• "contabilidad" → "account accounting financial"
• "suscripciones" → "subscription contract recurring"
• "documentos" → "document dms attachment file"

═══════════════════════════════════════════════════════════════
COMPLETE EXAMPLES:
═══════════════════════════════════════════════════════════════

User: "electronic invoicing for Spain"
✅ CORRECT: "l10n_es_facturae facturae FACE"
❌ INCORRECT: "electronic invoice e-invoice XML digital signature Spain..."

User: "model 303 for Spain"
✅ CORRECT: "l10n_es_aeat_mod303 modelo 303"

User: "inventory management with barcodes"
✅ CORRECT: "inventory stock barcode scanning warehouse"

User: "subscriptions and recurring contracts"
✅ CORRECT: "subscription contract recurring billing"
"""

VERSION_DESCRIPTION = """
Odoo version (10.0, 11.0,12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, or 19.0).

• If user does NOT specify version → ASK before searching
• If user says "latest" or "current" → use 17.0 or 18.0
• If context suggests an old version → confirm with user
"""

DEPENDENCIES_DESCRIPTION = """
Optional list of required dependencies.
Useful to filter modules that extend specific modules.

Examples:
• dependencies=["account"] → accounting modules
• dependencies=["stock"] → inventory modules
• dependencies=["sale", "purchase"] → sales+purchase modules
"""

LIMIT_DESCRIPTION = """
Maximum number of results (default: 5, max: 20).

Guide:
• 5 results → specific searches
• 10 results → exploratory searches
• 15-20 results → when user wants to see all options
"""


async def get_http_client() -> httpx.AsyncClient:
    """Create HTTP client with configured timeout."""
    return httpx.AsyncClient(
        base_url=API_BASE_URL,
        timeout=httpx.Timeout(API_TIMEOUT),
        headers={"Content-Type": "application/json"},
    )


@mcp.tool()
async def search_odoo_modules(
    query: Annotated[str, QUERY_DESCRIPTION],
    version: Annotated[str, VERSION_DESCRIPTION],
    dependencies: Annotated[Optional[list[str]], DEPENDENCIES_DESCRIPTION] = None,
    limit: Annotated[int, LIMIT_DESCRIPTION] = 5,
) -> str:
    """
    Search Odoo modules in the OCA ecosystem (16,000+ modules).

    Intelligent search flow:
    1. CLARIFY if needed (country, version, specific functionality)
    2. EXPAND query with synonyms ES/EN
    3. INTERPRET results by confidence level (HIGH/MEDIUM/LOW)
    4. CONFIRM with user and iterate if needed

    Rules:
    - NEVER invent modules not in results
    - NEVER assume Odoo version without asking
    - ALWAYS use GitHub links from results
    - ALWAYS offer alternatives when confidence is medium/low
    """
    if not query or not query.strip():
        return "❌ Error: Query cannot be empty"

    valid_versions = [
        "10.0",
        "11.0",
        "12.0",
        "13.0",
        "14.0",
        "15.0",
        "16.0",
        "17.0",
        "18.0",
        "19.0",
    ]
    if version not in valid_versions:
        return f"❌ Error: Invalid version '{version}'. Use: {', '.join(valid_versions)}"

    if limit < 1 or limit > 20:
        limit = min(max(1, limit), 20)

    logger.info(f"MCP search: query='{query[:80]}...', version={version}, limit={limit}")

    try:
        async with await get_http_client() as client:
            params = {"query": query, "version": version, "limit": limit}
            if dependencies:
                params["dependencies"] = ",".join(dependencies)

            response = await client.get("/search", params=params)

            if response.status_code != 200:
                error_detail = response.text[:200] if response.text else "Unknown error"
                logger.error(f"API error {response.status_code}: {error_detail}")
                return f"❌ API Error ({response.status_code}): {error_detail}"

            data = response.json()
            results = data.get("results", [])

            if not results:
                return _format_no_results(query, version)

            return _format_results_intelligent(results, query, version)

    except httpx.TimeoutException:
        logger.error(f"API timeout after {API_TIMEOUT}s")
        return f"❌ Timeout: API did not respond in {API_TIMEOUT} seconds. Try again."

    except httpx.ConnectError as e:
        logger.error(f"Connection error: {e}")
        return f"❌ Connection error: Could not connect to {API_BASE_URL}. Is the server running?"

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return f"❌ Unexpected error: {str(e)}"


def _calculate_confidence(results: list[dict]) -> str:
    """Calculate confidence level based on top result score."""
    if not results:
        return "NONE"
    top_score = results[0].get("score", 0)
    if top_score >= 80:
        return "HIGH"
    elif top_score >= 50:
        return "MEDIUM"
    return "LOW"


def _get_confidence_emoji(confidence: str) -> str:
    """Get emoji for confidence level."""
    return {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🟠", "NONE": "🔴"}.get(confidence, "⚪")


def _format_results_intelligent(results: list[dict], query: str, version: str) -> str:
    """Format search results with intelligent structure."""
    output = []
    confidence = _calculate_confidence(results)
    confidence_emoji = _get_confidence_emoji(confidence)

    output.append("# 🎯 Search Results")
    output.append(f"**Query:** {query[:100]}{'...' if len(query) > 100 else ''}")
    output.append(f"**Odoo Version:** {version}")
    output.append(f"**Results found:** {len(results)}")
    output.append(f"\n## {confidence_emoji} Confidence: {confidence}\n")

    recommended = [r for r in results if r.get("score", 0) >= 80]
    alternatives = [r for r in results if r.get("score", 0) < 80]

    if recommended:
        output.append("### ✅ RECOMMENDED\n")
        for module in recommended:
            output.append(_format_module_detailed(module, version))

    if alternatives:
        output.append("### 📋 ALTERNATIVES\n")
        for i, module in enumerate(alternatives, 1):
            output.append(_format_module_summary(module, index=i, version=version))

    output.append("\n---\n")
    output.append(_get_confidence_guidance(confidence))
    output.append("\n---\n")
    output.append("### 🤖 Assistant Instructions\n")
    output.append(_get_llm_instructions(confidence))

    return "\n".join(output)


def _format_module_detailed(module: dict, version: str) -> str:
    """Format module with full details (for recommended)."""
    score = module.get("score", 0)
    lines = []
    lines.append(f"**Module:** `{module.get('technical_name', 'unknown')}`")
    lines.append(f"**Name:** {module.get('name', 'Unknown')}")
    lines.append(f"**Score:** {score}/100")

    if module.get("summary"):
        lines.append(f"**Summary:** {module['summary']}")

    if module.get("description"):
        desc = module["description"]
        if len(desc) > 300:
            desc = desc[:300] + "..."
        lines.append(f"**Description:** {desc}")

    repo_name = module.get("repo_name", "unknown")
    lines.append(f"**Repository:** {repo_name}")

    repo_url = module.get("repo_url", f"https://github.com/OCA/{repo_name}")
    module_path = module.get("module_path", "").replace("/__manifest__.py", "")
    github_link = f"{repo_url}/tree/{version}/{module_path}"
    lines.append(f"**GitHub:** {github_link}")

    if module.get("depends"):
        deps = module["depends"][:7]
        deps_str = ", ".join(f"`{d}`" for d in deps)
        if len(module["depends"]) > 7:
            deps_str += f" (+{len(module['depends']) - 7} more)"
        lines.append(f"**Dependencies:** {deps_str}")

    lines.append(f"**Author:** {module.get('author', 'OCA')}")
    lines.append(f"**License:** {module.get('license', 'AGPL-3')}")

    if module.get("github_stars"):
        lines.append(f"**GitHub Stars:** ⭐ {module['github_stars']}")

    if module.get("last_commit_date"):
        lines.append(f"**Last updated:** {module['last_commit_date'][:10]}")

    lines.append("")
    return "\n".join(lines)


def _format_module_summary(module: dict, index: int, version: str) -> str:
    """Format module summary (for alternatives)."""
    score = module.get("score", 0)
    summary = module.get("summary", module.get("description", ""))[:100]
    if len(summary) == 100:
        summary += "..."

    repo_name = module.get("repo_name", "unknown")
    repo_url = module.get("repo_url", f"https://github.com/OCA/{repo_name}")
    module_path = module.get("module_path", "").replace("/__manifest__.py", "")
    github_link = f"{repo_url}/tree/{version}/{module_path}"
    tech_name = module.get("technical_name", "unknown")

    return f"""{index}. **`{tech_name}`** (Score: {score}/100)
   {summary}
   📦 Repo: {repo_name} | [View on GitHub]({github_link})
"""


def _get_confidence_guidance(confidence: str) -> str:
    """Generate contextual guidance based on confidence level."""
    if confidence == "HIGH":
        return """### 💡 Additional Information

The recommended modules are highly relevant to your search.

**To install an OCA module:**
1. Clone the repository: `git clone https://github.com/OCA/<repo> -b <version>`
2. Add the path to Odoo's `addons_path`
3. Update the app list in Odoo
4. Search and install the module

**Or via pip (if available):**
```
pip install odoo-addon-<technical_name>
```
"""
    elif confidence == "MEDIUM":
        return """### 💡 Additional Information

Results have moderate relevance. This may mean:
- No module exactly covers your need
- You may need to combine several modules
- Consider adjusting your search with more context

**Recommendations:**
- Review listed modules to find the best fit
- Consider if you need additional functionality
- Ask the user if any of these modules cover their case
"""
    else:
        return """### 💡 Additional Information

Results have low relevance. This may mean:

1. **No specific OCA module exists** for this functionality
   → Consider developing a custom module

2. **The functionality is in Odoo Enterprise**
   → Some advanced features are only in the paid version

3. **Different search terms**
   → The functionality may exist under another name

4. **Search in other repositories:**
   - [Odoo Apps Store](https://apps.odoo.com)
   - GitHub general search for "odoo <functionality>"
"""


def _get_llm_instructions(confidence: str) -> str:
    """Generate specific instructions for the LLM based on confidence."""
    if confidence == "HIGH":
        return """- **Recommend** the highest-scoring module directly
- **Explain** why it's the best option for the user
- **Ask**: "Does this module cover what you need?"
- If user confirms, offer help with installation/configuration"""
    elif confidence == "MEDIUM":
        return """- **Present** available options clearly
- **Explain** differences between found modules
- **Ask**: "Which of these modules best fits your case?"
- If none convinces the user, **ask for more details** about their need"""
    else:
        return """- **Be honest**: mention you didn't find an ideal result
- **Offer** found modules as partial options
- **Ask**: "Could you give me more details about what you need?"
- **Suggest** alternatives: custom development, Odoo Enterprise, other repos"""


def _format_no_results(query: str, version: str) -> str:
    """Format response when no results found."""
    return f"""# 🔍 No Results

**Query:** {query}
**Odoo Version:** {version}

## 🔴 Confidence: NONE

No OCA modules found matching your search.

### This may mean:

1. **No OCA module exists** for this specific functionality
   - Consider developing a custom module
   - Search on [Odoo Apps Store](https://apps.odoo.com)

2. **Search terms too specific or different**
   - Try synonyms or more general terms
   - Use English terms in addition to Spanish

3. **Functionality is in Odoo Enterprise**
   - Some features are only in the paid version

4. **Odoo version not supported**
   - Some modules aren't available for all versions
   - Try a different version (16.0 or 17.0 have more modules)

### Suggestions:

- Try a broader search
- Better specify the functional domain
- Check if there's a base module you can extend

---

### 🤖 Assistant Instructions

- **Ask** the user for more context about their need
- **Suggest** alternative searches based on what you understood
- **Offer** help designing a custom module if needed
- **DO NOT invent** modules that don't exist
"""


# HTTP server configuration
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8080"))
MCP_PATH = os.getenv("MCP_PATH", "/")


def main():
    """
    Entry point for MCP server.

    Modes:
    - STDIO (default): For Claude Desktop local
    - HTTP (--http flag): For Claude Web, Zed, Cursor, and other remote clients

    Environment variables:
    - MCP_TRANSPORT: "stdio" (default) or "http"
    - MCP_HOST: Host for HTTP (default: 0.0.0.0)
    - MCP_PORT: Port for HTTP (default: 8080)
    - MCP_PATH: MCP endpoint path (default: /)
    - AI_ODOOFINDER_API_URL: Backend API URL
    """
    import argparse

    parser = argparse.ArgumentParser(description="AI-OdooFinder MCP Server")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run in HTTP mode (for remote clients like Claude Web, Zed, Cursor)",
    )
    parser.add_argument("--host", default=MCP_HOST, help=f"Host to bind (default: {MCP_HOST})")
    parser.add_argument(
        "--port", type=int, default=MCP_PORT, help=f"Port to bind (default: {MCP_PORT})"
    )

    args = parser.parse_args()

    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if args.http:
        transport = "http"

    if transport == "http":
        logger.info(
            f"Starting AI-OdooFinder MCP Server in HTTP mode "
            f"(host={args.host}, port={args.port}, path={MCP_PATH})"
        )
        logger.info(f"Backend API: {API_BASE_URL}")
        logger.info(f"MCP endpoint: http://{args.host}:{args.port}{MCP_PATH}")
        mcp.run(transport="http", host=args.host, port=args.port, path=MCP_PATH)
    else:
        logger.info(f"Starting AI-OdooFinder MCP Server in STDIO mode (API: {API_BASE_URL})")
        mcp.run()


if __name__ == "__main__":
    main()
