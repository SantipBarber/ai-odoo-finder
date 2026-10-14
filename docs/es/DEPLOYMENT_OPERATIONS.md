# Guía de despliegue y operaciones de AI-OdooFinder

**Idioma**: [English](../en/DEPLOYMENT_OPERATIONS.md) | [Español](../es/DEPLOYMENT_OPERATIONS.md)

> **Nota:** La instancia pública de AI-OdooFinder se ejecuta en la infraestructura de [Eticco](https://www.eticco.es) en **`https://addon-finder.eticco.es`** (endpoint MCP en la URL raíz). No necesitas desplegar nada para usarla. Esta guía documenta el **despliegue Docker autoalojado de referencia**, para ejecutar tu propia instancia.

## Resumen de la arquitectura

Un único VPS ejecuta los tres servicios definidos en `docker-compose.yml`. Un proxy inverso situado delante termina TLS y reenvía el tráfico al servidor MCP.

```
                 +------------------+
                 | Cliente MCP (IA) |
                 +--------+---------+
                          |
                          | HTTPS
                          v
+--------------------------------------------------+
|                   VPS (Docker)                   |
|                                                  |
|   +------------------------------------------+   |
|   |          Proxy inverso (TLS)             |   |
|   +--------------------+---------------------+   |
|                        |                         |
|                        v                         |
|   +------------------------------------------+   |
|   |  mcp   :8080   (endpoint MCP en ruta /)  |   |
|   +--------------------+---------------------+   |
|                        |                         |
|                        v                         |
|   +------------------------------------------+   |
|   |  api   :8989   (REST con FastAPI)        |   |
|   +--------------------+---------------------+   |
|                        |                         |
|                        v                         |
|   +------------------------------------------+   |
|   |  db    :5432   (PostgreSQL 17 + pgvector)|   |
|   +------------------------------------------+   |
|                                                  |
+--------------------------------------------------+
```

Solo el servidor MCP necesita ser accesible desde internet. La API REST (`:8989`) la usa internamente el servidor MCP; exponla únicamente si quieres usar el [paquete STDIO local](#modo-local-stdio) desde otras máquinas.

## Información del servidor

| Elemento | Valor |
|----------|-------|
| **URL pública** | `https://<tu-dominio>` |
| **Proveedor** | Cualquier VPS |
| **Arquitectura** | ARM64 o x86_64 |
| **Sistema operativo** | Ubuntu 22.04+ LTS |
| **Recursos** | Un VPS pequeño (~2 GB de RAM) es suficiente para la API y PostgreSQL |
| **Ruta del proyecto** | `/opt/ai-odoo-finder` (los scripts auxiliares y la unidad systemd asumen esta ruta) |

## Servicios

### Contenedores Docker

| Servicio | Contenedor | Imagen | Puerto | Propósito |
|----------|------------|--------|--------|-----------|
| `db` | `odoofinder-postgres` | `pgvector/pgvector:pg17` | 5432 | PostgreSQL 17 + pgvector |
| `api` | `odoofinder-api` | Construida desde `Dockerfile` | 8989 | Backend FastAPI (API REST) |
| `mcp` | `odoofinder-mcp` | Construida desde `mcp-server/Dockerfile` | 8080 | Servidor MCP (Streamable HTTP) |

El endpoint MCP es la ruta raíz (`MCP_PATH=/`, el valor por defecto tanto en `mcp-server/Dockerfile` como en `docker-compose.yml`).

### Endpoints de la API (FastAPI - :8989)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información de la API |
| `/health` | GET | Comprobación de estado (conexión a la base de datos y número de módulos) |
| `/search` | GET, POST | Búsqueda híbrida (vectorial + BM25 + RRF) |
| `/modules/{id}` | GET | Obtener un módulo por ID |
| `/stats` | GET | Estadísticas de la base de datos (módulos por versión) |
| `/docs` | GET | Swagger UI |

### Endpoint MCP (servidor MCP - :8080)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | POST, GET | Endpoint MCP (Streamable HTTP) |
| `/health` | GET | Comprobación de vida, usada por el healthcheck de Docker |

### Parámetros de búsqueda

Tanto `GET` como `POST` reciben los parámetros en la query string:

```
GET /search?query=<texto>&version=<versión>&limit=<n>&dependencies=<dep1>&dependencies=<dep2>
```

| Parámetro | Obligatorio | Ejemplo | Descripción |
|-----------|-------------|---------|-------------|
| `query` | Sí | `sale order` | Texto de búsqueda (lenguaje natural) |
| `version` | Sí | `16.0` | Versión de Odoo: de `12.0` a `19.0` |
| `limit` | No | `10` | Máximo de resultados, 1–50 (por defecto: 10) |
| `min_score` | No | `30` | Puntuación mínima, 0–100 (por defecto: 0) |
| `dependencies` | No | `dependencies=sale&dependencies=stock` | Repite el parámetro por cada dependencia; devuelve los módulos que dependen de **cualquiera** de ellas |

## Estadísticas de la base de datos

El número de módulos indexados cambia con cada ejecución del ETL. Consúltalo en tu instancia:

```bash
curl http://localhost:8989/stats
```

## Servicio systemd (arranque automático)

`scripts/ai-odoo-finder.service` define una unidad systemd que arranca el stack Docker al iniciar el sistema. Instálala con `scripts/install_service.sh`.

### Comandos del servicio

```bash
# Ver estado
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

# Ver las últimas 50 líneas
journalctl -u ai-odoo-finder -n 50
```

### Scripts auxiliares

Ubicados en `/opt/ai-odoo-finder/scripts/`:

| Script | Descripción |
|--------|-------------|
| `start_system.sh` | Inicia todos los servicios Docker con comprobación de estado |
| `stop_system.sh` | Detiene todos los servicios Docker y limpia |
| `status_system.sh` | Muestra el estado detallado del sistema |
| `install_service.sh` | Instala o reinstala el servicio systemd |

### Comprobación manual del estado

```bash
/opt/ai-odoo-finder/scripts/status_system.sh
```

Muestra: contenedores Docker, estado de la API, estadísticas de la base de datos y uso de disco.

## Operaciones comunes

### Acceso SSH

```bash
ssh user@<tu-servidor>
cd /opt/ai-odoo-finder
```

### Ver logs

```bash
# Todos los servicios
docker compose logs -f

# Solo la API
docker compose logs -f api

# Solo el servidor MCP
docker compose logs -f mcp

# Solo PostgreSQL
docker compose logs -f db
```

### Reiniciar servicios

```bash
# Reiniciar todo
docker compose restart

# Reiniciar solo la API
docker compose restart api

# Reconstrucción completa (tras cambios de código)
git pull
docker compose build --no-cache api mcp
docker compose up -d api mcp
```

### Comprobar el estado de los servicios

```bash
docker compose ps
docker compose logs --tail 20
```

### Operaciones de base de datos

```bash
# Conectar a PostgreSQL
docker exec -it odoofinder-postgres psql -U odoofinder -d ai_odoofinder

# Contar módulos
docker exec odoofinder-postgres psql -U odoofinder -d ai_odoofinder -c "SELECT COUNT(*) FROM odoo_modules;"

# Contar por versión
docker exec odoofinder-postgres psql -U odoofinder -d ai_odoofinder -c "SELECT version, COUNT(*) FROM odoo_modules GROUP BY version ORDER BY version;"

# Copia de seguridad de la base de datos
docker exec odoofinder-postgres pg_dump -U odoofinder -d ai_odoofinder -F c -f /tmp/backup.dump
docker cp odoofinder-postgres:/tmp/backup.dump ./backup_$(date +%Y%m%d).dump

# Restaurar la base de datos
docker cp backup.dump odoofinder-postgres:/tmp/backup.dump
docker exec odoofinder-postgres pg_restore -U odoofinder -d ai_odoofinder --clean /tmp/backup.dump
```

### Probar la API

```bash
# Comprobación de estado
curl http://localhost:8989/health

# Prueba de búsqueda
curl "http://localhost:8989/search?query=sale%20order&version=16.0&limit=3"

# Búsqueda con dependencias
curl "http://localhost:8989/search?query=delivery&version=17.0&dependencies=sale&dependencies=stock"

# Estadísticas
curl http://localhost:8989/stats
```

## Variables de entorno

Ubicadas en `/opt/ai-odoo-finder/.env` (copia `.env.example`):

```env
# Base de datos
DATABASE_URL=postgresql://odoofinder:<password>@localhost:5432/ai_odoofinder
POSTGRES_DB=ai_odoofinder
POSTGRES_USER=odoofinder
POSTGRES_PASSWORD=<password>

# APIs externas
OPENROUTER_API_KEY=<key>    # Embeddings + enriquecimiento con IA (obligatoria)
GH_TOKEN=<token>            # API de GitHub para el ETL (debe existir, puede estar vacía)

# Configuración de la aplicación
ENVIRONMENT=production
LOG_LEVEL=INFO
```

- **`DATABASE_URL`**: Docker Compose establece su propio valor para el contenedor `api` (`postgresql+psycopg://...@db:5432/...`) a partir de las variables `POSTGRES_*`. El valor de `.env` solo lo usan los scripts que se ejecutan en el host (como el ETL), por eso apunta a `localhost:5432`.
- **`GH_TOKEN`**: la configuración del backend la declara sin valor por defecto, así que la variable debe estar definida aunque esté vacía. Un token permite límites de peticiones más altos en la API de GitHub durante el ETL.

**Nota**: El archivo `.env` está en `.gitignore` y nunca debe subirse al repositorio.

## Algoritmo de búsqueda híbrida

La búsqueda usa **Reciprocal Rank Fusion (RRF)** combinando:

1. **Búsqueda vectorial**: similitud semántica con embeddings `qwen/qwen3-embedding-4b` (2560 dimensiones, vía OpenRouter), calculada como distancia coseno exacta en pgvector
2. **Texto completo tipo BM25**: ranking de texto completo de PostgreSQL sobre el nombre técnico, el nombre, el resumen, el nombre del repositorio, la descripción generada por IA, las palabras clave y etiquetas, la descripción y el README del módulo (los campos de nombre tienen el mayor peso y el README el menor)

```
RRF_score = 1/(k + rank_vector) + 1/(k + rank_bm25)
```

Donde `k=60` (constante estándar de RRF).

## Solución de problemas

### La API no responde

```bash
# Comprobar si el contenedor está en ejecución
docker compose ps

# Revisar los logs en busca de errores
docker compose logs api --tail 50

# Reiniciar la API
docker compose restart api
```

### Problemas de conexión a la base de datos

```bash
# Comprobar que PostgreSQL está sano
docker compose ps db
docker exec odoofinder-postgres pg_isready -U odoofinder

# Comprobar que la base de datos existe
docker exec odoofinder-postgres psql -U odoofinder -l
```

### La búsqueda devuelve 0 resultados

1. Verificar que la versión existe: `curl http://localhost:8989/stats`
2. Revisar los logs en busca de errores: `docker compose logs api --tail 20`
3. Probar con una consulta sencilla: `curl "http://localhost:8989/search?query=sale&version=16.0&limit=1"`

### Sin espacio en disco

```bash
# Ver uso de disco
df -h

# Limpiar Docker
docker system prune -a

# Buscar archivos grandes
du -sh /opt/ai-odoo-finder/*
```

## Servidor MCP

El servidor MCP admite dos modos de funcionamiento.

### Modo remoto (Docker)

Para Claude.ai, Claude Code, Cursor, Zed y otros clientes con soporte MCP remoto. El servidor MCP se ejecuta como contenedor Docker junto a la API:

```bash
# Desplegar el servidor MCP (sin afectar a otros servicios)
docker compose build mcp
docker compose up -d mcp

# Ver los logs del servidor MCP
docker compose logs mcp --tail 20

# Probar el endpoint MCP
curl -X POST "http://localhost:8080/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

**Exposición:** expón el puerto 8080 a través de tu proxy inverso (TLS) en la ruta raíz, para que los clientes se conecten a `https://<tu-dominio>`. Sirve cualquier proxy inverso (Caddy, nginx, Traefik...); un túnel como Tailscale Funnel es otra opción.

### Modo local (STDIO)

Para clientes que ejecutan el servidor MCP como proceso local. Instala el paquete [`ai-odoofinder-mcp`](https://pypi.org/project/ai-odoofinder-mcp/) de PyPI y apúntalo a tu API. Requiere que el puerto de la API (8989) sea accesible desde la máquina del cliente.

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uvx",
      "args": ["ai-odoofinder-mcp"],
      "env": {
        "AI_ODOOFINDER_API_URL": "http://<tu-servidor>:8989"
      }
    }
  }
}
```

Ubicación del archivo de configuración de Claude Desktop:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

Para otros clientes, consulta [Configuraciones de clientes MCP](MCP_CLIENT_CONFIGURATIONS.md).

## ETL programado

El proceso ETL se ejecuta en el servidor mediante cron para mantener actualizado el índice de módulos. Se ejecuta desde el proyecto raíz, que requiere **Python 3.14** (gestionado con `uv`).

### Configuración de cron

Para ejecutar el ETL a diario a las 3:00:

```bash
# Editar crontab
crontab -e

# Añadir esta línea:
0 3 * * * /opt/ai-odoo-finder/scripts/cron_etl.sh >> /var/log/ai-odoofinder-etl.log 2>&1
```

### Ejecución manual

```bash
# Ejecutar el ETL manualmente
/opt/ai-odoo-finder/scripts/cron_etl.sh

# O directamente con uv
cd /opt/ai-odoo-finder
uv run python scripts/etl_oca_modules.py
```

### Contar módulos sin indexar

`scripts/count_oca_modules.py` recorre los repos de la OCA con las mismas funciones de descubrimiento que el ETL y cuenta los módulos por versión. No toca la base de datos ni OpenRouter; solo necesita `GH_TOKEN`. Tarda un par de minutos.

```bash
uv run python scripts/count_oca_modules.py
# Comparar con lo indexado y guardar el detalle por repo
uv run python scripts/count_oca_modules.py --stats-url http://localhost:8989/stats --output conteo.json
```

Cuenta lo que existe hoy en GitHub, no lo indexado: si el índice conserva ramas o módulos que ya no están, las cifras no coincidirán.

### Logs del ETL

```bash
# Ver los logs del ETL
tail -f /var/log/ai-odoofinder-etl.log

# Ver las últimas 100 líneas
tail -100 /var/log/ai-odoofinder-etl.log
```

### Características del ETL

- **Actualizaciones incrementales**: solo procesa módulos nuevos o modificados
- **Puntos de control**: se puede interrumpir y reanudar
- **Enriquecimiento con IA**: genera descripciones, etiquetas y palabras clave con `x-ai/grok-4-fast` (vía OpenRouter)
- **Embeddings**: crea vectores con `qwen/qwen3-embedding-4b` (vía OpenRouter)

---

## Historial de migraciones

| Fecha | Acción | Detalles |
|-------|--------|----------|
| 2025-11-29 | Despliegue inicial | Migrado de Neon a autoalojado |
| 2025-11-29 | PostgreSQL 16 -> 17 | Actualizado por compatibilidad del dump |
| 2025-11-29 | Migración de datos | 15.884 módulos con embeddings |
| 2025-11-30 | Servicio systemd | Añadido arranque automático al iniciar |
| 2025-11-30 | Eliminado Render | Consolidado en Docker autoalojado |
| 2026-10 | Instancia pública trasladada a la infraestructura de Eticco | `https://addon-finder.eticco.es` |

## Resumen de costes (histórico, despliegue personal)

| Servicio | Antes | Después |
|----------|-------|---------|
| PostgreSQL en Neon | 5 $/mes | 0 $ (autoalojado) |
| API en Render | Plan gratuito (limitado) | 0 $ (autoalojado) |
| VPS de Hetzner | Ya contratado | Sin coste adicional |
| **Total** | ~5 $/mes | **0 $/mes** |

---

*Última actualización: 2026-10-14*
