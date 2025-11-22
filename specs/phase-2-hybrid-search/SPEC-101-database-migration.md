# SPEC-101: Database Migration - Full-Text Search

**ID:** SPEC-101
**Componente:** Database Schema
**Archivo:** `migrations/002_add_fulltext_search.sql`
**Prioridad:** Crítica (Bloqueante para toda la fase)
**Estimación:** 2-3 horas
**Dependencias:** Fase 1 completada

---

## 📋 Descripción

Añadir capacidad de full-text search a la tabla `odoo_modules` usando PostgreSQL `tsvector` y índices GIN para permitir búsquedas BM25 eficientes sobre campos textuales con pesos diferenciados.

---

## 🎯 Objetivos

1. **Añadir columna `searchable_text`** tipo `tsvector`
2. **Crear índice GIN** para búsquedas rápidas
3. **Implementar trigger** para auto-actualización
4. **Poblar datos** existentes
5. **Validar performance** de búsquedas

---

## 📐 Cambios en Schema

### Columna Nueva

```sql
ALTER TABLE odoo_modules
ADD COLUMN searchable_text tsvector;
```

**Tipo:** `tsvector`
**Nullable:** YES (inicialmente, se poblará con trigger)
**Default:** NULL

### Índice GIN

```sql
CREATE INDEX idx_modules_fulltext
ON odoo_modules
USING GIN(searchable_text);
```

**Tipo:** GIN (Generalized Inverted Index)
**Razón:** Optimal para full-text search (3-5x más rápido que GIST)

---

## 🏗️ Estructura de Pesos

### Configuración de Pesos de Campos

```sql
searchable_text =
    setweight(to_tsvector('english', COALESCE(technical_name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(summary, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(description, '')), 'C') ||
    setweight(to_tsvector('english', COALESCE(readme, '')), 'D');
```

### Justificación de Pesos

| Campo | Peso | Justificación |
|-------|------|---------------|
| `technical_name` | A (1.0) | Match exacto más importante |
| `name` | A (1.0) | Nombre del módulo es crítico |
| `summary` | B (0.4) | Descripción corta relevante |
| `description` | C (0.2) | Contexto adicional |
| `readme` | D (0.1) | Info detallada pero menos prioritaria |

**Nota:** PostgreSQL usa estos pesos en `ts_rank_cd()`:
- A: 1.0
- B: 0.4
- C: 0.2
- D: 0.1

---

## 📄 Migration Script Completo

### Archivo: `migrations/002_add_fulltext_search.sql`

```sql
-- ============================================================================
-- Migration 002: Add Full-Text Search Support
-- ============================================================================
-- Description: Adds tsvector column and GIN index for BM25-like full-text
--              search on odoo_modules table
-- Author: AI-OdooFinder Team
-- Date: 2025-11-22
-- Dependencies: Migration 001 (initial schema)
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. Add searchable_text column
-- ----------------------------------------------------------------------------

ALTER TABLE odoo_modules
ADD COLUMN IF NOT EXISTS searchable_text tsvector;

COMMENT ON COLUMN odoo_modules.searchable_text IS
    'Full-text search index combining multiple text fields with weights';


-- ----------------------------------------------------------------------------
-- 2. Create GIN index for fast full-text search
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_modules_fulltext
ON odoo_modules
USING GIN(searchable_text);

-- Add comment for documentation
COMMENT ON INDEX idx_modules_fulltext IS
    'GIN index for full-text search on searchable_text column';


-- ----------------------------------------------------------------------------
-- 3. Create function to update searchable_text
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_odoo_modules_searchable_text()
RETURNS TRIGGER AS $$
BEGIN
    -- Combine text fields with different weights
    -- A (1.0): technical_name, name - highest priority
    -- B (0.4): summary - medium priority
    -- C (0.2): description - lower priority
    -- D (0.1): readme - lowest priority (most verbose)

    NEW.searchable_text :=
        setweight(to_tsvector('english', COALESCE(NEW.technical_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.readme, '')), 'D');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_odoo_modules_searchable_text() IS
    'Trigger function to automatically update searchable_text when text fields change';


-- ----------------------------------------------------------------------------
-- 4. Create trigger for automatic updates
-- ----------------------------------------------------------------------------

DROP TRIGGER IF EXISTS trigger_update_searchable_text ON odoo_modules;

CREATE TRIGGER trigger_update_searchable_text
    BEFORE INSERT OR UPDATE OF technical_name, name, summary, description, readme
    ON odoo_modules
    FOR EACH ROW
    EXECUTE FUNCTION update_odoo_modules_searchable_text();

COMMENT ON TRIGGER trigger_update_searchable_text ON odoo_modules IS
    'Automatically updates searchable_text when relevant fields are modified';


-- ----------------------------------------------------------------------------
-- 5. Populate searchable_text for existing records
-- ----------------------------------------------------------------------------

-- This may take a few minutes for large datasets
-- Progress can be monitored with: SELECT COUNT(*) FROM odoo_modules WHERE searchable_text IS NOT NULL;

UPDATE odoo_modules
SET searchable_text =
    setweight(to_tsvector('english', COALESCE(technical_name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(summary, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(description, '')), 'C') ||
    setweight(to_tsvector('english', COALESCE(readme, '')), 'D')
WHERE searchable_text IS NULL;

-- Verify population
DO $$
DECLARE
    total_count INTEGER;
    populated_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_count FROM odoo_modules;
    SELECT COUNT(*) INTO populated_count FROM odoo_modules WHERE searchable_text IS NOT NULL;

    RAISE NOTICE 'Full-text search population complete: % / % records', populated_count, total_count;

    IF populated_count < total_count THEN
        RAISE WARNING 'Not all records were populated. Expected %, got %', total_count, populated_count;
    END IF;
END $$;


-- ----------------------------------------------------------------------------
-- 6. Analyze table for query planner
-- ----------------------------------------------------------------------------

ANALYZE odoo_modules;


-- ----------------------------------------------------------------------------
-- 7. Create test query for validation
-- ----------------------------------------------------------------------------

-- Test query to validate full-text search works
DO $$
DECLARE
    test_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO test_count
    FROM odoo_modules
    WHERE searchable_text @@ plainto_tsquery('english', 'account invoice');

    RAISE NOTICE 'Test query found % modules matching "account invoice"', test_count;

    IF test_count = 0 THEN
        RAISE WARNING 'Test query returned 0 results - this may indicate an issue';
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- Migration 002 Complete
-- ============================================================================
```

---

## 🔄 Rollback Script

### Archivo: `migrations/002_add_fulltext_search_down.sql`

```sql
-- ============================================================================
-- Migration 002 Rollback: Remove Full-Text Search Support
-- ============================================================================

BEGIN;

-- Drop trigger first
DROP TRIGGER IF EXISTS trigger_update_searchable_text ON odoo_modules;

-- Drop function
DROP FUNCTION IF EXISTS update_odoo_modules_searchable_text();

-- Drop index
DROP INDEX IF EXISTS idx_modules_fulltext;

-- Drop column
ALTER TABLE odoo_modules
DROP COLUMN IF EXISTS searchable_text;

COMMIT;

-- ============================================================================
-- Rollback Complete
-- ============================================================================
```

---

## 🧪 Tests de Validación

### Test 1: Schema Changes Applied

```sql
-- Verify column exists
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'odoo_modules'
  AND column_name = 'searchable_text';

-- Expected: 1 row with data_type = 'tsvector'
```

### Test 2: Index Exists and Type

```sql
-- Verify GIN index exists
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'odoo_modules'
  AND indexname = 'idx_modules_fulltext';

-- Expected: 1 row with indexdef containing 'GIN'
```

### Test 3: Trigger Works

```sql
-- Insert test record
INSERT INTO odoo_modules (
    technical_name,
    name,
    summary,
    version
) VALUES (
    'test_fulltext_module',
    'Test Module',
    'This is a test summary for full-text search',
    '16.0'
) RETURNING id, searchable_text IS NOT NULL as has_searchable_text;

-- Expected: has_searchable_text = true

-- Cleanup
DELETE FROM odoo_modules WHERE technical_name = 'test_fulltext_module';
```

### Test 4: Search Works

```sql
-- Test search query
SELECT
    technical_name,
    name,
    ts_rank_cd(searchable_text, query) as rank
FROM odoo_modules,
     plainto_tsquery('english', 'account reconciliation') query
WHERE searchable_text @@ query
  AND version = '16.0'
ORDER BY rank DESC
LIMIT 10;

-- Expected: Returns results ordered by relevance
```

### Test 5: Performance Validation

```sql
-- Test query performance with EXPLAIN ANALYZE
EXPLAIN ANALYZE
SELECT technical_name, ts_rank_cd(searchable_text, query) as rank
FROM odoo_modules,
     plainto_tsquery('english', 'sales order') query
WHERE searchable_text @@ query
ORDER BY rank DESC
LIMIT 10;

-- Expected:
-- - Uses idx_modules_fulltext (Bitmap Index Scan on idx_modules_fulltext)
-- - Execution time < 50ms
```

---

## ✅ Criterios de Aceptación

### AC-1: Migration Executes Successfully
- ✅ Script ejecuta sin errores
- ✅ Transaction commits exitosamente
- ✅ No warnings críticos

### AC-2: Schema Changes Verified
- ✅ Columna `searchable_text` existe
- ✅ Tipo es `tsvector`
- ✅ Índice GIN creado

### AC-3: Data Populated
- ✅ 100% de registros tienen `searchable_text` populated
- ✅ `searchable_text IS NOT NULL` para todos los registros

### AC-4: Trigger Functions
- ✅ Nuevos inserts auto-populan `searchable_text`
- ✅ Updates a campos de texto actualizan `searchable_text`

### AC-5: Search Performance
- ✅ Búsqueda full-text < 50ms para 2,500 registros
- ✅ Query planner usa índice GIN
- ✅ Resultados ordenados por relevancia

---

## 🚨 Procedimiento de Aplicación

### Pre-requisitos

```bash
# 1. Backup de base de datos
pg_dump -h localhost -U postgres -d ai_odoo_finder > backup_before_migration_002.sql

# 2. Verificar espacio en disco (índice GIN necesita ~30% del tamaño de la tabla)
SELECT pg_size_pretty(pg_total_relation_size('odoo_modules'));

# 3. Estimar tiempo de migration (para 2,500 registros: ~30-60 segundos)
```

### Aplicar Migration (Desarrollo)

```bash
# 1. Aplicar en BD de desarrollo primero
psql -h localhost -U postgres -d ai_odoo_finder_dev < migrations/002_add_fulltext_search.sql

# 2. Ejecutar tests de validación
psql -h localhost -U postgres -d ai_odoo_finder_dev -f tests/sql/test_migration_002.sql

# 3. Verificar no hay errores
```

### Aplicar Migration (Producción)

```bash
# 1. Modo mantenimiento ON
# 2. Backup
pg_dump -h prod-db -U postgres -d ai_odoo_finder > backup_prod_$(date +%Y%m%d_%H%M%S).sql

# 3. Aplicar migration
psql -h prod-db -U postgres -d ai_odoo_finder < migrations/002_add_fulltext_search.sql

# 4. Validar
psql -h prod-db -U postgres -d ai_odoo_finder -f tests/sql/test_migration_002.sql

# 5. Modo mantenimiento OFF
```

---

## 📊 Impacto y Performance

### Disk Space

```
Estimación para 2,500 módulos:

Table data:               ~5 MB
searchable_text column:   ~2 MB  (40% del tamaño actual)
GIN index:               ~3 MB  (60% del tamaño actual)

Total additional:        ~5 MB
```

### Execution Time

```
Development (2,500 registros):
  - Add column:           < 1s
  - Create index:         < 5s
  - Create trigger:       < 1s
  - Populate data:        10-30s
  - Analyze:              2-5s
  Total:                  ~20-45s

Production (escala similar):
  - Similar timing
  - Puede requerir VACUUM después
```

### Search Performance

```
Antes (sin full-text):
  - N/A

Después (con full-text):
  - Simple query:     5-20ms
  - Complex query:    10-50ms
  - Con ts_rank:      20-80ms
```

---

## 🔧 Troubleshooting

### Error: "out of memory"

**Causa:** GIN index build consume mucha RAM

**Solución:**
```sql
-- Crear índice con parámetros más conservadores
CREATE INDEX idx_modules_fulltext ON odoo_modules
USING GIN(searchable_text)
WITH (fastupdate = off);
```

### Error: "index is too large"

**Causa:** Tablas muy grandes (millones de registros)

**Solución:**
```sql
-- Crear índice parcial solo para versiones activas
CREATE INDEX idx_modules_fulltext ON odoo_modules
USING GIN(searchable_text)
WHERE version IN ('16.0', '17.0', '18.0');
```

### Warning: "query doesn't use index"

**Causa:** Query no está usando índice GIN

**Solución:**
```sql
-- Verificar que estadísticas están actualizadas
ANALYZE odoo_modules;

-- Verificar query usa @@
-- ✅ Correcto:
WHERE searchable_text @@ plainto_tsquery('text')

-- ❌ Incorrecto:
WHERE to_tsvector(name) @@ plainto_tsquery('text')
```

---

## 📝 Notas de Implementación

### Diccionario 'english'

**Por qué 'english':**
- Stopwords estándar ('the', 'a', 'is')
- Stemming (account → account, accounts → account)
- Bien soportado

**Alternativas consideradas:**
- `'simple'`: Sin stemming, sin stopwords
- `'spanish'`: Para queries en español
- Custom dictionary: Más control

**Decisión:** Usar 'english' inicialmente, evaluar custom dictionary si es necesario.

### Actualización Incremental

```sql
-- Si la tabla es muy grande, actualizar en batches
DO $$
DECLARE
    batch_size INTEGER := 500;
    total INTEGER;
    updated INTEGER := 0;
BEGIN
    SELECT COUNT(*) INTO total FROM odoo_modules WHERE searchable_text IS NULL;

    WHILE updated < total LOOP
        UPDATE odoo_modules
        SET searchable_text =
            setweight(to_tsvector('english', COALESCE(technical_name, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(name, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(summary, '')), 'B') ||
            setweight(to_tsvector('english', COALESCE(description, '')), 'C') ||
            setweight(to_tsvector('english', COALESCE(readme, '')), 'D')
        WHERE id IN (
            SELECT id FROM odoo_modules
            WHERE searchable_text IS NULL
            LIMIT batch_size
        );

        updated := updated + batch_size;
        RAISE NOTICE 'Updated % / % records', updated, total;

        PERFORM pg_sleep(0.1); -- Small pause to avoid load spike
    END LOOP;
END $$;
```

---

## 🔗 Siguiente Paso

Una vez completado este SPEC y migration aplicada:
→ [SPEC-102: Hybrid Search Service](./SPEC-102-hybrid-search-service.md)

---

**Estado:** 🔴 Pendiente de implementación
**Blocker para:** SPEC-102, SPEC-103, SPEC-104
**Crítico:** ⚠️ DEBE hacerse backup antes de aplicar
