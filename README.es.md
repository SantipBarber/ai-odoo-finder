# AI-OdooFinder

> **Encuentra el módulo de Odoo perfecto con IA en segundos.**

Un servidor MCP (Model Context Protocol) que permite a los LLMs buscar módulos de Odoo en los repositorios de OCA usando búsqueda híbrida (semántica + full-text).

<div align="center">

![AI-OdooFinder Banner](docs/logo-banner.svg)

[![PyPI version](https://img.shields.io/pypi/v/ai-odoofinder-mcp.svg)](https://pypi.org/project/ai-odoofinder-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Odoo](https://img.shields.io/badge/Odoo-14.0%20to%2019.0-714B67)](https://www.odoo.com)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/SantipBarber/ai-odoo-finder)

**Idioma**: [English](README.md) | [Español](README.es.md)

</div>

---

## El Problema

Como desarrollador de Odoo:

- Desarrollas funcionalidades que ya existen en OCA
- Pierdes horas buscando el módulo correcto en GitHub
- Instalas módulos incompatibles con tu versión
- Descubres módulos abandonados después de integrarlos

---

## La Solución

**AI-OdooFinder** proporciona:

- **Búsqueda Híbrida**: Combina búsqueda semántica (embeddings) con BM25 full-text
- **Filtrado por Versión**: Solo muestra módulos compatibles (14.0 a 19.0)
- **Enriquecimiento con IA**: Descripciones, tags y keywords generados por Grok-4-fast
- **Integración MCP**: Úsalo desde Claude, ChatGPT, Cursor, VS Code, Zed... mediante una URL pública

---

## Arquitectura

```
┌──────────────────────────┐         ┌───────────────────────────────────────┐
│  Claude.ai / Desktop     │         │  Infraestructura de Eticco (Docker)   │
│  Claude Code · ChatGPT   │  HTTPS  │  ┌──────────────┐   ┌─────────────┐   │
│  Cursor · VS Code · Zed  │────────►│  │  MCP Server  │──►│   FastAPI   │   │
│  Windsurf · ...          │         │  │ (Streamable  │   │   backend   │   │
└──────────────────────────┘         │  │    HTTP)     │   └──────┬──────┘   │
   https://addon-finder.eticco.es    │  └──────────────┘          │          │
                                     │                     ┌──────▼──────┐   │
                                     │                     │ PostgreSQL  │   │
                                     │                     │ + pgvector  │   │
                                     │                     └─────────────┘   │
                                     └───────────────────────────────────────┘
```

**Modos de uso:**
- **MCP remoto (recomendado)**: Apunta cualquier cliente MCP a `https://addon-finder.eticco.es`, sin instalar nada
- **MCP local (STDIO)**: El [paquete de PyPI](https://pypi.org/project/ai-odoofinder-mcp/) se ejecuta en local contra tu propio backend (self-hosting)

**Componentes:**
- **MCP Server** (Streamable HTTP): endpoint público para clientes MCP
- **FastAPI Backend**: motor de búsqueda híbrida (interno)
- **PostgreSQL + pgvector**: más de 19.700 módulos con embeddings

> **Instancia pública** alojada por [Eticco](https://www.eticco.es). La búsqueda sobre módulos de la comunidad OCA es **abierta y no requiere login**. Eticco también está ampliando el servicio con sus propios módulos internos; esa parte requiere autenticación y es solo para uso interno.

---

## Estadísticas

| Métrica | Valor |
|---------|-------|
| Módulos indexados | **19.700+** |
| Versiones de Odoo | 6 (14.0 – 19.0) |
| Con enriquecimiento IA | **100%** |

---

## Instalación

**No hace falta instalar nada.** AI-OdooFinder está disponible como servidor MCP remoto público:

```
https://addon-finder.eticco.es
```

| | |
|---|---|
| **Transporte** | Streamable HTTP |
| **Autenticación** | Ninguna para módulos de la comunidad OCA |
| **Herramienta** | `search_odoo_modules` |

Añade esa URL a tu cliente MCP (ver más abajo). Si tu cliente solo admite servidores locales STDIO, usa el puente [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) (requiere Node.js):

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://addon-finder.eticco.es"]
    }
  }
}
```

### Configuración por IDE/Cliente

<details>
<summary><b>Claude.ai Web / Claude Desktop</b></summary>

1. Ve a **Ajustes** > **Conectores**
2. Haz clic en **"Añadir conector personalizado"**
3. Introduce la URL del servidor MCP:
   ```
   https://addon-finder.eticco.es
   ```
4. Guarda y empieza a buscar

> Los conectores personalizados se comparten entre Claude.ai y Claude Desktop. En versiones antiguas de Desktop sin conectores, usa la configuración de `mcp-remote` de arriba en `claude_desktop_config.json`.

</details>

<details>
<summary><b>Claude Code CLI</b></summary>

```bash
claude mcp add --transport http ai-odoofinder https://addon-finder.eticco.es
```

Uso:
```bash
claude
> Necesito un módulo de Odoo 17 para suscripciones
```

</details>

<details>
<summary><b>ChatGPT (Developer Mode)</b></summary>

1. Ve a **Settings** > **Apps & Connectors** > **Advanced** y activa **Developer Mode**
2. Crea un nuevo conector con la URL `https://addon-finder.eticco.es`
3. Autenticación: **Ninguna**

**Uso:**
```
Usa ai-odoofinder para buscar módulos de Odoo 17 para inventario
```

</details>

<details>
<summary><b>VS Code (GitHub Copilot)</b></summary>

Crea `.vscode/mcp.json` (proyecto) o añádelo a tu `mcp.json` de usuario:

```json
{
  "servers": {
    "ai-odoofinder": {
      "type": "http",
      "url": "https://addon-finder.eticco.es"
    }
  }
}
```

> **Para Business/Enterprise**: El administrador debe habilitar la política "MCP servers in Copilot".

</details>

<details>
<summary><b>Cursor</b></summary>

Añade a `.cursor/mcp.json` (proyecto) o `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "url": "https://addon-finder.eticco.es"
    }
  }
}
```

</details>

<details>
<summary><b>Windsurf</b></summary>

Añade a `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "serverUrl": "https://addon-finder.eticco.es"
    }
  }
}
```

</details>

<details>
<summary><b>Zed</b></summary>

Añade a `~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "ai-odoofinder": {
      "url": "https://addon-finder.eticco.es"
    }
  }
}
```

</details>

<details>
<summary><b>Antigravity y otros clientes solo STDIO</b></summary>

Usa el puente `mcp-remote`:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://addon-finder.eticco.es"]
    }
  }
}
```

> **Ver solución de problemas completa**: [Configuraciones de Clientes MCP](docs/es/MCP_CLIENT_CONFIGURATIONS.md)

</details>

<details>
<summary><b>Paquete STDIO local (backend propio)</b></summary>

El paquete de PyPI [`ai-odoofinder-mcp`](https://pypi.org/project/ai-odoofinder-mcp/) ejecuta el servidor MCP en local y se comunica con la API REST del backend FastAPI. La instancia pública no expone esa API REST, así que este modo está pensado para **tu propio despliegue** (ver [Despliegue y operaciones](docs/es/DEPLOYMENT_OPERATIONS.md)):

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uvx",
      "args": ["ai-odoofinder-mcp"],
      "env": {
        "AI_ODOOFINDER_API_URL": "http://localhost:8989"
      }
    }
  }
}
```

> Requiere [uv](https://docs.astral.sh/uv/).

</details>

**Guía completa de configuración**: [Configuraciones de Clientes MCP](docs/es/MCP_CLIENT_CONFIGURATIONS.md)

---

## Matriz de Compatibilidad de Clientes

| Cliente | URL remota | Vía `mcp-remote` | Notas |
|---------|:----------:|:----------------:|-------|
| Claude.ai Web | ✅ | — | Conector personalizado |
| Claude Desktop | ✅ | ✅ | Conector o puente |
| Claude Code CLI | ✅ | ✅ | `--transport http` |
| ChatGPT Dev Mode | ✅ | — | Developer Mode |
| VS Code Copilot | ✅ | ✅ | `type: http` |
| Cursor | ✅ | ✅ | |
| Windsurf | ✅ | ✅ | `serverUrl` |
| Zed | ✅ | ✅ | |
| Antigravity | ⚠️ | ✅ | Usa el puente |

**Detalles completos**: Ver [Configuraciones de Clientes MCP](docs/es/MCP_CLIENT_CONFIGURATIONS.md)

---

### Desplegar tu propia instancia

Ver [docs/es/DEPLOYMENT_OPERATIONS.md](docs/es/DEPLOYMENT_OPERATIONS.md) para instrucciones de despliegue con Docker.

---

## Uso

Una vez conectado, basta con preguntar en lenguaje natural:

```
"Necesito un módulo para Odoo 17 que gestione pagos recurrentes"
```

Tu asistente llamará a `search_odoo_modules` y te mostrará los módulos OCA compatibles con su repositorio, resumen y enlace a GitHub.

Comprueba el estado del servicio:

```bash
curl https://addon-finder.eticco.es/health
```

> La API REST de FastAPI (`/search`, `/stats`) solo está expuesta en despliegues propios (`http://localhost:8989`).

---

## Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Backend | FastAPI (Python 3.14) |
| Base de Datos | PostgreSQL 17 + pgvector |
| Embeddings | Qwen3-Embedding-4B vía OpenRouter |
| Enriquecimiento | Grok-4-fast vía OpenRouter |
| MCP Server | FastMCP (Python) |
| Contenedores | Docker + Docker Compose |
| Hosting | Infraestructura de Eticco (Docker + nginx) |

---

## Documentación

- [Showcase Interactivo](https://santipbarber.github.io/ai-odoo-finder/showcase/) - Presentación visual del proyecto
- [Configuraciones de Clientes MCP](docs/es/MCP_CLIENT_CONFIGURATIONS.md) - Guía completa para todos los clientes MCP
- [Despliegue y operaciones](docs/es/DEPLOYMENT_OPERATIONS.md) - Guía de despliegue y operaciones
- [Historia del proyecto](docs/es/PROJECT_HISTORY.md) - Evolución de la arquitectura del proyecto
- [Registro de cambios](docs/es/CHANGELOG.md) - Historial de cambios
- [README del servidor MCP](mcp-server/README.es.md) - Instalación y configuración del servidor MCP

---

## Desarrollo

### Requisitos

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (gestor de dependencias)
- Docker (para PostgreSQL local)

### Configuración local

```bash
# Clonar
git clone https://github.com/SantipBarber/ai-odoo-finder.git
cd ai-odoo-finder

# Instalar dependencias
uv sync

# Configurar variables
cp .env.example .env
# Editar .env con tus credenciales

# Iniciar PostgreSQL
docker compose up -d db

# Ejecutar ETL (indexar módulos)
uv run python scripts/etl_oca_modules.py

# Iniciar API
uv run uvicorn backend.app.main:app --port 8989
```

---

## Licencia

MIT - Ver [LICENSE](LICENSE)

---

## Autor

**Santiago Pérez Barber**
- GitHub: [@SantipBarber](https://github.com/SantipBarber)
- LinkedIn: [santipbarber](https://linkedin.com/in/santipbarber)

---

## Agradecimientos

- [Odoo Community Association (OCA)](https://odoo-community.org/) - Por su trabajo open source
- [Anthropic](https://www.anthropic.com/) - Por Claude y el protocolo MCP
