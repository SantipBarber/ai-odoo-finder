"""
AI-OdooFinder MCP Server

Servidor MCP (Model Context Protocol) para búsqueda semántica
de módulos Odoo en el ecosistema OCA.

Implementa el flujo inteligente de búsqueda según SPEC-602:
- Fase 1: Clarificación inteligente (instrucciones en tool description)
- Fase 2: Expansión de query (instrucciones en tool description)
- Fase 3: Respuesta estructurada con niveles de confianza
- Fase 4: Confirmación y bucle iterativo (instrucciones en tool description)

Este servidor se comunica con la API REST del backend (local o remoto).
"""

import logging
import os
import sys
from typing import Annotated, Optional

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

# Cargar variables de entorno
load_dotenv()

# Configurar logging a stderr (IMPORTANTE: stdout es para JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("ai-odoofinder-mcp")

# URL de la API (configurable via env)
API_BASE_URL = os.getenv("AI_ODOOFINDER_API_URL", "http://localhost:8989")
API_TIMEOUT = int(os.getenv("AI_ODOOFINDER_API_TIMEOUT", "60"))

# Crear instancia de FastMCP
mcp = FastMCP("AI-OdooFinder 🔍")


# ============================================================================
# TOOL DESCRIPTION ENRIQUECIDO (SPEC-602 Fase 1 y 2)
# ============================================================================

QUERY_DESCRIPTION = """
Query de búsqueda para módulos Odoo OCA.

⚠️ IMPORTANTE - FLUJO DE BÚSQUEDA INTELIGENTE:

═══════════════════════════════════════════════════════════════
PASO 1: ¿NECESITAS CLARIFICACIÓN?
═══════════════════════════════════════════════════════════════

PIDE ACLARACIONES si la query es:
• Genérica: "facturación", "inventario", "CRM"
  → Pregunta: ¿País? ¿Funcionalidad específica? ¿Versión Odoo?
• Ambigua: "gestión de documentos"
  → Pregunta: ¿DMS completo? ¿Solo adjuntos? ¿Con OCR?
• Sin versión clara
  → Pregunta: ¿Qué versión de Odoo usas?
• Localización sin país: "factura electrónica", "impuestos"
  → Pregunta: ¿Para qué país?

NO PIDAS aclaraciones si:
• Query específica: "modelo 303 AEAT España 16.0"
• Nombre técnico: "l10n_es_facturae"
• Contexto completo: "DMS para gestionar PDFs en Odoo 17"

═══════════════════════════════════════════════════════════════
PASO 2: CONSTRUYE LA QUERY
═══════════════════════════════════════════════════════════════

🚨 REGLA CRÍTICA PARA LOCALIZACIONES:
Si el usuario busca funcionalidad para un PAÍS ESPECÍFICO,
USA UNA QUERY CORTA con el prefijo l10n_XX_ como término principal.

EJEMPLOS DE QUERIES PARA LOCALIZACIONES:
• España + factura electrónica → "l10n_es_facturae facturae"
• España + impuestos AEAT     → "l10n_es_aeat modelo"
• España + TicketBAI          → "l10n_es_ticketbai"
• México + factura CFDI       → "l10n_mx_edi cfdi"
• Argentina + factura AFIP    → "l10n_ar_afipws factura"
• Colombia + factura DIAN     → "l10n_co_edi dian"
• Chile + factura SII         → "l10n_cl_dte sii"
• Francia + Chorus            → "l10n_fr_chorus facturx"
• Italia + fattura            → "l10n_it_fatturapa sdi"

⚠️ Para localizaciones: query de 2-4 palabras máximo
⚠️ El prefijo l10n_XX_ es MÁS IMPORTANTE que los sinónimos

═══════════════════════════════════════════════════════════════
PARA BÚSQUEDAS NO DE LOCALIZACIÓN:
═══════════════════════════════════════════════════════════════

Añade sinónimos español/inglés (máximo 15-20 palabras):
• "inventario" → "inventory stock warehouse management"
• "ventas" → "sale sales quotation order"
• "compras" → "purchase procurement vendor"
• "contabilidad" → "account accounting financial"
• "suscripciones" → "subscription contract recurring"
• "documentos" → "document dms attachment file"

═══════════════════════════════════════════════════════════════
EJEMPLOS COMPLETOS:
═══════════════════════════════════════════════════════════════

Usuario: "facturación electrónica para España"
✅ CORRECTO: "l10n_es_facturae facturae FACE"
❌ INCORRECTO: "factura electrónica e-invoice XML firma digital Spain..."

Usuario: "modelo 303 para España"
✅ CORRECTO: "l10n_es_aeat_mod303 modelo 303"

Usuario: "gestión de inventario con códigos de barras"
✅ CORRECTO: "inventory stock barcode scanning warehouse"

Usuario: "suscripciones y contratos recurrentes"
✅ CORRECTO: "subscription contract recurring billing"
"""

VERSION_DESCRIPTION = """
Versión de Odoo (12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, o 19.0).

• Si el usuario NO especifica versión → PREGUNTA antes de buscar
• Si el usuario dice "última" o "actual" → usa 17.0 o 18.0
• Si el contexto sugiere una versión antigua → confirma con el usuario
"""

DEPENDENCIES_DESCRIPTION = """
Lista opcional de dependencias requeridas.
Útil para filtrar módulos que extiendan módulos específicos.

Ejemplos:
• dependencies=["account"] → módulos de contabilidad
• dependencies=["stock"] → módulos de inventario
• dependencies=["sale", "purchase"] → módulos de ventas+compras
"""

LIMIT_DESCRIPTION = """
Número máximo de resultados (default: 5, max: 20).

Guía:
• 5 resultados → búsquedas específicas
• 10 resultados → búsquedas exploratorias
• 15-20 resultados → cuando el usuario quiere ver todas las opciones
"""


# ============================================================================
# HTTP CLIENT
# ============================================================================


async def get_http_client() -> httpx.AsyncClient:
    """Crea un cliente HTTP con timeout configurado."""
    return httpx.AsyncClient(
        base_url=API_BASE_URL,
        timeout=httpx.Timeout(API_TIMEOUT),
        headers={"Content-Type": "application/json"},
    )


# ============================================================================
# MCP TOOL
# ============================================================================


@mcp.tool()
async def search_odoo_modules(
    query: Annotated[str, QUERY_DESCRIPTION],
    version: Annotated[str, VERSION_DESCRIPTION],
    dependencies: Annotated[Optional[list[str]], DEPENDENCIES_DESCRIPTION] = None,
    limit: Annotated[int, LIMIT_DESCRIPTION] = 5,
) -> str:
    """
    Busca módulos de Odoo en el ecosistema OCA (15,000+ módulos).

    ═══════════════════════════════════════════════════════════════
    FLUJO COMPLETO DE BÚSQUEDA INTELIGENTE
    ═══════════════════════════════════════════════════════════════

    1️⃣ CLARIFICA si es necesario
       Pide al usuario: país, versión, funcionalidad específica
       (Ver instrucciones en parámetro 'query')

    2️⃣ EXPANDE la query
       Añade sinónimos ES/EN, términos técnicos, contexto localización
       (Ver instrucciones en parámetro 'query')

    3️⃣ INTERPRETA los resultados según nivel de confianza:
       • ALTA (score ≥ 80): Recomienda directamente
       • MEDIA (score 50-79): Presenta opciones, pide confirmación
       • BAJA (score < 50): Menciona limitaciones, ofrece alternativas

    4️⃣ CONFIRMA con el usuario
       "¿Este módulo cubre tu necesidad?"
       • Si dice "sí" → proporciona instrucciones de instalación
       • Si dice "no" → vuelve al paso 1 con más contexto
       • Si dice "casi" → sugiere módulos complementarios o extensiones

    5️⃣ Si NO HAY buenos resultados:
       • Sugiere módulos parciales que cubran parte del requisito
       • Indica si la funcionalidad existe en Odoo Enterprise
       • Ofrece guía para desarrollo de módulo custom

    ═══════════════════════════════════════════════════════════════
    REGLAS IMPORTANTES
    ═══════════════════════════════════════════════════════════════

    ⛔ NUNCA inventes módulos que no existen en los resultados
    ⛔ NUNCA asumas la versión de Odoo sin preguntar
    ⛔ NUNCA ignores cuando el usuario dice "no es lo que busco"
    ✅ SIEMPRE usa los links de GitHub proporcionados en los resultados
    ✅ SIEMPRE menciona las dependencias importantes
    ✅ SIEMPRE ofrece alternativas cuando la confianza es media/baja
    """
    # Validaciones
    if not query or not query.strip():
        return "❌ Error: La query no puede estar vacía"

    valid_versions = ["12.0", "13.0", "14.0", "15.0", "16.0", "17.0", "18.0", "19.0"]
    if version not in valid_versions:
        return f"❌ Error: Versión '{version}' inválida. Usa: {', '.join(valid_versions)}"

    if limit < 1 or limit > 20:
        limit = min(max(1, limit), 20)

    logger.info(f"MCP search: query='{query[:80]}...', version={version}, limit={limit}")

    try:
        async with await get_http_client() as client:
            # Llamar a la API (GET con query params)
            params = {
                "query": query,
                "version": version,
                "limit": limit,
            }
            if dependencies:
                params["dependencies"] = ",".join(dependencies)

            response = await client.get("/search", params=params)

            if response.status_code != 200:
                error_detail = response.text[:200] if response.text else "Unknown error"
                logger.error(f"API error {response.status_code}: {error_detail}")
                return f"❌ Error de API ({response.status_code}): {error_detail}"

            data = response.json()
            results = data.get("results", [])

            if not results:
                return _format_no_results(query, version)

            # Formatear resultados con estructura inteligente
            return _format_results_intelligent(results, query, version)

    except httpx.TimeoutException:
        logger.error(f"API timeout after {API_TIMEOUT}s")
        return f"❌ Timeout: La API no respondió en {API_TIMEOUT} segundos. Intenta de nuevo."

    except httpx.ConnectError as e:
        logger.error(f"Connection error: {e}")
        return (
            f"❌ Error de conexión: No se pudo conectar a {API_BASE_URL}. ¿Está el servidor activo?"
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return f"❌ Error inesperado: {str(e)}"


# ============================================================================
# FORMATO DE RESPUESTA ESTRUCTURADA (SPEC-602 Fase 3)
# ============================================================================


def _calculate_confidence(results: list[dict]) -> str:
    """Calcula el nivel de confianza basado en los scores de los resultados."""
    if not results:
        return "NINGUNA"

    top_score = results[0].get("score", 0)

    if top_score >= 80:
        return "ALTA"
    elif top_score >= 50:
        return "MEDIA"
    else:
        return "BAJA"


def _get_confidence_emoji(confidence: str) -> str:
    """Devuelve emoji según nivel de confianza."""
    return {"ALTA": "🟢", "MEDIA": "🟡", "BAJA": "🟠", "NINGUNA": "🔴"}.get(confidence, "⚪")


def _format_results_intelligent(results: list[dict], query: str, version: str) -> str:
    """
    Formatea los resultados de búsqueda con estructura inteligente según SPEC-602.
    """
    output = []
    confidence = _calculate_confidence(results)
    confidence_emoji = _get_confidence_emoji(confidence)

    # Header con nivel de confianza
    output.append("# 🎯 Resultados de Búsqueda")
    output.append(f"**Query:** {query[:100]}{'...' if len(query) > 100 else ''}")
    output.append(f"**Versión Odoo:** {version}")
    output.append(f"**Resultados encontrados:** {len(results)}")
    output.append(f"\n## {confidence_emoji} Confianza: {confidence}\n")

    # Separar en recomendados y alternativas
    recommended = [r for r in results if r.get("score", 0) >= 80]
    alternatives = [r for r in results if r.get("score", 0) < 80]

    # Sección RECOMENDADO
    if recommended:
        output.append("### ✅ RECOMENDADO\n")
        for module in recommended:
            output.append(_format_module_detailed(module, version))

    # Sección ALTERNATIVAS
    if alternatives:
        output.append("### 📋 ALTERNATIVAS\n")
        for i, module in enumerate(alternatives, 1):
            output.append(_format_module_summary(module, index=i, version=version))

    # Guía según nivel de confianza
    output.append("\n---\n")
    output.append(_get_confidence_guidance(confidence))

    # Instrucciones para el LLM
    output.append("\n---\n")
    output.append("### 🤖 Instrucciones para el Asistente\n")
    output.append(_get_llm_instructions(confidence))

    return "\n".join(output)


def _format_module_detailed(module: dict, version: str) -> str:
    """Formatea un módulo con todos los detalles (para recomendados)."""
    score = module.get("score", 0)

    lines = []
    lines.append(f"**Módulo:** `{module.get('technical_name', 'unknown')}`")
    lines.append(f"**Nombre:** {module.get('name', 'Unknown')}")
    lines.append(f"**Score:** {score}/100")

    if module.get("summary"):
        lines.append(f"**Resumen:** {module['summary']}")

    if module.get("description"):
        desc = module["description"]
        if len(desc) > 300:
            desc = desc[:300] + "..."
        lines.append(f"**Descripción:** {desc}")

    repo_name = module.get("repo_name", "unknown")
    lines.append(f"**Repositorio:** {repo_name}")

    # GitHub link
    repo_url = module.get("repo_url", f"https://github.com/OCA/{repo_name}")
    module_path = module.get("module_path", "").replace("/__manifest__.py", "")
    github_link = f"{repo_url}/tree/{version}/{module_path}"
    lines.append(f"**GitHub:** {github_link}")

    if module.get("depends"):
        deps = module["depends"][:7]
        deps_str = ", ".join(f"`{d}`" for d in deps)
        if len(module["depends"]) > 7:
            deps_str += f" (+{len(module['depends']) - 7} más)"
        lines.append(f"**Dependencias:** {deps_str}")

    lines.append(f"**Autor:** {module.get('author', 'OCA')}")
    lines.append(f"**Licencia:** {module.get('license', 'AGPL-3')}")

    if module.get("github_stars"):
        lines.append(f"**GitHub Stars:** ⭐ {module['github_stars']}")

    if module.get("last_commit_date"):
        lines.append(f"**Última actualización:** {module['last_commit_date'][:10]}")

    lines.append("")  # Línea en blanco
    return "\n".join(lines)


def _format_module_summary(module: dict, index: int, version: str) -> str:
    """Formatea un módulo de forma resumida (para alternativas)."""
    score = module.get("score", 0)
    summary = module.get("summary", module.get("description", ""))[:100]
    if len(summary) == 100:
        summary += "..."

    repo_name = module.get("repo_name", "unknown")
    repo_url = module.get("repo_url", f"https://github.com/OCA/{repo_name}")
    module_path = module.get("module_path", "").replace("/__manifest__.py", "")
    github_link = f"{repo_url}/tree/{version}/{module_path}"

    tech_name = module.get("technical_name", "unknown")

    lines = [
        f"{index}. **`{tech_name}`** (Score: {score}/100)",
        f"   {summary}",
        f"   📦 Repo: {repo_name} | [Ver en GitHub]({github_link})",
        "",
    ]
    return "\n".join(lines)


def _get_confidence_guidance(confidence: str) -> str:
    """Genera guía contextual según el nivel de confianza."""

    if confidence == "ALTA":
        return """### 💡 Información Adicional

Los módulos recomendados tienen alta relevancia para tu búsqueda.

**Para instalar un módulo OCA:**
1. Clona el repositorio: `git clone https://github.com/OCA/<repo> -b <version>`
2. Añade la ruta al `addons_path` de Odoo
3. Actualiza la lista de aplicaciones en Odoo
4. Busca e instala el módulo

**O vía pip (si está disponible):**
```
pip install odoo-addon-<nombre_tecnico>
```
"""

    elif confidence == "MEDIA":
        return """### 💡 Información Adicional

Los resultados tienen relevancia moderada. Puede que:
- Ningún módulo cubra exactamente tu necesidad
- Necesites combinar varios módulos
- Debas ajustar tu búsqueda con más contexto

**Recomendaciones:**
- Revisa los módulos listados para ver cuál se ajusta mejor
- Considera si necesitas funcionalidad adicional
- Pregunta al usuario si alguno de estos módulos cubre su caso
"""

    else:  # BAJA o NINGUNA
        return """### 💡 Información Adicional

Los resultados tienen baja relevancia. Esto puede significar:

1. **No existe módulo OCA específico** para esta funcionalidad
   → Considera desarrollar un módulo custom

2. **La funcionalidad está en Odoo Enterprise**
   → Algunas features avanzadas solo están en la versión de pago

3. **Términos de búsqueda diferentes**
   → La funcionalidad puede existir con otro nombre

4. **Buscar en otros repositorios:**
   - [Odoo Apps Store](https://apps.odoo.com)
   - GitHub búsqueda general de "odoo <funcionalidad>"
"""


def _get_llm_instructions(confidence: str) -> str:
    """Genera instrucciones específicas para el LLM según la confianza."""

    if confidence == "ALTA":
        return """- **Recomienda** el módulo con mayor score directamente
- **Explica** por qué es la mejor opción para el usuario
- **Pregunta**: "¿Este módulo cubre lo que necesitas?"
- Si el usuario confirma, ofrece ayuda con la instalación/configuración"""

    elif confidence == "MEDIA":
        return """- **Presenta** las opciones disponibles de forma clara
- **Explica** las diferencias entre los módulos encontrados
- **Pregunta**: "¿Cuál de estos módulos se ajusta mejor a tu caso?"
- Si ninguno convence al usuario, **pide más detalles** sobre su necesidad"""

    else:  # BAJA
        return """- **Sé honesto**: menciona que no encontraste un resultado ideal
- **Ofrece** los módulos encontrados como opciones parciales
- **Pregunta**: "¿Podrías darme más detalles sobre lo que necesitas?"
- **Sugiere** alternativas: desarrollo custom, Odoo Enterprise, otros repos"""


def _format_no_results(query: str, version: str) -> str:
    """Formatea respuesta cuando no hay resultados."""

    return f"""# 🔍 Sin Resultados

**Query:** {query}
**Versión Odoo:** {version}

## 🔴 Confianza: NINGUNA

No se encontraron módulos OCA que coincidan con tu búsqueda.

### Esto puede significar:

1. **No existe módulo OCA** para esta funcionalidad específica
   - Considera desarrollar un módulo custom
   - Busca en [Odoo Apps Store](https://apps.odoo.com)

2. **Términos de búsqueda muy específicos o diferentes**
   - Intenta con sinónimos o términos más generales
   - Usa términos en inglés además de español

3. **La funcionalidad está en Odoo Enterprise**
   - Algunas características solo están en la versión de pago

4. **Versión de Odoo sin soporte**
   - Algunos módulos no están disponibles para todas las versiones
   - Prueba con una versión diferente (16.0 o 17.0 tienen más módulos)

### Sugerencias:

- Prueba una búsqueda más amplia
- Especifica mejor el dominio funcional
- Revisa si hay un módulo base que puedas extender

---

### 🤖 Instrucciones para el Asistente

- **Pregunta** al usuario por más contexto sobre su necesidad
- **Sugiere** búsquedas alternativas basadas en lo que entendiste
- **Ofrece** ayuda para diseñar un módulo custom si es necesario
- **NO inventes** módulos que no existen
"""


# ============================================================================
# ENTRY POINT
# ============================================================================


def main():
    """Punto de entrada para el servidor MCP."""
    logger.info(f"Starting AI-OdooFinder MCP Server (API: {API_BASE_URL})")
    mcp.run()


if __name__ == "__main__":
    main()
