# Deployment Guide - AI-OdooFinder

This guide covers deploying AI-OdooFinder to a VPS server with Docker.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your VPS Server                          │
│  ┌─────────────────┐       ┌─────────────────────────────┐  │
│  │   PostgreSQL    │◄─────►│     FastAPI Backend         │  │
│  │   (pgVector)    │       │     (Port 8989)             │  │
│  │   Container     │       │     Container               │  │
│  └─────────────────┘       └─────────────────────────────┘  │
│          ▲                              ▲                    │
│          │                              │                    │
│          └──────────────┬───────────────┘                    │
│                         │                                    │
│              Docker Network (internal)                       │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Port 8989 (HTTPS via reverse proxy)
                          ▼
                    ┌───────────┐
                    │  Internet │
                    └───────────┘
```

## Prerequisites

- VPS with at least:
  - 2 vCPU
  - 2 GB RAM (4 GB recommended)
  - 10 GB free disk space
- Docker and Docker Compose installed
- Domain name (optional, for HTTPS)

## Quick Start

### 1. Clone the Repository

```bash
ssh root@your-server-ip
cd /opt  # or your preferred directory
git clone https://github.com/SantipBarber/ai-odoo-finder.git
cd ai-odoo-finder
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.docker.example .env

# Edit with your values
nano .env
```

Required variables:
```bash
POSTGRES_PASSWORD=your_secure_password
OPENROUTER_API_KEY=sk-or-v1-your_key
GH_TOKEN=ghp_your_token  # Optional but recommended
```

### 3. Start Services

```bash
# Build and start containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### 4. Migrate Data from Neon (if applicable)

If you're migrating from Neon PostgreSQL:

```bash
# Add Neon connection string to .env
echo 'NEON_DATABASE_URL=postgresql://user:pass@host/db?sslmode=require' >> .env

# Run migration script
./scripts/migrate_from_neon.sh
```

### 5. Verify Installation

```bash
# Check API health
curl http://localhost:8989/

# Test search
curl 'http://localhost:8989/search?query=inventory&version=17.0&limit=3'
```

## Production Setup

### HTTPS with Caddy (Recommended)

Create a Caddyfile:

```bash
cat > /etc/caddy/Caddyfile << 'EOF'
odoofinder.yourdomain.com {
    reverse_proxy localhost:8989
}
EOF

# Reload Caddy
systemctl reload caddy
```

### HTTPS with Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name odoofinder.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/odoofinder.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/odoofinder.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8989;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Firewall Configuration

```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (for Let's Encrypt)
ufw allow 443/tcp   # HTTPS
ufw enable
```

## MCP Server Configuration

For Claude Desktop users, the MCP server connects to your deployed API:

Edit `~/.config/Claude/claude_desktop_config.json` (Linux) or equivalent:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ai-odoo-finder/mcp-server",
        "run",
        "ai-odoofinder-mcp"
      ],
      "env": {
        "AI_ODOOFINDER_API_URL": "https://odoofinder.yourdomain.com"
      }
    }
  }
}
```

## Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f db
```

### Update Application

```bash
cd /opt/ai-odoo-finder
git pull origin main
docker-compose build api
docker-compose up -d api
```

### Backup Database

```bash
# Create backup
docker exec odoofinder-postgres pg_dump -U odoofinder ai_odoofinder > backup_$(date +%Y%m%d).sql

# Restore from backup
docker exec -i odoofinder-postgres psql -U odoofinder ai_odoofinder < backup_20241201.sql
```

### Run ETL (Update Module Index)

```bash
# Manual ETL run
docker-compose run --rm api python scripts/etl_oca_modules.py
```

Or set up a cron job:

```bash
# Edit crontab
crontab -e

# Add daily ETL at 3 AM
0 3 * * * cd /opt/ai-odoo-finder && docker-compose run --rm api python scripts/etl_oca_modules.py >> /var/log/odoofinder-etl.log 2>&1
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs api

# Common issues:
# - Missing environment variables
# - Port already in use
# - Database not ready
```

### Database connection errors

```bash
# Check PostgreSQL is running
docker-compose ps db

# Test connection
docker exec odoofinder-postgres pg_isready
```

### Memory issues

If running low on memory:

```bash
# Check memory usage
docker stats

# Limit container memory in docker-compose.yml:
services:
  api:
    deploy:
      resources:
        limits:
          memory: 512M
```

### Reset everything

```bash
# Stop and remove containers + volumes (DELETES DATA!)
docker-compose down -v

# Start fresh
docker-compose up -d
```

## Resource Usage

Expected resource usage after migration:

| Resource | Usage |
|----------|-------|
| Disk (PostgreSQL data) | ~500 MB - 1 GB |
| RAM (API container) | ~200-400 MB |
| RAM (PostgreSQL) | ~100-200 MB |
| CPU | < 5% idle, spikes during search |

## Security Checklist

- [ ] Strong POSTGRES_PASSWORD set
- [ ] API keys not exposed in logs
- [ ] Firewall configured (only 22, 80, 443 open)
- [ ] HTTPS enabled via reverse proxy
- [ ] Regular backups configured
- [ ] Docker containers run as non-root
