# Guía de Despliegue y Operaciones de AI-OdooFinder

**Language**: [English](../en/DEPLOYMENT_OPERATIONS.md) | [Español](../es/DEPLOYMENT_OPERATIONS.md)

## Resumen de Arquitectura

Solución auto-hospedada en VPS Hetzner con Docker. Anteriormente usaba Neon (PostgreSQL) y Render (API hosting), ahora consolidada en un solo servidor para eficiencia de costo y simplicidad.

```
                    +------------------+
                    |   Cliente/Claude  |
                    +--------+---------+
                             |
                             | HTTP :8989
                             v
+---------------------------------------------------+
|                 VPS Hetzner (Docker)               |
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

## Información del Servidor

| Item | Valor |
|------|-------|
| **URL Pública** | `https://<tu-servidor>.ts.net` |
| **Proveedor** | VPS (expuesto via Tailscale Funnel) |
| **Arquitectura** | ARM64 o x86_64 |
| **OS** | Ubuntu 22.04+ LTS |
| **Recursos Recomendados** | 2 vCPU, 4GB RAM, 40GB disco |
| **Ruta del Proyecto** | `/opt/ai-odoo-finder` |

## Servicios

### Contenedores Docker

| Contenedor | Imagen | Puerto | Propósito |
|------------|--------|--------|-----------|
| `odoofinder-postgres` | pgvector/pgvector:pg17 | 5432 | PostgreSQL 17 + pgvector |
| `odoofinder-api` | imagen personal | 8989 | Backend FastAPI |
| `odoofinder-mcp` | imagen personal | 8080 | Servidor MCP (HTTP Remoto) |

### Endpoints API (FastAPI - :8989)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información de la API y configuración MCP |
| `/health` | GET | Verificación de salud (conexión DB) |
| `/search` | GET | Búsqueda híbrida (Vector + BM25 + RRF) |
| `/modules/{id}` | GET | Obtener módulo por ID |
| `/stats` | GET | Estadísticas de base de datos |
| `/docs` | GET | Documentación Swagger UI |

### Endpoints MCP (Servidor MCP - :8080)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/mcp` | POST | Endpoint JSON-RPC de MCP (HTTP Streamable) |
| `/mcp` | GET | Endpoint SSE de MCP (legado) |

### Parámetros de Búsqueda

```
GET /search?query=<texto>&version=<version>&limit=<n>&dependencies=<dep1,dep2>
```

| Parámetro | Requerido | Ejemplo | Descripción |
|-----------|-----------|---------|-------------|
| `query` | Sí | `orden de venta` | Texto de búsqueda (lenguaje natural) |
| `version` | Sí | `16.0` | Filtro de versión Odoo |
| `limit` | No | `10` | Máx resultados (predeterminado: 10) |
| `dependencies` | No | `sale,stock` | Filtrar por dependencias |

## Estadísticas de Base de Datos

- **Módulos totales**: 15,884
- **Con embeddings**: 100%

| Versión | Módulos |
|---------|---------|
| 12.0 | 2,215 |
| 13.0 | 1,990 |
| 14.0 | 2,886 |
| 15.0 | 2,074 |
| 16.0 | 2,886 |
| 17.0 | 1,699 |
| 18.0 | 2,022 |
| 19.0 | 112 |

## Servicio Systemd (Auto-inicio)

El sistema está configurado como un servicio systemd que se inicia automáticamente al arranque.

### Comandos del Servicio

```bash
# Verificar estado
systemctl status ai-odoo-finder

# Iniciar servicios
systemctl start ai-odoo-finder

# Detener servicios
systemctl stop ai-odoo-finder

# Reiniciar servicios
systemctl restart ai-odoo-finder

# Ver logs
journalctl -u ai-odoo-finder

# Seguir logs en tiempo real
journalctl -u ai-odoo-finder -f

# Ver últimas 50 líneas
journalctl -u ai-odoo-finder -n 50
```

### Scripts de Ayuda

Ubicados en `/opt/ai-odoo-finder/scripts/`:

| Script | Descripción |
|--------|-------------|
| `start_system.sh` | Iniciar todos los contenedores Docker con verificación de salud |
| `stop_system.sh` | Detener todos los contenedores Docker y limpieza |
| `status_system.sh` | Mostrar estado detallado del sistema |
| `install_service.sh` | Instalar/reinstalar servicio systemd |

### Verificación Manual de Estado

```bash
/opt/ai-odoo-finder/scripts/status_system.sh
```

Muestra: contenedores Docker, salud API, estadísticas DB, uso de disco.

## Operaciones Comunes

### Acceso SSH

```bash
# Via Tailscale (recomendado)
ssh user@<tu-servidor-name>

# O via IP de Tailscale
ssh user@<tailscale-ip>

cd /opt/ai-odoo-finder
```

### Ver Logs

```bash
# Todos los servicios
docker compose logs -f

# Solo API
docker compose logs -f api

# Solo PostgreSQL
docker compose logs -f db
```

### Reiniciar Servicios

```bash
# Reiniciar todo
docker compose restart

# Reiniciar solo API
docker compose restart api

# Reconstrucción completa (después de cambios en código)
git pull
docker compose build --no-cache api
docker compose up -d api
```

### Verificar Estado del Servicio

```bash
docker compose ps
docker compose logs --tail 20
```

### Operaciones de Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it odoofinder-postgres psql -U odoofinder -d ai_odoofinder

# Contar módulos
docker exec odoofinder-postgres psql -U odoofinder -d ai_odoofinder -c "SELECT COUNT(*) FROM odoo_modules;"

# Verificar por versión
docker exec odoofinder-postgres psql -U odoofinder -d ai_odoofinder -c "SELECT version, COUNT(*) FROM odoo_modules GROUP BY version ORDER BY version;"

# Backup de base de datos
docker exec odoofinder-postgres pg_dump -U odoofinder -d ai_odoofinder -F c -f /tmp/backup.dump
docker cp odoofinder-postgres:/tmp/backup.dump ./backup_$(date +%Y%m%d).dump

# Restaurar base de datos
docker cp backup.dump odoofinder-postgres:/tmp/backup.dump
docker exec odoofinder-postgres pg_restore -U odoofinder -d ai_odoofinder --clean /tmp/backup.dump
```

### Probar API

```bash
# Verificación de salud
curl http://localhost:8989/health

# Prueba de búsqueda
curl "http://localhost:8989/search?query=orden%20de%20venta&version=16.0&limit=3"

# Estadísticas
curl http://localhost:8989/stats
```

## Variables de Entorno

Ubicadas en `/opt/ai-odoo-finder/.env`:

```env
# Base de datos
DATABASE_URL=postgresql://odoofinder:<password>@db:5432/ai_odoofinder
POSTGRES_DB=ai_odoofinder
POSTGRES_USER=odoofinder
POSTGRES_PASSWORD=<password>

# APIs externas
OPENROUTER_API_KEY=<key>    # Para generación de embeddings
GH_TOKEN=<token>            # Para API de GitHub (opcional)

# Configuración de la app
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Nota**: El archivo `.env` está en `.gitignore` y nunca debe ser commited.

## Algoritmo de Búsqueda Híbrida

La búsqueda usa **Fusión Recíproca de Ranking (RRF)** combinando:

1. **Búsqueda Vectorial**: Similitud semántica usando Qwen3-Embedding (2560 dimensiones)
2. **Full-Text BM25**: Coincidencia de keywords en technical_name, name, summary, description

```
RRF_score = 1/(k + rank_vector) + 1/(k + rank_bm25)
```

Dónde `k=60` (constante estándar RRF)

## Solución de Problemas

### API no responde

```bash
# Verificar que el contenedor está corriendo
docker compose ps

# Verificar logs por errores
docker compose logs api --tail 50

# Reiniciar API
docker compose restart api
```

### Problemas de conexión a base de datos

```bash
# Verificar que PostgreSQL esté saludable
docker compose ps db
docker exec odoofinder-postgres pg_isready -U odoofinder

# Verificar que la base de datos existe
docker exec odoofinder-postgres psql -U odoofinder -l
```

### Búsqueda devuelve 0 resultados

1. Verificar versión existe: `curl http://localhost:8989/stats`
2. Verificar logs por errores: `docker compose logs api --tail 20`
3. Probar con consulta simple: `curl "http://localhost:8989/search?query=venta&version=16.0&limit=1"`

### Sin espacio en disco

```bash
# Verificar uso de disco
df -h

# Limpiar Docker
docker system prune -a

# Verificar archivos grandes
du -sh /opt/ai-odoo-finder/*
```

## Servidor MCP

El Servidor MCP soporta dos modos de operación:

### Modo Remoto (Docker - para Claude.ai Web, Zed, Cursor)

El servidor MCP corre como un contenedor Docker junto a la API:

```bash
# Desplegar servidor MCP (sin afectar otros servicios)
docker compose build mcp
docker compose up -d mcp

# Verificar estado del servidor MCP
docker compose logs mcp --tail 20

# Probar endpoint MCP
curl -X POST "http://localhost:8080/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

**Configuración de Tailscale Funnel** (exponer MCP en puerto 8080):

```bash
# Añadir puerto 8080 a Tailscale Funnel
tailscale funnel 8080
```

### Modo Local (STDIO - para Claude Desktop)

Para Claude Desktop, ejecuta el servidor MCP localmente:

```bash
cd mcp-server
uv run ai-odoofinder-mcp
```

Configura en Claude Desktop:

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
        "AI_ODOOFINDER_API_URL": "https://<tu-servidor>.ts.net"
      }
    }
  }
}
```

## Historial de Migraciones

| Fecha | Acción | Detalles |
|------|--------|---------|
| 2025-11-29 | Despliegue inicial | Migrado de Neon a auto-hospedado |
| 2025-11-29 | PostgreSQL 16 -> 17 | Actualizado para compatibilidad de dump |
| 2025-11-29 | Migración de datos | 15,884 módulos con embeddings |
| 2025-11-30 | Servicio systemd | Añadido auto-inicio al arranque |
| 2025-11-30 | Removido Render | Consolidado a auto-hospedado Docker |

## Resumen de Costos

| Servicio | Antes | Después |
|---------|--------|-------|
| PostgreSQL Neon | $5/mes | $0 (auto-hospedado) |
| API Render | Tier gratuito (limitado) | $0 (auto-hospedado) |
| VPS Hetzner | Ya owned | Sin costo adicional |
| **Total** | ~$5/mes | **$0/mes** |

---

*Última actualización: 2025-11-30*