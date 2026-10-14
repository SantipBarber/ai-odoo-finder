# Servidor MCP de AI-OdooFinder

**Idioma**: [English](README.md) | [Español](README.es.md)

Servidor MCP (Model Context Protocol) para búsqueda semántica de módulos de Odoo en el ecosistema OCA.

## Resumen

Este servidor MCP proporciona una herramienta llamada `search_odoo_modules` que permite a los LLMs buscar entre más de 19.700 módulos de Odoo indexados desde repositorios OCA usando búsqueda híbrida (semántica + BM25).

## Inicio rápido

### Opción 1: Servidor remoto público (recomendado, sin instalación)

La forma más sencilla de usar AI-OdooFinder es el servidor MCP remoto público alojado por [Eticco](https://www.eticco.es):

```
https://addon-finder.eticco.es
```

- **Transporte**: Streamable HTTP
- **Autenticación**: Ninguna para módulos de la comunidad OCA

Añade esa URL a tu cliente MCP. Los clientes que solo admiten STDIO pueden usar el puente [`mcp-remote`](https://www.npmjs.com/package/mcp-remote): `npx -y mcp-remote https://addon-finder.eticco.es`. Para la configuración de cada cliente, consulta el [README principal del proyecto](../README.es.md#instalación).

### Opción 2: Paquete STDIO local (backend propio)

Este paquete está disponible en **[PyPI](https://pypi.org/project/ai-odoofinder-mcp/)**. Ejecuta el servidor MCP en local por STDIO y se comunica con la API REST del backend FastAPI. La instancia pública no expone esa API REST, así que usa este modo con **tu propio despliegue del backend** (ver [Despliegue y operaciones](../docs/es/DEPLOYMENT_OPERATIONS.md)).

```bash
# Usando pip
pip install ai-odoofinder-mcp

# Usando uvx (recomendado para clientes MCP)
uvx ai-odoofinder-mcp
```

Configuración del cliente MCP:

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

> **Nota**: Requiere el gestor de paquetes [uv](https://docs.astral.sh/uv/) instalado.

---

## Características

- **Búsqueda híbrida**: Combina búsqueda semántica (embeddings) con búsqueda de texto completo BM25
- **Filtrado por versión**: Solo muestra módulos compatibles (Odoo 14.0 a 19.0)
- **Enriquecimiento con IA**: Descripciones, etiquetas y palabras clave generadas por Grok-4-fast
- **Flujo inteligente**: Aclaraciones, expansión de consultas y niveles de confianza

---

## Arquitectura

```
┌─────────────────┐
│  Cliente MCP    │ (Claude Desktop, Zed, Cursor, etc.)
│  (STDIO/HTTP)   │
└────────┬────────┘
         │
         │ MCP (STDIO o Streamable HTTP)
         │
┌────────▼────────┐
│  Servidor MCP   │ (Este componente)
│  FastMCP + uv   │
└────────┬────────┘
         │
         │ HTTP (REST)
         │
┌────────▼────────┐
│   Backend API   │ (FastAPI + PostgreSQL)
│   :8989         │
└─────────────────┘
```

**Dos modos:**
- **STDIO** (por defecto): para clientes locales que lanzan el servidor como subproceso (p. ej. Claude Desktop con `uvx ai-odoofinder-mcp`)
- **HTTP** (Streamable HTTP, puerto `8080`, ruta `/`): para clientes remotos. Se activa con `--http` o `MCP_TRANSPORT=http`

---

## Herramientas

### `search_odoo_modules`

Busca módulos de Odoo usando consultas en lenguaje natural.

**Parámetros:**
- `query` (string, obligatorio): Consulta de búsqueda en lenguaje natural
- `version` (string, obligatorio): Versión de Odoo, de `14.0` a `19.0` (p. ej. `"16.0"`, `"17.0"`)
- `dependencies` (lista de strings, opcional): Filtra por dependencias requeridas, p. ej. `["account"]`
- `limit` (integer, opcional): Máximo de resultados (por defecto: 5, máximo: 20; los valores fuera de rango se ajustan a 1–20)

**Devuelve:**
- Texto en Markdown con los módulos encontrados, el nivel de confianza y orientaciones para el asistente

**Ejemplo:**
```json
{
  "query": "facturación electrónica para España",
  "version": "16.0",
  "limit": 5
}
```

---

## Flujo de búsqueda inteligente

El servidor implementa un flujo de búsqueda inteligente:

1. **Aclaración**: Solicita detalles si la consulta es genérica o falta versión
2. **Expansión de consulta**: Añade sinónimos ES/EN, prefijos de localización (`l10n_XX_`)
3. **Respuesta estructurada**: Devuelve resultados con niveles de confianza:
   - **HIGH** (puntuación ≥80): Formato detallado con recomendaciones
   - **MEDIUM** (50-79): Formato resumen con alternativas
   - **LOW** (<50): Sugerencias para refinar búsqueda
4. **Confirmación**: Valida con el usuario si encontró lo que buscaba

---

## Variables de entorno

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `AI_ODOOFINDER_API_URL` | `http://localhost:8989` | URL de la API backend |
| `AI_ODOOFINDER_API_TIMEOUT` | `60` | Tiempo máximo de espera de la API, en segundos |
| `MCP_TRANSPORT` | `stdio` | Transporte: `stdio` o `http` (`--http` fuerza `http`) |
| `MCP_HOST` | `0.0.0.0` | Host de escucha en modo HTTP (lo sobrescribe `--host`) |
| `MCP_PORT` | `8080` | Puerto en modo HTTP (lo sobrescribe `--port`) |
| `MCP_PATH` | `/` | Ruta del endpoint MCP en modo HTTP |

---

## Estructura del proyecto

```
mcp-server/
├── pyproject.toml           # Configuración del paquete (instalable con uvx)
├── README.md                # Documentación en inglés
├── README.es.md             # Este archivo
└── src/
    └── ai_odoofinder_mcp/
        ├── __init__.py
        └── server.py        # Servidor MCP principal (FastMCP)
```

---

## Desarrollo

### Pruebas locales

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

**Endpoint del backend utilizado:**
- `GET /search` - Búsqueda híbrida

**Algoritmo de búsqueda:**
1. Generar el embedding de la consulta (Qwen3-Embedding-4B vía OpenRouter)
2. Búsqueda vectorial (pgvector, distancia coseno exacta)
3. Búsqueda de texto completo BM25 (PostgreSQL tsvector)
4. Combinar resultados con Reciprocal Rank Fusion (RRF)

```
RRF_score = 1/(k + rank_vector) + 1/(k + rank_bm25)
```

Donde `k=60` (constante estándar RRF)

---

## Solución de problemas

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

1. **Verifica que el servicio está disponible:**
   ```bash
   # Instancia pública
   curl https://addon-finder.eticco.es/health

   # Backend propio
   curl http://localhost:8989/health
   ```

2. **Revisa el tiempo máximo de espera:**
   ```bash
   export AI_ODOOFINDER_API_TIMEOUT=120
   ```

### El cliente MCP no ve la herramienta

1. **Revisa los logs del cliente MCP** para errores de conexión
2. **Verifica que JSON-RPC funciona**: Usa MCP Inspector
3. **Reinicia el cliente MCP completamente**

---

## Publicación

El servidor MCP está publicado en **[PyPI](https://pypi.org/project/ai-odoofinder-mcp/)**.

### Instalar desde PyPI

```bash
# Usando pip
pip install ai-odoofinder-mcp

# Usando uvx
uvx ai-odoofinder-mcp
```

### Instalar desde Git (desarrollo)

```bash
uvx --from git+https://github.com/SantipBarber/ai-odoo-finder#subdirectory=mcp-server ai-odoofinder-mcp
```

### Publicar una nueva versión

```bash
cd mcp-server
# Actualizar versión en pyproject.toml
uv build
uv publish
```

---

## Documentación relacionada

- [README principal del proyecto](../README.es.md) - Guía de instalación para usuarios
- [API del backend](../backend/README.es.md) - API REST del backend FastAPI
- [Registro de cambios](../docs/es/CHANGELOG.md) - Historial de versiones
- [Protocolo MCP](https://modelcontextprotocol.io/) - Documentación oficial de MCP
- [FastMCP](https://github.com/jlowin/fastmcp) - Framework utilizado

---

## Licencia

MIT - Ver [LICENSE](../LICENSE)