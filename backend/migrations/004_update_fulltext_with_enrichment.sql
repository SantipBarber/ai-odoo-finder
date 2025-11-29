-- ============================================================================
-- Migration 004: Update Full-Text Search to Include Enrichment Fields
-- ============================================================================
-- This migration updates the searchable_text trigger to include:
-- - ai_description (weight B - same as summary)
-- - keywords (weight B - important for search)
-- - functional_tags (weight C - categories)
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. Update the trigger function to include enrichment fields
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_odoo_modules_searchable_text()
RETURNS TRIGGER AS $$
BEGIN
    -- Combine text fields with different weights
    -- A (1.0): technical_name, name - highest priority
    -- B (0.4): summary, ai_description, keywords - medium-high priority
    -- C (0.2): description, functional_tags - medium priority
    -- D (0.1): readme - lowest priority (most verbose)

    NEW.searchable_text :=
        -- Weight A: Names (highest priority)
        setweight(to_tsvector('english', COALESCE(NEW.technical_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
        -- Weight B: Summaries and keywords (high priority)
        setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.ai_description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.keywords, ' '), '')), 'B') ||
        -- Weight C: Descriptions and tags (medium priority)
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.functional_tags, ' '), '')), 'C') ||
        -- Weight D: README (lowest priority)
        setweight(to_tsvector('english', COALESCE(NEW.readme, '')), 'D');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_odoo_modules_searchable_text() IS
    'Trigger function to update searchable_text including enrichment fields (ai_description, keywords, functional_tags)';


-- ----------------------------------------------------------------------------
-- 2. Update trigger to fire on enrichment field changes too
-- ----------------------------------------------------------------------------

DROP TRIGGER IF EXISTS trigger_update_searchable_text ON odoo_modules;

CREATE TRIGGER trigger_update_searchable_text
    BEFORE INSERT OR UPDATE OF technical_name, name, summary, description, readme, ai_description, keywords, functional_tags
    ON odoo_modules
    FOR EACH ROW
    EXECUTE FUNCTION update_odoo_modules_searchable_text();

COMMENT ON TRIGGER trigger_update_searchable_text ON odoo_modules IS
    'Automatically updates searchable_text when text or enrichment fields are modified';


-- ----------------------------------------------------------------------------
-- 3. Regenerate searchable_text for all existing records
-- ----------------------------------------------------------------------------

UPDATE odoo_modules
SET searchable_text =
    setweight(to_tsvector('english', COALESCE(technical_name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(summary, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(ai_description, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(array_to_string(keywords, ' '), '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(description, '')), 'C') ||
    setweight(to_tsvector('english', COALESCE(array_to_string(functional_tags, ' '), '')), 'C') ||
    setweight(to_tsvector('english', COALESCE(readme, '')), 'D');

-- ----------------------------------------------------------------------------
-- 4. Verify update
-- ----------------------------------------------------------------------------

DO $$
DECLARE
    total_count INTEGER;
    with_enrichment INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_count FROM odoo_modules;
    SELECT COUNT(*) INTO with_enrichment FROM odoo_modules WHERE ai_description IS NOT NULL;

    RAISE NOTICE 'Migration 004 complete:';
    RAISE NOTICE '  Total modules: %', total_count;
    RAISE NOTICE '  With enrichment: %', with_enrichment;
    RAISE NOTICE '  searchable_text now includes ai_description, keywords, and functional_tags';
END;
$$;

COMMIT;

-- ============================================================================
-- Migration 004 Complete
-- Full-text search now includes enrichment fields for better search results
-- ============================================================================
