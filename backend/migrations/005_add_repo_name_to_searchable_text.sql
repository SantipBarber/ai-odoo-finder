-- ============================================================================
-- Migration 005: Add repo_name to Full-Text Search
-- ============================================================================
-- This migration updates the searchable_text to include repo_name field.
--
-- WHY: Localization modules like l10n_es_facturae have descriptions in Spanish
-- but the repo_name (l10n-spain) contains "spain" which helps find them
-- when users search for "facturae Spain" or similar queries.
--
-- PROBLEM SOLVED:
-- Before: "facturae Spain" -> BM25 finds nothing (description is in Spanish)
-- After:  "facturae Spain" -> BM25 finds l10n-spain modules via repo_name
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. Update the trigger function to include repo_name
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_odoo_modules_searchable_text()
RETURNS TRIGGER AS $$
BEGIN
    -- Combine text fields with different weights
    -- A (1.0): technical_name, name - highest priority
    -- B (0.4): summary, ai_description, keywords, repo_name - medium-high priority
    -- C (0.2): description, functional_tags - medium priority
    -- D (0.1): readme - lowest priority (most verbose)

    NEW.searchable_text :=
        -- Weight A: Names (highest priority)
        setweight(to_tsvector('english', COALESCE(NEW.technical_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
        -- Weight B: Summaries, keywords, and repo_name (high priority)
        setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.ai_description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.keywords, ' '), '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(REPLACE(NEW.repo_name, '-', ' '), '')), 'B') ||
        -- Weight C: Descriptions and tags (medium priority)
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.functional_tags, ' '), '')), 'C') ||
        -- Weight D: README (lowest priority)
        setweight(to_tsvector('english', COALESCE(NEW.readme, '')), 'D');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_odoo_modules_searchable_text() IS
    'Trigger function to update searchable_text including repo_name for better country/localization search';


-- ----------------------------------------------------------------------------
-- 2. Update trigger to fire on repo_name changes too
-- ----------------------------------------------------------------------------

DROP TRIGGER IF EXISTS trigger_update_searchable_text ON odoo_modules;

CREATE TRIGGER trigger_update_searchable_text
    BEFORE INSERT OR UPDATE OF technical_name, name, summary, description, readme, ai_description, keywords, functional_tags, repo_name
    ON odoo_modules
    FOR EACH ROW
    EXECUTE FUNCTION update_odoo_modules_searchable_text();

COMMENT ON TRIGGER trigger_update_searchable_text ON odoo_modules IS
    'Automatically updates searchable_text when text, enrichment, or repo_name fields are modified';


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
    setweight(to_tsvector('english', COALESCE(REPLACE(repo_name, '-', ' '), '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(description, '')), 'C') ||
    setweight(to_tsvector('english', COALESCE(array_to_string(functional_tags, ' '), '')), 'C') ||
    setweight(to_tsvector('english', COALESCE(readme, '')), 'D');

-- ----------------------------------------------------------------------------
-- 4. Verify update
-- ----------------------------------------------------------------------------

DO $$
DECLARE
    total_count INTEGER;
    spain_example INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_count FROM odoo_modules;

    -- Verify that we can now find l10n-spain modules by searching "spain"
    SELECT COUNT(*) INTO spain_example
    FROM odoo_modules
    WHERE searchable_text @@ plainto_tsquery('english', 'spain');

    RAISE NOTICE 'Migration 005 complete:';
    RAISE NOTICE '  Total modules updated: %', total_count;
    RAISE NOTICE '  Modules findable by "spain": %', spain_example;
    RAISE NOTICE '  searchable_text now includes repo_name for better country search';
END;
$$;

COMMIT;

-- ============================================================================
-- Migration 005 Complete
-- Full-text search now includes repo_name (e.g., l10n-spain -> "l10n spain")
-- This improves search for localization modules by country name
-- ============================================================================
