# AI-OdooFinder - Deployment & Operations Guide

## Server Information

| Item | Value |
|------|-------|
| **Server IP** | 157.180.41.130 |
| **Provider** | Hetzner |
| **Architecture** | ARM64 (aarch64) |
| **OS** | Ubuntu 22.04.5 LTS |
| **Resources** | 2 vCPU, 3.7GB RAM, 38GB disk |
| **Project Path** | `/opt/ai-odoo-finder` |

## Services

### Docker Containers

| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| `odoofinder-postgres` | pgvector/pgvector:pg17 | 5432 | PostgreSQL 17 + pgvector |
| `odoofinder-api` | custom build | 8989 | FastAPI Backend |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and MCP configuration |
| `/health` | GET | Health check (DB connection) |
| `/search` | GET | Hybrid search (Vector + BM25 + RRF) |
| `/modules/{id}` | GET | Get module by ID |
| `/stats` | GET | Database statistics |
| `/docs` | GET | Swagger UI documentation |

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
ssh root@157.180.41.130
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

### Stop/Start Services

```bash
# Stop all
docker compose down

# Start all
docker compose up -d

# Stop and remove volumes (CAUTION: deletes data!)
docker compose down -v
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
# Database (Docker internal)
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

## Architecture

```
                    +------------------+
                    |   Client/Claude  |
                    +--------+---------+
                             |
                             | HTTP :8989
                             v
+---------------------------------------------------+
|                    Server (Hetzner)                |
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

## Hybrid Search Algorithm

The search uses **Reciprocal Rank Fusion (RRF)** combining:

1. **Vector Search**: Semantic similarity using embeddings (OpenAI text-embedding-3-small)
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

## MCP Server (Standalone)

The MCP server for Claude integration is located at `mcp-server/` and runs separately:

```bash
cd mcp-server
uv run python -m mcp_odoofinder
```

Configure in Claude Desktop (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "odoofinder": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_odoofinder"],
      "cwd": "/path/to/ai-odoo-finder/mcp-server"
    }
  }
}
```

## Migration History

| Date | Action | Details |
|------|--------|---------|
| 2025-11-29 | Initial deployment | Migrated from Neon to self-hosted |
| 2025-11-29 | PostgreSQL 16 -> 17 | Upgraded for dump compatibility |
| 2025-11-29 | Data migration | 15,884 modules with embeddings |
| 2025-11-30 | Systemd service | Added auto-start on boot |

## Costs Saved

- **Neon PostgreSQL**: $5/month (cancelled)
- **Render hosting**: Free tier was limited
- **Now**: Self-hosted on existing Hetzner server (no additional cost)

---

*Last updated: 2025-11-29*
