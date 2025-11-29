# 🔍 AI-OdooFinder MCP Server

Servidor MCP (Model Context Protocol) para búsqueda semántica de módulos Odoo en el ecosistema OCA.

## 📋 Requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes recomendado)
- Claude Desktop instalado

## 🚀 Instalación

### Paso 1: Verificar que `uv` está instalado

```bash
# Instalar uv si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verificar instalación
uv --version
```

### Paso 2: Instalar dependencias del servidor MCP

```bash
cd /Users/spbarber/Desarrollo/ai-odoo-finder/mcp-server
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

Añade (o modifica) el contenido del archivo `claude_desktop_config.json`:

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
      ],
      "env": {
        "AI_ODOOFINDER_API_URL": "http://localhost:8989"
      }
    }
  }
}
```

> ⚠️ **IMPORTANTE:** Usa la **ruta absoluta** a tu directorio `mcp-server`.

### Paso 5: Configurar la URL de la API (opcional)

Por defecto, el servidor MCP se conecta a `http://localhost:8989`.

Si tu API está en otro lugar (ej: Render), modifica la variable de entorno:

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
      ],
      "env": {
        "AI_ODOOFINDER_API_URL": "https://tu-api.onrender.com"
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
2. Busca el ícono de herramientas (🔧) en la esquina inferior derecha
3. Deberías ver **"ai-odoofinder"** con la herramienta `search_odoo_modules`

## 🧪 Probar el servidor

### Test básico en Claude Desktop

Escribe en Claude:

```
¿Hay módulos de facturación electrónica para España en Odoo 16?
```

Claude debería automáticamente usar la herramienta `search_odoo_modules`.

### Test manual (sin Claude)

```bash
cd /Users/spbarber/Desarrollo/ai-odoo-finder/mcp-server
uv run ai-odoofinder-mcp
```

El servidor arrancará y esperará conexiones JSON-RPC por stdin/stdout.

## 🔧 Troubleshooting

### El servidor no aparece en Claude Desktop

1. **Verifica la ruta:** Debe ser absoluta (empieza con `/`)
2. **Verifica que `uv` está en PATH:**
   ```bash
   which uv
   ```
3. **Revisa los logs de Claude:**
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```
4. **Reinicia completamente Claude** (Cmd+Q, no solo cerrar ventana)

### Error "Connection refused" o timeout

1. **Verifica que la API está corriendo:**
   ```bash
   curl http://localhost:8989/api/v1/search \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "version": "16.0"}'
   ```

2. **Si usas Render:** La primera petición puede tardar ~30s si el servidor está en sleep

3. **Aumenta el timeout:** Modifica `AI_ODOOFINDER_API_TIMEOUT` en las variables de entorno

### Error "corrupted JSON-RPC"

Esto ocurre si hay `print()` en el código que escribe a stdout. 
El servidor MCP debe usar solo `logging` (que escribe a stderr).

## 📁 Estructura del proyecto

```
mcp-server/
├── pyproject.toml           # Configuración del paquete
├── README.md                # Este archivo
└── src/
    └── ai_odoofinder_mcp/
        ├── __init__.py
        └── server.py        # Servidor MCP principal
```

## 🌐 Variables de Entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `AI_ODOOFINDER_API_URL` | `http://localhost:8989` | URL de la API backend |
| `AI_ODOOFINDER_API_TIMEOUT` | `60` | Timeout en segundos para la API |

## 📚 Flujo Inteligente de Búsqueda

El servidor implementa el flujo inteligente según SPEC-602:

1. **Clarificación:** El LLM pide aclaraciones si la query es genérica
2. **Expansión:** El LLM expande la query con sinónimos ES/EN
3. **Respuesta estructurada:** Resultados con niveles de confianza (ALTA/MEDIA/BAJA)
4. **Confirmación:** El LLM confirma con el usuario si encontró lo que buscaba

## 📖 Documentación Técnica

### Implementación SPEC-602

Este servidor implementa el **Flujo Inteligente de Búsqueda** según SPEC-602:

**Documentos de referencia:**
- [SPEC-602: Flujo Inteligente](../specs/phase-6-intelligent-mcp/SPEC-602-intelligent-mcp-flow.md)
- [Resumen de Implementación](../specs/phase-6-intelligent-mcp/IMPLEMENTATION_SUMMARY.md)
- [Guía Rápida](../specs/phase-6-intelligent-mcp/QUICK_REFERENCE.md)
- [CHANGELOG](../docs/CHANGELOG.md)

### Cambios Clave

| Componente | Cambio | Impacto |
|------------|--------|---------|
| **Tool Description** | Instrucciones para localizaciones | Claude construye queries óptimas |
| **Formato Respuesta** | Niveles de confianza (ALTA/MEDIA/BAJA) | Mejor presentación al usuario |
| **Migración 005** | `repo_name` en `searchable_text` | 449 módulos encontrables por país |

### Testing

✅ 6 casos de prueba con 100% de éxito:
- Facturae España → `l10n_es_facturae_face`
- CFDI México → `l10n_mx_cfdi`
- Suscripciones → `contract`
- DMS + OCR → `dms`
- AEAT 303 → `l10n_es_aeat_mod303`
- Delivery carriers → `delivery_price_method`

## 🔗 Links útiles

- [Documentación MCP](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [AI-OdooFinder](https://github.com/SantipBarber/ai-odoo-finder)
- [SPEC-602 Completo](../specs/phase-6-intelligent-mcp/SPEC-602-intelligent-mcp-flow.md)