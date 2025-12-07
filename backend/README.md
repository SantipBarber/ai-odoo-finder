# AI-OdooFinder Backend API

**Language**: [English](README.md) | [Español](README.es.md)

FastAPI-based backend server for semantic search of Odoo modules using hybrid search (vector embeddings + BM25 full-text search).

## Overview

The backend provides REST APIs and a hybrid search engine that powers the AI-OdooFinder system. It indexes over 16,494 Odoo modules from OCA repositories and enables intelligent module discovery through:

- **Vector Search**: Semantic similarity using Qwen3-Embedding-4B embeddings
- **BM25 Full-Text Search**: Traditional keyword-based search with PostgreSQL `tsvector`
- **Hybrid Search**: Combines both methods using Reciprocal Rank Fusion (RRF)
- **Version Filtering**: Support for Odoo 12.0 through 19.0
- **AI Enrichment**: Generated descriptions, tags, and keywords via Grok-4-fast

## Quick Start

### Prerequisites

- Python 3.13+ (3.11+ minimum)
- PostgreSQL 14+ with pgvector extension
- uv package manager (recommended) or pip

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/SantipBarber/ai-odoo-finder.git
cd ai-odoo-finder/backend
```

2. **Install dependencies:**
```bash
# Using uv (recommended)
cd ..
uv sync

# Or using pip
pip install -e ".[dev]"
```

3. **Setup environment variables:**
```bash
cp .env.example .env
```

Configure your `.env` file:
```bash
# Database
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/ai_odoo_finder

# APIs
OPENROUTER_API_KEY=your_openrouter_api_key
GH_TOKEN=your_github_token

# App
ENVIRONMENT=development
LOG_LEVEL=INFO

# Embedding
EMBEDDING_MODEL=qwen/qwen3-embedding-4b
EMBEDDING_DIMENSIONS=2560
```

4. **Setup PostgreSQL with pgvector:**
```bash
# Start PostgreSQL (if using Docker)
docker run -d \
  --name postgres-pgvector \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=ai_odoo_finder \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Then create the database and enable pgvector
psql postgresql://user:password@localhost:5432/ai_odoo_finder
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

5. **Run the backend:**
```bash
# Using uv
cd backend
uv run python -m app.main

# Or directly with Python
python -m app.main

# Or with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8989 --reload
```

The API will be available at `http://localhost:8989`

---

## API Endpoints

### Root & Health

#### `GET /`
Root endpoint with API information.

**Response:**
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
Health check - verifies API and database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "total_modules": 16494
}
```

---

### Search

#### `GET /search` or `POST /search`
Hybrid search for Odoo modules using natural language queries.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Natural language search query |
| `version` | string | Yes | Odoo version (12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0) |
| `limit` | integer | No | Max results (1-50, default: 10) |
| `dependencies` | array | No | Filter by module dependencies (comma-separated) |
| `min_score` | integer | No | Minimum score threshold (0-100, default: 0) |

**Example Request (GET):**
```bash
curl "http://localhost:8989/search?query=sales+subscriptions&version=17.0&limit=5"
```

**Example Request (POST):**
```bash
curl -X POST "http://localhost:8989/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "invoice generation",
    "version": "16.0",
    "limit": 10,
    "min_score": 50
  }'
```

**Response:**
```json
{
  "query": "sales subscriptions",
  "version": "17.0",
  "dependencies": null,
  "total_results": 5,
  "results": [
    {
      "id": 1234,
      "technical_name": "sale_subscription",
      "name": "Sale Subscription",
      "version": "17.0",
      "summary": "Manage subscription sales",
      "description": "Allows you to create and manage subscriptions...",
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

**Response Fields:**
- `score`: Combined score (0-100) - normalized from RRF ranking
- `rrf_score`: Raw Reciprocal Rank Fusion score
- `vector_score`: Semantic similarity score (0-1)
- `bm25_score`: Full-text search relevance score

---

### Module Details

#### `GET /modules/{module_id}`
Get complete details for a specific module by ID.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `module_id` | integer | Yes | Module database ID |

**Example Request:**
```bash
curl "http://localhost:8989/modules/1234"
```

**Response:**
```json
{
  "id": 1234,
  "technical_name": "sale_subscription",
  "name": "Sale Subscription",
  "version": "17.0",
  "summary": "Manage subscription sales",
  "description": "Allows you to create and manage subscriptions...",
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

### Statistics

#### `GET /stats`
Get general database statistics.

**Example Request:**
```bash
curl "http://localhost:8989/stats"
```

**Response:**
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

## Search Algorithm

The hybrid search uses **Reciprocal Rank Fusion (RRF)** to combine vector and BM25 scores:

```
RRF_score = 1/(k + rank_vector) + 1/(k + rank_bm25)
```

Where `k=60` (standard RRF constant)

### Search Flow

1. **Query Embedding**: Generate 2560-dimensional vector using Qwen3-Embedding-4B
2. **Vector Search**: PostgreSQL pgvector HNSW index for semantic similarity
3. **BM25 Search**: PostgreSQL `tsvector` for full-text keyword matching
4. **Fusion**: Combine rankings using RRF formula
5. **Filtering**: Apply version and dependency filters
6. **Normalization**: Convert RRF score to 0-100 scale

### Search Modes

The search service supports three modes:

- **`hybrid`** (default): Combines vector + BM25 with RRF
- **`vector`**: Semantic search only (legacy)
- **`bm25`**: Full-text search only

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Server                        │
│                      (0.0.0.0:8989)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Layer (main.py)                     │  │
│  │  /search  /modules/{id}  /stats  /health            │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │          Search Service Layer                       │   │
│  │  - SearchService (orchestration)                    │   │
│  │  - HybridSearchService (RRF fusion)                 │   │
│  │  - EmbeddingService (Qwen3)                         │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │      Data Layer (SQLAlchemy ORM)                    │   │
│  │  - OdooModule model                                 │   │
│  │  - Database session management                      │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │      PostgreSQL 14+                │
        │  ├─ pgvector (vector index)        │
        │  ├─ tsvector (full-text search)    │
        │  ├─ pg_trgm (similarity search)    │
        │  └─ OdooModule table               │
        └────────────────────────────────────┘
```

---

## Database Schema

### `odoo_modules` Table

```sql
CREATE TABLE odoo_modules (
  -- Basic Info
  id SERIAL PRIMARY KEY,
  technical_name VARCHAR UNIQUE NOT NULL,
  name VARCHAR NOT NULL,
  version VARCHAR NOT NULL,
  
  -- Dependencies
  depends TEXT[] DEFAULT '{}',
  
  -- Metadata
  author VARCHAR,
  license VARCHAR DEFAULT 'AGPL-3',
  
  -- Content
  summary VARCHAR,
  description TEXT,
  readme TEXT,
  
  -- Repository
  repo_name VARCHAR NOT NULL,
  repo_url VARCHAR,
  module_path VARCHAR,
  
  -- GitHub
  github_stars INTEGER DEFAULT 0,
  github_issues_open INTEGER DEFAULT 0,
  last_commit_date TIMESTAMP,
  
  -- Search Indexes
  embedding VECTOR(2560),
  searchable_text TSVECTOR,
  
  -- AI Enrichment
  ai_description TEXT,
  functional_tags TEXT[],
  keywords TEXT[],
  enriched_at TIMESTAMP,
  enrichment_version VARCHAR(20),
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_technical_name ON odoo_modules(technical_name);
CREATE INDEX idx_version ON odoo_modules(version);
CREATE INDEX idx_repo_name ON odoo_modules(repo_name);
CREATE INDEX idx_embedding ON odoo_modules USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_searchable_text ON odoo_modules USING GIN (searchable_text);
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | PostgreSQL connection string (required) |
| `OPENROUTER_API_KEY` | - | OpenRouter API key for AI enrichment |
| `GH_TOKEN` | - | GitHub personal access token |
| `ENVIRONMENT` | `development` | `development`, `staging`, or `production` |
| `LOG_LEVEL` | `INFO` | Logging level |
| `EMBEDDING_MODEL` | `qwen/qwen3-embedding-4b` | Embedding model identifier |
| `EMBEDDING_DIMENSIONS` | `2560` | Embedding vector dimensions |

### Settings

Configuration is managed in `app/config.py` using Pydantic Settings:

```python
from app.config import get_settings

settings = get_settings()
print(settings.database_url)
print(settings.embedding_model)
```

---

## Development

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app and routes
│   ├── config.py               # Configuration settings
│   ├── database.py             # SQLAlchemy setup
│   ├── models.py               # ORM models
│   ├── schemas.py              # Pydantic schemas
│   ├── mcp_tools.py            # MCP tool definitions
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependency injection
│   │   └── endpoints/          # API route blueprints
│   │
│   ├── services/
│   │   ├── search_service.py           # Main search orchestration
│   │   ├── hybrid_search_service.py    # RRF fusion logic
│   │   ├── embedding_service.py        # Vector embedding generation
│   │   ├── scoring_service.py          # Score normalization
│   │   ├── enrichment_service.py       # AI enrichment
│   │   ├── github_service.py           # GitHub API integration
│   │   ├── cache_service.py            # Caching layer
│   │   └── content_extraction_service.py
│   │
│   ├── core/
│   │   ├── logging.py          # Logging configuration
│   │   └── ...
│   │
│   ├── utils/
│   │   └── ...
│   │
│   ├── metrics/
│   │   └── ...
│
├── migrations/                 # Alembic database migrations
├── tests/                      # Test suite
├── pyproject.toml             # Package configuration
└── README.md                  # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_search.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black .

# Type checking
mypy app/

# Linting
ruff check .

# All checks
uv run check  # (if defined in pyproject.toml)
```

### Local Development Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8989 --reload

# Or using uv
uv run app.main

# With specific log level
LOG_LEVEL=DEBUG uvicorn app.main:app --host 0.0.0.0 --port 8989 --reload
```

### Interactive API Docs

Once running, visit:
- **Swagger UI**: http://localhost:8989/docs
- **ReDoc**: http://localhost:8989/redoc

---

## Troubleshooting

### Database Connection Issues

**Error:** `psycopg.OperationalError: connection failed`

1. **Verify PostgreSQL is running:**
```bash
psql -U postgres -h localhost -c "SELECT 1;"
```

2. **Check DATABASE_URL format:**
```bash
# Correct format
postgresql+psycopg://user:password@localhost:5432/database_name
```

3. **Create database if missing:**
```bash
createdb -U user ai_odoo_finder
psql -U user ai_odoo_finder -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Embedding Generation Fails

**Error:** `Failed to generate embedding`

1. **Check model is available:**
```bash
# The embedding model should be downloaded automatically
# Force download with:
python -c "from transformers import AutoModel; AutoModel.from_pretrained('Qwen/Qwen3-Embedding-4B')"
```

2. **Check GPU/CPU availability:**
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

### Search Returns No Results

1. **Verify modules are indexed:**
```bash
curl http://localhost:8989/stats
```

2. **Check version filter:**
```bash
# Make sure the version exists (16.0, 17.0, etc.)
curl "http://localhost:8989/search?query=test&version=17.0"
```

3. **Lower the min_score threshold:**
```bash
curl "http://localhost:8989/search?query=test&version=17.0&min_score=0"
```

### High Memory Usage

The embedding model requires significant memory. Options:

1. **Use CPU instead of GPU:**
```bash
export CUDA_VISIBLE_DEVICES=""
```

2. **Use a smaller model (modify config.py):**
```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # ~22M parameters
```

---

## Performance Optimization

### Database Indexing

Ensure indexes are created:
```bash
# Vector index on embeddings
CREATE INDEX IF NOT EXISTS idx_embedding 
ON odoo_modules USING hnsw (embedding vector_cosine_ops);

# Full-text index on searchable_text
CREATE INDEX IF NOT EXISTS idx_searchable_text 
ON odoo_modules USING GIN (searchable_text);
```

### Caching

The search service implements caching for:
- Embeddings (query-based)
- Search results (time-based TTL)

Configure via environment or `cache_service.py`.

### Connection Pooling

SQLAlchemy is configured with connection pooling:
```python
engine = create_engine(
    database_url,
    pool_pre_ping=True,      # Verify connections before use
    pool_recycle=3600,       # Recycle connections after 1 hour
)
```

---

## API Integration Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8989"

# Search
response = requests.get(
    f"{BASE_URL}/search",
    params={
        "query": "invoicing",
        "version": "17.0",
        "limit": 5
    }
)
results = response.json()
print(f"Found {results['total_results']} modules")

# Get module details
module_response = requests.get(f"{BASE_URL}/modules/1234")
module = module_response.json()
print(f"Module: {module['name']}")
```

### JavaScript/Node.js

```javascript
const BASE_URL = "http://localhost:8989";

// Search
const response = await fetch(
  `${BASE_URL}/search?query=invoicing&version=17.0&limit=5`
);
const results = await response.json();
console.log(`Found ${results.total_results} modules`);

// Get module details
const moduleResponse = await fetch(`${BASE_URL}/modules/1234`);
const module = await moduleResponse.json();
console.log(`Module: ${module.name}`);
```

### cURL

```bash
# Search
curl -X GET "http://localhost:8989/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "invoicing",
    "version": "17.0",
    "limit": 5
  }'

# Get stats
curl http://localhost:8989/stats | jq .

# Health check
curl http://localhost:8989/health | jq .
```

---

## Deployment

### Docker

```bash
# Build image
docker build -t ai-odoofinder-backend .

# Run container
docker run -d \
  --name ai-odoofinder \
  -p 8989:8989 \
  -e DATABASE_URL="postgresql://..." \
  -e OPENROUTER_API_KEY="..." \
  ai-odoofinder-backend
```

### Docker Compose

```bash
# Start all services (backend + PostgreSQL)
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### Production Deployment

For production, use:
- **ASGI Server**: Uvicorn with Gunicorn workers
- **Reverse Proxy**: Nginx for load balancing
- **Database**: Managed PostgreSQL (AWS RDS, Azure, etc.)
- **Container Orchestration**: Kubernetes or similar

See main project `docker-compose.yml` for production setup.

---

## Related Documentation

- [Main Project README](../README.md) - User installation guide
- [MCP Server](../mcp-server/README.md) - MCP protocol server
- [CHANGELOG](../docs/en/CHANGELOG.md) - Version history
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - API framework docs
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/) - ORM docs
- [PostgreSQL pgvector](https://github.com/pgvector/pgvector) - Vector database

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Follow the code style (Black, Ruff)
5. Submit a pull request

See [Contributing Guide](../CONTRIBUTING.md) for details.

---

## License

MIT - See [LICENSE](../LICENSE)
