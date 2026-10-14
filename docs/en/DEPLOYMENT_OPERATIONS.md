# AI-OdooFinder - Deployment & Operations Guide

**Language**: [English](../en/DEPLOYMENT_OPERATIONS.md) | [Español](../es/DEPLOYMENT_OPERATIONS.md)

> **Note:** The public AI-OdooFinder instance runs on [Eticco](https://www.eticco.es) infrastructure at **`https://addon-finder.eticco.es`** (MCP endpoint at the root URL). You don't need to deploy anything to use it. This guide documents the **reference self-hosted Docker deployment**, for running your own instance.

## Architecture Overview

A single VPS runs the three services defined in `docker-compose.yml`. A reverse proxy in front of it terminates TLS and forwards traffic to the MCP server.

```
                 +------------------+
                 |  MCP client (AI) |
                 +--------+---------+
                          |
                          | HTTPS
                          v
+--------------------------------------------------+
|                   VPS (Docker)                   |
|                                                  |
|   +------------------------------------------+   |
|   |          Reverse proxy (TLS)             |   |
|   +--------------------+---------------------+   |
|                        |                         |
|                        v                         |
|   +------------------------------------------+   |
|   |  mcp   :8080   (MCP endpoint at path /)  |   |
|   +--------------------+---------------------+   |
|                        |                         |
|                        v                         |
|   +------------------------------------------+   |
|   |  api   :8989   (FastAPI REST)            |   |
|   +--------------------+---------------------+   |
|                        |                         |
|                        v                         |
|   +------------------------------------------+   |
|   |  db    :5432   (PostgreSQL 17 + pgvector)|   |
|   +------------------------------------------+   |
|                                                  |
+--------------------------------------------------+
```

Only the MCP server needs to be reachable from the internet. The REST API (`:8989`) is used internally by the MCP server; expose it only if you want to use the [local STDIO package](#local-mode-stdio) from other machines.

## Server Information

| Item | Value |
|------|-------|
| **Public URL** | `https://<your-domain>` |
| **Provider** | Any VPS |
| **Architecture** | ARM64 or x86_64 |
| **OS** | Ubuntu 22.04+ LTS |
| **Resources** | A small VPS (~2 GB RAM) is enough for the API and PostgreSQL |
| **Project path** | `/opt/ai-odoo-finder` (the helper scripts and systemd unit assume this path) |

## Services

### Docker Containers

| Service | Container | Image | Port | Purpose |
|---------|-----------|-------|------|---------|
| `db` | `odoofinder-postgres` | `pgvector/pgvector:pg17` | 5432 | PostgreSQL 17 + pgvector |
| `api` | `odoofinder-api` | Built from `Dockerfile` | 8989 | FastAPI backend (REST API) |
| `mcp` | `odoofinder-mcp` | Built from `mcp-server/Dockerfile` | 8080 | MCP server (Streamable HTTP) |

The MCP endpoint is the root path (`MCP_PATH=/`, the default in both `mcp-server/Dockerfile` and `docker-compose.yml`).

### API Endpoints (FastAPI - :8989)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check (database connection and module count) |
| `/search` | GET, POST | Hybrid search (vector + BM25 + RRF) |
| `/modules/{id}` | GET | Get a module by ID |
| `/stats` | GET | Database statistics (modules per version) |
| `/docs` | GET | Swagger UI |

### MCP Endpoint (MCP Server - :8080)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | POST, GET | MCP endpoint (Streamable HTTP) |
| `/health` | GET | Liveness check, used by the Docker healthcheck |

### Search Parameters

Both `GET` and `POST` take the parameters in the query string:

```
GET /search?query=<text>&version=<version>&limit=<n>&dependencies=<dep1>&dependencies=<dep2>
```

| Parameter | Required | Example | Description |
|-----------|----------|---------|-------------|
| `query` | Yes | `sale order` | Search text (natural language) |
| `version` | Yes | `16.0` | Odoo version: `14.0` to `19.0` |
| `limit` | No | `10` | Max results, 1–50 (default: 10) |
| `min_score` | No | `30` | Minimum score, 0–100 (default: 0) |
| `dependencies` | No | `dependencies=sale&dependencies=stock` | Repeat the parameter for each dependency; returns modules that depend on **any** of them |

## Database Statistics

The number of indexed modules changes with every ETL run. Check your instance:

```bash
curl http://localhost:8989/stats
```

## Systemd Service (Auto-start)

`scripts/ai-odoo-finder.service` defines a systemd unit that starts the Docker stack on boot. Install it with `scripts/install_service.sh`.

### Service Commands

```bash
# Check status
systemctl status ai-odoo-finder

# Start services
systemctl start ai-odoo-finder

# Stop services
systemctl stop ai-odoo-finder

# Restart services
systemctl restart ai-odoo-finder

# View logs
journalctl -u ai-odoo-finder

# Follow logs in real time
journalctl -u ai-odoo-finder -f

# View last 50 lines
journalctl -u ai-odoo-finder -n 50
```

### Helper Scripts

Located in `/opt/ai-odoo-finder/scripts/`:

| Script | Description |
|--------|-------------|
| `start_system.sh` | Start all Docker services with health check |
| `stop_system.sh` | Stop all Docker services and clean up |
| `status_system.sh` | Show detailed system status |
| `install_service.sh` | Install/reinstall the systemd service |

### Manual Status Check

```bash
/opt/ai-odoo-finder/scripts/status_system.sh
```

This shows: Docker containers, API health, database stats, disk usage.

## Common Operations

### SSH Access

```bash
ssh user@<your-server>
cd /opt/ai-odoo-finder
```

### View Logs

```bash
# All services
docker compose logs -f

# API only
docker compose logs -f api

# MCP server only
docker compose logs -f mcp

# PostgreSQL only
docker compose logs -f db
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart API only
docker compose restart api

# Full rebuild (after code changes)
git pull
docker compose build --no-cache api mcp
docker compose up -d api mcp
```

### Check Service Status

```bash
docker compose ps
docker compose logs --tail 20
```

### Database Operations

```bash
# Connect to PostgreSQL
docker exec -it odoofinder-postgres psql -U odoofinder -d ai_odoofinder

# Count modules
docker exec odoofinder-postgres psql -U odoofinder -d ai_odoofinder -c "SELECT COUNT(*) FROM odoo_modules;"

# Check by version
docker exec odoofinder-postgres psql -U odoofinder -d ai_odoofinder -c "SELECT version, COUNT(*) FROM odoo_modules GROUP BY version ORDER BY version;"

# Back up database
docker exec odoofinder-postgres pg_dump -U odoofinder -d ai_odoofinder -F c -f /tmp/backup.dump
docker cp odoofinder-postgres:/tmp/backup.dump ./backup_$(date +%Y%m%d).dump

# Restore database
docker cp backup.dump odoofinder-postgres:/tmp/backup.dump
docker exec odoofinder-postgres pg_restore -U odoofinder -d ai_odoofinder --clean /tmp/backup.dump
```

### Test API

```bash
# Health check
curl http://localhost:8989/health

# Search test
curl "http://localhost:8989/search?query=sale%20order&version=16.0&limit=3"

# Search with dependencies
curl "http://localhost:8989/search?query=delivery&version=17.0&dependencies=sale&dependencies=stock"

# Stats
curl http://localhost:8989/stats
```

## Environment Variables

Located at `/opt/ai-odoo-finder/.env` (copy `.env.example`):

```env
# Database
DATABASE_URL=postgresql://odoofinder:<password>@localhost:5432/ai_odoofinder
POSTGRES_DB=ai_odoofinder
POSTGRES_USER=odoofinder
POSTGRES_PASSWORD=<password>

# External APIs
OPENROUTER_API_KEY=<key>    # Embeddings + AI enrichment (required)
GH_TOKEN=<token>            # GitHub API for the ETL (must exist, may be empty)

# App config
ENVIRONMENT=production
LOG_LEVEL=INFO
```

- **`DATABASE_URL`**: Docker Compose sets its own value for the `api` container (`postgresql+psycopg://...@db:5432/...`), built from the `POSTGRES_*` variables. The value in `.env` is only used by scripts that run on the host (such as the ETL), so it points to `localhost:5432`.
- **`GH_TOKEN`**: the backend settings declare it without a default, so the variable must be defined even if it is empty. A token gives higher GitHub API rate limits during the ETL.

**Note**: The `.env` file is in `.gitignore` and must never be committed.

## Hybrid Search Algorithm

The search uses **Reciprocal Rank Fusion (RRF)** combining:

1. **Vector search**: semantic similarity with `qwen/qwen3-embedding-4b` embeddings (2560 dimensions, via OpenRouter), computed as exact cosine distance in pgvector
2. **BM25-style full-text**: PostgreSQL full-text ranking over the module's technical name, name, summary, repository name, AI-generated description, keywords and tags, description and README (name fields carry the highest weight, README the lowest)

```
RRF_score = 1/(k + rank_vector) + 1/(k + rank_bm25)
```

Where `k=60` (standard RRF constant).

## Troubleshooting

### API not responding

```bash
# Check if container is running
docker compose ps

# Check logs for errors
docker compose logs api --tail 50

# Restart API
docker compose restart api
```

### Database connection issues

```bash
# Check PostgreSQL is healthy
docker compose ps db
docker exec odoofinder-postgres pg_isready -U odoofinder

# Check database exists
docker exec odoofinder-postgres psql -U odoofinder -l
```

### Search returns 0 results

1. Check the version exists: `curl http://localhost:8989/stats`
2. Check logs for errors: `docker compose logs api --tail 20`
3. Test with a simple query: `curl "http://localhost:8989/search?query=sale&version=16.0&limit=1"`

### Out of disk space

```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a

# Check large files
du -sh /opt/ai-odoo-finder/*
```

## MCP Server

The MCP server supports two modes of operation.

### Remote Mode (Docker)

For Claude.ai, Claude Code, Cursor, Zed and other clients with remote MCP support. The MCP server runs as a Docker container alongside the API:

```bash
# Deploy MCP server (without affecting other services)
docker compose build mcp
docker compose up -d mcp

# Check MCP server logs
docker compose logs mcp --tail 20

# Test MCP endpoint
curl -X POST "http://localhost:8080/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

**Exposing it:** expose port 8080 through your reverse proxy (TLS) at the root path, so clients connect to `https://<your-domain>`. Any reverse proxy works (Caddy, nginx, Traefik...); a tunnel such as Tailscale Funnel is another option.

### Local Mode (STDIO)

For clients that run the MCP server as a local process. Install the [`ai-odoofinder-mcp`](https://pypi.org/project/ai-odoofinder-mcp/) package from PyPI and point it to your API. This requires the API port (8989) to be reachable from the client machine.

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uvx",
      "args": ["ai-odoofinder-mcp"],
      "env": {
        "AI_ODOOFINDER_API_URL": "http://<your-server>:8989"
      }
    }
  }
}
```

Claude Desktop config file location:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

For other clients, see [MCP Client Configurations](MCP_CLIENT_CONFIGURATIONS.md).

## Scheduled ETL

The ETL process runs on the server via cron to keep the module index updated. It runs from the root project, which requires **Python 3.14** (managed by `uv`).

### Cron Configuration

To run the ETL daily at 3 AM:

```bash
# Edit crontab
crontab -e

# Add this line:
0 3 * * * /opt/ai-odoo-finder/scripts/cron_etl.sh >> /var/log/ai-odoofinder-etl.log 2>&1
```

### Manual Execution

```bash
# Run ETL manually
/opt/ai-odoo-finder/scripts/cron_etl.sh

# Or directly with uv
cd /opt/ai-odoo-finder
uv run python scripts/etl_oca_modules.py
```

### Counting modules without indexing

`scripts/count_oca_modules.py` walks the OCA repos with the same discovery functions as the ETL and counts modules per version. It does not touch the database or OpenRouter; it only needs `GH_TOKEN`. It takes a couple of minutes.

```bash
uv run python scripts/count_oca_modules.py
# Compare with what is indexed and save the per-repo breakdown
uv run python scripts/count_oca_modules.py --stats-url http://localhost:8989/stats --output count.json
```

It counts what exists on GitHub today, not what is indexed: if the index keeps branches or modules that are gone, the numbers will differ.

### ETL Logs

```bash
# View ETL logs
tail -f /var/log/ai-odoofinder-etl.log

# View last 100 lines
tail -100 /var/log/ai-odoofinder-etl.log
```

### ETL Features

- **Incremental updates**: only processes new/changed modules
- **Checkpoints**: can be interrupted and resumed
- **AI enrichment**: generates descriptions, tags and keywords with `x-ai/grok-4-fast` (via OpenRouter)
- **Embeddings**: creates vectors with `qwen/qwen3-embedding-4b` (via OpenRouter)

---

## Migration History

| Date | Action | Details |
|------|--------|---------|
| 2025-11-29 | Initial deployment | Migrated from Neon to self-hosted |
| 2025-11-29 | PostgreSQL 16 -> 17 | Upgraded for dump compatibility |
| 2025-11-29 | Data migration | 15,884 modules with embeddings |
| 2025-11-30 | Systemd service | Added auto-start on boot |
| 2025-11-30 | Removed Render | Consolidated to self-hosted Docker |
| 2026-10 | Public instance moved to Eticco infrastructure | `https://addon-finder.eticco.es` |

## Cost Summary (historical, personal deployment)

| Service | Before | After |
|---------|--------|-------|
| Neon PostgreSQL | $5/month | $0 (self-hosted) |
| Render API | Free tier (limited) | $0 (self-hosted) |
| Hetzner VPS | Already owned | No additional cost |
| **Total** | ~$5/month | **$0/month** |

---

*Last updated: 2026-10-14*
