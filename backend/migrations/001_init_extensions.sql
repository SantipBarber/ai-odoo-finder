-- AI-OdooFinder: Initialize PostgreSQL Extensions
-- This script runs automatically on first container startup

-- Enable pgVector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for fuzzy text search (optional but useful)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Verify extensions
DO $$
BEGIN
    RAISE NOTICE 'Extensions installed successfully:';
    RAISE NOTICE '  - vector (pgVector)';
    RAISE NOTICE '  - pg_trgm (Trigram)';
END $$;

-- ============================================================================
-- Base table
-- ============================================================================
-- Migrations 002-005 alter odoo_modules, so it has to exist before they run.
-- It mirrors the ORM model in backend/app/models.py; the API's init_db()
-- (create_all) then finds the table already there and leaves it alone.
-- Rollback scripts live in rollback/ so docker-entrypoint-initdb.d never
-- runs them.
CREATE TABLE IF NOT EXISTS odoo_modules (
    id SERIAL PRIMARY KEY,
    technical_name VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    version VARCHAR NOT NULL,
    depends VARCHAR[],
    author VARCHAR,
    license VARCHAR,
    summary VARCHAR,
    description TEXT,
    readme TEXT,
    repo_name VARCHAR NOT NULL,
    repo_url VARCHAR,
    module_path VARCHAR,
    github_stars INTEGER,
    github_issues_open INTEGER,
    last_commit_date TIMESTAMP WITHOUT TIME ZONE,
    embedding vector(2560),
    searchable_text tsvector,
    ai_description TEXT,
    functional_tags VARCHAR[],
    keywords VARCHAR[],
    enriched_at TIMESTAMP WITHOUT TIME ZONE,
    enrichment_version VARCHAR(20),
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

-- Same index names SQLAlchemy uses for index=True columns
CREATE INDEX IF NOT EXISTS ix_odoo_modules_id ON odoo_modules (id);
CREATE INDEX IF NOT EXISTS ix_odoo_modules_technical_name ON odoo_modules (technical_name);
CREATE INDEX IF NOT EXISTS ix_odoo_modules_version ON odoo_modules (version);
