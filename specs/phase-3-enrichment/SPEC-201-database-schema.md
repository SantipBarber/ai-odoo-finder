# SPEC-201: Database Schema - Enrichment Fields

**ID:** SPEC-201
**Componente:** Database Schema
**Archivo:** `migrations/003_add_enrichment_fields.sql`
**Prioridad:** Crítica
**Estimación:** 30 minutos
**Dependencias:** Fase 2 completada

---

## 📋 Descripción

Añadir campos a la tabla `odoo_modules` para almacenar datos enriquecidos: descripciones generadas por IA, tags funcionales, keywords extraídos, y metadata de enrichment.

---

## 📐 Cambios en Schema

### Nuevas Columnas

```sql
ALTER TABLE odoo_modules
ADD COLUMN ai_description TEXT,
ADD COLUMN functional_tags TEXT[],
ADD COLUMN keywords TEXT[],
ADD COLUMN enrichment_metadata JSONB;
```

| Columna | Tipo | Nullable | Descripción |
|---------|------|----------|-------------|
| `ai_description` | TEXT | YES | Descripción generada por Claude (para módulos sin README) |
| `functional_tags` | TEXT[] | YES | Tags categóricos (e.g., ['sales_workflow', 'b2b_commerce']) |
| `keywords` | TEXT[] | YES | Keywords extraídos (e.g., ['invoice', 'recurring', 'subscription']) |
| `enrichment_metadata` | JSONB | YES | Metadata del enrichment (timestamp, model_used, etc.) |

---

## 📄 Migration Script Completo

### Archivo: `migrations/003_add_enrichment_fields.sql`

```sql
-- ============================================================================
-- Migration 003: Add Data Enrichment Fields
-- ============================================================================
-- Description: Adds fields for AI-generated descriptions, functional tags,
--              keywords, and enrichment metadata
-- Author: AI-OdooFinder Team
-- Date: 2025-11-22
-- Dependencies: Migration 002 (full-text search)
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. Add enrichment columns
-- ----------------------------------------------------------------------------

ALTER TABLE odoo_modules
ADD COLUMN IF NOT EXISTS ai_description TEXT,
ADD COLUMN IF NOT EXISTS functional_tags TEXT[],
ADD COLUMN IF NOT EXISTS keywords TEXT[],
ADD COLUMN IF NOT EXISTS enrichment_metadata JSONB;

-- Add comments for documentation
COMMENT ON COLUMN odoo_modules.ai_description IS
    'AI-generated description for modules without README (Claude Haiku)';

COMMENT ON COLUMN odoo_modules.functional_tags IS
    'Functional category tags (e.g., sales_workflow, b2b_commerce)';

COMMENT ON COLUMN odoo_modules.keywords IS
    'Extracted keywords for improved search (TF-IDF + manual)';

COMMENT ON COLUMN odoo_modules.enrichment_metadata IS
    'Metadata about enrichment: {enriched_at, model_used, prompt_version, etc.}';


-- ----------------------------------------------------------------------------
-- 2. Create GIN index for array columns (fast search)
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_modules_functional_tags
ON odoo_modules USING GIN(functional_tags);

CREATE INDEX IF NOT EXISTS idx_modules_keywords
ON odoo_modules USING GIN(keywords);

-- GIN index for JSONB metadata (optional, for advanced queries)
CREATE INDEX IF NOT EXISTS idx_modules_enrichment_metadata
ON odoo_modules USING GIN(enrichment_metadata);

COMMENT ON INDEX idx_modules_functional_tags IS
    'GIN index for fast array containment queries on functional_tags';

COMMENT ON INDEX idx_modules_keywords IS
    'GIN index for fast array containment queries on keywords';


-- ----------------------------------------------------------------------------
-- 3. Update searchable_text trigger to include enrichment data
-- ----------------------------------------------------------------------------

-- Drop existing trigger
DROP TRIGGER IF EXISTS trigger_update_searchable_text ON odoo_modules;

-- Update function to include enrichment fields
CREATE OR REPLACE FUNCTION update_odoo_modules_searchable_text()
RETURNS TRIGGER AS $$
BEGIN
    -- Combine all text fields with weights
    -- NEW: Include ai_description, functional_tags, keywords

    NEW.searchable_text :=
        -- Original fields
        setweight(to_tsvector('english', COALESCE(NEW.technical_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.readme, '')), 'D') ||

        -- NEW: Enrichment fields
        setweight(to_tsvector('english', COALESCE(NEW.ai_description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.functional_tags, ' '), '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.keywords, ' '), '')), 'A');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_odoo_modules_searchable_text() IS
    'Updated to include enrichment fields (ai_description, tags, keywords)';

-- Recreate trigger
CREATE TRIGGER trigger_update_searchable_text
    BEFORE INSERT OR UPDATE OF
        technical_name, name, summary, description, readme,
        ai_description, functional_tags, keywords
    ON odoo_modules
    FOR EACH ROW
    EXECUTE FUNCTION update_odoo_modules_searchable_text();


-- ----------------------------------------------------------------------------
-- 4. Helper functions for enrichment queries
-- ----------------------------------------------------------------------------

-- Function to check if module needs enrichment
CREATE OR REPLACE FUNCTION needs_enrichment(module_row odoo_modules)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (
        -- No AI description AND (no README OR short README)
        module_row.ai_description IS NULL
        AND (
            module_row.readme IS NULL
            OR LENGTH(module_row.readme) < 500
        )
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION needs_enrichment IS
    'Returns true if module should be enriched (no AI description and poor README)';

-- Function to count modules needing enrichment
CREATE OR REPLACE FUNCTION count_modules_needing_enrichment()
RETURNS TABLE(
    total_modules BIGINT,
    needs_enrichment BIGINT,
    already_enriched BIGINT,
    percentage_needing NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE ai_description IS NULL AND (readme IS NULL OR LENGTH(readme) < 500)) as needs,
        COUNT(*) FILTER (WHERE ai_description IS NOT NULL) as enriched,
        ROUND(
            100.0 * COUNT(*) FILTER (WHERE ai_description IS NULL AND (readme IS NULL OR LENGTH(readme) < 500))
            / COUNT(*)
        , 2) as pct
    FROM odoo_modules;
END;
$$ LANGUAGE plpgsql;


-- ----------------------------------------------------------------------------
-- 5. Validation queries
-- ----------------------------------------------------------------------------

-- Test: Count modules by enrichment status
DO $$
DECLARE
    stats RECORD;
BEGIN
    SELECT * INTO stats FROM count_modules_needing_enrichment();

    RAISE NOTICE 'Enrichment status:';
    RAISE NOTICE '  Total modules: %', stats.total_modules;
    RAISE NOTICE '  Need enrichment: % (%.1f%%)',
        stats.needs_enrichment, stats.percentage_needing;
    RAISE NOTICE '  Already enriched: %', stats.already_enriched;
END $$;

COMMIT;

-- ============================================================================
-- Migration 003 Complete
-- ============================================================================
```

---

## 🔄 Rollback Script

### Archivo: `migrations/003_add_enrichment_fields_down.sql`

```sql
-- ============================================================================
-- Migration 003 Rollback: Remove Enrichment Fields
-- ============================================================================

BEGIN;

-- Drop helper functions
DROP FUNCTION IF EXISTS count_modules_needing_enrichment();
DROP FUNCTION IF EXISTS needs_enrichment(odoo_modules);

-- Revert trigger function to original
DROP TRIGGER IF EXISTS trigger_update_searchable_text ON odoo_modules;

CREATE OR REPLACE FUNCTION update_odoo_modules_searchable_text()
RETURNS TRIGGER AS $$
BEGIN
    NEW.searchable_text :=
        setweight(to_tsvector('english', COALESCE(NEW.technical_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.readme, '')), 'D');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_searchable_text
    BEFORE INSERT OR UPDATE OF technical_name, name, summary, description, readme
    ON odoo_modules
    FOR EACH ROW
    EXECUTE FUNCTION update_odoo_modules_searchable_text();

-- Drop indexes
DROP INDEX IF EXISTS idx_modules_enrichment_metadata;
DROP INDEX IF EXISTS idx_modules_keywords;
DROP INDEX IF EXISTS idx_modules_functional_tags;

-- Drop columns
ALTER TABLE odoo_modules
DROP COLUMN IF EXISTS enrichment_metadata,
DROP COLUMN IF EXISTS keywords,
DROP COLUMN IF EXISTS functional_tags,
DROP COLUMN IF EXISTS ai_description;

COMMIT;
```

---

## 🧪 Tests de Validación

### Test 1: Columns Exist

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'odoo_modules'
  AND column_name IN ('ai_description', 'functional_tags', 'keywords', 'enrichment_metadata');

-- Expected: 4 rows
```

### Test 2: Indexes Created

```sql
SELECT indexname
FROM pg_indexes
WHERE tablename = 'odoo_modules'
  AND indexname LIKE '%enrichment%' OR indexname LIKE '%tags%' OR indexname LIKE '%keywords%';

-- Expected: 3 indexes
```

### Test 3: Trigger Updated

```sql
-- Test that trigger includes new fields
INSERT INTO odoo_modules (
    technical_name,
    name,
    summary,
    functional_tags,
    keywords,
    version
) VALUES (
    'test_enrichment_module',
    'Test Module',
    'Testing enrichment',
    ARRAY['sales_workflow', 'automation'],
    ARRAY['test', 'automation', 'workflow'],
    '16.0'
) RETURNING searchable_text IS NOT NULL;

-- Expected: true

-- Cleanup
DELETE FROM odoo_modules WHERE technical_name = 'test_enrichment_module';
```

### Test 4: Helper Functions Work

```sql
-- Test count function
SELECT * FROM count_modules_needing_enrichment();

-- Expected: Returns stats with total_modules > 0
```

---

## ✅ Criterios de Aceptación

### AC-1: Migration Applies Successfully
- ✅ Script ejecuta sin errores
- ✅ Rollback script funciona

### AC-2: Columns Created
- ✅ Las 4 columnas existen
- ✅ Tipos correctos (TEXT, TEXT[], JSONB)

### AC-3: Indexes Created
- ✅ 3 índices GIN creados
- ✅ Query planner los usa

### AC-4: Trigger Updated
- ✅ searchable_text incluye enrichment fields
- ✅ Trigger se dispara en UPDATE de nuevos campos

### AC-5: Helper Functions
- ✅ `needs_enrichment()` funciona
- ✅ `count_modules_needing_enrichment()` retorna stats

---

## 📊 Storage Impact

```
Estimación para 2,500 módulos:

ai_description:         ~1-2 KB por módulo = 2-5 MB
functional_tags:        ~50 bytes por módulo = 125 KB
keywords:              ~100 bytes por módulo = 250 KB
enrichment_metadata:    ~200 bytes por módulo = 500 KB

Indexes (GIN):         ~1 MB

Total adicional:       ~4-7 MB
```

**Impacto:** Mínimo (< 10 MB para dataset completo)

---

## 🔗 Siguiente Paso

Una vez completado este SPEC:
→ [SPEC-202: AI Description Generator](./SPEC-202-ai-description-generator.md)

---

**Estado:** 🔴 Pendiente de implementación
**Blocker para:** SPEC-202, SPEC-203, SPEC-204, SPEC-205
