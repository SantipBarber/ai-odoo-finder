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
