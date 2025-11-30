# AI-OdooFinder

> **Encuentra el modulo de Odoo perfecto con IA en segundos.**

Un servidor MCP (Model Context Protocol) que permite a Claude buscar modulos de Odoo en los repositorios de OCA usando busqueda hibrida (semantica + full-text).

<div align="center">

![AI-OdooFinder Banner](docs/logo-banner.svg)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Odoo](https://img.shields.io/badge/Odoo-10.0%20to%2019.0-714B67)](https://www.odoo.com)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)

**Idioma**: [English](README.md) | [Español](README.es.md)

</div>

---

## El Problema

Como desarrollador de Odoo:

- Desarrollas funcionalidades que ya existen en OCA
- Pierdes horas buscando el modulo correcto en GitHub
- Instalas modulos incompatibles con tu version
- Descubres modulos abandonados despues de integrarlos

---

## La Solucion

**AI-OdooFinder** proporciona:

- **Busqueda Hibrida**: Combina busqueda semantica (embeddings) con BM25 full-text
- **Filtrado por Version**: Solo muestra modulos compatibles (10.0 a 19.0)
- **Enrichment con IA**: Descripciones, tags y keywords generados por Grok-4-fast
- **Integracion MCP**: Usa directamente desde Claude Desktop o Claude.ai

---

## Arquitectura

```
┌─────────────────────┐      ┌──────────────────────────────────────┐
│  Claude.ai Web      │      │        Hetzner VPS (Docker)          │
│  Zed / Cursor       │─────►│  ┌─────────────┐  ┌──────────────┐   │
│  (remote MCP)       │ HTTPS│  │ MCP Server  │  │   FastAPI    │   │
└─────────────────────┘      │  │  :8080/mcp  │─►│   :8989      │   │
                             │  └─────────────┘  └──────┬───────┘   │
┌─────────────────────┐      │                          │           │
│   Claude Desktop    │      │                   ┌──────▼───────┐   │
│   + MCP Server      │─────►│                   │  PostgreSQL  │   │
│   (local, STDIO)    │ HTTPS│                   │  + pgvector  │   │
└─────────────────────┘      │                   └──────────────┘   │
                             └──────────────────────────────────────┘
```

**Modos de uso:**
- **Remote MCP** (Claude.ai Web, Zed, Cursor): Conectan al MCP Server remoto via HTTP
- **Local MCP** (Claude Desktop): MCP Server corre localmente via STDIO
- **API REST directa**: Para integraciones custom

**Componentes:**
- **MCP Server HTTP** (remoto, :8080): Servidor MCP para clientes remotos
- **FastAPI Backend** (remoto, :8989): API REST con busqueda hibrida
- **PostgreSQL + pgvector** (remoto): 16,494 modulos con embeddings

---

## Estadisticas

| Metrica | Valor |
|---------|-------|
| Modulos Indexados | **16,494** |
| Versiones Odoo | 10 (v10.0 - v19.0) |
| Repositorios OCA | **244** |
| Con AI Enrichment | **100%** |
| Tiempo respuesta | < 500ms |

### Modulos por Version

| Version | Modulos |
|---------|---------|
| 10.0 | 2,312 |
| 11.0 | 2,105 |
| 12.0 | 2,215 |
| 13.0 | 1,990 |
| 14.0 | 2,886 |
| 15.0 | 2,074 |
| 16.0 | 2,886 |
| 17.0 | 1,699 |
| 18.0 | 2,022 |
| 19.0 | 112 |

---

## Instalacion

AI-OdooFinder soporta multiples plataformas. Elige la que uses:

### Claude.ai Web (Remote MCP)

Conecta directamente desde Claude.ai sin instalar nada:

1. Ve a **Claude.ai** > **Settings** > **Conectores**
2. Click en **"Anadir conector personalizado"**
3. Introduce la URL del servidor MCP:
   ```
   https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp
   ```
4. Guarda y empieza a buscar modulos

> **Nota**: El servidor es publico y no requiere autenticacion.

---

### Claude Desktop (Local MCP)

Para usar con Claude Desktop en tu maquina:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/SantipBarber/ai-odoo-finder#subdirectory=mcp-server", "ai-odoofinder-mcp"],
      "env": {
        "AI_ODOOFINDER_API_URL": "https://strategy-orchestrator-prod.tailf7d690.ts.net"
      }
    }
  }
}
```

Reinicia Claude Desktop y pregunta sobre modulos de Odoo.

---

### Zed Editor

Configura en `~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "ai-odoofinder": {
      "command": {
        "path": "uvx",
        "args": ["--from", "git+https://github.com/SantipBarber/ai-odoo-finder#subdirectory=mcp-server", "ai-odoofinder-mcp"],
        "env": {
          "AI_ODOOFINDER_API_URL": "https://strategy-orchestrator-prod.tailf7d690.ts.net"
        }
      }
    }
  }
}
```

---

### Cursor

Configura en `.cursor/mcp.json` (proyecto) o `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/SantipBarber/ai-odoo-finder#subdirectory=mcp-server", "ai-odoofinder-mcp"],
      "env": {
        "AI_ODOOFINDER_API_URL": "https://strategy-orchestrator-prod.tailf7d690.ts.net"
      }
    }
  }
}
```

---

### Otros Clientes MCP (Remote HTTP)

Para cualquier cliente que soporte MCP remoto via HTTP/SSE:

**URL del servidor MCP:**
```
https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp
```

**Protocolo**: Streamable HTTP (MCP spec 2024-11-05)
**Autenticacion**: Ninguna (servidor publico)

---

### Desplegar tu propia instancia

Ver [docs/DEPLOYMENT_OPERATIONS.md](docs/DEPLOYMENT_OPERATIONS.md) para instrucciones de despliegue con Docker.

---

## Uso

### Desde Claude Desktop (MCP)

Simplemente pregunta en lenguaje natural:

```
"Necesito un modulo para Odoo 17 que maneje pagos recurrentes"
```

Claude usara el MCP Server para buscar y te mostrara los resultados.

### API REST Directa

```bash
# Health check
curl https://strategy-orchestrator-prod.tailf7d690.ts.net/health

# Busqueda
curl "https://strategy-orchestrator-prod.tailf7d690.ts.net/search?query=subscription&version=17.0&limit=5"

# Estadisticas
curl https://strategy-orchestrator-prod.tailf7d690.ts.net/stats
```

---

## Stack Tecnologico

| Componente | Tecnologia |
|------------|------------|
| Backend | FastAPI (Python 3.13+) |
| Base de Datos | PostgreSQL 17 + pgvector |
| Embeddings | Qwen3-Embedding-4B via OpenRouter |
| Enrichment | Grok-4-fast via OpenRouter |
| MCP Server | FastMCP (Python) |
| Contenedores | Docker + Docker Compose |
| Hosting | Hetzner VPS (ARM64) |
| Tunnel | Tailscale Funnel (HTTPS) |

---

## Documentacion

- [Deployment & Operations](docs/DEPLOYMENT_OPERATIONS.md) - Guia de despliegue y operaciones
- [MCP Design](docs/MCP_DESIGN.md) - Diseno del servidor MCP
- [Changelog](docs/CHANGELOG.md) - Historial de cambios

---

## Desarrollo

### Requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (gestor de dependencias)
- Docker (para PostgreSQL local)

### Setup Local

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

# Ejecutar ETL (indexar modulos)
uv run python scripts/etl_oca_modules.py

# Iniciar API
uv run uvicorn backend.app.main:app --port 8989
```

---

## Licencia

MIT - Ver [LICENSE](LICENSE)

---

## Autor

**Santiago Perez Barber**
- GitHub: [@SantipBarber](https://github.com/SantipBarber)
- LinkedIn: [santipbarber](https://linkedin.com/in/santipbarber)

---

## Agradecimientos

- [Odoo Community Association (OCA)](https://odoo-community.org/) - Por su trabajo open source
- [Anthropic](https://www.anthropic.com/) - Por Claude y el protocolo MCP
