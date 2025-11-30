# AI-OdooFinder MCP Server

MCP (Model Context Protocol) server for semantic search of Odoo modules in the OCA ecosystem.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended package manager)
- Claude Desktop installed (for local usage)

## Installation

### Step 1: Verify that `uv` is installed

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### Step 2: Install MCP server dependencies

```bash
cd <your-path>/ai-odoo-finder/mcp-server
uv sync
```

### Step 3: Configure Claude Desktop

Open the Claude Desktop configuration file:

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

If the file doesn't exist, create it.

### Step 4: Add the MCP server configuration

Add (or modify) the content of `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uv",
      "args": [
        "--directory",
        "<your-path>/ai-odoo-finder/mcp-server",
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

> **IMPORTANT:** Use the **absolute path** to your `mcp-server` directory.

### Step 5: Configure the API URL (optional)

By default, the MCP server connects to `http://localhost:8989`.

If your API is elsewhere (e.g., remote server), modify the environment variable:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uv",
      "args": [
        "--directory",
        "<your-path>/ai-odoo-finder/mcp-server",
        "run",
        "ai-odoofinder-mcp"
      ],
      "env": {
        "AI_ODOOFINDER_API_URL": "https://<your-server>.ts.net"
      }
    }
  }
}
```

### Step 6: Restart Claude Desktop

**IMPORTANT:** You must close Claude Desktop completely and reopen it.

- **macOS:** `Cmd+Q` (not just close the window)
- **Windows:** Close from the system tray

### Step 7: Verify the installation

1. Open Claude Desktop
2. Look for the tools icon in the bottom right corner
3. You should see **"ai-odoofinder"** with the `search_odoo_modules` tool

## Testing the server

### Basic test in Claude Desktop

Type in Claude:

```
Are there electronic invoicing modules for Spain in Odoo 16?
```

Claude should automatically use the `search_odoo_modules` tool.

### Manual test (without Claude)

```bash
cd <your-path>/ai-odoo-finder/mcp-server
uv run ai-odoofinder-mcp
```

The server will start and wait for JSON-RPC connections via stdin/stdout.

## Troubleshooting

### The server doesn't appear in Claude Desktop

1. **Verify the path:** Must be absolute (starts with `/` on macOS/Linux or drive letter on Windows)
2. **Verify that `uv` is in PATH:**
   ```bash
   which uv
   ```
3. **Check Claude logs:**
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```
4. **Restart Claude completely** (Cmd+Q, not just close window)

### "Connection refused" or timeout error

1. **Verify the API is running:**
   ```bash
   curl http://localhost:8989/api/v1/search \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "version": "16.0"}'
   ```

2. **Increase timeout:** Modify `AI_ODOOFINDER_API_TIMEOUT` in environment variables

### "corrupted JSON-RPC" error

This occurs if there's `print()` in the code that writes to stdout.
The MCP server must use only `logging` (which writes to stderr).

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

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_ODOOFINDER_API_URL` | `http://localhost:8989` | Backend API URL |
| `AI_ODOOFINDER_API_TIMEOUT` | `60` | API timeout in seconds |

## Intelligent Search Flow

The server implements the intelligent flow according to SPEC-602:

1. **Clarification:** The LLM asks for clarifications if the query is generic
2. **Expansion:** The LLM expands the query with ES/EN synonyms
3. **Structured response:** Results with confidence levels (HIGH/MEDIUM/LOW)
4. **Confirmation:** The LLM confirms with the user if it found what they were looking for

## Technical Documentation

### SPEC-602 Implementation

This server implements the **Intelligent Search Flow** according to SPEC-602:

**Reference documents:**
- [SPEC-602: Intelligent Flow](../specs/phase-6-intelligent-mcp/SPEC-602-intelligent-mcp-flow.md)
- [Implementation Summary](../specs/phase-6-intelligent-mcp/IMPLEMENTATION_SUMMARY.md)
- [Quick Reference](../specs/phase-6-intelligent-mcp/QUICK_REFERENCE.md)
- [CHANGELOG](../docs/CHANGELOG.md)

### Key Changes

| Component | Change | Impact |
|-----------|--------|--------|
| **Tool Description** | Instructions for localizations | Claude builds optimal queries |
| **Response Format** | Confidence levels (HIGH/MEDIUM/LOW) | Better presentation to user |
| **Migration 005** | `repo_name` in `searchable_text` | 449 modules findable by country |

### Testing

6 test cases with 100% success:
- Facturae Spain -> `l10n_es_facturae_face`
- CFDI Mexico -> `l10n_mx_cfdi`
- Subscriptions -> `contract`
- DMS + OCR -> `dms`
- AEAT 303 -> `l10n_es_aeat_mod303`
- Delivery carriers -> `delivery_price_method`

## Useful Links

- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [AI-OdooFinder](https://github.com/SantipBarber/ai-odoo-finder)
- [Full SPEC-602](../specs/phase-6-intelligent-mcp/SPEC-602-intelligent-mcp-flow.md)
