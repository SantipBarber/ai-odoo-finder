# AI-OdooFinder - Deployment & Operations Guide

**Language**: [English](../en/DEPLOYMENT_OPERATIONS.md) | [Español](../es/DEPLOYMENT_OPERATIONS.md)

## Architecture Overview

Self-hosted solution on Hetzner VPS with Docker. Previously used Neon (PostgreSQL) and Render (API hosting), now consolidated to a single server for cost efficiency and simplicity.

```
                    +------------------+
                    |   Client/Claude  |
                    +--------+---------+
                             |
                             | HTTP :8989
                             v
+---------------------------------------------------+
|                 Hetzner VPS (Docker)               |
|                                                   |
|  +-------------+          +-------------------+   |
|  | PostgreSQL  |<-------->|   FastAPI (API)   |   |
|  | + pgvector  |  :5432   |                   |   |
|  | (db)        |          | - /search         |   |
|  +-------------+          | - /stats          |   |
|                           | - /health         |   |
|                           +-------------------+   |
|                                                   |
+---------------------------------------------------+
```

## Server Information

| Item | Value |
|------|-------|
| **Public URL** | `https://<your-server>.ts.net` |
| **Provider** | VPS (exposed via Tailscale Funnel) |
| **Architecture** | ARM64 or x86_64 |
| **OS** | Ubuntu 22.04+ LTS |
| **Recommended Resources** | 2 vCPU, 4GB RAM, 40GB disk |
| **Project Path** | `/opt/ai-odoo-finder` |

## Services

### Docker Containers

| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| `odoofinder-postgres` | pgvector/pgvector:pg17 | 5432 | PostgreSQL 17 + pgvector |
| `odoofinder-api` | custom build | 8989 | FastAPI Backend |
| `odoofinder-mcp` | custom build | 8080 | MCP Server (Remote HTTP) |

### API Endpoints (FastAPI - :8989)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and MCP configuration |
| `/health` | GET | Health check (DB connection) |
| `/search` | GET | Hybrid search (Vector + BM25 + RRF) |
| `/modules/{id}` | GET | Get module by ID |
| `/stats` | GET | Database statistics |
| `/docs` | GET | Swagger UI documentation |

### MCP Endpoints (MCP Server - :8080)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp` | POST | MCP JSON-RPC endpoint (Streamable HTTP) |
| `/mcp` | GET | MCP SSE endpoint (legacy) |

### Search Parameters

```
GET /search?query=<text>&version=<version>&limit=<n>&dependencies=<dep1,dep2>
```

| Parameter | Required | Example | Description |
|-----------|----------|---------|-------------|
| `query` | Yes | `sale order` | Search text (natural language) |
| `version` | Yes | `16.0` | Odoo version filter |
| `limit` | No | `10` | Max results (default: 10) |
| `dependencies` | No | `sale,stock` | Filter by dependencies |

## Database Statistics

- **Total modules**: 15,884
- **With embeddings**: 100%

| Version | Modules |
|---------|---------|
| 12.0 | 2,215 |
| 13.0 | 1,990 |
| 14.0 | 2,886 |
| 15.0 | 2,074 |
| 16.0 | 2,886 |
| 17.0 | 1,699 |
| 18.0 | 2,022 |
| 19.0 | 112 |

## Systemd Service (Auto-start)

The system is configured as a systemd service that starts automatically on boot.

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

# Follow logs in real-time
journalctl -u ai-odoo-finder -f

# View last 50 lines
journalctl -u ai-odoo-finder -n 50
```

### Helper Scripts

Located in `/opt/ai-odoo-finder/scripts/`:

| Script | Description |
|--------|-------------|
| `start_system.sh` | Start all Docker services with health check |
| `stop_system.sh` | Stop all Docker services and cleanup |
| `status_system.sh` | Show detailed system status |
| `install_service.sh` | Install/reinstall systemd service |

### Manual Status Check

```bash
/opt/ai-odoo-finder/scripts/status_system.sh
```

This shows: Docker containers, API health, database stats, disk usage.

## Common Operations

### SSH Access

```bash
# Via Tailscale (recommended)
ssh user@<your-server-name>

# Or via Tailscale IP
ssh user@<tailscale-ip>

cd /opt/ai-odoo-finder
```

### View Logs

```bash
# All services
docker compose logs -f

# API only
docker compose logs -f api

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
docker compose build --no-cache api
docker compose up -d api
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

# Backup database
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

# Stats
curl http://localhost:8989/stats
```

## Environment Variables

Located at `/opt/ai-odoo-finder/.env`:

```env
# Database
DATABASE_URL=postgresql://odoofinder:<password>@db:5432/ai_odoofinder
POSTGRES_DB=ai_odoofinder
POSTGRES_USER=odoofinder
POSTGRES_PASSWORD=<password>

# External APIs
OPENROUTER_API_KEY=<key>    # For embeddings generation
GH_TOKEN=<token>            # For GitHub API (optional)

# App config
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Note**: The `.env` file is in `.gitignore` and should never be committed.

## Hybrid Search Algorithm

The search uses **Reciprocal Rank Fusion (RRF)** combining:

1. **Vector Search**: Semantic similarity using Qwen3-Embedding (2560 dimensions)
2. **BM25 Full-Text**: Keyword matching on technical_name, name, summary, description

```
RRF_score = 1/(k + rank_vector) + 1/(k + rank_bm25)
```

Where `k=60` (standard RRF constant)

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

1. Check version exists: `curl http://localhost:8989/stats`
2. Check logs for errors: `docker compose logs api --tail 20`
3. Test with simple query: `curl "http://localhost:8989/search?query=sale&version=16.0&limit=1"`

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

The MCP Server supports two modes of operation:

### Remote Mode (Docker - for Claude.ai Web, Zed, Cursor)

The MCP server runs as a Docker container alongside the API:

```bash
# Deploy MCP server (without affecting other services)
docker compose build mcp
docker compose up -d mcp

# Check MCP server status
docker compose logs mcp --tail 20

# Test MCP endpoint
curl -X POST "http://localhost:8080/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

**Tailscale Funnel Setup** (expose MCP on port 8080):

```bash
# Add port 8080 to Tailscale Funnel
tailscale funnel 8080
```

### Local Mode (STDIO - for Claude Desktop)

For Claude Desktop, run the MCP server locally:

```bash
cd mcp-server
uv run ai-odoofinder-mcp
```

Configure in Claude Desktop:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/SantipBarber/ai-odoo-finder#subdirectory=mcp-server", "ai-odoofinder-mcp"],
      "env": {
        "AI_ODOOFINDER_API_URL": "https://<your-server>.ts.net"
      }
    }
  }
}
```

## Scheduled ETL

The ETL process runs automatically via cron job on the server to keep the module index updated.

### Cron Configuration

The ETL runs daily at 3 AM UTC. To configure:

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

### ETL Logs

```bash
# View ETL logs
tail -f /var/log/ai-odoofinder-etl.log

# View last 100 lines
tail -100 /var/log/ai-odoofinder-etl.log
```

### ETL Features

- **Incremental updates**: Only processes new/changed modules
- **Checkpoints**: Can be interrupted and resumed
- **AI Enrichment**: Generates descriptions, tags, and keywords with Grok-4-fast
- **Embeddings**: Creates vectors with Qwen3-Embedding-4B

---

## Migration History

| Date | Action | Details |
|------|--------|---------|
| 2025-11-29 | Initial deployment | Migrated from Neon to self-hosted |
| 2025-11-29 | PostgreSQL 16 -> 17 | Upgraded for dump compatibility |
| 2025-11-29 | Data migration | 15,884 modules with embeddings |
| 2025-11-30 | Systemd service | Added auto-start on boot |
| 2025-11-30 | Removed Render | Consolidated to self-hosted Docker |

## Cost Summary

| Service | Before | After |
|---------|--------|-------|
| Neon PostgreSQL | $5/month | $0 (self-hosted) |
| Render API | Free tier (limited) | $0 (self-hosted) |
| Hetzner VPS | Already owned | No additional cost |
| **Total** | ~$5/month | **$0/month** |

---

*Last updated: 2025-11-30*
