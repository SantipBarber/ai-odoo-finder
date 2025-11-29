-- ============================================================================
-- Migration 005: Add Clean Description Fields for Phase 6
-- ============================================================================
-- Date: 2025-11-28
-- Description: Add fields to store clean descriptions extracted from GitHub
--              readme/DESCRIPTION.rst or cleaned README.rst content
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. Add new columns for clean content
-- ----------------------------------------------------------------------------

-- Clean description extracted from readme/DESCRIPTION.rst or cleaned README
ALTER TABLE odoo_modules ADD COLUMN IF NOT EXISTS description_clean TEXT;

-- Source of the clean description:
-- 'description_rst' - From readme/DESCRIPTION.rst (best quality)
-- 'readme_rst_cleaned' - From README.rst after cleaning
-- 'readme_md_cleaned' - From README.md after cleaning
-- 'manifest' - From __manifest__.py description field
-- 'none' - No description available
ALTER TABLE odoo_modules ADD COLUMN IF NOT EXISTS content_source VARCHAR(50);

-- Timestamp when content was extracted
ALTER TABLE odoo_modules ADD COLUMN IF NOT EXISTS content_extracted_at TIMESTAMP;

-- ----------------------------------------------------------------------------
-- 2. Add index for finding modules needing content extraction
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_modules_needs_content_extraction
ON odoo_modules(content_extracted_at)
WHERE content_extracted_at IS NULL;

-- Index on content_source for statistics
CREATE INDEX IF NOT EXISTS idx_modules_content_source
ON odoo_modules(content_source);

-- ----------------------------------------------------------------------------
-- 3. Add comments
-- ----------------------------------------------------------------------------

COMMENT ON COLUMN odoo_modules.description_clean IS
    'Clean description extracted from GitHub (readme/DESCRIPTION.rst preferred)';
COMMENT ON COLUMN odoo_modules.content_source IS
    'Source of description_clean: description_rst, readme_rst_cleaned, readme_md_cleaned, manifest, none';
COMMENT ON COLUMN odoo_modules.content_extracted_at IS
    'Timestamp when content was extracted from GitHub';

-- ----------------------------------------------------------------------------
-- 4. Verify migration
-- ----------------------------------------------------------------------------

DO $$
DECLARE
    total_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_count FROM odoo_modules;

    RAISE NOTICE 'Migration 005 complete:';
    RAISE NOTICE '  Total modules: %', total_count;
    RAISE NOTICE '  Added columns: description_clean, content_source, content_extracted_at';
    RAISE NOTICE '  Next step: Run extract_clean_descriptions.py to populate';
END;
$$;

COMMIT;

-- ============================================================================
-- Migration 005 Complete
-- New columns ready for clean content extraction from OCA GitHub
-- ============================================================================