# AI-OdooFinder - MCP Client Configurations

**Language**: [English](../en/MCP_CLIENT_CONFIGURATIONS.md) | [Español](../es/MCP_CLIENT_CONFIGURATIONS.md)

> Complete guide for connecting AI-OdooFinder to different AI clients and IDEs.

---

## Table of Contents

- [Quick Start](#quick-start)
  - [Tool](#tool)
- [Connection Methods](#connection-methods)
  - [Remote Mode (Recommended)](#remote-mode-recommended)
  - [mcp-remote Bridge (STDIO-only clients)](#mcp-remote-bridge-stdio-only-clients)
  - [Local STDIO Package (Self-Hosted Backend)](#local-stdio-package-self-hosted-backend)
- [Client Configurations](#client-configurations)
  - [Claude.ai Web / Claude Desktop](#claudeai-web--claude-desktop)
  - [Claude Code CLI](#claude-code-cli)
  - [ChatGPT Developer Mode](#chatgpt-developer-mode)
  - [VSCode Copilot](#vscode-copilot)
  - [Cursor](#cursor)
  - [Zed](#zed)
  - [Windsurf](#windsurf)
  - [Antigravity](#antigravity)
- [Troubleshooting](#troubleshooting)
- [Environment Variables (Local Package)](#environment-variables-local-package)
- [Compatibility Matrix](#compatibility-matrix)

---

## Quick Start

AI-OdooFinder is available as a **public remote MCP server**, hosted by [Eticco](https://www.eticco.es):

```
https://addon-finder.eticco.es
```

| | |
|---|---|
| **Transport** | Streamable HTTP (endpoint at the root URL, no `/mcp` suffix) |
| **Authentication** | None for OCA community modules |
| **Tool** | `search_odoo_modules` |
| **Health check** | `https://addon-finder.eticco.es/health` |

**No installation needed.** Add the URL to your MCP client. If your client only supports local STDIO servers, use the [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) bridge:

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

### Tool

The server exposes a single tool:

```python
search_odoo_modules(query: str, version: str, dependencies: list[str] | None = None, limit: int = 5)
```

| Parameter | Description |
|-----------|-------------|
| `query` | Natural-language description of the functionality you need (English or Spanish) |
| `version` | Odoo version: `14.0`, `15.0`, `16.0`, `17.0`, `18.0` or `19.0` |
| `dependencies` | Optional list of technical module names (e.g. `["sale", "stock"]`) to restrict results to modules that depend on them |
| `limit` | Number of results, clamped to the range 1–20 (default `5`) |

The tool returns a Markdown-formatted list of modules with their GitHub links. You don't call it directly: your AI client invokes it when you ask for Odoo modules in the chat.

---

## Connection Methods

| Method | Best For | Requirements |
|--------|----------|--------------|
| **Remote (HTTP)** | Any client with remote MCP support | Internet connection only |
| **mcp-remote bridge** | STDIO-only clients | Node.js 18+ |
| **Local STDIO package** | Your own self-hosted backend | `uv` + a running AI-OdooFinder backend |

### Remote Mode (Recommended)

**Pros:**
- ✅ Zero installation
- ✅ Always up to date (index and server)
- ✅ Same config across devices

**Cons:**
- ❌ Requires internet
- ❌ Some older clients don't support remote servers (use the bridge)

### mcp-remote Bridge (STDIO-only clients)

[`mcp-remote`](https://www.npmjs.com/package/mcp-remote) runs a small local STDIO process that forwards requests to the remote server. Requires Node.js 18+:

```bash
node --version  # Requires Node.js 18+
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

### Local STDIO Package (Self-Hosted Backend)

The [`ai-odoofinder-mcp`](https://pypi.org/project/ai-odoofinder-mcp/) PyPI package runs the MCP server locally and talks to the FastAPI backend REST API (`/search`, `/health`, ...). **The public instance does not expose that REST API**, so this mode only works against **your own deployment** (see [Deployment & Operations](DEPLOYMENT_OPERATIONS.md)).

**Install uv:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify
uv --version
```

**Configuration:**
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

Replace `http://localhost:8989` with the URL of your backend if it runs elsewhere. Each client section below shows how to adapt this block to the client's own format.

---

## Client Configurations

### Claude.ai Web / Claude Desktop

**Status:** ✅ Fully Supported (Remote HTTP)

Custom connectors are shared between Claude.ai and Claude Desktop.

#### Setup Steps

1. Go to **[Claude.ai](https://claude.ai)** (or open Claude Desktop)
2. Navigate to **Settings** → **Connectors**
3. Click **"Add custom connector"**
4. Enter configuration:
   - **Name**: AI-OdooFinder
   - **URL**: `https://addon-finder.eticco.es`
5. Click **Save**
6. Start using in chat!

#### Alternative: Claude Desktop config file

On older Desktop versions without connectors, use the `mcp-remote` bridge in `claude_desktop_config.json`:

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

For a self-hosted backend, use the [local STDIO package](#local-stdio-package-self-hosted-backend) block instead. **Restart Claude Desktop** to apply changes.

#### Usage

```
Find me an Odoo 16 module for inventory management
```

---

### Claude Code CLI

**Status:** ✅ Fully Supported (Remote HTTP)

Claude Code is Anthropic's agentic coding tool for the terminal.

#### Quick Setup

```bash
claude mcp add --transport http ai-odoofinder https://addon-finder.eticco.es
```

#### Self-hosted backend (local STDIO package)

```bash
claude mcp add ai-odoofinder \
  --env AI_ODOOFINDER_API_URL=http://localhost:8989 \
  -- uvx ai-odoofinder-mcp
```

#### Usage

```bash
# Start a session
claude

# Use in chat
> I need an Odoo 17 module for recurring payments

# Check MCP status
/mcp
```

---

### ChatGPT Developer Mode

**Status:** ✅ Supported (Developer Mode)

#### Requirements

- ChatGPT plan with Developer Mode available
- Developer Mode enabled

#### Setup Steps

1. Go to **Settings** → **Apps & Connectors** → **Advanced** and enable **Developer Mode**
2. Create a new connector with:
   - **URL**: `https://addon-finder.eticco.es`
   - **Authentication**: None
3. Save and enable it in the chat

#### Usage

```
Use ai-odoofinder to search for Odoo 17 modules related to subscriptions
```

---

### VSCode Copilot

**Status:** ✅ Generally Available

GitHub Copilot in VSCode supports MCP since version 1.102.

#### Requirements

- VSCode 1.102 or later
- GitHub Copilot subscription (Free, Pro, Pro+, Business, or Enterprise)
- MCP policy enabled (for Business/Enterprise)

#### Configuration

Create `.vscode/mcp.json` in your project, or add it to your user `mcp.json` (Command Palette → "MCP: Open User Configuration"):

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

**Self-hosted backend (local STDIO package):**

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

**Reload VSCode** (`Ctrl/Cmd + Shift + P` → "Reload Window")

#### Usage

Open GitHub Copilot Chat (Agent mode) and ask:
```
Find an Odoo module for payment processing in v17
```

#### For Business/Enterprise Users

Administrators must enable the **"MCP servers in Copilot"** policy:

1. Go to **Organization/Enterprise Settings**
2. Navigate to **Copilot** → **Policies**
3. Enable **"MCP servers in Copilot"**

See [GitHub Docs](https://docs.github.com/copilot/customizing-copilot/using-model-context-protocol/extending-copilot-chat-with-mcp) for details.

---

### Cursor

**Status:** ✅ Fully Supported (Remote HTTP)

#### Configuration

**File location:** `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global)

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "url": "https://addon-finder.eticco.es"
    }
  }
}
```

For a self-hosted backend, use the [local STDIO package](#local-stdio-package-self-hosted-backend) block (same `mcpServers` format). **Restart Cursor** to apply changes.

#### Usage

In Cursor chat:
```
Find Odoo 16 modules for accounting
```

---

### Zed

**Status:** ✅ Supported (Remote HTTP)

#### Configuration

**File location:** `~/.config/zed/settings.json`

```json
{
  "context_servers": {
    "ai-odoofinder": {
      "url": "https://addon-finder.eticco.es"
    }
  }
}
```

**Self-hosted backend (local STDIO package):**

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

**Status:** ✅ Supported (Remote HTTP)

#### Configuration

**File location:** `~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "serverUrl": "https://addon-finder.eticco.es"
    }
  }
}
```

For a self-hosted backend, use the [local STDIO package](#local-stdio-package-self-hosted-backend) block (same `mcpServers` format). **Restart Windsurf** (or refresh MCP servers) to apply changes.

See [Windsurf MCP docs](https://docs.windsurf.com/windsurf/cascade/mcp) for more info.

---

### Antigravity

**Status:** ⚠️ Use the `mcp-remote` bridge

Google Antigravity has had compatibility issues with direct remote connections and with `uvx`.

#### Known Issues

1. ⚠️ Direct remote connections may stall indefinitely
2. ❌ `uvx` command may not be recognized

#### Recommended Solution: mcp-remote bridge

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

#### Self-hosted backend: full path to uvx

If you use the [local STDIO package](#local-stdio-package-self-hosted-backend) and `uvx` is not found, use its full path:

```bash
where uvx  # Windows
which uvx  # macOS/Linux
```

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "C:\\Users\\YOUR_USER\\.local\\bin\\uvx.exe",
      "args": ["ai-odoofinder-mcp"],
      "env": {
        "AI_ODOOFINDER_API_URL": "http://localhost:8989"
      }
    }
  }
}
```

---

## Troubleshooting

### Connection refused / Cannot connect

**Check:**
1. The server is up: `curl https://addon-finder.eticco.es/health`
2. You are using the **root URL** `https://addon-finder.eticco.es` (not `/mcp`, which returns 404)
3. Your client supports Streamable HTTP; otherwise use the [`mcp-remote` bridge](#mcp-remote-bridge-stdio-only-clients)
4. No proxy/firewall blocking outgoing HTTPS

### Local package returns errors / no results

The `ai-odoofinder-mcp` package needs a backend exposing the REST API. The public instance does **not** expose it (`/search` and `/stats` return 404), so point `AI_ODOOFINDER_API_URL` to your own deployment (e.g. `http://localhost:8989`) or switch to remote mode.

```bash
curl http://localhost:8989/health
```

### npx / mcp-remote not found

Install Node.js 18+ and verify with `node --version`. On Windows, some clients need the full path to `npx.cmd`.

### uvx: command not found (local package)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### MCP server not recognized

**Check:**
1. Configuration file is in the correct location
2. JSON syntax is valid (use a JSON validator)
3. Restart your IDE/client after changes
4. Check IDE logs for errors

### Server stalls indefinitely (Antigravity)

**This is a known issue.** Use the [`mcp-remote` bridge](#antigravity).

---

## Environment Variables (Local Package)

These only apply to the local `ai-odoofinder-mcp` package. Remote mode needs no configuration. All variables are optional.

### Backend connection

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_ODOOFINDER_API_URL` | URL of your self-hosted backend REST API | `http://localhost:8989` |
| `AI_ODOOFINDER_API_TIMEOUT` | Timeout for backend requests (seconds) | `60` |

### Transport (only when serving MCP over HTTP yourself)

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_TRANSPORT` | `stdio` or `http` | `stdio` |
| `MCP_HOST` | Host to bind in HTTP mode | `0.0.0.0` |
| `MCP_PORT` | Port to bind in HTTP mode | `8080` |
| `MCP_PATH` | MCP endpoint path in HTTP mode | `/` |

The equivalent command-line flags are `--http` (same as `MCP_TRANSPORT=http`), `--host` and `--port`.

### Setting Environment Variables

**In configuration file:**
```json
{
  "env": {
    "AI_ODOOFINDER_API_URL": "http://localhost:8989",
    "AI_ODOOFINDER_API_TIMEOUT": "60"
  }
}
```

**System-wide (Linux/macOS):**
```bash
export AI_ODOOFINDER_API_URL="http://localhost:8989"
```

**System-wide (Windows):**
```powershell
$env:AI_ODOOFINDER_API_URL="http://localhost:8989"
```

---

## Compatibility Matrix

| Client | Remote URL | Via `mcp-remote` | Local package (self-hosted) | Notes |
|--------|:---------:|:----------------:|:---------------------------:|-------|
| Claude.ai Web | ✅ | — | — | Custom connector |
| Claude Desktop | ✅ | ✅ | ✅ | Connector or bridge |
| Claude Code CLI | ✅ | ✅ | ✅ | `--transport http` |
| ChatGPT Dev Mode | ✅ | — | — | Developer Mode |
| VSCode Copilot | ✅ | ✅ | ✅ | `type: http`, policy required for Business/Enterprise |
| Cursor | ✅ | ✅ | ✅ | `url` |
| Windsurf | ✅ | ✅ | ✅ | `serverUrl` |
| Zed | ✅ | ✅ | ✅ | `context_servers` |
| Antigravity | ⚠️ | ✅ | ⚠️ | Use the bridge |

**Legend:**
- ✅ Supported
- ⚠️ Partial support / workarounds needed
- — Not applicable

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/SantipBarber/ai-odoo-finder/issues)
- **Documentation**: [Main README](../../README.md)
- **MCP Spec**: [Model Context Protocol](https://modelcontextprotocol.io/)

---

## Contributing

Found a new client or workaround? Please contribute!

1. Test the configuration
2. Document the steps
3. Submit a PR to this file
4. Share your experience

---

**Last updated:** October 2026  
**Public server:** `https://addon-finder.eticco.es` (hosted by [Eticco](https://www.eticco.es))  
**Transport:** Streamable HTTP
