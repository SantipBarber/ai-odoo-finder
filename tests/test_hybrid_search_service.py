"""
Tests para HybridSearchService.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.hybrid_search_service import HybridSearchService, SearchResult


class TestVectorSearch:
    """Tests para _vector_search."""

    @pytest.mark.asyncio
    async def test_vector_search_returns_results(self, mock_db):
        """Test básico de vector search."""

        # Mock DB response
        mock_db.execute = AsyncMock(return_value=Mock(
            fetchall=Mock(return_value=[
                Mock(
                    id=1,
                    technical_name='account_reconciliation',
                    name='Account Reconciliation',
                    summary='Reconcile accounts',
                    version='16.0',
                    depends=['account'],
                    github_stars=50,
                    similarity_score=0.92
                )
            ])
        ))

        service = HybridSearchService(mock_db)
        results = await service._vector_search(
            embedding=[0.1] * 1024,
            version='16.0',
            dependencies=None,
            limit=10
        )

        assert len(results) == 1
        assert results[0].technical_name == 'account_reconciliation'
        assert results[0].vector_score == 0.92
        assert results[0].vector_rank == 1

    @pytest.mark.asyncio
    async def test_vector_search_with_dependencies(self, mock_db):
        """Test vector search con filtro de dependencias."""

        mock_db.execute = AsyncMock(return_value=Mock(
            fetchall=Mock(return_value=[])
        ))

        service = HybridSearchService(mock_db)

        await service._vector_search(
            embedding=[0.1] * 1024,
            version='16.0',
            dependencies=['account', 'sale'],
            limit=10
        )

        # Verify SQL was called with deps parameter
        call_args = mock_db.execute.call_args
        assert call_args[0][1]['deps'] == ['account', 'sale']


class TestFullTextSearch:
    """Tests para _fulltext_search."""

    @pytest.mark.asyncio
    async def test_fulltext_search_returns_results(self, mock_db):
        """Test básico de BM25 search."""

        mock_db.execute = AsyncMock(return_value=Mock(
            fetchall=Mock(return_value=[
                Mock(
                    id=2,
                    technical_name='account_invoice',
                    name='Account Invoice',
                    summary='Invoice management',
                    version='16.0',
                    depends=['account'],
                    github_stars=30,
                    bm25_score=5.2
                )
            ])
        ))

        service = HybridSearchService(mock_db)
        results = await service._fulltext_search(
            query='invoice management',
            version='16.0',
            dependencies=None,
            limit=10
        )

        assert len(results) == 1
        assert results[0].technical_name == 'account_invoice'
        assert results[0].bm25_score == 5.2
        assert results[0].bm25_rank == 1


class TestRRF:
    """Tests para Reciprocal Rank Fusion."""

    def test_rrf_basic(self):
        """Test RRF con overlap simple."""

        service = HybridSearchService(Mock())

        vector_results = [
            SearchResult(id=1, technical_name='A', name='', summary='', version='16.0', vector_rank=1),
            SearchResult(id=2, technical_name='B', name='', summary='', version='16.0', vector_rank=2),
        ]

        fulltext_results = [
            SearchResult(id=2, technical_name='B', name='', summary='', version='16.0', bm25_rank=1),
            SearchResult(id=1, technical_name='A', name='', summary='', version='16.0', bm25_rank=3),
        ]

        fused = service._reciprocal_rank_fusion(vector_results, fulltext_results, k=60)

        # Module 2 (B) should rank first:
        # RRF(B) = 1/(60+2) + 1/(60+1) = 0.0161 + 0.0164 = 0.0325
        # RRF(A) = 1/(60+1) + 1/(60+3) = 0.0164 + 0.0159 = 0.0323

        assert fused[0].id == 2
        assert fused[0].technical_name == 'B'
        assert abs(fused[0].rrf_score - 0.0325) < 0.0001

    def test_rrf_no_overlap(self):
        """Test RRF sin overlap entre listas."""

        service = HybridSearchService(Mock())

        vector_results = [
            SearchResult(id=1, technical_name='A', name='', summary='', version='16.0', vector_rank=1),
        ]

        fulltext_results = [
            SearchResult(id=2, technical_name='B', name='', summary='', version='16.0', bm25_rank=1),
        ]

        fused = service._reciprocal_rank_fusion(vector_results, fulltext_results, k=60)

        # Ambos deberían estar, ordenados por RRF
        assert len(fused) == 2

        # RRF(A) = 1/(60+1) = 0.0164
        # RRF(B) = 1/(60+1) = 0.0164
        # (Empate, orden puede variar - depende de implementación)

    def test_rrf_empty_lists(self):
        """Test RRF con listas vacías."""

        service = HybridSearchService(Mock())

        fused = service._reciprocal_rank_fusion([], [], k=60)
        assert fused == []


class TestHybridSearch:
    """Tests de integración para search()."""

    @pytest.mark.asyncio
    async def test_search_combines_both_methods(self, mock_db):
        """Test que search() combina vector y BM25."""

        service = HybridSearchService(mock_db)

        # Mock both methods
        service._vector_search = AsyncMock(return_value=[
            SearchResult(id=1, technical_name='A', name='', summary='', version='16.0', vector_rank=1)
        ])

        service._fulltext_search = AsyncMock(return_value=[
            SearchResult(id=2, technical_name='B', name='', summary='', version='16.0', bm25_rank=1)
        ])

        results = await service.search(
            query='test query',
            query_embedding=[0.1] * 1024,
            version='16.0',
            limit=5
        )

        # Should have called both methods
        service._vector_search.assert_called_once()
        service._fulltext_search.assert_called_once()

        # Should return fused results
        assert len(results) <= 5

    @pytest.mark.asyncio
    async def test_search_validates_embedding_dimension(self, mock_db):
        """Test que valida dimensión del embedding."""

        service = HybridSearchService(mock_db)

        with pytest.raises(ValueError, match="Expected embedding dimension 1024"):
            await service.search(
                query='test',
                query_embedding=[0.1] * 512,  # Wrong dimension
                version='16.0'
            )


# Fixtures
@pytest.fixture
def mock_db():
    """Mock async database session."""
    db = Mock()
    db.execute = AsyncMock()
    return db
