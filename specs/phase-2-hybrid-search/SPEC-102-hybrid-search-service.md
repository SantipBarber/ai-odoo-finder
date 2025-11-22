# SPEC-102: Hybrid Search Service

**ID:** SPEC-102
**Componente:** Search Service Layer
**Archivo:** `app/services/hybrid_search_service.py`
**Prioridad:** Alta
**Estimación:** 4-5 horas
**Dependencias:** SPEC-101 (Migration aplicada)

---

## 📋 Descripción

Implementar servicio que ejecute búsquedas híbridas combinando:
1. **Vector similarity search** (semántica)
2. **BM25 full-text search** (keywords)
3. **Reciprocal Rank Fusion (RRF)** para fusionar resultados

---

## 🎯 Objetivos

1. **Modular:** Separar responsabilidades (vector, BM25, fusion)
2. **Testeable:** Cada método unit testeable independientemente
3. **Configurable:** Parámetros ajustables (k, limit, weights)
4. **Performante:** < 400ms para búsquedas combinadas

---

## 🏗️ Arquitectura del Servicio

```
HybridSearchService
├── __init__(db: AsyncSession)
├── search()                      # Main entry point
│   ├── _vector_search()         # Vector similarity (pgVector)
│   ├── _fulltext_search()       # BM25 (tsvector)
│   └── _reciprocal_rank_fusion() # RRF fusion
└── Helper methods
    ├── _normalize_scores()
    └── _deduplicate_results()
```

---

## 📐 API Specification

### Clase Principal

```python
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Resultado de búsqueda híbrida."""
    id: int
    technical_name: str
    name: str
    summary: str
    version: str
    depends: List[str]
    github_stars: int

    # Scores individuales
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None
    rrf_score: Optional[float] = None

    # Rankings
    vector_rank: Optional[int] = None
    bm25_rank: Optional[int] = None
    final_rank: Optional[int] = None


class HybridSearchService:
    """
    Servicio de búsqueda híbrida que combina vector similarity y BM25.

    Usa Reciprocal Rank Fusion (RRF) para combinar rankings de ambas
    estrategias de búsqueda.
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            db: Sesión async de SQLAlchemy
        """
        self.db = db

    async def search(
        self,
        query: str,
        query_embedding: List[float],
        version: str,
        dependencies: Optional[List[str]] = None,
        limit: int = 5,
        k: int = 60,
        top_candidates: int = 50
    ) -> List[SearchResult]:
        """
        Ejecuta búsqueda híbrida y retorna top N resultados.

        Args:
            query: Query de texto del usuario
            query_embedding: Vector embedding de la query (1024 dims)
            version: Versión Odoo (e.g., "16.0")
            dependencies: Filtro opcional de dependencias
            limit: Número de resultados finales a retornar
            k: Parámetro RRF (default 60, valores típicos 30-90)
            top_candidates: Cuántos candidatos extraer de cada método

        Returns:
            Lista de SearchResult ordenados por RRF score (descendente)

        Raises:
            ValueError: Si query_embedding dimensión incorrecta
            DatabaseError: Si query SQL falla

        Example:
            >>> service = HybridSearchService(db)
            >>> results = await service.search(
            ...     query="account reconciliation",
            ...     query_embedding=[0.1, 0.2, ...],  # 1024 dims
            ...     version="16.0",
            ...     limit=5
            ... )
            >>> results[0].technical_name
            'account_reconciliation_widget'
            >>> results[0].rrf_score
            0.0325
        """
        ...

    async def _vector_search(
        self,
        embedding: List[float],
        version: str,
        dependencies: Optional[List[str]],
        limit: int
    ) -> List[SearchResult]:
        """
        Ejecuta búsqueda por similitud vectorial.

        Args:
            embedding: Vector de query
            version: Versión Odoo
            dependencies: Filtro de dependencias
            limit: Número de resultados

        Returns:
            Lista de SearchResult con vector_score y vector_rank

        SQL Query:
            SELECT *, 1 - (embedding <=> :embedding) as similarity
            FROM odoo_modules
            WHERE version = :version
            ORDER BY embedding <=> :embedding
            LIMIT :limit
        """
        ...

    async def _fulltext_search(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]],
        limit: int
    ) -> List[SearchResult]:
        """
        Ejecuta búsqueda BM25 full-text.

        Args:
            query: Query de texto
            version: Versión Odoo
            dependencies: Filtro de dependencias
            limit: Número de resultados

        Returns:
            Lista de SearchResult con bm25_score y bm25_rank

        SQL Query:
            SELECT *, ts_rank_cd(searchable_text, query) as rank
            FROM odoo_modules, plainto_tsquery('english', :query) query
            WHERE searchable_text @@ query
              AND version = :version
            ORDER BY rank DESC
            LIMIT :limit
        """
        ...

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[SearchResult],
        fulltext_results: List[SearchResult],
        k: int = 60
    ) -> List[SearchResult]:
        """
        Fusiona dos listas de resultados usando RRF.

        Formula:
            RRF_score(d) = Σ 1/(k + rank_i(d))

        Args:
            vector_results: Resultados de vector search
            fulltext_results: Resultados de full-text search
            k: Constante de suavizado (default 60)

        Returns:
            Lista fusionada ordenada por rrf_score descendente

        Example:
            >>> vector = [SearchResult(id=1, vector_rank=1),
            ...           SearchResult(id=2, vector_rank=2)]
            >>> fulltext = [SearchResult(id=2, bm25_rank=1),
            ...             SearchResult(id=1, bm25_rank=3)]
            >>> fused = service._reciprocal_rank_fusion(vector, fulltext, k=60)
            >>> fused[0].id  # Module 2 should rank first
            2
            >>> fused[0].rrf_score
            0.0323  # 1/(60+2) + 1/(60+1) = 0.0161 + 0.0164
        """
        ...
```

---

## 💻 Implementación Completa

### Archivo: `app/services/hybrid_search_service.py`

```python
"""
Hybrid Search Service: Combines vector similarity and BM25 full-text search.
"""
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Resultado de búsqueda con múltiples scores."""

    id: int
    technical_name: str
    name: str
    summary: str
    version: str
    depends: List[str] = field(default_factory=list)
    github_stars: int = 0

    # Scores
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None
    rrf_score: Optional[float] = None

    # Rankings
    vector_rank: Optional[int] = None
    bm25_rank: Optional[int] = None
    final_rank: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'technical_name': self.technical_name,
            'name': self.name,
            'summary': self.summary,
            'version': self.version,
            'depends': self.depends,
            'github_stars': self.github_stars,
            'vector_score': self.vector_score,
            'bm25_score': self.bm25_score,
            'rrf_score': self.rrf_score,
            'vector_rank': self.vector_rank,
            'bm25_rank': self.bm25_rank,
            'final_rank': self.final_rank
        }


class HybridSearchService:
    """Servicio de búsqueda híbrida (Vector + BM25)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        query: str,
        query_embedding: List[float],
        version: str,
        dependencies: Optional[List[str]] = None,
        limit: int = 5,
        k: int = 60,
        top_candidates: int = 50
    ) -> List[SearchResult]:
        """Ejecuta búsqueda híbrida con RRF."""

        logger.info(f"Hybrid search: query='{query}', version={version}, limit={limit}")

        # Validate embedding
        if len(query_embedding) != 1024:
            raise ValueError(f"Expected embedding dimension 1024, got {len(query_embedding)}")

        # 1. Vector similarity search
        logger.debug(f"Executing vector search (top {top_candidates})")
        vector_results = await self._vector_search(
            embedding=query_embedding,
            version=version,
            dependencies=dependencies,
            limit=top_candidates
        )
        logger.debug(f"Vector search returned {len(vector_results)} results")

        # 2. BM25 full-text search
        logger.debug(f"Executing BM25 search (top {top_candidates})")
        fulltext_results = await self._fulltext_search(
            query=query,
            version=version,
            dependencies=dependencies,
            limit=top_candidates
        )
        logger.debug(f"BM25 search returned {len(fulltext_results)} results")

        # 3. Reciprocal Rank Fusion
        logger.debug(f"Fusing results with RRF (k={k})")
        fused_results = self._reciprocal_rank_fusion(
            vector_results=vector_results,
            fulltext_results=fulltext_results,
            k=k
        )

        # 4. Return top N
        final_results = fused_results[:limit]
        logger.info(f"Hybrid search complete: returning {len(final_results)} results")

        return final_results

    async def _vector_search(
        self,
        embedding: List[float],
        version: str,
        dependencies: Optional[List[str]],
        limit: int
    ) -> List[SearchResult]:
        """Búsqueda vectorial por similitud."""

        query_sql = text("""
            SELECT
                id,
                technical_name,
                name,
                summary,
                version,
                depends,
                github_stars,
                1 - (embedding <=> :embedding::vector) as similarity_score
            FROM odoo_modules
            WHERE version = :version
                AND (:deps::text[] IS NULL OR depends && :deps)
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """)

        result = await self.db.execute(query_sql, {
            "embedding": embedding,
            "version": version,
            "deps": dependencies,
            "limit": limit
        })

        rows = result.fetchall()

        return [
            SearchResult(
                id=row.id,
                technical_name=row.technical_name,
                name=row.name or '',
                summary=row.summary or '',
                version=row.version,
                depends=row.depends or [],
                github_stars=row.github_stars or 0,
                vector_score=float(row.similarity_score),
                vector_rank=i + 1
            )
            for i, row in enumerate(rows)
        ]

    async def _fulltext_search(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]],
        limit: int
    ) -> List[SearchResult]:
        """Búsqueda BM25 full-text."""

        query_sql = text("""
            SELECT
                id,
                technical_name,
                name,
                summary,
                version,
                depends,
                github_stars,
                ts_rank_cd(searchable_text, query) as bm25_score
            FROM odoo_modules,
                 plainto_tsquery('english', :query) query
            WHERE version = :version
                AND (:deps::text[] IS NULL OR depends && :deps)
                AND searchable_text @@ query
            ORDER BY bm25_score DESC
            LIMIT :limit
        """)

        result = await self.db.execute(query_sql, {
            "query": query,
            "version": version,
            "deps": dependencies,
            "limit": limit
        })

        rows = result.fetchall()

        return [
            SearchResult(
                id=row.id,
                technical_name=row.technical_name,
                name=row.name or '',
                summary=row.summary or '',
                version=row.version,
                depends=row.depends or [],
                github_stars=row.github_stars or 0,
                bm25_score=float(row.bm25_score),
                bm25_rank=i + 1
            )
            for i, row in enumerate(rows)
        ]

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[SearchResult],
        fulltext_results: List[SearchResult],
        k: int = 60
    ) -> List[SearchResult]:
        """
        Fusiona resultados con RRF.

        Formula: RRF_score(d) = Σ 1/(k + rank_i(d))
        """

        # Build index of all modules by ID
        modules: Dict[int, SearchResult] = {}
        rrf_scores: Dict[int, float] = {}

        # Add vector results
        for result in vector_results:
            module_id = result.id
            modules[module_id] = result
            rrf_scores[module_id] = 1.0 / (k + result.vector_rank)

        # Add BM25 results
        for result in fulltext_results:
            module_id = result.id

            if module_id in modules:
                # Module in both lists - merge
                modules[module_id].bm25_score = result.bm25_score
                modules[module_id].bm25_rank = result.bm25_rank
                rrf_scores[module_id] += 1.0 / (k + result.bm25_rank)
            else:
                # Module only in BM25 list
                modules[module_id] = result
                rrf_scores[module_id] = 1.0 / (k + result.bm25_rank)

        # Set RRF scores
        for module_id, score in rrf_scores.items():
            modules[module_id].rrf_score = score

        # Sort by RRF score
        sorted_modules = sorted(
            modules.values(),
            key=lambda m: m.rrf_score or 0,
            reverse=True
        )

        # Set final ranks
        for i, module in enumerate(sorted_modules, 1):
            module.final_rank = i

        return sorted_modules
```

---

## 🧪 Tests Unitarios

### Archivo: `tests/test_hybrid_search_service.py`

```python
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
```

---

## ✅ Criterios de Aceptación

### AC-1: Service Implementado
- ✅ Archivo `hybrid_search_service.py` creado
- ✅ Clase HybridSearchService con todos los métodos
- ✅ Type hints completos

### AC-2: Vector Search Funciona
- ✅ `_vector_search()` retorna resultados
- ✅ Usa índice pgVector
- ✅ Filtra por versión y dependencias

### AC-3: BM25 Search Funciona
- ✅ `_fulltext_search()` retorna resultados
- ✅ Usa índice GIN y searchable_text
- ✅ Ranking por ts_rank_cd

### AC-4: RRF Correcto
- ✅ Formula RRF implementada correctamente
- ✅ Maneja overlap entre listas
- ✅ Maneja listas sin overlap

### AC-5: Tests Passing
- ✅ 10+ unit tests
- ✅ Coverage > 90%
- ✅ Tests de casos edge

---

## 🔗 Siguiente Paso

Una vez completado este SPEC:
→ [SPEC-103: RRF Algorithm Deep Dive](./SPEC-103-rrf-algorithm.md) (opcional, para detalles matemáticos)
→ [SPEC-104: Search Service Integration](./SPEC-104-search-integration.md)

---

**Estado:** 🔴 Pendiente de implementación
**Prerequisito:** SPEC-101 completado
**Blocker para:** SPEC-104
