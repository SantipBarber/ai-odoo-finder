# Servidor MCP de AI-OdooFinder

**Language**: [English](README.md) | [Español](README.es.md)

Servidor MCP (Protocolo de Contexto Modelo) para búsqueda semántica de módulos de Odoo en el ecosistema OCA.

## Resumen

Este servidor MCP proporciona una herramienta llamada `search_odoo_modules` que permite a los LLMs buscar entre 16,494 módulos de Odoo indexados desde repositorios OCA usando búsqueda híbrida (semántica + BM25).

## Inicio Rápido

Para instrucciones de instalación, consulta el [README principal del proyecto](../README.es.md#instalacion).

Configuración básica:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/SantipBarber/ai-odoo-finder#subdirectory=mcp-server",
        "ai-odoofinder-mcp"
      ],
      "env": {
        "AI_ODOOFINDER_API_URL": "https://strategy-orchestrator-prod.tailf7d690.ts.net"
      }
    }
  }
}
```

> **Nota**: Requiere el gestor de paquetes [uv](https://docs.astral.sh/uv/) instalado.

---

## Características

- **Búsqueda Híbrida**: Combina búsqueda semántica (embeddings) con BM25 full-text
- **Filtrado por Versión**: Solo muestra módulos compatibles (Odoo 10.0 a 19.0)
- **Enriquecimiento IA**: Descripciones, tags y keywords generados por Grok-4-fast
- **Flujo Inteligente**: Aclaraciones inteligentes, expansión de consultas, niveles de confianza

---

## Arquitectura

```
┌─────────────────┐
│  Cliente MCP    │ (Claude Desktop, Zed, Cursor, etc.)
│  (STDIO/HTTP)   │
└────────┬────────┘
         │
         │ JSON-RPC / SSE
         │
┌────────▼────────┐
│  Servidor MCP   │ (Este componente)
│  FastMCP + uv   │
└────────┬────────┘
         │
         │ HTTPS
         │
┌────────▼────────┐
│   Backend API   │ (FastAPI + PostgreSQL)
│   :8989         │
└─────────────────┘
```

**Dos modos:**
- **STDIO**: Para clientes locales (Claude Desktop)
- **HTTP/SSE**: Para clientes remotos (Claude.ai Web, requiere puerto 8080)

---

## Herramientas

### `search_odoo_modules`

Busca módulos de Odoo usando consultas en lenguaje natural.

**Parámetros:**
- `query` (string, requerido): Consulta de búsqueda en lenguaje natural
- `version` (string, requerido): Versión de Odoo (ej. "16.0", "17.0")
- `limit` (integer, opcional): Máximo de resultados (predeterminado: 10, máx: 50)
- `dependencies` (string, opcional): Filtrar por dependencias (separadas por comas)

**Devuelve:**
- JSON estructurado con módulos, nivel de confianza y guía

**Ejemplo:**
```json
{
  "query": "facturación electrónica para España",
  "version": "16.0",
  "limit": 5
}
```

---

## Flujo de Búsqueda Inteligente

El servidor implementa un flujo de búsqueda inteligente:

1. **Aclaración**: Solicita detalles si la consulta es genérica o falta versión
2. **Expansión de Consulta**: Añade sinónimos ES/EN, prefijos de localización (`l10n_XX_`)
3. **Respuesta Estructurada**: Devuelve resultados con niveles de confianza:
   - **HIGH** (puntuación ≥80): Formato detallado con recomendaciones
   - **MEDIUM** (50-79): Formato resumen con alternativas
   - **LOW** (<50): Sugerencias para refinar búsqueda
4. **Confirmación**: Valida con el usuario si encontró lo que buscaba

---

## Variables de Entorno

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `AI_ODOOFINDER_API_URL` | `http://localhost:8989` | URL de la API backend |
| `AI_ODOOFINDER_API_TIMEOUT` | `60` | Timeout de la API en segundos |

---

## Estructura del Proyecto

```
mcp-server/
├── pyproject.toml           # Configuración del paquete (instalable con uvx)
├── README.md                # Este archivo
└── src/
    └── ai_odoofinder_mcp/
        ├── __init__.py
        └── server.py        # Servidor MCP principal (FastMCP)
```

---

## Desarrollo

### Pruebas Locales

```bash
# Instalar dependencias
cd mcp-server
uv sync

# Ejecutar servidor (modo STDIO)
uv run ai-odoofinder-mcp

# Probar con MCP Inspector
npx @modelcontextprotocol/inspector uv run ai-odoofinder-mcp
```

### Modo HTTP (para clientes remotos)

```bash
# Ejecutar con transporte HTTP
uv run ai-odoofinder-mcp --http --port 8080
```

---

## Integración con la API

El servidor MCP se conecta al backend FastAPI en la URL especificada en `AI_ODOOFINDER_API_URL`.

**Endpoints del backend utilizados:**
- `GET /api/v1/search` - Búsqueda híbrida
- `GET /health` - Verificación de salud

**Algoritmo de búsqueda:**
1. Generar embedding para la consulta (Qwen3-Embedding-4B)
2. Búsqueda vectorial (pgvector HNSW)
3. Búsqueda full-text BM25 (PostgreSQL tsvector)
4. Combinar resultados con Fusión Recíproca de Ranking (RRF)

```
RRF_score = 1/(k + rank_vector) + 1/(k + rank_bm25)
```

Donde `k=60` (constante estándar RRF)

---

## Solución de Problemas

### El servidor no arranca

1. **Verifica que `uv` está instalado:**
   ```bash
   uv --version
   ```

2. **Verifica la versión de Python:**
   ```bash
   python --version  # Debe ser 3.11+
   ```

3. **Reinstala las dependencias:**
   ```bash
   uv sync --reinstall
   ```

### Falla la conexión a la API

1. **Verifica que la API es accesible:**
   ```bash
   curl https://strategy-orchestrator-prod.tailf7d690.ts.net/health
   ```

2. **Verifica configuración de timeout:**
   ```bash
   export AI_ODOOFINDER_API_TIMEOUT=120
   ```

### El cliente MCP no ve la herramienta

1. **Revisa los logs del cliente MCP** para errores de conexión
2. **Verifica que JSON-RPC funciona**: Usa MCP Inspector
3. **Reinicia el cliente MCP completamente**

---

## Publicación

El servidor MCP es instalable via `uvx` directamente desde Git:

```bash
uvx --from git+https://github.com/SantipBarber/ai-odoo-finder#subdirectory=mcp-server ai-odoofinder-mcp
```

Para publicar en PyPI (futuro):

```bash
cd mcp-server
uv build
uv publish
```

---

## Documentación Relacionada

- [README Principal del Proyecto](../README.es.md) - Guía de instalación para usuarios
- [Backend API](../backend/README.md) - Backend FastAPI
- [CHANGELOG](../docs/es/CHANGELOG.md) - Historial de versiones
- [Protocolo MCP](https://modelcontextprotocol.io/) - Documentación oficial de MCP
- [FastMCP](https://github.com/jlowin/fastmcp) - Framework utilizado

---

## Licencia

MIT - Ver [LICENSE](../LICENSE)