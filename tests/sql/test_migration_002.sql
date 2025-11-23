-- ============================================================================
-- Tests de Validación - Migration 002
-- ============================================================================

-- Test 1: Verify column exists
-- Expected: 1 row with data_type = 'tsvector'
SELECT
    'TEST 1: Column exists' as test_name,
    CASE
        WHEN COUNT(*) = 1 AND data_type = 'tsvector' THEN '✅ PASSED'
        ELSE '❌ FAILED'
    END as result
FROM information_schema.columns
WHERE table_name = 'odoo_modules'
  AND column_name = 'searchable_text'
GROUP BY data_type;

-- Test 2: Verify GIN index exists
-- Expected: 1 row with indexdef containing 'gin'
SELECT
    'TEST 2: GIN index exists' as test_name,
    CASE
        WHEN COUNT(*) = 1 AND indexdef ILIKE '%gin%' THEN '✅ PASSED'
        ELSE '❌ FAILED'
    END as result
FROM pg_indexes
WHERE tablename = 'odoo_modules'
  AND indexname = 'idx_modules_fulltext'
GROUP BY indexdef;

-- Test 3: Verify all records have searchable_text populated
-- Expected: 100% populated
SELECT
    'TEST 3: All records populated' as test_name,
    CASE
        WHEN COUNT(*) FILTER (WHERE searchable_text IS NULL) = 0 THEN '✅ PASSED'
        ELSE '❌ FAILED - ' || COUNT(*) FILTER (WHERE searchable_text IS NULL) || ' records missing'
    END as result
FROM odoo_modules;

-- Test 4: Verify trigger exists
-- Expected: 1 row
SELECT
    'TEST 4: Trigger exists' as test_name,
    CASE
        WHEN COUNT(*) = 1 THEN '✅ PASSED'
        ELSE '❌ FAILED'
    END as result
FROM pg_trigger
WHERE tgname = 'trigger_update_searchable_text';

-- Test 5: Verify function exists
-- Expected: 1 row
SELECT
    'TEST 5: Function exists' as test_name,
    CASE
        WHEN COUNT(*) = 1 THEN '✅ PASSED'
        ELSE '❌ FAILED'
    END as result
FROM pg_proc
WHERE proname = 'update_odoo_modules_searchable_text';

-- Test 6: Test full-text search works
-- Expected: At least some results for common query
SELECT
    'TEST 6: Full-text search works' as test_name,
    CASE
        WHEN COUNT(*) > 0 THEN '✅ PASSED - Found ' || COUNT(*) || ' results'
        ELSE '❌ FAILED - No results found'
    END as result
FROM odoo_modules
WHERE searchable_text @@ plainto_tsquery('english', 'account');

-- Test 7: Test ranking works
-- Expected: Results ordered by rank
SELECT
    'TEST 7: Ranking works' as test_name,
    CASE
        WHEN MAX(rank) > 0 THEN '✅ PASSED - Max rank: ' || ROUND(MAX(rank)::numeric, 4)
        ELSE '❌ FAILED'
    END as result
FROM (
    SELECT ts_rank_cd(searchable_text, query) as rank
    FROM odoo_modules,
         plainto_tsquery('english', 'account invoice') query
    WHERE searchable_text @@ query
    LIMIT 10
) ranked_results;

-- Summary
SELECT '===================' as summary;
SELECT 'VALIDATION COMPLETE' as summary;
SELECT '===================' as summary;
