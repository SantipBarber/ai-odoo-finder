# AI-OdooFinder - MCP Client Configurations

**Language**: [English](../en/MCP_CLIENT_CONFIGURATIONS.md) | [Español](../es/MCP_CLIENT_CONFIGURATIONS.md)

> Complete guide for installing and configuring AI-OdooFinder MCP server across different AI clients and IDEs.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Local Mode (STDIO)](#local-mode-stdio)
  - [Remote Mode (HTTP)](#remote-mode-http)
- [Client Configurations](#client-configurations)
  - [Claude Desktop](#claude-desktop)
  - [Claude Code CLI](#claude-code-cli)
  - [Claude.ai Web](#claudeai-web-remote)
  - [ChatGPT Developer Mode](#chatgpt-developer-mode)
  - [VSCode Copilot](#vscode-copilot)
  - [Cursor](#cursor)
  - [Zed](#zed)
  - [Windsurf](#windsurf)
  - [Antigravity](#antigravity)
- [Troubleshooting](#troubleshooting)
- [Environment Variables](#environment-variables)
- [Compatibility Matrix](#compatibility-matrix)

---

## Quick Start

**Choose your installation method:**

| Method | Best For | Requirements |
|--------|----------|--------------|
| **Local (STDIO)** | Desktop apps, CLI tools | `uv` or `npx` installed |
| **Remote (HTTP)** | Web apps, zero-install | Internet connection only |

**Base configuration (adapt to your client):**

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

## Prerequisites

### For Local Mode (STDIO)

**Option 1: uv (Recommended)**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify
uv --version
```

**Option 2: Node.js (Alternative)**
```bash
# If you prefer npx over uvx
node --version  # Requires Node.js 18+
```

### For Remote Mode (HTTP)

No installation required! Just use the remote URL:
```
https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp
```

---

## Installation Methods

### Local Mode (STDIO)

**Pros:**
- ✅ Works offline
- ✅ No network latency
- ✅ Direct process communication
- ✅ Better for desktop apps

**Cons:**
- ❌ Requires local installation
- ❌ Manual updates needed

### Remote Mode (HTTP)

**Pros:**
- ✅ Zero installation
- ✅ Auto-updates
- ✅ Same config across devices
- ✅ Works everywhere

**Cons:**
- ❌ Requires internet
- ❌ Network latency
- ❌ Some clients don't support it

---

## Client Configurations

### Claude Desktop

**Status:** ✅ Fully Supported (Local STDIO)

#### Configuration

**File locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

**1. Using uvx (Recommended):**

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

**2. Using npx (Alternative):**

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

**3. Restart Claude Desktop** to apply changes.

---

### Claude Code CLI

**Status:** ✅ Fully Supported (Terminal)

Claude Code is Anthropic's official CLI tool for using Claude in the terminal.

#### Installation

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version
```

#### Quick Setup

```bash
# Option 1: Interactive wizard
claude mcp add

# Follow prompts:
# - Name: ai-odoofinder
# - Command: uvx
# - Args: --from git+https://github.com/SantipBarber/ai-odoo-finder#subdirectory=mcp-server ai-odoofinder-mcp
# - Env: AI_ODOOFINDER_API_URL=https://strategy-orchestrator-prod.tailf7d690.ts.net
```

#### Manual Configuration

Edit `~/.claude.json`:

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

#### Usage

```bash
# Start a session with MCP
claude

# Use in chat
> I need an Odoo 17 module for recurring payments

# Check MCP status
/mcp

# List available tools
/tools
```

---

### Claude.ai Web (Remote)

**Status:** ✅ Fully Supported (Remote HTTP)

No installation required! Connect directly from the web interface.

#### Setup Steps

1. Go to **[Claude.ai](https://claude.ai)**
2. Navigate to **Settings** → **Connectors**
3. Click **"Add custom connector"**
4. Enter configuration:
   - **Name**: AI-OdooFinder
   - **URL**: `https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp`
   - **Protocol**: Streamable HTTP (MCP 2024-11-05)
5. Click **Save**
6. Start using in chat!

#### Usage

Simply ask questions like:
```
Find me an Odoo 16 module for inventory management
```

---

### ChatGPT Developer Mode

**Status:** ✅ Supported (Beta - September 2025)

OpenAI added full MCP support to ChatGPT in September 2025 with **Developer Mode**.

#### Requirements

- ChatGPT Plus, Pro, or Team subscription
- Developer Mode enabled (beta)

#### Setup Steps

1. Go to **[ChatGPT Settings](https://chat.openai.com/settings)**
2. Navigate to **Beta Features**
3. Enable **"Developer Mode"**
4. Go to **Integrations** → **MCP Servers**
5. Click **"Add MCP Server"**

#### Configuration Options

**Option 1: Remote (Easiest)**
```
URL: https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp
Protocol: HTTP/Streamable
```

**Option 2: Local (Advanced)**

Create `~/.chatgpt/mcp.json`:
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

#### Usage

```
Use ai-odoofinder to search for Odoo 17 modules related to subscriptions
```

**Note:** Full write capabilities are available (not just read-only).

---

### VSCode Copilot

**Status:** ✅ Generally Available (GA - July 2025)

GitHub Copilot in VSCode supports MCP since version 1.102 (July 2025).

#### Requirements

- VSCode 1.102 or later
- GitHub Copilot subscription (Free, Pro, Pro+, Business, or Enterprise)
- MCP policy enabled (for Business/Enterprise)

#### Configuration

**File location:** `.vscode/mcp.json` (project) or `~/.config/Code/User/mcp.json` (global)

**1. Project-level configuration:**

Create `.vscode/mcp.json` in your project:

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

**2. Global configuration:**

Edit `~/.config/Code/User/mcp.json`:

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

**3. Reload VSCode** (`Ctrl/Cmd + Shift + P` → "Reload Window")

#### Usage

Open GitHub Copilot Chat and ask:
```
@workspace Find an Odoo module for payment processing in v17
```

#### For Business/Enterprise Users

Administrators must enable the **"MCP servers in Copilot"** policy:

1. Go to **Organization/Enterprise Settings**
2. Navigate to **Copilot** → **Policies**
3. Enable **"MCP servers in Copilot"**

See [GitHub Docs](https://docs.github.com/copilot/customizing-copilot/using-model-context-protocol/extending-copilot-chat-with-mcp) for details.

---

### Cursor

**Status:** ✅ Fully Supported

#### Configuration

**File location:** `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global)

**1. Global configuration (Recommended):**

```bash
# Create config directory
mkdir -p ~/.cursor

# Edit config
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

**2. Project-specific configuration:**

Create `.cursor/mcp.json` in your project root.

**3. Restart Cursor**

#### Usage

In Cursor chat:
```
Find Odoo 16 modules for accounting
```

---

### Zed

**Status:** ✅ Supported

#### Configuration

**File location:** `~/.config/zed/settings.json`

```bash
# Edit Zed settings
nano ~/.config/zed/settings.json
```

Add to your settings:

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

**Restart Zed** to apply changes.

---

### Windsurf

**Status:** ✅ Supported

#### Configuration

**File location:** `~/.windsurf/mcp.json` (global) or `.windsurf/mcp.json` (project)

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

**Restart Windsurf** to apply changes.

See [Windsurf MCP docs](https://docs.windsurf.com/windsurf/mcp) for more info.

---

### Antigravity

**Status:** ⚠️ Partial Support (Known Issues)

Google Antigravity has known compatibility issues with `uvx` and remote MCP servers.

#### Known Issues

1. ❌ `uvx` command not recognized
2. ❌ SSE (Server-Sent Events) protocol incompatibility
3. ⚠️ Remote connections may stall indefinitely

#### Recommended Solutions

**Solution 1: Use npx instead of uvx**

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

**Solution 2: Use full path to uvx (Windows)**

Find your uvx path:
```bash
where uvx  # Windows
which uvx  # macOS/Linux
```

Update configuration with full path:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "C:\\Users\\YOUR_USER\\.cargo\\bin\\uvx.exe",
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

**Solution 3: Use Python directly**

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

#### Current Limitations

- ❌ **Remote mode NOT supported** - Antigravity uses SSE protocol, but our server uses Streamable HTTP (MCP 2024-11-05)
- ✅ **Local mode WORKS** - Use one of the solutions above
- ⚠️ **May require manual installation** - Install package first, then configure

#### Alternative: Use mcp-remote proxy

```bash
# Install mcp-remote
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

## Troubleshooting

### uvx: command not found

**Solution 1: Install uv**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

**Solution 2: Use npx instead**
```json
{
  "command": "npx",
  "args": ["-y", "@SantipBarber/ai-odoofinder-mcp"]
}
```

### Connection refused / Cannot connect

**Check:**
1. Server is running: `curl https://strategy-orchestrator-prod.tailf7d690.ts.net/health`
2. Environment variable is set correctly
3. No firewall blocking connections
4. Try remote mode instead of local

### MCP server not recognized

**Check:**
1. Configuration file is in the correct location
2. JSON syntax is valid (use a JSON validator)
3. Restart your IDE/client after changes
4. Check IDE logs for errors

### Slow performance

**Try:**
1. Use local mode instead of remote
2. Check internet connection
3. Clear IDE cache
4. Restart IDE

### Server stalls indefinitely (Antigravity)

**This is a known issue.** See [Antigravity section](#antigravity) for solutions.

Use npx or full path to uvx instead.

---

## Environment Variables

### Required

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_ODOOFINDER_API_URL` | Backend API URL | `https://strategy-orchestrator-prod.tailf7d690.ts.net` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `TIMEOUT` | Request timeout (seconds) | `30` |

### Setting Environment Variables

**In configuration file:**
```json
{
  "env": {
    "AI_ODOOFINDER_API_URL": "https://your-custom-url.com",
    "LOG_LEVEL": "DEBUG"
  }
}
```

**System-wide (Linux/macOS):**
```bash
export AI_ODOOFINDER_API_URL="https://your-custom-url.com"
```

**System-wide (Windows):**
```powershell
$env:AI_ODOOFINDER_API_URL="https://your-custom-url.com"
```

---

## Compatibility Matrix

| Client | Local | Remote | Status | Notes |
|--------|-------|--------|--------|-------|
| Claude Desktop | ✅ | ❌ | Stable | Best experience |
| Claude Code CLI | ✅ | ✅ | Stable | Terminal-based |
| Claude.ai Web | ❌ | ✅ | Stable | Zero install |
| ChatGPT Dev Mode | ✅ | ✅ | Beta | New! Sept 2025 |
| VSCode Copilot | ✅ | ⚠️ | GA | Policy required |
| Cursor | ✅ | ❌ | Stable | Popular choice |
| Zed | ✅ | ❌ | Stable | Fast editor |
| Windsurf | ✅ | ❌ | Stable | Full support |
| Antigravity | ⚠️ | ❌ | Issues | Use npx/workarounds |

**Legend:**
- ✅ Fully supported
- ⚠️ Partial support / workarounds needed
- ❌ Not supported

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/SantipBarber/ai-odoo-finder/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SantipBarber/ai-odoo-finder/discussions)
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

**Last updated:** January 2025  
**MCP Spec Version:** 2024-11-05  
**Server Version:** 1.0.0