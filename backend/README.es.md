# API Backend de AI-OdooFinder

**Idioma**: [English](README.md) | [Español](README.es.md)

Servidor backend basado en FastAPI para búsqueda semántica de módulos de Odoo en el ecosistema OCA.

## Descripción General

El backend proporciona APIs REST y un motor de búsqueda híbrida que potencia el sistema AI-OdooFinder. Indexa más de 16,494 módulos de Odoo de repositorios OCA y permite el descubrimiento inteligente de módulos a través de:

- **Búsqueda Vectorial**: Similitud semántica usando embeddings de Qwen3-Embedding-4B
- **Búsqueda BM25**: Búsqueda tradicional por palabras clave con `tsvector` de PostgreSQL
- **Búsqueda Híbrida**: Combina ambos métodos usando Reciprocal Rank Fusion (RRF)
- **Filtrado por Versión**: Compatible con Odoo 12.0 a 19.0
- **Enriquecimiento con IA**: Descripciones, etiquetas y palabras clave generadas vía Grok-4-fast

## Inicio Rápido

### Requisitos Previos

- Python 3.13+ (mínimo 3.11)
- PostgreSQL 14+ con extensión pgvector
- Gestor de paquetes uv (recomendado) o pip

### Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/SantipBarber/ai-odoo-finder.git
cd ai-odoo-finder/backend
```

2. **Instalar dependencias:**
```bash
# Usando uv (recomendado)
cd ..
uv sync

# O usando pip
pip install -e ".[dev]"
```

3. **Configurar variables de entorno:**
```bash
cp .env.example .env
```

Configura tu archivo `.env`:
```bash
# Base de datos
DATABASE_URL=postgresql+psycopg://usuario:contraseña@localhost:5432/ai_odoo_finder

# APIs
OPENROUTER_API_KEY=tu_clave_openrouter_api
GH_TOKEN=tu_token_github

# Aplicación
ENVIRONMENT=development
LOG_LEVEL=INFO

# Embedding
EMBEDDING_MODEL=qwen/qwen3-embedding-4b
EMBEDDING_DIMENSIONS=2560
```

4. **Configurar PostgreSQL con pgvector:**
```bash
# Iniciar PostgreSQL (si usas Docker)
docker run -d \
  --name postgres-pgvector \
  -e POSTGRES_PASSWORD=contraseña \
  -e POSTGRES_DB=ai_odoo_finder \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Luego crear la base de datos y habilitar pgvector
psql postgresql://usuario:contraseña@localhost:5432/ai_odoo_finder
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

5. **Ejecutar el backend:**
```bash
# Usando uv
cd backend
uv run python -m app.main

# O directamente con Python
python -m app.main

# O con uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8989 --reload
```

La API estará disponible en `http://localhost:8989`

---

## Endpoints de la API

### Raíz y Estado

#### `GET /`
Endpoint raíz con información de la API.

**Respuesta:**
```json
{
  "name": "AI-OdooFinder API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "mcp": {
    "endpoint": "/mcp/",
    "protocol": "HTTP/SSE",
    "tools": ["search_odoo_modules"]
  }
}
```

#### `GET /health`
Verificación de estado - verifica la conectividad con la API y la base de datos.

**Respuesta:**
```json
{
  "status": "healthy",
  "database": "connected",
  "total_modules": 16494
}
```

---

### Búsqueda

#### `GET /search` o `POST /search`
Búsqueda híbrida de módulos de Odoo usando consultas en lenguaje natural.

**Parámetros:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `query` | string | Sí | Consulta de búsqueda en lenguaje natural |
| `version` | string | Sí | Versión de Odoo (12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0) |
| `limit` | integer | No | Máximo de resultados (1-50, predeterminado: 10) |
| `dependencies` | array | No | Filtrar por dependencias de módulos (separadas por comas) |
| `min_score` | integer | No | Umbral de puntuación mínima (0-100, predeterminado: 0) |

**Ejemplo de Solicitud (GET):**
```bash
curl "http://localhost:8989/search?query=suscripciones+de+venta&version=17.0&limit=5"
```

**Ejemplo de Solicitud (POST):**
```bash
curl -X POST "http://localhost:8989/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "generación de facturas",
    "version": "16.0",
    "limit": 10,
    "min_score": 50
  }'
```

**Respuesta:**
```json
{
  "query": "suscripciones de venta",
  "version": "17.0",
  "dependencies": null,
  "total_results": 5,
  "results": [
    {
      "id": 1234,
      "technical_name": "sale_subscription",
      "name": "Suscripción de Ventas",
      "version": "17.0",
      "summary": "Gestionar suscripciones de ventas",
      "description": "Permite crear y gestionar suscripciones...",
      "depends": ["sale"],
      "author": "Odoo S.A.",
      "license": "LGPL-3",
      "repo_name": "sale-workflow",
      "repo_url": "https://github.com/OCA/sale-workflow",
      "module_path": "sale_subscription",
      "github_stars": 245,
      "github_issues_open": 12,
      "last_commit_date": "2024-01-15T10:30:00",
      "score": 89,
      "rrf_score": 0.0185,
      "vector_score": 0.82,
      "bm25_score": 25.5
    }
  ]
}
```

**Campos de Respuesta:**
- `score`: Puntuación combinada (0-100) - normalizada del ranking RRF
- `rrf_score`: Puntuación bruta de Reciprocal Rank Fusion
- `vector_score`: Puntuación de similitud semántica (0-1)
- `bm25_score`: Puntuación de relevancia de búsqueda de texto completo

---

### Detalles del Módulo

#### `GET /modules/{module_id}`
Obtener detalles completos de un módulo específico por ID.

**Parámetros:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `module_id` | integer | Sí | ID de la base de datos del módulo |

**Ejemplo de Solicitud:**
```bash
curl "http://localhost:8989/modules/1234"
```

**Respuesta:**
```json
{
  "id": 1234,
  "technical_name": "sale_subscription",
  "name": "Suscripción de Ventas",
  "version": "17.0",
  "summary": "Gestionar suscripciones de ventas",
  "description": "Permite crear y gestionar suscripciones...",
  "depends": ["sale"],
  "author": "Odoo S.A.",
  "license": "LGPL-3",
  "repo_name": "sale-workflow",
  "repo_url": "https://github.com/OCA/sale-workflow",
  "module_path": "sale_subscription",
  "github_stars": 245,
  "github_issues_open": 12,
  "last_commit_date": "2024-01-15T10:30:00",
  "created_at": "2024-01-10T08:00:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

---

### Estadísticas

#### `GET /stats`
Obtener estadísticas generales de la base de datos.

**Ejemplo de Solicitud:**
```bash
curl "http://localhost:8989/stats"
```

**Respuesta:**
```json
{
  "total_modules": 16494,
  "by_version": {
    "12.0": 1245,
    "13.0": 1389,
    "14.0": 1567,
    "15.0": 1823,
    "16.0": 2156,
    "17.0": 2341,
    "18.0": 2189,
    "19.0": 1794
  },
  "top_repositories": [
    {
      "name": "server-tools",
      "modules": 342
    },
    {
      "name": "web",
      "modules": 289
    },
    {
      "name": "sale-workflow",
      "modules": 267
    }
  ]
}
```

---

## Algoritmo de Búsqueda

La búsqueda híbrida utiliza **Reciprocal Rank Fusion (RRF)** para combinar puntuaciones vectoriales y BM25:

```
RRF_score = 1/(k + rank_vector) + 1/(k + rank_bm25)
```

Donde `k=60` (constante RRF estándar)

### Flujo de Búsqueda

1. **Embedding de Consulta**: Generar vector de 2560 dimensiones usando Qwen3-Embedding-4B
2. **Búsqueda Vectorial**: Índice HNSW de pgvector de PostgreSQL para similitud semántica
3. **Búsqueda BM25**: `tsvector` de PostgreSQL para coincidencia de palabras clave de texto completo
4. **Fusión**: Combinar rankings usando la fórmula RRF
5. **Filtrado**: Aplicar filtros de versión y dependencias
6. **Normalización**: Convertir puntuación RRF a escala 0-100

### Modos de Búsqueda

El servicio de búsqueda soporta tres modos:

- **`hybrid`** (predeterminado): Combina vector + BM25 con RRF
- **`vector`**: Búsqueda semántica únicamente (heredada)
- **`bm25`**: Búsqueda de texto completo únicamente

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Servidor FastAPI                         │
│                     (0.0.0.0:8989)                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Capa de API (main.py)                   │  │
│  │  /search  /modules/{id}  /stats  /health            │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │          Capa de Servicio de Búsqueda               │   │
│  │  - SearchService (orquestación)                     │   │
│  │  - HybridSearchService (fusión RRF)                 │   │
│  │  - EmbeddingService (Qwen3)                         │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │      Capa de Datos (SQLAlchemy ORM)                 │   │
│  │  - Modelo OdooModule                                │   │
│  │  - Gestión de sesiones de base de datos             │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │      PostgreSQL 14+                │
        │  ├─ pgvector (índice vectorial)    │
        │  ├─ tsvector (búsqueda de texto)   │
        │  ├─ pg_trgm (búsqueda similar)     │
        │  └─ Tabla OdooModule               │
        └────────────────────────────────────┘
```

---

## Esquema de Base de Datos

### Tabla `odoo_modules`

```sql
CREATE TABLE odoo_modules (
  -- Información Básica
  id SERIAL PRIMARY KEY,
  technical_name VARCHAR UNIQUE NOT NULL,
  name VARCHAR NOT NULL,
  version VARCHAR NOT NULL,
  
  -- Dependencias
  depends TEXT[] DEFAULT '{}',
  
  -- Metadatos
  author VARCHAR,
  license VARCHAR DEFAULT 'AGPL-3',
  
  -- Contenido
  summary VARCHAR,
  description TEXT,
  readme TEXT,
  
  -- Repositorio
  repo_name VARCHAR NOT NULL,
  repo_url VARCHAR,
  module_path VARCHAR,
  
  -- GitHub
  github_stars INTEGER DEFAULT 0,
  github_issues_open INTEGER DEFAULT 0,
  last_commit_date TIMESTAMP,
  
  -- Índices de Búsqueda
  embedding VECTOR(2560),
  searchable_text TSVECTOR,
  
  -- Enriquecimiento con IA
  ai_description TEXT,
  functional_tags TEXT[],
  keywords TEXT[],
  enriched_at TIMESTAMP,
  enrichment_version VARCHAR(20),
  
  -- Marcas de Tiempo
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_technical_name ON odoo_modules(technical_name);
CREATE INDEX idx_version ON odoo_modules(version);
CREATE INDEX idx_repo_name ON odoo_modules(repo_name);
CREATE INDEX idx_embedding ON odoo_modules USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_searchable_text ON odoo_modules USING GIN (searchable_text);
```

---

## Configuración

### Variables de Entorno

| Variable | Predeterminado | Descripción |
|----------|---------|-------------|
| `DATABASE_URL` | - | Cadena de conexión PostgreSQL (requerida) |
| `OPENROUTER_API_KEY` | - | Clave de API de OpenRouter para enriquecimiento de IA |
| `GH_TOKEN` | - | Token de acceso personal de GitHub |
| `ENVIRONMENT` | `development` | `development`, `staging` o `production` |
| `LOG_LEVEL` | `INFO` | Nivel de logging |
| `EMBEDDING_MODEL` | `qwen/qwen3-embedding-4b` | Identificador del modelo de embedding |
| `EMBEDDING_DIMENSIONS` | `2560` | Dimensiones del vector de embedding |

### Configuración

La configuración se gestiona en `app/config.py` usando Pydantic Settings:

```python
from app.config import get_settings

settings = get_settings()
print(settings.database_url)
print(settings.embedding_model)
```

---

## Desarrollo

### Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación FastAPI y rutas
│   ├── config.py               # Configuración
│   ├── database.py             # Configuración de SQLAlchemy
│   ├── models.py               # Modelos ORM
│   ├── schemas.py              # Esquemas Pydantic
│   ├── mcp_tools.py            # Definiciones de herramientas MCP
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Inyección de dependencias
│   │   └── endpoints/          # Blueprints de rutas de API
│   │
│   ├── services/
│   │   ├── search_service.py           # Orquestación principal de búsqueda
│   │   ├── hybrid_search_service.py    # Lógica de fusión RRF
│   │   ├── embedding_service.py        # Generación de embeddings vectoriales
│   │   ├── scoring_service.py          # Normalización de puntuaciones
│   │   ├── enrichment_service.py       # Enriquecimiento con IA
│   │   ├── github_service.py           # Integración de API de GitHub
│   │   ├── cache_service.py            # Capa de caché
│   │   └── content_extraction_service.py
│   │
│   ├── core/
│   │   ├── logging.py          # Configuración de logging
│   │   └── ...
│   │
│   ├── utils/
│   │   └── ...
│   │
│   ├── metrics/
│   │   └── ...
│
├── migrations/                 # Migraciones de base de datos de Alembic
├── tests/                      # Suite de pruebas
├── pyproject.toml             # Configuración del paquete
└── README.md                  # Este archivo
```

### Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=app

# Ejecutar archivo de prueba específico
pytest tests/test_search.py

# Ejecutar con salida detallada
pytest -v
```

### Calidad del Código

```bash
# Formatear código
black .

# Verificación de tipos
mypy app/

# Linting
ruff check .

# Todas las verificaciones
uv run check  # (si está definido en pyproject.toml)
```

### Servidor de Desarrollo Local

```bash
# Modo desarrollo con recarga automática
uvicorn app.main:app --host 0.0.0.0 --port 8989 --reload

# O usando uv
uv run app.main

# Con nivel de logging específico
LOG_LEVEL=DEBUG uvicorn app.main:app --host 0.0.0.0 --port 8989 --reload
```

### Documentación Interactiva de API

Una vez en ejecución, visita:
- **Swagger UI**: http://localhost:8989/docs
- **ReDoc**: http://localhost:8989/redoc

---

## Solución de Problemas

### Problemas de Conexión a Base de Datos

**Error:** `psycopg.OperationalError: connection failed`

1. **Verificar que PostgreSQL está ejecutándose:**
```bash
psql -U postgres -h localhost -c "SELECT 1;"
```

2. **Verificar el formato de DATABASE_URL:**
```bash
# Formato correcto
postgresql+psycopg://usuario:contraseña@localhost:5432/nombre_base_datos
```

3. **Crear base de datos si falta:**
```bash
createdb -U usuario ai_odoo_finder
psql -U usuario ai_odoo_finder -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### La Generación de Embedding Falla

**Error:** `Failed to generate embedding`

1. **Verificar que el modelo está disponible:**
```bash
# El modelo de embedding debería descargarse automáticamente
# Forzar descarga con:
python -c "from transformers import AutoModel; AutoModel.from_pretrained('Qwen/Qwen3-Embedding-4B')"
```

2. **Verificar disponibilidad de GPU/CPU:**
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

### La Búsqueda No Retorna Resultados

1. **Verificar que los módulos están indexados:**
```bash
curl http://localhost:8989/stats
```

2. **Verificar el filtro de versión:**
```bash
# Asegúrate de que la versión existe (16.0, 17.0, etc.)
curl "http://localhost:8989/search?query=prueba&version=17.0"
```

3. **Reducir el umbral de min_score:**
```bash
curl "http://localhost:8989/search?query=prueba&version=17.0&min_score=0"
```

### Uso Alto de Memoria

El modelo de embedding requiere memoria significativa. Opciones:

1. **Usar CPU en lugar de GPU:**
```bash
export CUDA_VISIBLE_DEVICES=""
```

2. **Usar un modelo más pequeño (modificar config.py):**
```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # ~22M parámetros
```

---

## Optimización del Rendimiento

### Indexación de Base de Datos

Asegúrate de que los índices estén creados:
```bash
# Índice vectorial en embeddings
CREATE INDEX IF NOT EXISTS idx_embedding 
ON odoo_modules USING hnsw (embedding vector_cosine_ops);

# Índice de búsqueda de texto completo en searchable_text
CREATE INDEX IF NOT EXISTS idx_searchable_text 
ON odoo_modules USING GIN (searchable_text);
```

### Caché

El servicio de búsqueda implementa caché para:
- Embeddings (basado en consulta)
- Resultados de búsqueda (TTL basado en tiempo)

Configura vía variables de entorno o `cache_service.py`.

### Agrupación de Conexiones

SQLAlchemy está configurado con agrupación de conexiones:
```python
engine = create_engine(
    database_url,
    pool_pre_ping=True,      # Verificar conexiones antes de usar
    pool_recycle=3600,       # Reciclar conexiones después de 1 hora
)
```

---

## Ejemplos de Integración de API

### Python

```python
import requests

BASE_URL = "http://localhost:8989"

# Búsqueda
response = requests.get(
    f"{BASE_URL}/search",
    params={
        "query": "facturación",
        "version": "17.0",
        "limit": 5
    }
)
results = response.json()
print(f"Se encontraron {results['total_results']} módulos")

# Obtener detalles del módulo
module_response = requests.get(f"{BASE_URL}/modules/1234")
module = module_response.json()
print(f"Módulo: {module['name']}")
```

### JavaScript/Node.js

```javascript
const BASE_URL = "http://localhost:8989";

// Búsqueda
const response = await fetch(
  `${BASE_URL}/search?query=facturación&version=17.0&limit=5`
);
const results = await response.json();
console.log(`Se encontraron ${results.total_results} módulos`);

// Obtener detalles del módulo
const moduleResponse = await fetch(`${BASE_URL}/modules/1234`);
const module = await moduleResponse.json();
console.log(`Módulo: ${module.name}`);
```

### cURL

```bash
# Búsqueda
curl -X GET "http://localhost:8989/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "facturación",
    "version": "17.0",
    "limit": 5
  }'

# Obtener estadísticas
curl http://localhost:8989/stats | jq .

# Verificación de estado
curl http://localhost:8989/health | jq .
```

---

## Despliegue

### Docker

```bash
# Construir imagen
docker build -t ai-odoofinder-backend .

# Ejecutar contenedor
docker run -d \
  --name ai-odoofinder \
  -p 8989:8989 \
  -e DATABASE_URL="postgresql://..." \
  -e OPENROUTER_API_KEY="..." \
  ai-odoofinder-backend
```

### Docker Compose

```bash
# Iniciar todos los servicios (backend + PostgreSQL)
docker-compose up -d

# Ver logs
docker-compose logs -f backend
```

### Despliegue en Producción

Para producción, usa:
- **Servidor ASGI**: Uvicorn con workers de Gunicorn
- **Proxy Inverso**: Nginx para balanceo de carga
- **Base de Datos**: PostgreSQL gestionado (AWS RDS, Azure, etc.)
- **Orquestación de Contenedores**: Kubernetes o similar

Consulta el `docker-compose.yml` del proyecto principal para configuración de producción.

---

## Documentación Relacionada

- [README del Proyecto Principal](../README.md) - Guía de instalación del usuario
- [Servidor MCP](../mcp-server/README.md) - Servidor del protocolo MCP
- [CHANGELOG](../docs/en/CHANGELOG.md) - Historial de versiones
- [Documentación de FastAPI](https://fastapi.tiangolo.com/) - Documentación del framework de API
- [Documentación de SQLAlchemy](https://docs.sqlalchemy.org/) - Documentación del ORM
- [PostgreSQL pgvector](https://github.com/pgvector/pgvector) - Base de datos vectorial

---

## Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Hacer un fork del repositorio
2. Crear una rama de característica
3. Agregar pruebas para la nueva funcionalidad
4. Seguir el estilo de código (Black, Ruff)
5. Enviar una solicitud de extracción

Consulta la [Guía de Contribución](../CONTRIBUTING.md) para más detalles.

---

## Licencia

MIT - Consulta [LICENCIA](../LICENSE)