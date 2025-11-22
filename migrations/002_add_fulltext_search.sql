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
