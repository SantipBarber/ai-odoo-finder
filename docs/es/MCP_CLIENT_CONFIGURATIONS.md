# AI-OdooFinder - Configuraciones de Clientes MCP

**Idioma**: [English](../en/MCP_CLIENT_CONFIGURATIONS.md) | [Español](../es/MCP_CLIENT_CONFIGURATIONS.md)

> Guía completa para instalar y configurar el servidor MCP de AI-OdooFinder en diferentes clientes de IA e IDEs.

---

## Tabla de Contenidos

- [Inicio Rápido](#inicio-rápido)
- [Prerequisitos](#prerequisitos)
- [Métodos de Instalación](#métodos-de-instalación)
  - [Modo Local (STDIO)](#modo-local-stdio)
  - [Modo Remoto (HTTP)](#modo-remoto-http)
- [Configuraciones por Cliente](#configuraciones-por-cliente)
  - [Claude Desktop](#claude-desktop)
  - [Claude Code CLI](#claude-code-cli)
  - [Claude.ai Web](#claudeai-web-remoto)
  - [ChatGPT Developer Mode](#chatgpt-developer-mode)
  - [VSCode Copilot](#vscode-copilot)
  - [Cursor](#cursor)
  - [Zed](#zed)
  - [Windsurf](#windsurf)
  - [Antigravity](#antigravity)
- [Solución de Problemas](#solución-de-problemas)
- [Variables de Entorno](#variables-de-entorno)
- [Matriz de Compatibilidad](#matriz-de-compatibilidad)

---

## Inicio Rápido

**Elige tu método de instalación:**

| Método | Mejor Para | Requisitos |
|--------|------------|------------|
| **Local (STDIO)** | Apps de escritorio, herramientas CLI | `uv` o `npx` instalado |
| **Remoto (HTTP)** | Apps web, sin instalación | Solo conexión a internet |

**Configuración base (adapta a tu cliente):**

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

---

## Prerequisitos

### Para Modo Local (STDIO)

**Opción 1: uv (Recomendado)**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verificar
uv --version
```

**Opción 2: Node.js (Alternativa)**
```bash
# Si prefieres npx sobre uvx
node --version  # Requiere Node.js 18+
```

### Para Modo Remoto (HTTP)

¡No requiere instalación! Solo usa la URL remota:
```
https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp
```

---

## Métodos de Instalación

### Modo Local (STDIO)

**Ventajas:**
- ✅ Funciona sin conexión
- ✅ Sin latencia de red
- ✅ Comunicación directa por proceso
- ✅ Mejor para apps de escritorio

**Desventajas:**
- ❌ Requiere instalación local
- ❌ Actualizaciones manuales necesarias

### Modo Remoto (HTTP)

**Ventajas:**
- ✅ Sin instalación
- ✅ Auto-actualizaciones
- ✅ Misma config en todos los dispositivos
- ✅ Funciona en cualquier lugar

**Desventajas:**
- ❌ Requiere internet
- ❌ Latencia de red
- ❌ Algunos clientes no lo soportan

---

## Configuraciones por Cliente

### Claude Desktop

**Estado:** ✅ Totalmente Soportado (Local STDIO)

#### Configuración

**Ubicación del archivo:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

**1. Usando uvx (Recomendado):**

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

**2. Usando npx (Alternativa):**

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "npx",
      "args": [
        "-y",
        "@SantipBarber/ai-odoofinder-mcp"
      ],
      "env": {
        "AI_ODOOFINDER_API_URL": "https://strategy-orchestrator-prod.tailf7d690.ts.net"
      }
    }
  }
}
```

**3. Reinicia Claude Desktop** para aplicar los cambios.

---

### Claude Code CLI

**Estado:** ✅ Totalmente Soportado (Terminal)

Claude Code es la herramienta CLI oficial de Anthropic para usar Claude en la terminal.

#### Instalación

```bash
# Instalar Claude Code
npm install -g @anthropic-ai/claude-code

# Verificar instalación
claude --version
```

#### Configuración Rápida

```bash
# Opción 1: Asistente interactivo
claude mcp add

# Sigue las indicaciones:
# - Nombre: ai-odoofinder
# - Comando: uvx
# - Args: --from git+https://github.com/SantipBarber/ai-odoo-finder#subdirectory=mcp-server ai-odoofinder-mcp
# - Env: AI_ODOOFINDER_API_URL=https://strategy-orchestrator-prod.tailf7d690.ts.net
```

#### Configuración Manual

Edita `~/.claude.json`:

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

#### Uso

```bash
# Iniciar una sesión con MCP
claude

# Usar en el chat
> Necesito un módulo de Odoo 17 para pagos recurrentes

# Verificar estado del MCP
/mcp

# Listar herramientas disponibles
/tools
```

---

### Claude.ai Web (Remoto)

**Estado:** ✅ Totalmente Soportado (Remote HTTP)

¡No requiere instalación! Conéctate directamente desde la interfaz web.

#### Pasos de Configuración

1. Ve a **[Claude.ai](https://claude.ai)**
2. Navega a **Settings** → **Conectores**
3. Haz clic en **"Añadir conector personalizado"**
4. Introduce la configuración:
   - **Nombre**: AI-OdooFinder
   - **URL**: `https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp`
   - **Protocolo**: Streamable HTTP (MCP 2024-11-05)
5. Haz clic en **Guardar**
6. ¡Empieza a usar en el chat!

#### Uso

Simplemente pregunta como:
```
Encuéntrame un módulo de Odoo 16 para gestión de inventario
```

---

### ChatGPT Developer Mode

**Estado:** ✅ Soportado (Beta - Septiembre 2025)

OpenAI añadió soporte completo MCP a ChatGPT en septiembre de 2025 con **Developer Mode**.

#### Requisitos

- Suscripción a ChatGPT Plus, Pro o Team
- Developer Mode habilitado (beta)

#### Pasos de Configuración

1. Ve a **[ChatGPT Settings](https://chat.openai.com/settings)**
2. Navega a **Beta Features**
3. Habilita **"Developer Mode"**
4. Ve a **Integrations** → **MCP Servers**
5. Haz clic en **"Add MCP Server"**

#### Opciones de Configuración

**Opción 1: Remoto (Más Fácil)**
```
URL: https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp
Protocolo: HTTP/Streamable
```

**Opción 2: Local (Avanzado)**

Crea `~/.chatgpt/mcp.json`:
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

#### Uso

```
Usa ai-odoofinder para buscar módulos de Odoo 17 relacionados con suscripciones
```

**Nota:** Capacidades completas de escritura disponibles (no solo lectura).

---

### VSCode Copilot

**Estado:** ✅ Generalmente Disponible (GA - Julio 2025)

GitHub Copilot en VSCode soporta MCP desde la versión 1.102 (julio 2025).

#### Requisitos

- VSCode 1.102 o posterior
- Suscripción a GitHub Copilot (Free, Pro, Pro+, Business o Enterprise)
- Política MCP habilitada (para Business/Enterprise)

#### Configuración

**Ubicación del archivo:** `.vscode/mcp.json` (proyecto) o `~/.config/Code/User/mcp.json` (global)

**1. Configuración a nivel de proyecto:**

Crea `.vscode/mcp.json` en tu proyecto:

```json
{
  "servers": {
    "ai-odoofinder": {
      "type": "stdio",
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

**2. Configuración global:**

Edita `~/.config/Code/User/mcp.json`:

```json
{
  "servers": {
    "ai-odoofinder": {
      "type": "stdio",
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

**3. Recarga VSCode** (`Ctrl/Cmd + Shift + P` → "Reload Window")

#### Uso

Abre GitHub Copilot Chat y pregunta:
```
@workspace Encuentra un módulo de Odoo para procesamiento de pagos en v17
```

#### Para Usuarios Business/Enterprise

Los administradores deben habilitar la política **"MCP servers in Copilot"**:

1. Ve a **Configuración de Organización/Enterprise**
2. Navega a **Copilot** → **Políticas**
3. Habilita **"MCP servers in Copilot"**

Ver [GitHub Docs](https://docs.github.com/copilot/customizing-copilot/using-model-context-protocol/extending-copilot-chat-with-mcp) para detalles.

---

### Cursor

**Estado:** ✅ Totalmente Soportado

#### Configuración

**Ubicación del archivo:** `.cursor/mcp.json` (proyecto) o `~/.cursor/mcp.json` (global)

**1. Configuración global (Recomendado):**

```bash
# Crear directorio de configuración
mkdir -p ~/.cursor

# Editar configuración
nano ~/.cursor/mcp.json
```

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

**2. Configuración específica del proyecto:**

Crea `.cursor/mcp.json` en la raíz de tu proyecto.

**3. Reinicia Cursor**

#### Uso

En el chat de Cursor:
```
Encuentra módulos de Odoo 16 para contabilidad
```

---

### Zed

**Estado:** ✅ Soportado

#### Configuración

**Ubicación del archivo:** `~/.config/zed/settings.json`

```bash
# Editar configuración de Zed
nano ~/.config/zed/settings.json
```

Añade a tu configuración:

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

**Reinicia Zed** para aplicar los cambios.

---

### Windsurf

**Estado:** ✅ Soportado

#### Configuración

**Ubicación del archivo:** `~/.windsurf/mcp.json` (global) o `.windsurf/mcp.json` (proyecto)

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

**Reinicia Windsurf** para aplicar los cambios.

Ver [documentación MCP de Windsurf](https://docs.windsurf.com/windsurf/mcp) para más información.

---

### Antigravity

**Estado:** ⚠️ Soporte Parcial (Problemas Conocidos)

Google Antigravity tiene problemas de compatibilidad conocidos con `uvx` y servidores MCP remotos.

#### Problemas Conocidos

1. ❌ Comando `uvx` no reconocido
2. ❌ Incompatibilidad con protocolo SSE (Server-Sent Events)
3. ⚠️ Conexiones remotas pueden bloquearse indefinidamente

#### Soluciones Recomendadas

**Solución 1: Usar npx en lugar de uvx**

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "npx",
      "args": [
        "-y",
        "@SantipBarber/ai-odoofinder-mcp"
      ],
      "env": {
        "AI_ODOOFINDER_API_URL": "https://strategy-orchestrator-prod.tailf7d690.ts.net"
      }
    }
  }
}
```

**Solución 2: Usar ruta completa a uvx (Windows)**

Encuentra la ruta de uvx:
```bash
where uvx  # Windows
which uvx  # macOS/Linux
```

Actualiza la configuración con la ruta completa:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "C:\\Users\\TU_USUARIO\\.cargo\\bin\\uvx.exe",
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

**Solución 3: Usar Python directamente**

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "python",
      "args": [
        "-m",
        "pip",
        "install",
        "--quiet",
        "git+https://github.com/SantipBarber/ai-odoo-finder#subdirectory=mcp-server",
        "&&",
        "python",
        "-m",
        "ai_odoofinder_mcp.server"
      ],
      "env": {
        "AI_ODOOFINDER_API_URL": "https://strategy-orchestrator-prod.tailf7d690.ts.net"
      }
    }
  }
}
```

#### Limitaciones Actuales

- ❌ **Modo remoto NO soportado** - Antigravity usa protocolo SSE, pero nuestro servidor usa Streamable HTTP (MCP 2024-11-05)
- ✅ **Modo local FUNCIONA** - Usa una de las soluciones anteriores
- ⚠️ **Puede requerir instalación manual** - Instala el paquete primero, luego configura

#### Alternativa: Usar proxy mcp-remote

```bash
# Instalar mcp-remote
npm install -g mcp-remote
```

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp"
      ]
    }
  }
}
```

---

## Solución de Problemas

### uvx: command not found

**Solución 1: Instalar uv**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Añadir al PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

**Solución 2: Usar npx en su lugar**
```json
{
  "command": "npx",
  "args": ["-y", "@SantipBarber/ai-odoofinder-mcp"]
}
```

### Connection refused / No se puede conectar

**Verificar:**
1. El servidor está funcionando: `curl https://strategy-orchestrator-prod.tailf7d690.ts.net/health`
2. La variable de entorno está configurada correctamente
3. No hay firewall bloqueando conexiones
4. Intenta modo remoto en lugar de local

### Servidor MCP no reconocido

**Verificar:**
1. El archivo de configuración está en la ubicación correcta
2. La sintaxis JSON es válida (usa un validador JSON)
3. Reinicia tu IDE/cliente después de los cambios
4. Revisa los logs del IDE para errores

### Rendimiento lento

**Intenta:**
1. Usar modo local en lugar de remoto
2. Verificar conexión a internet
3. Limpiar caché del IDE
4. Reiniciar IDE

### El servidor se bloquea indefinidamente (Antigravity)

**Este es un problema conocido.** Ver [sección Antigravity](#antigravity) para soluciones.

Usa npx o ruta completa a uvx en su lugar.

---

## Variables de Entorno

### Requeridas

| Variable | Descripción | Por Defecto |
|----------|-------------|-------------|
| `AI_ODOOFINDER_API_URL` | URL de la API backend | `https://strategy-orchestrator-prod.tailf7d690.ts.net` |

### Opcionales

| Variable | Descripción | Por Defecto |
|----------|-------------|-------------|
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `TIMEOUT` | Timeout de peticiones (segundos) | `30` |

### Configurar Variables de Entorno

**En archivo de configuración:**
```json
{
  "env": {
    "AI_ODOOFINDER_API_URL": "https://tu-url-personalizada.com",
    "LOG_LEVEL": "DEBUG"
  }
}
```

**A nivel de sistema (Linux/macOS):**
```bash
export AI_ODOOFINDER_API_URL="https://tu-url-personalizada.com"
```

**A nivel de sistema (Windows):**
```powershell
$env:AI_ODOOFINDER_API_URL="https://tu-url-personalizada.com"
```

---

## Matriz de Compatibilidad

| Cliente | Local | Remoto | Estado | Notas |
|---------|-------|--------|--------|-------|
| Claude Desktop | ✅ | ❌ | Estable | Mejor experiencia |
| Claude Code CLI | ✅ | ✅ | Estable | Basado en terminal |
| Claude.ai Web | ❌ | ✅ | Estable | Sin instalación |
| ChatGPT Dev Mode | ✅ | ✅ | Beta | ¡Nuevo! Sept 2025 |
| VSCode Copilot | ✅ | ⚠️ | GA | Política requerida |
| Cursor | ✅ | ❌ | Estable | Opción popular |
| Zed | ✅ | ❌ | Estable | Editor rápido |
| Windsurf | ✅ | ❌ | Estable | Soporte completo |
| Antigravity | ⚠️ | ❌ | Problemas | Usar npx/workarounds |

**Leyenda:**
- ✅ Totalmente soportado
- ⚠️ Soporte parcial / workarounds necesarios
- ❌ No soportado

---

## Obtener Ayuda

- **Issues**: [GitHub Issues](https://github.com/SantipBarber/ai-odoo-finder/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/SantipBarber/ai-odoo-finder/discussions)
- **Documentación**: [README Principal](../../README.es.md)
- **Especificación MCP**: [Model Context Protocol](https://modelcontextprotocol.io/)

---

## Contribuir

¿Encontraste un nuevo cliente o workaround? ¡Por favor contribuye!

1. Prueba la configuración
2. Documenta los pasos
3. Envía un PR a este archivo
4. Comparte tu experiencia

---

**Última actualización:** Enero 2025  
**Versión de Especificación MCP:** 2024-11-05  
**Versión del Servidor:** 1.0.0