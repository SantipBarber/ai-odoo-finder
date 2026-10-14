# AI-OdooFinder - Configuraciones de clientes MCP

**Idioma**: [English](../en/MCP_CLIENT_CONFIGURATIONS.md) | [Español](../es/MCP_CLIENT_CONFIGURATIONS.md)

> Guía completa para conectar AI-OdooFinder con diferentes clientes de IA e IDEs.

---

## Tabla de contenidos

- [Inicio rápido](#inicio-rápido)
  - [Herramienta](#herramienta)
- [Métodos de conexión](#métodos-de-conexión)
  - [Modo remoto (recomendado)](#modo-remoto-recomendado)
  - [Puente mcp-remote (clientes solo STDIO)](#puente-mcp-remote-clientes-solo-stdio)
  - [Paquete STDIO local (backend autoalojado)](#paquete-stdio-local-backend-autoalojado)
- [Configuraciones por cliente](#configuraciones-por-cliente)
  - [Claude.ai Web / Claude Desktop](#claudeai-web--claude-desktop)
  - [Claude Code CLI](#claude-code-cli)
  - [ChatGPT Developer Mode](#chatgpt-developer-mode)
  - [VSCode Copilot](#vscode-copilot)
  - [Cursor](#cursor)
  - [Zed](#zed)
  - [Windsurf](#windsurf)
  - [Antigravity](#antigravity)
- [Solución de problemas](#solución-de-problemas)
- [Variables de entorno (paquete local)](#variables-de-entorno-paquete-local)
- [Matriz de compatibilidad](#matriz-de-compatibilidad)

---

## Inicio rápido

AI-OdooFinder está disponible como **servidor MCP remoto público**, alojado por [Eticco](https://www.eticco.es):

```
https://addon-finder.eticco.es
```

| | |
|---|---|
| **Transporte** | Streamable HTTP (endpoint en la URL raíz, sin sufijo `/mcp`) |
| **Autenticación** | Ninguna para módulos de la comunidad OCA |
| **Herramienta** | `search_odoo_modules` |
| **Comprobación de estado** | `https://addon-finder.eticco.es/health` |

**No necesitas instalar nada.** Añade la URL a tu cliente MCP. Si tu cliente solo soporta servidores STDIO locales, usa el puente [`mcp-remote`](https://www.npmjs.com/package/mcp-remote):

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

### Herramienta

El servidor expone una única herramienta:

```python
search_odoo_modules(query: str, version: str, dependencies: list[str] | None = None, limit: int = 5)
```

| Parámetro | Descripción |
|-----------|-------------|
| `query` | Descripción en lenguaje natural de la funcionalidad que necesitas (en español o en inglés) |
| `version` | Versión de Odoo: `14.0`, `15.0`, `16.0`, `17.0`, `18.0` o `19.0` |
| `dependencies` | Lista opcional de nombres técnicos de módulos (p. ej. `["sale", "stock"]`) para limitar los resultados a módulos que dependen de ellos |
| `limit` | Número de resultados, acotado al rango 1–20 (por defecto `5`) |

La herramienta devuelve una lista de módulos en formato Markdown con sus enlaces a GitHub. No la llamas directamente: tu cliente de IA la invoca cuando le pides módulos de Odoo en el chat.

---

## Métodos de conexión

| Método | Mejor para | Requisitos |
|--------|------------|------------|
| **Remoto (HTTP)** | Cualquier cliente con soporte MCP remoto | Solo conexión a internet |
| **Puente mcp-remote** | Clientes solo STDIO | Node.js 18+ |
| **Paquete STDIO local** | Tu propio backend autoalojado | `uv` + un backend de AI-OdooFinder en marcha |

### Modo remoto (recomendado)

**Ventajas:**
- ✅ Sin instalación
- ✅ Siempre actualizado (índice y servidor)
- ✅ Misma configuración en todos los dispositivos

**Desventajas:**
- ❌ Requiere internet
- ❌ Algunos clientes antiguos no soportan servidores remotos (usa el puente)

### Puente mcp-remote (clientes solo STDIO)

[`mcp-remote`](https://www.npmjs.com/package/mcp-remote) ejecuta un pequeño proceso STDIO local que reenvía las peticiones al servidor remoto. Requiere Node.js 18+:

```bash
node --version  # Requiere Node.js 18+
```

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

### Paquete STDIO local (backend autoalojado)

El paquete de PyPI [`ai-odoofinder-mcp`](https://pypi.org/project/ai-odoofinder-mcp/) ejecuta el servidor MCP en local y se comunica con la API REST del backend FastAPI (`/search`, `/health`, ...). **La instancia pública no expone esa API REST**, por lo que este modo solo funciona contra **tu propio despliegue** (consulta [Despliegue y operaciones](DEPLOYMENT_OPERATIONS.md)).

**Instalar uv:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verificar
uv --version
```

**Configuración:**
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

Sustituye `http://localhost:8989` por la URL de tu backend si se ejecuta en otro lugar. Cada sección de cliente indica cómo adaptar este bloque a su formato.

---

## Configuraciones por cliente

### Claude.ai Web / Claude Desktop

**Estado:** ✅ Totalmente soportado (HTTP remoto)

Los conectores personalizados se comparten entre Claude.ai y Claude Desktop.

#### Pasos de configuración

1. Ve a **[Claude.ai](https://claude.ai)** (o abre Claude Desktop)
2. Navega a **Settings** → **Connectors**
3. Haz clic en **"Add custom connector"**
4. Introduce la configuración:
   - **Name**: AI-OdooFinder
   - **URL**: `https://addon-finder.eticco.es`
5. Haz clic en **Save**
6. ¡Empieza a usarlo en el chat!

#### Alternativa: archivo de configuración de Claude Desktop

En versiones antiguas de Desktop sin conectores, usa el puente `mcp-remote` en `claude_desktop_config.json`:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

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

Para un backend autoalojado, usa en su lugar el bloque del [paquete STDIO local](#paquete-stdio-local-backend-autoalojado). **Reinicia Claude Desktop** para aplicar los cambios.

#### Uso

```
Búscame un módulo de Odoo 16 para gestión de inventario
```

---

### Claude Code CLI

**Estado:** ✅ Totalmente soportado (HTTP remoto)

Claude Code es la herramienta de programación agéntica de Anthropic para la terminal.

#### Configuración rápida

```bash
claude mcp add --transport http ai-odoofinder https://addon-finder.eticco.es
```

#### Backend autoalojado (paquete STDIO local)

```bash
claude mcp add ai-odoofinder \
  --env AI_ODOOFINDER_API_URL=http://localhost:8989 \
  -- uvx ai-odoofinder-mcp
```

#### Uso

```bash
# Iniciar una sesión
claude

# Usar en el chat
> Necesito un módulo de Odoo 17 para pagos recurrentes

# Comprobar estado MCP
/mcp
```

---

### ChatGPT Developer Mode

**Estado:** ✅ Soportado (Developer Mode)

#### Requisitos

- Plan de ChatGPT con Developer Mode disponible
- Developer Mode activado

#### Pasos de configuración

1. Ve a **Settings** → **Apps & Connectors** → **Advanced** y activa **Developer Mode**
2. Crea un nuevo conector con:
   - **URL**: `https://addon-finder.eticco.es`
   - **Authentication**: None
3. Guarda y actívalo en el chat

#### Uso

```
Usa ai-odoofinder para buscar módulos de Odoo 17 relacionados con suscripciones
```

---

### VSCode Copilot

**Estado:** ✅ Disponible de forma general (GA)

GitHub Copilot en VSCode soporta MCP desde la versión 1.102.

#### Requisitos

- VSCode 1.102 o posterior
- Suscripción a GitHub Copilot (Free, Pro, Pro+, Business o Enterprise)
- Política MCP habilitada (para Business/Enterprise)

#### Configuración

Crea `.vscode/mcp.json` en tu proyecto, o añádelo a tu `mcp.json` de usuario (Paleta de comandos → "MCP: Open User Configuration"):

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

**Backend autoalojado (paquete STDIO local):**

```json
{
  "servers": {
    "ai-odoofinder": {
      "type": "stdio",
      "command": "uvx",
      "args": ["ai-odoofinder-mcp"],
      "env": {
        "AI_ODOOFINDER_API_URL": "http://localhost:8989"
      }
    }
  }
}
```

**Recarga VSCode** (`Ctrl/Cmd + Shift + P` → "Reload Window")

#### Uso

Abre GitHub Copilot Chat (modo Agent) y pregunta:
```
Encuentra un módulo de Odoo para procesamiento de pagos en v17
```

#### Para usuarios Business/Enterprise

Los administradores deben habilitar la política **"MCP servers in Copilot"**:

1. Ve a **Organization/Enterprise Settings**
2. Navega a **Copilot** → **Policies**
3. Habilita **"MCP servers in Copilot"**

Consulta la [documentación de GitHub](https://docs.github.com/copilot/customizing-copilot/using-model-context-protocol/extending-copilot-chat-with-mcp) para más detalles.

---

### Cursor

**Estado:** ✅ Totalmente soportado (HTTP remoto)

#### Configuración

**Ubicación del archivo:** `.cursor/mcp.json` (proyecto) o `~/.cursor/mcp.json` (global)

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "url": "https://addon-finder.eticco.es"
    }
  }
}
```

Para un backend autoalojado, usa el bloque del [paquete STDIO local](#paquete-stdio-local-backend-autoalojado) (mismo formato `mcpServers`). **Reinicia Cursor** para aplicar los cambios.

#### Uso

En el chat de Cursor:
```
Encuentra módulos de Odoo 16 para contabilidad
```

---

### Zed

**Estado:** ✅ Soportado (HTTP remoto)

#### Configuración

**Ubicación del archivo:** `~/.config/zed/settings.json`

```json
{
  "context_servers": {
    "ai-odoofinder": {
      "url": "https://addon-finder.eticco.es"
    }
  }
}
```

**Backend autoalojado (paquete STDIO local):**

```json
{
  "context_servers": {
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

---

### Windsurf

**Estado:** ✅ Soportado (HTTP remoto)

#### Configuración

**Ubicación del archivo:** `~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "serverUrl": "https://addon-finder.eticco.es"
    }
  }
}
```

Para un backend autoalojado, usa el bloque del [paquete STDIO local](#paquete-stdio-local-backend-autoalojado) (mismo formato `mcpServers`). **Reinicia Windsurf** (o refresca los servidores MCP) para aplicar los cambios.

Consulta la [documentación MCP de Windsurf](https://docs.windsurf.com/windsurf/cascade/mcp) para más información.

---

### Antigravity

**Estado:** ⚠️ Usa el puente `mcp-remote`

Google Antigravity ha tenido problemas de compatibilidad con conexiones remotas directas y con `uvx`.

#### Problemas conocidos

1. ⚠️ Las conexiones remotas directas pueden quedarse bloqueadas indefinidamente
2. ❌ El comando `uvx` puede no ser reconocido

#### Solución recomendada: puente mcp-remote

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

#### Backend autoalojado: ruta completa a uvx

Si usas el [paquete STDIO local](#paquete-stdio-local-backend-autoalojado) y `uvx` no se encuentra, usa su ruta completa:

```bash
where uvx  # Windows
which uvx  # macOS/Linux
```

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "C:\\Users\\TU_USUARIO\\.local\\bin\\uvx.exe",
      "args": ["ai-odoofinder-mcp"],
      "env": {
        "AI_ODOOFINDER_API_URL": "http://localhost:8989"
      }
    }
  }
}
```

---

## Solución de problemas

### Conexión rechazada / No se puede conectar

**Comprueba:**
1. Que el servidor está activo: `curl https://addon-finder.eticco.es/health`
2. Que usas la **URL raíz** `https://addon-finder.eticco.es` (no `/mcp`, que devuelve 404)
3. Que tu cliente soporta Streamable HTTP; si no, usa el [puente `mcp-remote`](#puente-mcp-remote-clientes-solo-stdio)
4. Que ningún proxy/firewall bloquea el HTTPS saliente

### El paquete local devuelve errores / sin resultados

El paquete `ai-odoofinder-mcp` necesita un backend que exponga la API REST. La instancia pública **no** la expone (`/search` y `/stats` devuelven 404), así que apunta `AI_ODOOFINDER_API_URL` a tu propio despliegue (p. ej. `http://localhost:8989`) o cambia a modo remoto.

```bash
curl http://localhost:8989/health
```

### npx / mcp-remote no encontrado

Instala Node.js 18+ y verifica con `node --version`. En Windows, algunos clientes necesitan la ruta completa a `npx.cmd`.

### uvx: command not found (paquete local)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Añadir al PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Servidor MCP no reconocido

**Comprueba:**
1. El archivo de configuración está en la ubicación correcta
2. La sintaxis JSON es válida (usa un validador JSON)
3. Reinicia tu IDE/cliente tras los cambios
4. Revisa los logs del IDE en busca de errores

### El servidor se bloquea indefinidamente (Antigravity)

**Es un problema conocido.** Usa el [puente `mcp-remote`](#antigravity).

---

## Variables de entorno (paquete local)

Solo aplican al paquete local `ai-odoofinder-mcp`. El modo remoto no necesita configuración. Todas las variables son opcionales.

### Conexión con el backend

| Variable | Descripción | Por defecto |
|----------|-------------|-------------|
| `AI_ODOOFINDER_API_URL` | URL de la API REST de tu backend autoalojado | `http://localhost:8989` |
| `AI_ODOOFINDER_API_TIMEOUT` | Tiempo máximo de espera de las peticiones al backend (segundos) | `60` |

### Transporte (solo si sirves tú mismo MCP por HTTP)

| Variable | Descripción | Por defecto |
|----------|-------------|-------------|
| `MCP_TRANSPORT` | `stdio` o `http` | `stdio` |
| `MCP_HOST` | Host en el que escucha en modo HTTP | `0.0.0.0` |
| `MCP_PORT` | Puerto en el que escucha en modo HTTP | `8080` |
| `MCP_PATH` | Ruta del endpoint MCP en modo HTTP | `/` |

Las opciones de línea de comandos equivalentes son `--http` (igual que `MCP_TRANSPORT=http`), `--host` y `--port`.

### Configurar variables de entorno

**En el archivo de configuración:**
```json
{
  "env": {
    "AI_ODOOFINDER_API_URL": "http://localhost:8989",
    "AI_ODOOFINDER_API_TIMEOUT": "60"
  }
}
```

**A nivel de sistema (Linux/macOS):**
```bash
export AI_ODOOFINDER_API_URL="http://localhost:8989"
```

**A nivel de sistema (Windows):**
```powershell
$env:AI_ODOOFINDER_API_URL="http://localhost:8989"
```

---

## Matriz de compatibilidad

| Cliente | URL remota | Vía `mcp-remote` | Paquete local (autoalojado) | Notas |
|---------|:----------:|:----------------:|:----------------------------:|-------|
| Claude.ai Web | ✅ | — | — | Conector personalizado |
| Claude Desktop | ✅ | ✅ | ✅ | Conector o puente |
| Claude Code CLI | ✅ | ✅ | ✅ | `--transport http` |
| ChatGPT Dev Mode | ✅ | — | — | Developer Mode |
| VSCode Copilot | ✅ | ✅ | ✅ | `type: http`, política requerida en Business/Enterprise |
| Cursor | ✅ | ✅ | ✅ | `url` |
| Windsurf | ✅ | ✅ | ✅ | `serverUrl` |
| Zed | ✅ | ✅ | ✅ | `context_servers` |
| Antigravity | ⚠️ | ✅ | ⚠️ | Usa el puente |

**Leyenda:**
- ✅ Soportado
- ⚠️ Soporte parcial / requiere soluciones alternativas
- — No aplica

---

## Obtener ayuda

- **Issues**: [GitHub Issues](https://github.com/SantipBarber/ai-odoo-finder/issues)
- **Documentación**: [README principal](../../README.es.md)
- **Especificación MCP**: [Model Context Protocol](https://modelcontextprotocol.io/)

---

## Contribuir

¿Has encontrado un nuevo cliente o una solución alternativa? ¡Contribuye!

1. Prueba la configuración
2. Documenta los pasos
3. Envía un PR a este archivo
4. Comparte tu experiencia

---

**Última actualización:** octubre de 2026  
**Servidor público:** `https://addon-finder.eticco.es` (alojado por [Eticco](https://www.eticco.es))  
**Transporte:** Streamable HTTP
