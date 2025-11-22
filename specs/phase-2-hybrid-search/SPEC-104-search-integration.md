# SPEC-104: Search Service Integration

**ID:** SPEC-104
**Componente:** Search Service Layer
**Archivo:** `app/services/search_service.py` (modificado)
**Prioridad:** Alta
**Estimación:** 1-2 horas
**Dependencias:** SPEC-101, SPEC-102

---

## 📋 Descripción

Integrar `HybridSearchService` en el `SearchService` principal, añadiendo un parámetro `search_mode` que permita alternar entre búsqueda vectorial pura, BM25 puro, o híbrida.

---

## 🎯 Objetivos

1. **Backward compatible:** No romper código existente
2. **Feature flag:** `search_mode` para A/B testing
3. **Default híbrido:** Nueva búsqueda por defecto
4. **Fácil rollback:** Poder volver a vector solo

---

## 📐 Cambios en SearchService

### Archivo Actual: `app/services/search_service.py`

```python
# ANTES (solo vector search)
class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()

    async def search_modules(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[ModuleResult]:
        # 1. Generate embedding
        query_embedding = await self.embedding_service.get_embedding(query)

        # 2. Vector search only
        sql = """
            SELECT *, 1 - (embedding <=> :query_vector) as similarity_score
            FROM odoo_modules
            WHERE version = :version
            ORDER BY embedding <=> :query_vector
            LIMIT :limit
        """
        # ... execute and return
```

### Archivo Modificado: `app/services/search_service.py`

```python
from app.services.hybrid_search_service import HybridSearchService
from app.services.embedding_service import EmbeddingService
from typing import List, Optional, Literal

SearchMode = Literal["vector", "bm25", "hybrid"]


class SearchService:
    """Servicio principal de búsqueda con soporte multi-modal."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.hybrid_search_service = HybridSearchService(db)

    async def search_modules(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]] = None,
        limit: int = 5,
        search_mode: SearchMode = "hybrid"  # NEW: default hybrid
    ) -> List[ModuleResult]:
        """
        Busca módulos usando el modo especificado.

        Args:
            query: Query de texto
            version: Versión Odoo
            dependencies: Filtro opcional
            limit: Número de resultados
            search_mode: Modo de búsqueda
                - "vector": Solo vector similarity (legacy)
                - "bm25": Solo full-text search
                - "hybrid": Vector + BM25 con RRF (recommended)

        Returns:
            Lista de módulos ordenados por relevancia

        Example:
            >>> service = SearchService(db)
            >>> results = await service.search_modules(
            ...     query="account reconciliation",
            ...     version="16.0",
            ...     search_mode="hybrid"
            ... )
        """

        # Generate embedding (needed for vector and hybrid)
        query_embedding = None
        if search_mode in ["vector", "hybrid"]:
            query_embedding = await self.embedding_service.get_embedding(query)

        # Route to appropriate search method
        if search_mode == "hybrid":
            return await self._hybrid_search(
                query=query,
                query_embedding=query_embedding,
                version=version,
                dependencies=dependencies,
                limit=limit
            )
        elif search_mode == "vector":
            return await self._vector_search(
                query_embedding=query_embedding,
                version=version,
                dependencies=dependencies,
                limit=limit
            )
        elif search_mode == "bm25":
            return await self._bm25_search(
                query=query,
                version=version,
                dependencies=dependencies,
                limit=limit
            )
        else:
            raise ValueError(f"Invalid search_mode: {search_mode}")

    async def _hybrid_search(self, query, query_embedding, version, dependencies, limit):
        """Hybrid search usando HybridSearchService."""

        results = await self.hybrid_search_service.search(
            query=query,
            query_embedding=query_embedding,
            version=version,
            dependencies=dependencies,
            limit=limit
        )

        # Convert SearchResult to ModuleResult
        return [
            ModuleResult(
                id=r.id,
                technical_name=r.technical_name,
                name=r.name,
                summary=r.summary,
                version=r.version,
                depends=r.depends,
                github_stars=r.github_stars,
                score=r.rrf_score,
                rank=r.final_rank
            )
            for r in results
        ]

    async def _vector_search(self, query_embedding, version, dependencies, limit):
        """Vector search only (legacy)."""

        results = await self.hybrid_search_service._vector_search(
            embedding=query_embedding,
            version=version,
            dependencies=dependencies,
            limit=limit
        )

        return [
            ModuleResult(
                id=r.id,
                technical_name=r.technical_name,
                name=r.name,
                summary=r.summary,
                version=r.version,
                depends=r.depends,
                github_stars=r.github_stars,
                score=r.vector_score,
                rank=r.vector_rank
            )
            for r in results
        ]

    async def _bm25_search(self, query, version, dependencies, limit):
        """BM25 full-text search only."""

        results = await self.hybrid_search_service._fulltext_search(
            query=query,
            version=version,
            dependencies=dependencies,
            limit=limit
        )

        return [
            ModuleResult(
                id=r.id,
                technical_name=r.technical_name,
                name=r.name,
                summary=r.summary,
                version=r.version,
                depends=r.depends,
                github_stars=r.github_stars,
                score=r.bm25_score,
                rank=r.bm25_rank
            )
            for r in results
        ]
```

---

## 🔧 Cambios en MCP Tool

### Archivo: `app/mcp/tools.py` (o donde esté definido)

```python
# ANTES
async def search_odoo_modules(
    query: str,
    version: str = "16.0",
    dependencies: Optional[List[str]] = None,
    limit: int = 5
) -> Dict:
    """Search Odoo modules."""

    service = SearchService(db)
    results = await service.search_modules(query, version, dependencies, limit)
    return {"modules": [r.dict() for r in results]}


# DESPUÉS
async def search_odoo_modules(
    query: str,
    version: str = "16.0",
    dependencies: Optional[List[str]] = None,
    limit: int = 5,
    search_mode: str = "hybrid"  # NEW parameter
) -> Dict:
    """
    Search Odoo modules using hybrid search (vector + BM25).

    Args:
        query: Search query
        version: Odoo version (e.g., "16.0")
        dependencies: Filter by dependencies
        limit: Max results
        search_mode: "hybrid" (default), "vector", or "bm25"

    Returns:
        Dict with modules list
    """

    service = SearchService(db)
    results = await service.search_modules(
        query=query,
        version=version,
        dependencies=dependencies,
        limit=limit,
        search_mode=search_mode
    )

    return {
        "modules": [r.dict() for r in results],
        "search_mode": search_mode,
        "count": len(results)
    }
```

---

## 🧪 Tests de Integración

```python
# tests/test_search_service_integration.py

import pytest
from app.services.search_service import SearchService


class TestSearchServiceIntegration:
    """Tests de integración para SearchService."""

    @pytest.mark.asyncio
    async def test_search_mode_hybrid(self, db_session):
        """Test búsqueda híbrida."""

        service = SearchService(db_session)

        results = await service.search_modules(
            query="account reconciliation",
            version="16.0",
            search_mode="hybrid"
        )

        assert len(results) > 0
        assert results[0].score is not None  # RRF score

    @pytest.mark.asyncio
    async def test_search_mode_vector(self, db_session):
        """Test búsqueda vectorial pura."""

        service = SearchService(db_session)

        results = await service.search_modules(
            query="account reconciliation",
            version="16.0",
            search_mode="vector"
        )

        assert len(results) > 0
        # Score debería ser similarity score [0-1]
        assert 0 <= results[0].score <= 1

    @pytest.mark.asyncio
    async def test_search_mode_bm25(self, db_session):
        """Test búsqueda BM25 pura."""

        service = SearchService(db_session)

        results = await service.search_modules(
            query="account reconciliation",
            version="16.0",
            search_mode="bm25"
        )

        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_invalid_search_mode(self, db_session):
        """Test modo inválido."""

        service = SearchService(db_session)

        with pytest.raises(ValueError, match="Invalid search_mode"):
            await service.search_modules(
                query="test",
                version="16.0",
                search_mode="invalid"
            )

    @pytest.mark.asyncio
    async def test_backward_compatibility(self, db_session):
        """Test que API antigua sigue funcionando."""

        service = SearchService(db_session)

        # Llamada sin search_mode (debería usar hybrid por default)
        results = await service.search_modules(
            query="account",
            version="16.0"
        )

        assert len(results) > 0
```

---

## 🎛️ Feature Flags y Configuration

### Environment Variables

```bash
# .env
SEARCH_MODE_DEFAULT=hybrid  # Options: hybrid, vector, bm25
ENABLE_HYBRID_SEARCH=true   # Kill switch
RRF_K_VALUE=60              # Tuning parameter
```

### Config Loading

```python
# app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings

    # Search configuration
    search_mode_default: str = "hybrid"
    enable_hybrid_search: bool = True
    rrf_k_value: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
```

### Usage in Service

```python
from app.config import settings

class SearchService:
    async def search_modules(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]] = None,
        limit: int = 5,
        search_mode: Optional[SearchMode] = None  # Optional now
    ):
        # Use config default if not specified
        if search_mode is None:
            search_mode = settings.search_mode_default

        # Check if hybrid is enabled
        if search_mode == "hybrid" and not settings.enable_hybrid_search:
            # Fallback to vector
            search_mode = "vector"

        # ... rest of implementation
```

---

## ✅ Criterios de Aceptación

### AC-1: Integration Completa
- ✅ `search_mode` parámetro añadido
- ✅ Los 3 modos funcionan (hybrid, vector, bm25)
- ✅ Default es "hybrid"

### AC-2: Backward Compatible
- ✅ Código existente sin `search_mode` funciona
- ✅ No breaking changes en API

### AC-3: Feature Flags
- ✅ Environment variables configuradas
- ✅ Kill switch para hybrid search
- ✅ Fallback a vector si híbrido disabled

### AC-4: Tests Passing
- ✅ Integration tests para cada modo
- ✅ Test de backward compatibility
- ✅ Test de error handling

---

## 🚀 Plan de Rollout

### Fase 1: Testing (Días 1-2)
```yaml
Ambiente: Development
search_mode_default: hybrid
enable_hybrid_search: true
```

### Fase 2: Canary (Día 3)
```yaml
Ambiente: Production
search_mode_default: vector  # Keep old behavior
enable_hybrid_search: true   # But make it available

# MCP tool: allow users to opt-in with search_mode="hybrid"
```

### Fase 3: Gradual Rollout (Día 4-5)
```yaml
# Change default for 10% of users
if random() < 0.1:
    search_mode = "hybrid"
else:
    search_mode = "vector"
```

### Fase 4: Full Rollout (Día 6+)
```yaml
search_mode_default: hybrid  # Everyone uses hybrid
```

---

## 📊 Monitoring

### Métricas a Trackear

```python
# Log cada búsqueda
logger.info(
    "search_request",
    extra={
        "query": query,
        "version": version,
        "search_mode": search_mode,
        "results_count": len(results),
        "execution_time_ms": execution_time,
        "first_result": results[0].technical_name if results else None
    }
)
```

### Dashboard Metrics

```
- Requests por search_mode (hybrid vs vector vs bm25)
- Avg latency por search_mode
- P50/P95/P99 latency
- Error rate por search_mode
- Top queries por search_mode
```

---

## 🔗 Siguiente Paso

Una vez completado este SPEC:
→ [SPEC-105: Acceptance Criteria & Benchmarking](./SPEC-105-acceptance-criteria.md)

---

**Estado:** 🔴 Pendiente de implementación
**Prerequisito:** SPEC-102 completado
**Blocker para:** SPEC-105
