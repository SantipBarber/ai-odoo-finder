# API Backend de AI-OdooFinder

**Idioma**: [English](README.md) | [Español](README.es.md)

Backend FastAPI para buscar módulos de Odoo con búsqueda híbrida (embeddings vectoriales + búsqueda de texto completo tipo BM25).

> **Solo para despliegues propios.** Esta API REST está pensada para despliegues autoalojados. El servidor público (`https://addon-finder.eticco.es`) solo expone MCP en `/` y `/health`; `/search`, `/stats` y el resto de endpoints REST no son públicos.

## Descripción general

El backend proporciona la API REST y el motor de búsqueda híbrida de AI-OdooFinder. Indexa más de 19.700 módulos de Odoo de los repositorios de OCA y permite descubrir módulos mediante:

- **Búsqueda vectorial**: similitud semántica con embeddings de Qwen3-Embedding-4B (2560 dimensiones), generados a través de la API de OpenRouter
- **Búsqueda de texto completo**: búsqueda por palabras clave con `tsvector` de PostgreSQL (columna `searchable_text`, ordenada con `ts_rank_cd`)
- **Búsqueda híbrida**: combina ambos rankings con Reciprocal Rank Fusion (RRF, `k=60`)
- **Filtrado por versión**: Odoo 12.0 a 19.0
- **Enriquecimiento con IA**: descripciones, etiquetas y palabras clave generadas por Grok-4-fast vía OpenRouter

## Inicio rápido

### Requisitos previos

- Python 3.14+ (el `pyproject.toml` raíz exige `>=3.14`; la imagen Docker usa `python:3.12-slim` con dependencias fijadas)
- PostgreSQL 17 con la extensión pgvector (Docker Compose usa `pgvector/pgvector:pg17`)
- [uv](https://docs.astral.sh/uv/)
- Una clave de API de [OpenRouter](https://openrouter.ai/) (obligatoria: embeddings de las consultas y enriquecimiento)

### Instalación

Todos los comandos se ejecutan desde la **raíz del repositorio**: allí están `pyproject.toml` y `.env.example`, y el backend lee `.env` del directorio de trabajo actual.

1. **Clonar el repositorio:**
```bash
git clone https://github.com/SantipBarber/ai-odoo-finder.git
cd ai-odoo-finder
```

2. **Instalar dependencias:**
```bash
uv sync
```

3. **Configurar las variables de entorno:**
```bash
cp .env.example .env
```

Edita `.env`:
```bash
# Base de datos (misma base de datos y usuario que docker-compose.yml)
DATABASE_URL=postgresql://odoofinder:tu_contraseña@localhost:5432/ai_odoofinder
POSTGRES_DB=ai_odoofinder
POSTGRES_USER=odoofinder
POSTGRES_PASSWORD=tu_contraseña

# APIs
OPENROUTER_API_KEY=tu_clave_de_openrouter   # obligatoria
GH_TOKEN=                                   # debe estar definida; puede ir vacía (solo la usa el ETL)

# Aplicación
ENVIRONMENT=development

# Embedding (opcional, estos son los valores por defecto)
# EMBEDDING_MODEL=qwen/qwen3-embedding-4b
# EMBEDDING_DIMENSIONS=2560
```

Las URL `postgresql://` se convierten automáticamente a `postgresql+psycopg://`.

4. **Arrancar PostgreSQL con pgvector:**
```bash
docker compose up -d db
```

Los ficheros SQL de `backend/migrations/` se montan en `/docker-entrypoint-initdb.d`, así que PostgreSQL los ejecuta automáticamente **solo la primera vez** que se inicializa el volumen de datos. `001_init_extensions.sql` habilita las extensiones `vector` y `pg_trgm`. `001` crea además la tabla `odoo_modules` (igual que `backend/app/models.py`), y `002`–`005` le añaden la búsqueda de texto completo, los campos de enriquecimiento y los índices. Los scripts de rollback están en `backend/migrations/rollback/`, que PostgreSQL ignora durante la inicialización.

5. **Ejecutar el backend:**
```bash
# Con recarga automática
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8989 --reload

# O con el script auxiliar
uv run python scripts/run_server.py
```

La API estará disponible en `http://localhost:8989`.

---

## Endpoints de la API

### Raíz y estado

#### `GET /`
Endpoint raíz con información básica de la API (`name`, `version`, `status`, `docs`).

```json
{
  "name": "AI-OdooFinder API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

#### `GET /health`
Comprobación de estado: verifica la API y la conexión con la base de datos. Devuelve `503` si la base de datos no responde.

**Respuesta:**
```json
{
  "status": "healthy",
  "database": "connected",
  "total_modules": 12345
}
```

---

### Búsqueda

#### `GET /search` o `POST /search`
Búsqueda híbrida de módulos de Odoo con consultas en lenguaje natural. Ambos métodos reciben **solo parámetros en la query string** (el cuerpo JSON no se lee; sin parámetros en la URL la petición devuelve `422`).

**Parámetros:**
| Parámetro | Tipo | Obligatorio | Descripción |
|-----------|------|-------------|-------------|
| `query` | string | Sí | Consulta en lenguaje natural |
| `version` | string | Sí | Versión de Odoo (`12.0` a `19.0`) |
| `dependencies` | string (repetible) | No | Dependencia requerida. Repite el parámetro para indicar varias (`&dependencies=sale&dependencies=stock`); un módulo coincide si depende de **cualquiera** de ellas |
| `limit` | integer | No | Máximo de resultados (1-50, por defecto: 10) |
| `min_score` | integer | No | Puntuación mínima (0-100, por defecto: 0) |

**Ejemplo de petición (GET):**
```bash
curl "http://localhost:8989/search?query=product+recommendation&version=17.0&limit=5"
```

**Ejemplo de petición (POST):**
```bash
curl -X POST "http://localhost:8989/search?query=invoice+generation&version=16.0&limit=10&min_score=50"
```

**Ejemplo con dependencias:**
```bash
curl "http://localhost:8989/search?query=recurring+invoices&version=17.0&dependencies=account&dependencies=sale"
```

**Respuesta:**
```json
{
  "query": "product recommendation",
  "version": "17.0",
  "dependencies": null,
  "total_results": 5,
  "results": [
    {
      "id": 1234,
      "technical_name": "sale_order_product_recommendation",
      "name": "Sale Order Product Recommendation",
      "version": "17.0",
      "summary": "Recommend products to sell to customer based on history",
      "description": "Sale Order Product Recommendation...",
      "depends": ["sale"],
      "author": "Tecnativa, Odoo Community Association (OCA)",
      "license": "AGPL-3",
      "repo_name": "sale-workflow",
      "repo_url": "https://github.com/OCA/sale-workflow",
      "module_path": "sale_order_product_recommendation/__manifest__.py",
      "github_stars": 358,
      "github_issues_open": 12,
      "last_commit_date": "2025-11-06T10:30:00",
      "score": 89,
      "rrf_score": 0.0185,
      "vector_score": 0.82,
      "bm25_score": 0.45
    }
  ]
}
```

(`id`, `github_issues_open`, las puntuaciones y las fechas son ilustrativos.)

**Campos de la respuesta:**
- `score`: puntuación de 0 a 100 derivada de la puntuación RRF (`min(100, rrf_score × 6000)`)
- `rrf_score`: puntuación Reciprocal Rank Fusion sin normalizar
- `vector_score`: similitud coseno (`1 - distancia coseno`); `null` si el módulo solo apareció en la búsqueda de texto completo
- `bm25_score`: relevancia de texto completo (`ts_rank_cd`); `null` si el módulo solo apareció en la búsqueda vectorial
- `description`: truncada a 200 caracteres

---

### Detalle de módulo

#### `GET /modules/{module_id}`
Devuelve todos los datos de un módulo a partir de su ID en la base de datos. Devuelve `404` si no existe.

**Ejemplo de petición:**
```bash
curl "http://localhost:8989/modules/1234"
```

**Respuesta:**
```json
{
  "id": 1234,
  "technical_name": "sale_order_product_recommendation",
  "name": "Sale Order Product Recommendation",
  "version": "17.0",
  "summary": "Recommend products to sell to customer based on history",
  "description": "Sale Order Product Recommendation...",
  "depends": ["sale"],
  "author": "Tecnativa, Odoo Community Association (OCA)",
  "license": "AGPL-3",
  "repo_name": "sale-workflow",
  "repo_url": "https://github.com/OCA/sale-workflow",
  "module_path": "sale_order_product_recommendation/__manifest__.py",
  "github_stars": 358,
  "github_issues_open": 12,
  "last_commit_date": "2025-11-06T10:30:00",
  "created_at": "2025-11-20T08:00:00",
  "updated_at": "2025-11-25T10:30:00"
}
```

---

### Estadísticas

#### `GET /stats`
Estadísticas generales de la base de datos: total de módulos, módulos por versión y los 10 repositorios con más módulos.

**Ejemplo de petición:**
```bash
curl "http://localhost:8989/stats"
```

**Ejemplo (valores ilustrativos):**
```json
{
  "total_modules": 12000,
  "by_version": {
    "14.0": 2600,
    "15.0": 1900,
    "16.0": 2700,
    "17.0": 2300,
    "18.0": 2100,
    "19.0": 400
  },
  "top_repositories": [
    {
      "name": "l10n-spain",
      "modules": 950
    },
    {
      "name": "server-tools",
      "modules": 610
    },
    {
      "name": "sale-workflow",
      "modules": 580
    }
  ]
}
```

---

## Algoritmo de búsqueda

La búsqueda híbrida usa **Reciprocal Rank Fusion (RRF)** para combinar el ranking vectorial y el de texto completo:

```
RRF_score = 1/(k + rank_vector) + 1/(k + rank_bm25)
```

Donde `k=60` (constante estándar de RRF). Un módulo encontrado por un solo método solo suma ese término.

### Flujo de búsqueda

1. **Embedding de la consulta**: se genera un vector de 2560 dimensiones con `qwen/qwen3-embedding-4b` a través de la API de OpenRouter
2. **Búsqueda vectorial**: recorrido exacto por distancia coseno con pgvector (operador `<=>`), filtrado por versión (y dependencias), 50 mejores candidatos. No hay índice vectorial: pgvector no puede indexar columnas `vector` de 2560 dimensiones
3. **Búsqueda de texto completo**: `plainto_tsquery('english', …)` sobre `searchable_text`, ordenada con `ts_rank_cd`, 50 mejores candidatos
4. **Fusión**: se combinan ambos rankings con RRF y se conservan los `limit` primeros
5. **Normalización**: la puntuación RRF se convierte en `score` de 0 a 100 y se aplica `min_score`

La columna `searchable_text` la mantiene un trigger de base de datos que pondera `technical_name`/`name` (A), `summary`/`ai_description`/`keywords`/`repo_name` (B), `description`/`functional_tags` (C) y `readme` (D).

> `SearchService` tiene además los modos internos `vector` y `bm25` (los usan los scripts de benchmark). No se exponen a través de la API REST, que siempre usa `hybrid`.

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Servidor FastAPI                         │
│                    (0.0.0.0:8989)                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Capa de API (main.py)                   │   │
│  │  /search  /modules/{id}  /stats  /health             │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │          Capa de servicios de búsqueda               │   │
│  │  - SearchService (orquestación)                      │   │
│  │  - HybridSearchService (fusión RRF)                  │   │
│  │  - EmbeddingService (Qwen3 vía OpenRouter)           │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │      Capa de datos (ORM SQLAlchemy)                  │   │
│  │  - Modelo OdooModule                                 │   │
│  │  - Gestión de sesiones de base de datos              │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │      PostgreSQL 17                 │
        │  ├─ pgvector (coseno exacto)       │
        │  ├─ tsvector + GIN (texto completo)│
        │  ├─ pg_trgm (extensión habilitada) │
        │  └─ tabla odoo_modules             │
        └────────────────────────────────────┘
```

---

## Esquema de base de datos

### Tabla `odoo_modules`

La crea el modelo ORM (`backend/app/models.py`) y la amplían las migraciones SQL de `backend/migrations/`.

```sql
CREATE TABLE odoo_modules (
  -- Información básica
  id SERIAL PRIMARY KEY,
  technical_name VARCHAR NOT NULL,   -- no es única: una fila por módulo y versión
  name VARCHAR NOT NULL,
  version VARCHAR NOT NULL,

  -- Dependencias
  depends VARCHAR[],

  -- Metadatos
  author VARCHAR,
  license VARCHAR,                   -- valor por defecto en el ORM: 'AGPL-3'

  -- Contenido
  summary VARCHAR,
  description TEXT,
  readme TEXT,

  -- Repositorio
  repo_name VARCHAR NOT NULL,
  repo_url VARCHAR,
  module_path VARCHAR,

  -- GitHub
  github_stars INTEGER,
  github_issues_open INTEGER,
  last_commit_date TIMESTAMP,

  -- Búsqueda
  embedding VECTOR(2560),
  searchable_text TSVECTOR,          -- migración 002, mantenida por trigger

  -- Enriquecimiento con IA (migración 003)
  ai_description TEXT,
  functional_tags TEXT[],
  keywords TEXT[],
  enriched_at TIMESTAMP,
  enrichment_version VARCHAR(20),

  -- Contenido limpio (migración 005, no mapeado en models.py)
  description_clean TEXT,
  content_source VARCHAR(50),
  content_extracted_at TIMESTAMP,

  -- Marcas de tiempo
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**Índices:**

| Índice | Definición | Origen |
|--------|------------|--------|
| `ix_odoo_modules_id` | `id` | ORM (`index=True`) |
| `ix_odoo_modules_technical_name` | `technical_name` | ORM (`index=True`) |
| `ix_odoo_modules_version` | `version` | ORM (`index=True`) |
| `idx_modules_fulltext` | GIN (`searchable_text`) | Migración 002 |
| `idx_modules_needs_enrichment` | `enriched_at` WHERE `enriched_at IS NULL` | Migración 003 |
| `idx_modules_functional_tags` | GIN (`functional_tags`) | Migración 003 |
| `idx_modules_keywords` | GIN (`keywords`) | Migración 003 |
| `idx_modules_needs_content_extraction` | `content_extracted_at` WHERE `content_extracted_at IS NULL` | Migración 005 |
| `idx_modules_content_source` | `content_source` | Migración 005 |

No hay índice vectorial sobre `embedding` (ver [Flujo de búsqueda](#flujo-de-búsqueda)).

---

## Configuración

### Variables de entorno

Las lee `backend/app/config.py` (Pydantic Settings) del entorno o de un fichero `.env` en el directorio de trabajo actual.

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `DATABASE_URL` | - | Cadena de conexión a PostgreSQL (**obligatoria**) |
| `OPENROUTER_API_KEY` | - | Clave de API de OpenRouter (**obligatoria**): embeddings de las consultas y enriquecimiento con IA |
| `GH_TOKEN` | - | Token de GitHub que usa el ETL. **Debe estar definida** (no tiene valor por defecto), pero puede ir vacía |
| `ENVIRONMENT` | `development` | Etiqueta libre del entorno |
| `LOG_LEVEL` | `INFO` | Nivel de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `EMBEDDING_MODEL` | `qwen/qwen3-embedding-4b` | Opcional. Modelo de embeddings en OpenRouter |
| `EMBEDDING_DIMENSIONS` | `2560` | Opcional. Debe coincidir con la columna `VECTOR(2560)` |

El nivel de log está fijado en `INFO` en `main.py`.

### Ajustes

```python
from backend.app.config import get_settings

settings = get_settings()
print(settings.database_url)
print(settings.embedding_model)
```

---

## Desarrollo

### Estructura del proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación FastAPI y rutas
│   ├── config.py               # Configuración
│   ├── database.py             # Configuración de SQLAlchemy
│   ├── models.py               # Modelos ORM
│   ├── schemas.py              # Esquemas Pydantic
│   ├── mcp_tools.py            # Herramientas MCP heredadas, no se importan (el servidor MCP está en mcp-server/)
│   │
│   ├── api/
│   │   ├── deps.py             # Inyección de dependencias
│   │   └── endpoints/          # No montados: las rutas se definen en main.py
│   │
│   ├── services/
│   │   ├── search_service.py           # Orquestación de la búsqueda
│   │   ├── hybrid_search_service.py    # Consultas vectorial y de texto completo, fusión RRF
│   │   ├── embedding_service.py        # Embeddings vía OpenRouter
│   │   ├── scoring_service.py          # Esqueleto, no lo usa la búsqueda
│   │   ├── enrichment_service.py       # Enriquecimiento con IA (Grok-4-fast vía OpenRouter)
│   │   ├── github_service.py           # Integración con la API de GitHub
│   │   ├── cache_service.py            # No lo usa la búsqueda
│   │   └── content_extraction_service.py
│   │
│   ├── core/                   # Logging, excepciones, seguridad
│   ├── utils/                  # Utilidades, parsers, validadores
│   └── metrics/                # Métricas de benchmark
│
├── migrations/                 # Migraciones SQL planas (001–005)
├── tests/                      # unit/, integration/, e2e/ y tests de aceptación
├── README.md
└── README.es.md
```

El `pyproject.toml` del proyecto está en la raíz del repositorio. Hay más tests en el directorio `tests/` de la raíz.

### Ejecutar los tests

`pytest` no está declarado como dependencia, así que se añade al vuelo. La mayoría de los tests necesitan una base de datos con datos y una `OPENROUTER_API_KEY` válida.

```bash
# Todos los tests
uv run --with pytest pytest backend/tests tests

# Solo tests unitarios
uv run --with pytest pytest backend/tests/unit -v
```

### Calidad de código

Ruff y Black están configurados en el `pyproject.toml` raíz:

```bash
uvx ruff check .
uvx black --check .
```

### Documentación interactiva de la API

Con el servidor en marcha, visita:
- **Swagger UI**: http://localhost:8989/docs
- **ReDoc**: http://localhost:8989/redoc

---

## Solución de problemas

### El arranque falla con un error de validación

`DATABASE_URL`, `OPENROUTER_API_KEY` y `GH_TOKEN` deben estar definidas (en `.env` o en el entorno). `GH_TOKEN` puede ir vacía. Arranca el servidor desde la raíz del repositorio para que encuentre `.env`.

### Problemas de conexión con la base de datos

**Error:** `psycopg.OperationalError: connection failed`

1. **Comprueba que PostgreSQL está en marcha:**
```bash
docker compose ps db
psql "postgresql://odoofinder:tu_contraseña@localhost:5432/ai_odoofinder" -c "SELECT 1;"
```

2. **Revisa el formato de `DATABASE_URL`:**
```bash
postgresql://usuario:contraseña@host:5432/nombre_base_datos
```

3. **Comprueba las extensiones:**
```bash
psql "postgresql://odoofinder:tu_contraseña@localhost:5432/ai_odoofinder" -c "\dx"
```

### La búsqueda no devuelve resultados o da errores

Los embeddings de las consultas se obtienen de la API de OpenRouter. Si falla su generación, la búsqueda registra `Error generating embedding` y devuelve una lista vacía.

1. **Comprueba que `OPENROUTER_API_KEY`** es válida y la cuenta tiene saldo.
2. **Verifica que hay módulos indexados:**
```bash
curl http://localhost:8989/stats
```
3. **Comprueba la versión**: debe tener módulos (`by_version` en `/stats`) y estar entre `12.0` y `19.0`.

---

## Notas de rendimiento

### Búsqueda vectorial

La búsqueda vectorial es un recorrido exacto por distancia coseno (`ORDER BY embedding <=> consulta`), filtrado antes por `version` (indexada). pgvector no puede indexar columnas `vector` de 2560 dimensiones, así que no hay índice vectorial aproximado.

### Búsqueda de texto completo

`searchable_text` está indexada con GIN (`idx_modules_fulltext`).

### Caché

Actualmente no hay caché: cada búsqueda llama a OpenRouter para obtener el embedding de la consulta y ejecuta ambas consultas. `cache_service.py` existe, pero la búsqueda no lo usa.

### Pool de conexiones

SQLAlchemy está configurado con pool de conexiones:
```python
engine = create_engine(
    database_url,
    pool_pre_ping=True,      # Verifica las conexiones antes de usarlas
    pool_recycle=3600,       # Recicla las conexiones cada hora
)
```

---

## Ejemplos de integración con la API

### Python

```python
import requests

BASE_URL = "http://localhost:8989"

# Búsqueda
response = requests.get(
    f"{BASE_URL}/search",
    params={
        "query": "invoicing",
        "version": "17.0",
        "dependencies": ["account", "sale"],  # se envían como parámetros repetidos
        "limit": 5,
    },
)
results = response.json()
print(f"Encontrados {results['total_results']} módulos")

# Detalle de un módulo
module_response = requests.get(f"{BASE_URL}/modules/1234")
module = module_response.json()
print(f"Módulo: {module['name']}")
```

### JavaScript/Node.js

```javascript
const BASE_URL = "http://localhost:8989";

// Búsqueda
const response = await fetch(
  `${BASE_URL}/search?query=invoicing&version=17.0&limit=5`
);
const results = await response.json();
console.log(`Encontrados ${results.total_results} módulos`);

// Detalle de un módulo
const moduleResponse = await fetch(`${BASE_URL}/modules/1234`);
const module = await moduleResponse.json();
console.log(`Módulo: ${module.name}`);
```

### cURL

```bash
# Búsqueda
curl "http://localhost:8989/search?query=invoicing&version=17.0&limit=5"

# Estadísticas
curl http://localhost:8989/stats | jq .

# Comprobación de estado
curl http://localhost:8989/health | jq .
```

---

## Despliegue

### Docker

El `Dockerfile` del backend está en la raíz del repositorio (contexto de build: la raíz):

```bash
# Construir la imagen (desde la raíz del repositorio)
docker build -t ai-odoofinder-api .

# Ejecutar el contenedor
docker run -d \
  --name ai-odoofinder-api \
  -p 8989:8989 \
  -e DATABASE_URL="postgresql://odoofinder:tu_contraseña@host-bd:5432/ai_odoofinder" \
  -e OPENROUTER_API_KEY="..." \
  -e GH_TOKEN="" \
  ai-odoofinder-api
```

### Docker Compose

`docker-compose.yml` (raíz del repositorio) define tres servicios:

| Servicio | Imagen / build | Puerto | Notas |
|----------|----------------|--------|-------|
| `db` | `pgvector/pgvector:pg17` | 5432 | Ejecuta `backend/migrations/*.sql` en la primera inicialización |
| `api` | `Dockerfile` (raíz) | 8989 | Este backend |
| `mcp` | `mcp-server/Dockerfile` | 8080 | Servidor MCP en modo HTTP (`MCP_PATH=/`), llama a `http://api:8989` |

```bash
# Arrancar todos los servicios
docker compose up -d

# Ver los logs de la API
docker compose logs -f api
```

`POSTGRES_PASSWORD` y `OPENROUTER_API_KEY` deben estar definidas en `.env`. Consulta [Despliegue y operaciones](../docs/es/DEPLOYMENT_OPERATIONS.md) para la guía completa.

---

## Documentación relacionada

- [README principal del proyecto](../README.es.md) - Guía de instalación para usuarios
- [Servidor MCP](../mcp-server/README.es.md) - Servidor del protocolo MCP
- [Despliegue y operaciones](../docs/es/DEPLOYMENT_OPERATIONS.md) - Guía de despliegue
- [Registro de cambios](../docs/es/CHANGELOG.md) - Historial de versiones
- [Documentación de FastAPI](https://fastapi.tiangolo.com/) - Framework de la API
- [Documentación de SQLAlchemy](https://docs.sqlalchemy.org/) - ORM
- [PostgreSQL pgvector](https://github.com/pgvector/pgvector) - Extensión de similitud vectorial

---

## Contribuir

Las contribuciones son bienvenidas:

1. Haz un fork del repositorio
2. Crea una rama para tu cambio
3. Añade tests para la nueva funcionalidad
4. Sigue el estilo de código (Ruff, Black)
5. Abre una pull request

---

## Licencia

MIT - Ver [LICENSE](../LICENSE)
