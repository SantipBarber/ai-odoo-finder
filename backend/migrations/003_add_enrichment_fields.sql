-- Migration 003: Add enrichment fields for Phase 3
-- Date: 2025-11-25
-- Description: Add fields to track AI-generated descriptions, tags, keywords, and enrichment status

-- Add enrichment fields
ALTER TABLE odoo_modules ADD COLUMN IF NOT EXISTS ai_description TEXT;
ALTER TABLE odoo_modules ADD COLUMN IF NOT EXISTS functional_tags TEXT[];
ALTER TABLE odoo_modules ADD COLUMN IF NOT EXISTS keywords TEXT[];
ALTER TABLE odoo_modules ADD COLUMN IF NOT EXISTS enriched_at TIMESTAMP;
ALTER TABLE odoo_modules ADD COLUMN IF NOT EXISTS enrichment_version VARCHAR(20);

-- Create index for finding modules needing enrichment
CREATE INDEX IF NOT EXISTS idx_modules_needs_enrichment
ON odoo_modules(enriched_at)
WHERE enriched_at IS NULL;

-- Create GIN index for array searches on tags and keywords
CREATE INDEX IF NOT EXISTS idx_modules_functional_tags
ON odoo_modules USING GIN (functional_tags);

CREATE INDEX IF NOT EXISTS idx_modules_keywords
ON odoo_modules USING GIN (keywords);

-- Comment on columns
COMMENT ON COLUMN odoo_modules.ai_description IS 'AI-generated description in English for better search';
COMMENT ON COLUMN odoo_modules.functional_tags IS 'Functional category tags (e.g., sales, accounting, inventory)';
COMMENT ON COLUMN odoo_modules.keywords IS 'Extracted keywords for improved search';
COMMENT ON COLUMN odoo_modules.enriched_at IS 'Timestamp when module was enriched';
COMMENT ON COLUMN odoo_modules.enrichment_version IS 'Version of enrichment process (e.g., v1.0)';
