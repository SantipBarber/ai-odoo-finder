# 🚀 Guía de Configuración Neon

## Índice
1. [Crear Cuenta y Proyecto](#crear-cuenta-y-proyecto)
2. [Habilitar pgVector](#habilitar-pgvector)
3. [Configurar Connection Pooling](#configurar-connection-pooling)
4. [Branching para Testing](#branching-para-testing)
5. [Monitoreo y Optimización](#monitoreo-y-optimización)

---

## Crear Cuenta y Proyecto

### 1. Registro
```bash
# Ir a: https://console.neon.tech/signup
# Opciones: GitHub, Google, o Email
```

### 2. Crear Proyecto
```
Nombre: ai-odoofinder
Región: us-east-2 (o más cercana)
Postgres: 16 (recomendado)
```

### 3. Obtener Connection String
```bash
# Dashboard → Connection Details → Copy
postgresql://user:pass@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

---

## Habilitar pgVector

### Vía SQL Editor (Web)
```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
```

### Vía psql (Local)
```bash
psql "postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require"

# En psql:
CREATE EXTENSION vector;
\dx vector
```

---

## Configurar Connection Pooling

Neon incluye pooling nativo, pero puedes ajustarlo:
```python
# backend/app/database.py
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=5,          # Conexiones persistentes
    max_overflow=10,      # Conexiones extra bajo carga
    pool_pre_ping=True,   # Verificar conexión antes de usar
    pool_recycle=3600     # Reciclar conexiones cada hora
)
```

---

## Branching para Testing

### Crear Branch de Testing
```bash
# Via Neon Console:
# Projects → ai-odoofinder → Branches → Create Branch

Nombre: testing
Basado en: main
```

### Usar en Código
```bash
# .env.testing
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?options=branch%3Dtesting
```

### Workflow Recomendado
```
main branch     → Producción (usuarios reales)
testing branch  → CI/CD, tests automáticos
dev-{nombre}    → Desarrollo individual
```

---

## Monitoreo y Optimización

### Verificar Uso
```sql
-- Tamaño de base de datos
SELECT pg_size_pretty(pg_database_size('neondb'));

-- Tamaño de vectores
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE tablename = 'module_embeddings';
```

### Optimizar Índices HNSW
```sql
-- Ver índices existentes
SELECT * FROM pg_indexes WHERE tablename = 'module_embeddings';

-- Crear índice optimizado (si no existe)
CREATE INDEX IF NOT EXISTS module_embeddings_idx
ON module_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### Dashboard Neon
- **Metrics:** CPU, RAM, Storage usage
- **Queries:** Ver queries lentas
- **Logs:** Errores y warnings

---

## Costos y Límites

### Free Tier
- Storage: 0.5 GB
- Compute: 191 hours/mes
- Branches: 10
- Projects: 1

### Cuándo Upgradear
- Storage > 0.5 GB → Launch ($19/mes, 3GB)
- Más compute hours → Autoscaling en Launch
- Más proyectos → Scale plan

---

## Troubleshooting

### Error: "too many connections"
```python
# Reducir pool_size en database.py
pool_size=3, max_overflow=5
```

### Error: "extension vector not found"
```sql
-- Verificar que existe
SELECT * FROM pg_available_extensions WHERE name = 'vector';

-- Si no existe, contactar soporte Neon
```

### Lentitud en Búsquedas
```sql
-- Verificar que existe índice HNSW
SELECT * FROM pg_indexes
WHERE tablename = 'module_embeddings'
AND indexdef LIKE '%hnsw%';

-- Si no existe, crear según sección "Optimizar Índices"
```

---

## Recursos
- [Neon Docs](https://neon.com/docs)
- [pgVector en Neon](https://neon.com/docs/extensions/pgvector)
- [Neon API](https://api-docs.neon.tech/reference/getting-started-with-neon-api)
