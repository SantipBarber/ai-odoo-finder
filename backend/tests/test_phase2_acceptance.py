"""
Tests de aceptación para Fase 2: Hybrid Search.
"""
import pytest
import json
from pathlib import Path
from sqlalchemy import text


class TestPhase2Acceptance:
    """Tests de aceptación para Fase 2."""

    def test_migration_applied(self, db_session):
        """AC-1: Migration aplicada correctamente."""

        # Check column exists
        result = db_session.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'odoo_modules' AND column_name = 'searchable_text'
        """))
        column_name = result.scalar()

        assert column_name == 'searchable_text', \
            "Column searchable_text does not exist"

    def test_all_modules_have_searchable_text(self, db_session):
        """AC-1: Todos los módulos tienen searchable_text poblado."""

        result = db_session.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(searchable_text) as populated
            FROM odoo_modules
        """))
        row = result.fetchone()

        assert row.total > 0, "No modules in database"
        assert row.total == row.populated, \
            f"Not all modules have searchable_text: {row.populated}/{row.total}"

    def test_gin_index_exists(self, db_session):
        """AC-1: Índice GIN creado correctamente."""

        result = db_session.execute(text("""
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'odoo_modules'
              AND indexname = 'idx_modules_fulltext'
        """))
        index_name = result.scalar()

        assert index_name == 'idx_modules_fulltext', \
            "GIN index idx_modules_fulltext does not exist"

    def test_hybrid_search_works(self, db_session):
        """AC-2, AC-3: Hybrid search funciona correctamente."""

        from backend.app.services.search_service import SearchService

        service = SearchService(db_session)

        results = service.search(
            query="account reconciliation",
            version="16.0",
            search_mode="hybrid"
        )

        assert len(results) > 0, "Hybrid search returned no results"
        assert results[0]['score'] is not None, "Results have no score"

        # Check that hybrid-specific scores are present
        if 'rrf_score' in results[0]:
            assert results[0]['rrf_score'] is not None

    def test_all_search_modes_work(self, db_session):
        """AC-3: Los 3 modos de búsqueda funcionan."""

        from backend.app.services.search_service import SearchService

        service = SearchService(db_session)
        query = "account invoice"
        version = "16.0"

        # Test each mode
        for mode in ["vector", "bm25", "hybrid"]:
            results = service.search(
                query=query,
                version=version,
                search_mode=mode
            )
            assert len(results) > 0, f"Mode '{mode}' returned no results"

            # Verify mode-specific scores
            if mode == "bm25":
                assert 'bm25_score' in results[0] or 'score' in results[0]
            elif mode == "vector":
                assert 'distance' in results[0] or 'score' in results[0]
            elif mode == "hybrid":
                # Hybrid might have all scores
                assert 'score' in results[0]

    def test_backward_compatibility(self, db_session):
        """AC-3: Backward compatibility mantenida."""

        from backend.app.services.search_service import SearchService

        service = SearchService(db_session)

        # Call without search_mode (should default to hybrid)
        results = service.search(
            query="account",
            version="16.0"
        )

        assert len(results) > 0, "Default search returned no results"

    def test_benchmark_results_exist(self):
        """AC-4: Archivos de benchmark existen."""

        results_dir = Path("tests/results")

        # Check for baseline
        baseline_files = list(results_dir.glob("baseline_*.json"))
        assert len(baseline_files) > 0, "No baseline benchmark results found"

        # Check for hybrid (optional, may not exist yet)
        hybrid_files = list(results_dir.glob("hybrid_*.json"))
        if len(hybrid_files) == 0:
            pytest.skip("Hybrid benchmark not run yet - run: python scripts/run_benchmark.py --search-mode hybrid")

    def test_improvement_over_baseline(self):
        """AC-4: Mejora >15% sobre baseline (si hybrid existe)."""

        results_dir = Path("tests/results")

        # Load most recent of each
        baseline_files = sorted(results_dir.glob("baseline_*.json"))
        hybrid_files = sorted(results_dir.glob("hybrid_*.json"))

        assert len(baseline_files) > 0, "No baseline results found"

        if len(hybrid_files) == 0:
            pytest.skip("Hybrid benchmark not run yet - run: python scripts/run_benchmark.py --search-mode hybrid")

        with open(baseline_files[-1]) as f:
            baseline = json.load(f)

        with open(hybrid_files[-1]) as f:
            hybrid = json.load(f)

        baseline_p3 = baseline['aggregate_metrics']['precision@3']
        hybrid_p3 = hybrid['aggregate_metrics']['precision@3']

        improvement = hybrid_p3 - baseline_p3

        print(f"\nBaseline P@3: {baseline_p3:.1%}")
        print(f"Hybrid P@3: {hybrid_p3:.1%}")
        print(f"Improvement: {improvement:+.1%}")

        assert improvement >= 0.15, \
            f"Improvement {improvement:.1%} < 15% target. Need to tune RRF k or check BM25."


# Fixtures
@pytest.fixture
def db_session():
    """Provide database session for tests."""
    from backend.app.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
