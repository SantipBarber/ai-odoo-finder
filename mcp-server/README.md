# AI-OdooFinder MCP Server

**Language**: [English](README.md) | [Español](README.es.md)

MCP (Model Context Protocol) server for semantic search of Odoo modules in the OCA ecosystem.

## Getting Started

Add the following config to your MCP client:

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

> **Note**: Requires [uv](https://docs.astral.sh/uv/) package manager installed.

---

## MCP Client Configuration

<details>
<summary><b>Claude Desktop</b></summary>

Add to `claude_desktop_config.json`:

**File locations:**
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

Restart Claude Desktop.

</details>

<details>
<summary><b>Claude.ai Web (Remote)</b></summary>

No installation required. Connect directly:

1. Go to **Claude.ai** > **Settings** > **Connectors**
2. Click **"Add custom connector"**
3. Enter the MCP server URL:
   ```
   https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp
   ```
4. Save and start searching

> **Protocol**: Streamable HTTP (MCP spec 2024-11-05)

</details>

<details>
<summary><b>Zed</b></summary>

Add to `~/.config/zed/settings.json`:

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

Add to `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global):

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

Add to your Antigravity MCP configuration file:

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

**Windows troubleshooting**: If `uvx` is not found, use the full path:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "C:\\Users\\YOUR_USER\\.cargo\\bin\\uvx.exe",
      "args": [ /* same as above */ ]
    }
  }
}
```

> **Note**: Antigravity uses SSE protocol. Remote connections may fail due to our Streamable HTTP implementation. Use local mode.

</details>

<details>
<summary><b>Windsurf</b></summary>

Add to your Windsurf MCP configuration:

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
<summary><b>Other MCP Clients</b></summary>

For any MCP-compatible client:

**Local mode (STDIO)**: Use the configuration shown in "Getting Started"

**Remote mode (HTTP/SSE)**: Use the server URL:
```
https://strategy-orchestrator-prod.tailf7d690.ts.net/mcp
```

**Protocol**: Streamable HTTP (MCP spec 2024-11-05)  
**Authentication**: None (public server)

</details>

---

## Your First Prompt

Enter the following prompt in your MCP client to check if everything is working:

```
I need a module for Odoo 17 that handles recurring payments
```

The MCP server should search and return relevant modules like `contract` or `subscription_oca`.

> **Note**: The MCP server connects to the remote API automatically. No additional setup required.

---

## Features

- **Hybrid Search**: Combines semantic search (embeddings) with BM25 full-text
- **Version Filtering**: Only shows compatible modules (Odoo 10.0 to 19.0)
- **AI Enrichment**: Descriptions, tags, and keywords generated by Grok-4-fast
- **16,494 modules** indexed from OCA repositories

---

## Intelligent Search Flow

The server implements an intelligent search flow:

1. **Clarification**: The LLM asks for clarifications if the query is generic
2. **Expansion**: The LLM expands the query with ES/EN synonyms
3. **Structured response**: Results with confidence levels (HIGH/MEDIUM/LOW)
4. **Confirmation**: The LLM confirms with the user if it found what they were looking for

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_ODOOFINDER_API_URL` | `http://localhost:8989` | Backend API URL |
| `AI_ODOOFINDER_API_TIMEOUT` | `60` | API timeout in seconds |

---

## Project Structure

```
mcp-server/
├── pyproject.toml           # Package configuration
├── README.md                # This file
└── src/
    └── ai_odoofinder_mcp/
        ├── __init__.py
        └── server.py        # Main MCP server
```

---

## Troubleshooting

### The server doesn't appear in the MCP client

1. **Verify that `uv` is installed:**
   ```bash
   uv --version
   ```

2. **Check MCP client logs** for error messages

3. **Restart the MCP client completely** (not just close the window)

### "Connection refused" or timeout error

1. **Verify the API is running:**
   ```bash
   curl https://strategy-orchestrator-prod.tailf7d690.ts.net/health
   ```

2. **Increase timeout**: Set `AI_ODOOFINDER_API_TIMEOUT` to a higher value (e.g., `120`)

### "uvx not found" error

- **Make sure `uv` is in PATH**: Run `which uv` (Unix) or `where uv` (Windows)
- **Use full path**: If `uv` is not in PATH, use the absolute path in the config

---

## Useful Links

- [Main Project](https://github.com/SantipBarber/ai-odoo-finder)
- [CHANGELOG](../docs/en/CHANGELOG.md)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)