# Servidor MCP de AI-OdooFinder

**Language**: [English](README.md) | [Español](README.es.md)

Servidor MCP (Protocolo de Contexto Modelo) para búsqueda semántica de módulos de Odoo en el ecosistema OCA.

## Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes recomendado)
- Claude Desktop instalado (para uso local)

## Instalación

### Paso 1: Verificar que `uv` está instalado

```bash
# Instalar uv si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verificar instalación
uv --version
```

### Paso 2: Instalar dependencias del servidor MCP

```bash
cd <tu-ruta>/ai-odoo-finder/mcp-server
uv sync
```

### Paso 3: Configurar Claude Desktop

Abre el archivo de configuración de Claude Desktop:

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

Si el archivo no existe, créalo.

### Paso 4: Añadir la configuración del servidor MCP

Añade (o modifica) el contenido de `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uv",
      "args": [
        "--directory",
        "<tu-ruta>/ai-odoo-finder/mcp-server",
        "run",
        "ai-odoofinder-mcp"
      ],
      "env": {
        "AI_ODOOFINDER_API_URL": "http://localhost:8989"
      }
    }
  }
}
```

> **IMPORTANTE:** Usa la **ruta absoluta** a tu directorio `mcp-server`.

### Paso 5: Configurar la URL de la API (opcional)

Por defecto, el servidor MCP se conecta a `http://localhost:8989`.

Si tu API está en otro lugar (ej., servidor remoto), modifica la variable de entorno:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uv",
      "args": [
        "--directory",
        "<tu-ruta>/ai-odoo-finder/mcp-server",
        "run",
        "ai-odoofinder-mcp"
      ],
      "env": {
        "AI_ODOOFINDER_API_URL": "https://<tu-servidor>.ts.net"
      }
    }
  }
}
```

### Paso 6: Reiniciar Claude Desktop

**IMPORTANTE:** Debes cerrar Claude Desktop completamente y volver a abrirlo.

- **macOS:** `Cmd+Q` (no solo cerrar la ventana)
- **Windows:** Cerrar desde la bandeja del sistema

### Paso 7: Verificar la instalación

1. Abre Claude Desktop
2. Busca el icono de herramientas en la esquina inferior derecha
3. Deberías ver **"ai-odoofinder"** con la herramienta `search_odoo_modules`

## Probar el servidor

### Prueba básica en Claude Desktop

Escribe en Claude:

```
¿Hay módulos de facturación electrónica para España en Odoo 16?
```

Claude debería usar automáticamente la herramienta `search_odoo_modules`.

### Prueba manual (sin Claude)

```bash
cd <tu-ruta>/ai-odoo-finder/mcp-server
uv run ai-odoofinder-mcp
```

El servidor se iniciará y esperará conexiones JSON-RPC via stdin/stdout.

## Solución de problemas

### El servidor no aparece en Claude Desktop

1. **Verifica la ruta:** Debe ser absoluta (empieza con `/` en macOS/Linux o letra de unidad en Windows)
2. **Verifica que `uv` está en PATH:**
   ```bash
   which uv
   ```
3. **Revisa los logs de Claude:**
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```
4. **Reinicia Claude completamente** (Cmd+Q, no solo cerrar ventana)

### Error "Connection refused" o timeout

1. **Verifica que la API esté ejecutándose:**
   ```bash
   curl http://localhost:8989/api/v1/search \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "version": "16.0"}'
   ```

2. **Aumentar timeout:** Modifica `AI_ODOOFINDER_API_TIMEOUT` en variables de entorno

### Error "corrupted JSON-RPC"

Esto ocurre si hay `print()` en el código que escribe a stdout.
El servidor MCP debe usar solo `logging` (que escribe a stderr).

## Estructura del proyecto

```
mcp-server/
├── pyproject.toml           # Configuración del paquete
├── README.md                # Este archivo
└── src/
    └── ai_odoofinder_mcp/
        ├── __init__.py
        └── server.py        # Servidor MCP principal
```

## Variables de entorno

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `AI_ODOOFINDER_API_URL` | `http://localhost:8989` | URL de la API backend |
| `AI_ODOOFINDER_API_TIMEOUT` | `60` | Timeout de la API en segundos |

## Flujo de búsqueda inteligente

El servidor implementa el flujo inteligente según SPEC-602:

1. **Aclaración:** El LLM pide aclaraciones si la consulta es genérica
2. **Expansión:** El LLM expande la consulta con sinónimos ES/EN
3. **Respuesta estructurada:** Resultados con niveles de confianza (HIGH/MEDIUM/LOW)
4. **Confirmación:** El LLM confirma con el usuario si encontró lo que buscaba

## Enlaces útiles

- [Documentación MCP](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [AI-OdooFinder](https://github.com/SantipBarber/ai-odoo-finder)
- [CHANGELOG](../docs/es/CHANGELOG.md)