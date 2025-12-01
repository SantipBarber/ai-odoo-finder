# Servidor MCP de AI-OdooFinder

**Language**: [English](README.md) | [Español](README.es.md)

Servidor MCP (Protocolo de Contexto Modelo) para búsqueda semántica de módulos de Odoo en el ecosistema OCA.

## Comenzar

Añade la siguiente configuración a tu cliente MCP:

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

## Configuración por Cliente MCP

<details>
<summary><b>Claude Desktop</b></summary>

Añade a `claude_desktop_config.json`:

**Ubicación del archivo:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

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

Reinicia Claude Desktop.

</details>

<details>
<summary><b>Claude.ai Web (Remoto)</b></summary>

Sin instalación requerida. Conéctate directamente:

1. Ve a **Claude.ai** > **Settings** > **Conectores**
2. Haz clic en **"Añadir conector personalizado"**
3. Introduce la URL del servidor MCP:
   ```
   https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp
   ```
4. Guarda y empieza a buscar

> **Protocolo**: Streamable HTTP (especificación MCP 2024-11-05)

</details>

<details>
<summary><b>Zed</b></summary>

Añade a `~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "ai-odoofinder": {
      "command": {
        "path": "uvx",
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
}
```

</details>

<details>
<summary><b>Cursor</b></summary>

Añade a `.cursor/mcp.json` (proyecto) o `~/.cursor/mcp.json` (global):

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

</details>

<details>
<summary><b>Antigravity</b></summary>

Añade a tu archivo de configuración MCP de Antigravity:

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
        "AI_ODOOFINDER_API_URL": "https://strategy-orchestrador-prod.tailf7d690.ts.net"
      }
    }
  }
}
```

**Solución de problemas en Windows**: Si no encuentra `uvx`, usa la ruta completa:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "C:\\Users\\TU_USUARIO\\.cargo\\bin\\uvx.exe",
      "args": [ /* mismo que arriba */ ]
    }
  }
}
```

> **Nota**: Antigravity usa el protocolo SSE. Las conexiones remotas pueden fallar debido a nuestra implementación de Streamable HTTP. Usa modo local.

</details>

<details>
<summary><b>Windsurf</b></summary>

Añade a tu configuración MCP de Windsurf:

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

</details>

<details>
<summary><b>Otros Clientes MCP</b></summary>

Para cualquier cliente compatible con MCP:

**Modo local (STDIO)**: Usa la configuración mostrada en "Comenzar"

**Modo remoto (HTTP/SSE)**: Usa la URL del servidor:
```
https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp
```

**Protocolo**: Streamable HTTP (especificación MCP 2024-11-05)  
**Autenticación**: Ninguna (servidor público)

</details>

---

## Tu Primer Prompt

Introduce el siguiente prompt en tu cliente MCP para verificar que todo funciona:

```
Necesito un módulo para Odoo 17 que maneje pagos recurrentes
```

El servidor MCP debería buscar y devolver módulos relevantes como `contract` o `subscription_oca`.

> **Nota**: El servidor MCP se conecta automáticamente a la API remota. No se requiere configuración adicional.

---

## Características

- **Búsqueda Híbrida**: Combina búsqueda semántica (embeddings) con BM25 full-text
- **Filtrado por Versión**: Solo muestra módulos compatibles (Odoo 10.0 a 19.0)
- **Enriquecimiento IA**: Descripciones, tags y keywords generados por Grok-4-fast
- **16,494 módulos** indexados desde repositorios OCA

---

## Flujo de Búsqueda Inteligente

El servidor implementa un flujo de búsqueda inteligente:

1. **Aclaración**: El LLM pide aclaraciones si la consulta es genérica
2. **Expansión**: El LLM expande la consulta con sinónimos ES/EN
3. **Respuesta estructurada**: Resultados con niveles de confianza (HIGH/MEDIUM/LOW)
4. **Confirmación**: El LLM confirma con el usuario si encontró lo que buscaba

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
├── pyproject.toml           # Configuración del paquete
├── README.md                # Este archivo
└── src/
    └── ai_odoofinder_mcp/
        ├── __init__.py
        └── server.py        # Servidor MCP principal
```

---

## Solución de Problemas

### El servidor no aparece en el cliente MCP

1. **Verifica que `uv` está instalado:**
   ```bash
   uv --version
   ```

2. **Revisa los logs del cliente MCP** para mensajes de error

3. **Reinicia el cliente MCP completamente** (no solo cerrar la ventana)

### Error "Connection refused" o timeout

1. **Verifica que la API está funcionando:**
   ```bash
   curl https://strategy-orchestrator-prod.tailf7d690.ts.net/health
   ```

2. **Aumenta el timeout**: Establece `AI_ODOOFINDER_API_TIMEOUT` a un valor mayor (ej. `120`)

### Error "uvx not found"

- **Asegúrate de que `uv` está en PATH**: Ejecuta `which uv` (Unix) o `where uv` (Windows)
- **Usa la ruta completa**: Si `uv` no está en PATH, usa la ruta absoluta en la configuración

---

## Enlaces Útiles

- [Proyecto Principal](https://github.com/SantipBarber/ai-odoo-finder)
- [CHANGELOG](../docs/es/CHANGELOG.md)
- [Documentación del Protocolo MCP](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)