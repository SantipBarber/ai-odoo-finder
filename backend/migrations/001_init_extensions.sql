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
