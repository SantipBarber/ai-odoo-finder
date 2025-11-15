# 🔌 Diseño de Arquitectura - Servidor MCP Remoto AI-OdooFinder

**Fecha de creación:** 15 Noviembre 2025
**Última actualización:** 15 Noviembre 2025 (Arquitectura actualizada a MCP remoto)
**Sprint:** 2 - Implementación MCP
**Versión:** 2.0 - **MCP Remoto en Render**

---

## 📋 Tabla de Contenidos

- [Resumen Ejecutivo](#resumen-ejecutivo)
- [Decisiones Técnicas](#decisiones-técnicas)
- [Arquitectura del Servidor MCP Remoto](#arquitectura-del-servidor-mcp-remoto)
- [Especificación del Tool](#especificación-del-tool)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Plan de Implementación](#plan-de-implementación)
- [Testing y Validación](#testing-y-validación)
- [Configuración y Deploy](#configuración-y-deploy)

---

## Resumen Ejecutivo

### ¿Qué es MCP?

**Model Context Protocol (MCP)** es un estándar de código abierto desarrollado por Anthropic para conectar aplicaciones de IA (como Claude) a sistemas externos de forma normalizada.

**Analogía:** MCP es como un "USB-C para aplicaciones de IA" - un protocolo único que permite conectar cualquier cliente (Claude Desktop, Claude Web) a cualquier servidor (bases de datos, APIs, herramientas).

### Objetivo del Proyecto

Implementar un **servidor MCP remoto** hospedado en Render.com que exponga la funcionalidad de búsqueda de módulos Odoo, permitiendo que Claude Web y Claude Desktop se conecten directamente mediante **Conectores Personalizados** sin necesidad de instalación local ni copy-paste.

### Beneficios

**Situación Actual:**
- ✅ Claude Code: Funciona nativamente con el Skill.md
- ⚠️ Claude Web: Requiere copy-paste del Skill.md en cada conversación
- ⚠️ Claude Desktop: No soportado

**Con MCP Remoto Implementado:**
- ✅ Claude Web: Conector personalizado nativo (sin copy-paste) ⭐ **NOVEDAD**
- ✅ Claude Desktop: Conector personalizado nativo ⭐ **NOVEDAD**
- ✅ Claude Code: Sigue funcionando con Skill.md (mantiene compatibilidad)
- ✅ Mejor UX: Claude detecta automáticamente cuándo buscar módulos Odoo
- ✅ Más robusto: Un solo servidor para todos los clientes
- ✅ Cero instalación: Usuarios solo agregan URL del servidor en configuración

---

## Decisiones Técnicas

### 1. Stack Tecnológico: Python + FastAPI ✅

**Decisión:** Usar **Python** con `FastMCP` y FastAPI para servidor HTTP

**Razones:**
1. **Consistencia total:** Proyecto ya usa Python (FastAPI), mismas dependencias
2. **Integración en mismo codebase:** Servidor MCP y API REST en el mismo proyecto
3. **FastMCP soporta HTTP:** `mcp.run(transport="http")` es nativo
4. **Type hints nativos:** Genera definiciones de tools automáticamente
5. **Un solo deployment:** Todo en Render, una sola app

**Alternativas consideradas:**
- ❌ **TypeScript/Node.js:** Stack adicional, complicaría deployment
- ❌ **Servidor local:** Requeriría instalación por usuario (mala UX)

### 2. Arquitectura: MCP Remoto en Render ✅ **ACTUALIZADO**

**Decisión:** Servidor MCP **remoto** hospedado en Render.com, accesible vía HTTP/SSE

**Razones:**
1. **Conectores Personalizados de Claude Web (Beta):** Permite agregar servidores remotos sin instalación
2. **Cero fricción para usuarios:** Solo copian URL en configuración de Claude
3. **Un solo servidor:** Mismo deployment que la API actual
4. **Mantenimiento centralizado:** Actualizaciones benefician a todos los usuarios
5. **Escalabilidad:** Render escala automáticamente según demanda

**Arquitectura Actualizada:**
```
Claude Web/Desktop
       ↓ HTTPS (Conector Personalizado)
Servidor MCP Remoto (Render.com)
  - Endpoint: /mcp (FastMCP con HTTP transport)
       ↓ HTTP interno (mismo server)
API FastAPI (Render.com - mismo proceso)
  - Endpoint: /search
       ↓ PostgreSQL
Neon Database (pgVector)
```

**🎯 Ventaja clave:** Todo en el mismo proceso de Render, requests internos ultrarrápidos

**Alternativa inicial descartada:**
- ❌ **Servidor MCP local (STDIO):** Requeriría instalación en cada máquina, mala UX

### 3. Transporte: HTTP/SSE ✅ **ACTUALIZADO**

**Decisión:** Usar **HTTP con SSE** (Server-Sent Events) como transporte

**Razones:**
1. **Soporte de Claude Web:** Los conectores personalizados usan HTTP/SSE
2. **Acceso remoto:** Funciona a través de internet (HTTPS)
3. **No requiere OAuth:** MCP no define autenticación estándar, podemos empezar sin ella
4. **FastMCP nativo:** `mcp.run(transport="http")` ya lo soporta

**Configuración:**
```python
from fastmcp import FastMCP

mcp = FastMCP("ai-odoofinder")

# ... definir tools ...

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000))
    )
```

**Alternativa inicial descartada:**
- ❌ **STDIO:** Solo funciona localmente, no soportado por Claude Web

### 4. Integración con API Existente: Mismo Proceso ✅

**Decisión:** Integrar servidor MCP y API FastAPI en el **mismo proceso/aplicación**

**Opciones evaluadas:**

**Opción A: Servidor MCP separado** ❌
```
- MCP Server (puerto 8001) → API Server (puerto 8000) → Neon
- Requiere 2 deployments en Render
- Latencia adicional entre procesos
```

**Opción B: Mismo proceso (elegida)** ✅
```
- MCP Server + API Server (mismo puerto 8000)
- Un solo deployment
- Requests internos (sin latencia de red)
```

**Implementación:**
```python
# backend/app/main.py (actualizado)
from fastapi import FastAPI
from fastmcp import FastMCP

# API existente
app = FastAPI()

# Servidor MCP integrado
mcp = FastMCP.from_fastapi(app=app)  # ← Reutiliza la app FastAPI

@mcp.tool()
async def search_odoo_modules(...):
    # Llama directamente a la lógica de búsqueda
    # NO hace HTTP request, usa imports locales
    from app.services.search_service import SearchService
    results = await SearchService().search(...)
    return format_results(results)
```

**Ventajas:**
- ✅ Cero latencia entre MCP y API (mismo proceso)
- ✅ Reutiliza conexión a DB
- ✅ Un solo deployment en Render
- ✅ Costos reducidos (1 instancia en lugar de 2)

---

## Arquitectura del Servidor MCP Remoto

### Diagrama de Flujo Completo

```
┌─────────────────────────────────────────────────────────────┐
│                  USUARIO (Desarrollador Odoo)                │
│  - En Claude Web (navegador)                                │
│  - En Claude Desktop (app nativa)                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               CLAUDE WEB / CLAUDE DESKTOP                    │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Conector Personalizado Configurado:                  │ │
│  │  Nombre: "AI-OdooFinder"                              │ │
│  │  URL: https://ai-odoo-finder.onrender.com/mcp        │ │
│  │  OAuth: No requerido (MVP)                            │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  - Detecta intención: "buscar módulo de inventario en v17" │
│  - Identifica tool disponible: search_odoo_modules         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼ HTTPS (MCP Protocol via HTTP/SSE)
┌─────────────────────────────────────────────────────────────┐
│           RENDER.COM (ai-odoo-finder.onrender.com)          │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  PROCESO UNIFICADO (Puerto 8000)                      │ │
│  │                                                        │ │
│  │  ┌──────────────────────────────────────────────┐    │ │
│  │  │  SERVIDOR MCP (FastMCP integrado)            │    │ │
│  │  │  Endpoint: /mcp                              │    │ │
│  │  │                                               │    │ │
│  │  │  Tool: search_odoo_modules                   │    │ │
│  │  │  - Valida parámetros                         │    │ │
│  │  │  - Llama directamente a SearchService        │    │ │
│  │  │  - Formatea respuesta para Claude            │    │ │
│  │  └──────────────────┬───────────────────────────┘    │ │
│  │                     │ imports locales (mismo proceso)│ │
│  │                     ▼                                 │ │
│  │  ┌──────────────────────────────────────────────┐    │ │
│  │  │  API REST FASTAPI                            │    │ │
│  │  │  Endpoints: /search, /health, /docs          │    │ │
│  │  │                                               │    │ │
│  │  │  SearchService:                              │    │ │
│  │  │  - Filtrado SQL (version, depends)           │    │ │
│  │  │  - Búsqueda vectorial (pgVector)             │    │ │
│  │  │  - Scoring de calidad                        │    │ │
│  │  └──────────────────┬───────────────────────────┘    │ │
│  └────────────────────────┼────────────────────────────────┘ │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            ▼ PostgreSQL (via SQLAlchemy)
┌─────────────────────────────────────────────────────────────┐
│         NEON POSTGRES (Base de Datos con pgVector)          │
│  Endpoint: ep-xxx.neon.tech                                 │
│                                                             │
│  - 2,508 módulos indexados (v12.0 - v19.0)                 │
│  - Metadata: name, version, depends, description           │
│  - Embeddings vectoriales (4096 dims)                      │
│  - Búsqueda semántica con pgVector                         │
└─────────────────────────────────────────────────────────────┘
```

### 🎯 Flujo de una Búsqueda

```
1. Usuario en Claude Web: "Necesito módulo de inventario v17"
   ↓
2. Claude detecta que debe usar tool search_odoo_modules del conector "AI-OdooFinder"
   ↓
3. Claude hace: POST https://ai-odoo-finder.onrender.com/mcp
   Payload: {"query": "inventario", "version": "17.0"}
   ↓
4. Servidor MCP (FastMCP) recibe request
   ↓
5. MCP llama DIRECTAMENTE a SearchService (import local, mismo proceso)
   → SearchService.search(query="inventario", version="17.0")
   ↓
6. SearchService consulta Neon DB:
   - Filtra: WHERE version='17.0'
   - Búsqueda vectorial con pgVector
   - Calcula scores de calidad
   ↓
7. SearchService retorna list[OdooModule]
   ↓
8. MCP formatea resultados para Claude
   ↓
9. Claude muestra resultados al usuario
```

**⚡ Ventaja:** Pasos 5-7 son instantáneos (sin HTTP overhead)

### Componentes

#### 1. Servidor MCP (Integrado en `backend/app/main.py`)

**Ubicación:** Mismo archivo que API FastAPI

**Responsabilidades:**
- Exponer tool `search_odoo_modules` vía HTTP/SSE
- Validar parámetros de entrada
- Llamar directamente a `SearchService` (import local)
- Formatear respuestas para Claude
- Manejar errores

**Tecnologías:**
- `fastmcp` (para FastMCP.from_fastapi)
- `mcp[cli]` SDK
- Reutiliza servicios existentes de la API

**Código clave:**
```python
from fastmcp import FastMCP
from .services.search_service import SearchService

app = FastAPI()  # API existente
mcp = FastMCP.from_fastapi(app=app)

@mcp.tool()
async def search_odoo_modules(query: str, version: str, ...):
    # Llama directamente al servicio (NO HTTP)
    service = SearchService(db)
    results = await service.search(query, version, ...)
    return format_results(results)
```

#### 2. API REST (Ya existente en `backend/app/`)

**Responsabilidades:**
- Endpoints REST: `/search`, `/health`, `/docs`
- Búsqueda híbrida (SQL + vectorial)
- Scoring de calidad
- Acceso a base de datos

**Cambios requeridos:** ✅ NINGUNO
- Sigue funcionando exactamente igual
- El MCP usa sus servicios internamente

#### 3. Base de Datos Neon (Ya existente)

**Cambios requeridos:** ✅ NINGUNO
- Contiene los 2,508 módulos ya indexados
- SearchService sigue usándola igual

---

## Especificación del Tool

### Tool: `search_odoo_modules`

#### Descripción

Busca módulos de Odoo en repositorios OCA usando búsqueda inteligente impulsada por IA.

#### Firma del Tool

```python
@mcp.tool()
async def search_odoo_modules(
    query: str,
    version: str,
    depends: list[str] | None = None,
    limit: int = 5
) -> str:
    """
    Busca módulos de Odoo compatibles con una versión específica.

    Args:
        query: Descripción de la funcionalidad deseada en lenguaje natural.
               Ejemplos: "gestión de inventario", "pagos recurrentes",
               "reportes de ventas avanzados"

        version: Versión de Odoo requerida.
                Valores válidos: "12.0", "13.0", "14.0", "15.0", "16.0",
                                "17.0", "18.0", "19.0"

        depends: Lista opcional de módulos de los que debe depender.
                Ejemplos: ["sale"], ["account", "stock"]

        limit: Número máximo de resultados a retornar (default: 5, max: 20)

    Returns:
        Resumen formateado de los módulos encontrados con:
        - Nombre y nombre técnico
        - Descripción
        - URL del repositorio
        - Dependencias
        - Score de calidad y similitud
        - Metadata (stars, última actualización)
    """
```

#### Ejemplo de Llamada

**Input (desde Claude):**
```json
{
  "query": "gestión de pagos recurrentes para suscripciones",
  "version": "17.0",
  "depends": ["sale"],
  "limit": 3
}
```

**Procesamiento (MCP Server):**
1. Valida parámetros
2. Construye request HTTP:
   ```python
   response = await http_client.post(
       "https://ai-odoo-finder.onrender.com/search",
       json={
           "query": query,
           "version": version,
           "depends": depends,
           "limit": limit
       }
   )
   ```
3. Recibe respuesta de API
4. Formatea para Claude

**Output (a Claude):**
```
Encontré 3 módulos compatibles con Odoo 17.0:

1. ⭐ Sale Subscription (Score: 87/100)
   Nombre técnico: sale_subscription
   Repositorio: https://github.com/OCA/sale-workflow
   Dependencias: sale, account, payment

   Descripción: Gestión completa de suscripciones con pagos recurrentes,
   renovación automática y facturación periódica.

   Metadata: ⭐ 245 stars | Actualizado hace 2 días | 15 issues abiertos

2. Contract Management (Score: 82/100)
   ...

3. Subscription Payment (Score: 78/100)
   ...
```

#### Casos de Error

**Versión inválida:**
```
Error: La versión "99.0" no es válida.
Versiones soportadas: 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0
```

**Sin resultados:**
```
No encontré módulos que cumplan con:
- Versión: 17.0
- Funcionalidad: "integración con TikTok"
- Dependencias: ninguna

Sugerencias:
1. Intenta con una descripción más general
2. Verifica la versión de Odoo
3. Considera desarrollar un módulo personalizado
```

**Error de API:**
```
Error al conectar con el servicio de búsqueda.
Por favor, intenta de nuevo en unos momentos.
```

---

## Estructura del Proyecto

### Árbol de Directorios

```
ai-odoo-finder/
├── mcp-server/                  # ← NUEVO: Servidor MCP
│   ├── pyproject.toml          # Configuración uv + dependencias
│   ├── README.md               # Documentación del servidor MCP
│   ├── src/
│   │   └── ai_odoofinder_mcp/
│   │       ├── __init__.py
│   │       ├── server.py       # Servidor MCP principal
│   │       ├── client.py       # Cliente HTTP a API
│   │       └── formatters.py   # Formateo de respuestas
│   └── tests/
│       ├── __init__.py
│       ├── test_server.py      # Tests del servidor
│       └── test_integration.py # Tests de integración con API
│
├── backend/                     # Existente (sin cambios)
│   └── app/
│       └── main.py             # API FastAPI
│
├── claude-skill/                # Existente (se mantiene para Code)
│   └── ai-odoofinder-skill/
│       └── Skill.md
│
└── docs/
    ├── MCP_DESIGN.md           # ← Este documento
    ├── MCP_INSTALLATION.md     # ← Guía de instalación para usuarios
    └── ...
```

### Archivos Clave

#### `mcp-server/pyproject.toml`

```toml
[project]
name = "ai-odoofinder-mcp"
version = "0.1.0"
description = "MCP server para búsqueda inteligente de módulos Odoo"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.2.0",
    "httpx>=0.24.0",
    "pydantic>=2.0.0"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
ai-odoofinder-mcp = "ai_odoofinder_mcp.server:main"
```

#### `mcp-server/src/ai_odoofinder_mcp/server.py` (esqueleto)

```python
"""
AI-OdooFinder MCP Server

Servidor MCP que expone búsqueda de módulos Odoo a Claude.
"""

import logging
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Configuración
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    # IMPORTANTE: escribir a stderr, NO stdout (corrompe JSON-RPC)
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Inicializar servidor MCP
mcp = FastMCP("ai-odoofinder")

# URL de la API en producción
API_BASE_URL = "https://ai-odoo-finder.onrender.com"

# Cliente HTTP reutilizable
http_client: httpx.AsyncClient | None = None


async def get_http_client() -> httpx.AsyncClient:
    """Obtener cliente HTTP singleton."""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "ai-odoofinder-mcp/0.1.0"}
        )
    return http_client


@mcp.tool()
async def search_odoo_modules(
    query: str,
    version: str,
    depends: list[str] | None = None,
    limit: int = 5
) -> str:
    """
    Busca módulos de Odoo compatibles con una versión específica.

    Args:
        query: Descripción de funcionalidad (ej: "gestión de inventario")
        version: Versión de Odoo ("12.0" a "19.0")
        depends: Dependencias requeridas (opcional)
        limit: Máximo de resultados (default: 5, max: 20)

    Returns:
        Resumen formateado de módulos encontrados
    """
    # Validar versión
    valid_versions = ["12.0", "13.0", "14.0", "15.0", "16.0", "17.0", "18.0", "19.0"]
    if version not in valid_versions:
        return f"Error: Versión '{version}' inválida. Versiones soportadas: {', '.join(valid_versions)}"

    # Validar limit
    if limit < 1 or limit > 20:
        limit = min(max(limit, 1), 20)

    try:
        client = await get_http_client()

        # Preparar request
        request_data = {
            "query": query,
            "version": version,
            "limit": limit
        }
        if depends:
            request_data["depends"] = depends

        logger.info(f"Buscando módulos: query='{query}', version={version}, depends={depends}")

        # Llamar a API
        response = await client.post(
            f"{API_BASE_URL}/search",
            json=request_data
        )
        response.raise_for_status()

        results = response.json()

        # Formatear respuesta
        if not results:
            return format_no_results(query, version, depends)

        return format_results(results, version)

    except httpx.TimeoutException:
        logger.error("Timeout al conectar con API")
        return "Error: Tiempo de espera agotado. La API tardó demasiado en responder."

    except httpx.HTTPStatusError as e:
        logger.error(f"Error HTTP: {e.response.status_code}")
        return f"Error al buscar módulos (HTTP {e.response.status_code}). Intenta de nuevo."

    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return "Error al buscar módulos. Por favor, intenta de nuevo."


def format_results(results: list[dict[str, Any]], version: str) -> str:
    """Formatea resultados de búsqueda para Claude."""
    output = [f"Encontré {len(results)} módulos compatibles con Odoo {version}:\n"]

    for i, module in enumerate(results, 1):
        quality = module.get("quality_score", 0)
        similarity = module.get("similarity_score", 0)

        # Emoji según calidad
        if quality >= 70:
            emoji = "⭐"
            badge = "✅ Muy recomendado"
        elif quality >= 40:
            emoji = "📦"
            badge = ""
        else:
            emoji = "⚠️"
            badge = "⚠️ Poco mantenido"

        output.append(f"{i}. {emoji} {module['name']} (Score: {quality}/100) {badge}")
        output.append(f"   Nombre técnico: {module['technical_name']}")
        output.append(f"   Repositorio: {module['repo_url']}")
        output.append(f"   Dependencias: {', '.join(module['depends'])}")

        if module.get('description'):
            desc = module['description'][:200] + "..." if len(module['description']) > 200 else module['description']
            output.append(f"   Descripción: {desc}")

        # Metadata
        stars = module.get('github_stars', 0)
        last_update = module.get('last_commit_date', 'Desconocido')
        issues = module.get('github_issues_open', 0)
        output.append(f"   Metadata: ⭐ {stars} stars | Actualizado: {last_update} | {issues} issues abiertos")
        output.append("")  # Línea en blanco

    return "\n".join(output)


def format_no_results(query: str, version: str, depends: list[str] | None) -> str:
    """Formatea mensaje cuando no hay resultados."""
    output = ["No encontré módulos que cumplan con:\n"]
    output.append(f"- Versión: {version}")
    output.append(f"- Funcionalidad: \"{query}\"")
    if depends:
        output.append(f"- Dependencias: {', '.join(depends)}")
    else:
        output.append("- Dependencias: ninguna")

    output.append("\nSugerencias:")
    output.append("1. Intenta con una descripción más general")
    output.append("2. Verifica la versión de Odoo")
    output.append("3. Revisa las dependencias requeridas")
    output.append("4. Considera desarrollar un módulo personalizado")

    return "\n".join(output)


def main():
    """Punto de entrada del servidor MCP."""
    logger.info("Iniciando servidor MCP AI-OdooFinder...")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
```

---

## Plan de Implementación

### Fase 1: Implementación Core (3-4 días)

#### Día 1: Setup del Proyecto
- [ ] Crear directorio `mcp-server/`
- [ ] Configurar `pyproject.toml` con dependencias
- [ ] Crear estructura de carpetas (`src/`, `tests/`)
- [ ] Configurar logging (stderr, no stdout)
- [ ] Setup de entorno con `uv`

#### Día 2: Implementación del Tool
- [ ] Implementar `search_odoo_modules` tool
- [ ] Cliente HTTP a la API de Render
- [ ] Validación de parámetros
- [ ] Formateo de respuestas
- [ ] Manejo de errores (timeout, HTTP errors, API down)

#### Día 3: Testing Local
- [ ] Tests unitarios del tool
- [ ] Tests de integración con API real
- [ ] Testing con `uv run mcp dev server.py` (inspector)
- [ ] Validar logging (verificar que no usa stdout)

#### Día 4: Documentación
- [ ] README del servidor MCP
- [ ] Guía de instalación para Claude Desktop
- [ ] Ejemplos de uso
- [ ] Troubleshooting

### Fase 2: Testing en Claude Desktop (2-3 días)

#### Día 5: Instalación y Configuración
- [ ] Instalar servidor en Claude Desktop: `uv run mcp install server.py`
- [ ] Verificar `claude_desktop_config.json`
- [ ] Reiniciar Claude Desktop
- [ ] Verificar que aparece en "Search and tools"

#### Día 6: Testing Funcional
- [ ] Caso 1: Búsqueda simple ("módulo de inventario en v17")
- [ ] Caso 2: Con dependencias ("módulo de ventas que use account en v16")
- [ ] Caso 3: Sin resultados ("módulo de TikTok en v12")
- [ ] Caso 4: Versión inválida (error handling)
- [ ] Caso 5: API caída (error handling)

#### Día 7: Refinamiento
- [ ] Ajustar formateo de respuestas según feedback
- [ ] Optimizar mensajes de error
- [ ] Mejorar logging
- [ ] Documentar casos de edge encontrados

### Fase 3: Documentación y Deploy (1-2 días)

#### Día 8: Documentación Final
- [ ] Actualizar [NEXT_STEPS.md](NEXT_STEPS.md)
- [ ] Actualizar [ROADMAP.md](ROADMAP.md)
- [ ] Crear [MCP_INSTALLATION.md](MCP_INSTALLATION.md) para usuarios
- [ ] Actualizar README principal

#### Día 9: Preparar Release
- [ ] Tag de versión v0.1.0
- [ ] Release notes
- [ ] Video tutorial (opcional)
- [ ] Publicar en GitHub

---

## Testing y Validación

### Tests Unitarios

#### `tests/test_server.py`

```python
import pytest
from unittest.mock import AsyncMock, patch
from ai_odoofinder_mcp.server import search_odoo_modules, format_results

@pytest.mark.asyncio
async def test_search_valid_version():
    """Test búsqueda con versión válida."""
    with patch('ai_odoofinder_mcp.server.get_http_client') as mock_client:
        # Mock response de API
        mock_response = AsyncMock()
        mock_response.json.return_value = [
            {
                "name": "Stock Management",
                "technical_name": "stock_management",
                "version": "17.0",
                "depends": ["stock"],
                "quality_score": 85,
                "similarity_score": 0.9,
                "repo_url": "https://github.com/OCA/stock",
                "description": "Gestión avanzada de inventario",
                "github_stars": 150,
                "last_commit_date": "2025-01-10",
                "github_issues_open": 5
            }
        ]
        mock_response.raise_for_status = AsyncMock()

        mock_http = AsyncMock()
        mock_http.post.return_value = mock_response
        mock_client.return_value = mock_http

        result = await search_odoo_modules(
            query="gestión de inventario",
            version="17.0"
        )

        assert "Stock Management" in result
        assert "17.0" in result
        assert "✅ Muy recomendado" in result

@pytest.mark.asyncio
async def test_search_invalid_version():
    """Test búsqueda con versión inválida."""
    result = await search_odoo_modules(
        query="test",
        version="99.0"
    )

    assert "Error" in result
    assert "99.0" in result
    assert "inválida" in result

@pytest.mark.asyncio
async def test_search_timeout():
    """Test manejo de timeout."""
    with patch('ai_odoofinder_mcp.server.get_http_client') as mock_client:
        mock_http = AsyncMock()
        mock_http.post.side_effect = httpx.TimeoutException("Timeout")
        mock_client.return_value = mock_http

        result = await search_odoo_modules(
            query="test",
            version="17.0"
        )

        assert "Tiempo de espera agotado" in result
```

### Tests de Integración

#### `tests/test_integration.py`

```python
import pytest
import httpx
from ai_odoofinder_mcp.server import search_odoo_modules

@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_api_search():
    """Test con API real (requiere que API esté corriendo)."""
    result = await search_odoo_modules(
        query="sale",
        version="16.0",
        limit=3
    )

    # Verificar que no hay errores
    assert "Error" not in result
    # Verificar formato
    assert "módulos compatibles con Odoo 16.0" in result
```

### Testing Manual con Claude Desktop

**Casos de Prueba:**

1. **Búsqueda Simple:**
   ```
   Usuario: "Necesito un módulo de inventario para Odoo 17"
   Esperado: Lista de módulos de stock/inventory con score alto
   ```

2. **Con Dependencias:**
   ```
   Usuario: "Busca módulos de ventas que usen accounting en v16"
   Esperado: Solo módulos con "account" en depends
   ```

3. **Sin Resultados:**
   ```
   Usuario: "Módulo de integración con TikTok en Odoo 12"
   Esperado: Mensaje claro de "no encontrado" + sugerencias
   ```

4. **Error Handling:**
   ```
   Simular: API caída (detener Render temporalmente)
   Esperado: Mensaje de error amigable, no crash
   ```

---

## Configuración y Deploy

### Configuración en Claude Desktop

**Ubicación del archivo de configuración:**

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Contenido de `claude_desktop_config.json`:**

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/spbarber/Desarrollo/ai-odoo-finder/mcp-server",
        "run",
        "ai-odoofinder-mcp"
      ]
    }
  }
}
```

**⚠️ IMPORTANTE:** Usar **ruta absoluta**, no relativa.

### Instalación Automática

Comando recomendado para usuarios:

```bash
cd /Users/spbarber/Desarrollo/ai-odoo-finder/mcp-server
uv run mcp install src/ai_odoofinder_mcp/server.py
```

Esto actualiza automáticamente `claude_desktop_config.json`.

### Verificación

1. **Reiniciar Claude Desktop completamente** (Cmd+Q en macOS, no solo cerrar ventana)

2. **Verificar logs:**
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

3. **Verificar en Claude Desktop:**
   - Buscar ícono "Search and tools"
   - Debe aparecer "ai-odoofinder" con tool "search_odoo_modules"

4. **Test básico:**
   ```
   "¿Hay módulos de inventario para Odoo 17?"
   ```
   Claude debería automáticamente usar el tool.

### Troubleshooting

**Problema:** El servidor no aparece en Claude Desktop

**Soluciones:**
1. Verificar ruta absoluta en config
2. Verificar que `uv` está en PATH
3. Revisar logs: `~/Library/Logs/Claude/mcp*.log`
4. Reiniciar completamente Claude (Cmd+Q)

**Problema:** Errores en logs sobre "corrupted JSON-RPC"

**Solución:** Asegurar que el servidor NO usa `print()` - solo `logging` a stderr

**Problema:** API timeout

**Solución:**
1. Verificar que Render no esté en "sleep mode"
2. Aumentar timeout en `httpx.AsyncClient(timeout=60.0)`

---

## Criterios de Éxito

### Fase 1 Completada ✅

- [ ] Servidor MCP funcional localmente
- [ ] Tool `search_odoo_modules` implementado
- [ ] Validación de parámetros funcionando
- [ ] Formateo de respuestas claro y útil
- [ ] Manejo de errores robusto
- [ ] Logging correcto (stderr, no stdout)
- [ ] Tests unitarios pasando (>80% coverage)

### Fase 2 Completada ✅

- [ ] Instalado en Claude Desktop
- [ ] Aparece en "Search and tools"
- [ ] Búsquedas simples funcionan
- [ ] Búsquedas con dependencias funcionan
- [ ] Mensajes de error claros
- [ ] Sin crashes en 10 consultas consecutivas
- [ ] Logs limpios sin errores

### Fase 3 Completada ✅

- [ ] Documentación completa ([MCP_INSTALLATION.md](MCP_INSTALLATION.md))
- [ ] README del servidor actualizado
- [ ] [NEXT_STEPS.md](NEXT_STEPS.md) actualizado
- [ ] Video tutorial (opcional)
- [ ] Release v0.1.0 publicado

---

## Próximos Pasos

Una vez completado el Sprint 2 (MCP Server):

1. **Sprint 4:** Odoo App Store (scraping módulos oficiales)
2. **Sprint 5:** Módulos Custom (indexar módulos privados de empresas)
3. **Mejoras MCP:**
   - Agregar más tools (ej: `get_module_details`, `check_dependencies`)
   - Recursos MCP (ej: acceso a documentación de módulos)
   - Prompts especializados

---

## Referencias

- [Model Context Protocol Docs](https://modelcontextprotocol.io)
- [Python SDK GitHub](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop MCP Guide](https://docs.anthropic.com/claude/docs/mcp)
- [FastMCP API Reference](https://github.com/modelcontextprotocol/python-sdk#fastmcp)
- [MCP Servers Examples](https://github.com/modelcontextprotocol/servers)

---

**Última actualización:** 15 Noviembre 2025
**Próxima revisión:** Al completar Fase 1
