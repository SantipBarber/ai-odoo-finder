# SPEC-303: Search Flow Integration

**ID:** SPEC-303
**Componente:** Search Service Integration
**Archivo:** `app/services/search_service.py` (modificar)
**Prioridad:** Alta
**Estimación:** 1 hora
**Dependencias:** SPEC-301

---

## 📋 Descripción

Integrar reranking en el flujo de búsqueda principal con feature flag para A/B testing y rollout gradual.

---

## 📐 Modified Search Service

```python
# app/services/search_service.py

from app.services.reranking_service import RerankingService

class SearchService:
    """Search service con two-stage retrieval."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.hybrid_search_service = HybridSearchService(db)
        self.reranking_service = RerankingService(
            api_key=settings.anthropic_api_key
        )  # NEW

    async def search_modules(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]] = None,
        limit: int = 5,
        search_mode: str = "hybrid",
        enable_reranking: bool = True  # NEW: Feature flag
    ) -> List[ModuleResult]:
        """
        Búsqueda con optional reranking.

        Args:
            ...existing params...
            enable_reranking: Si True, aplica LLM reranking (default True)

        Flow:
            1. Hybrid search (top 50)
            2. If enable_reranking: Rerank with LLM
            3. Return top N
        """

        # Stage 1: Fast Retrieval (Hybrid Search)
        candidate_limit = 50 if enable_reranking else limit

        hybrid_results = await self.hybrid_search_service.search(
            query=query,
            query_embedding=await self.embedding_service.get_embedding(query),
            version=version,
            dependencies=dependencies,
            limit=candidate_limit
        )

        # Stage 2: Precision Reranking (Optional)
        if enable_reranking and len(hybrid_results) > 0:
            logger.info(f"Reranking {len(hybrid_results)} candidates")

            reranked = await self.reranking_service.rerank(
                query=query,
                candidates=[r.to_dict() for r in hybrid_results],
                version=version,
                limit=limit
            )

            # Convert RerankResult to ModuleResult
            return [
                ModuleResult(
                    id=r.id,
                    technical_name=r.technical_name,
                    name=r.name,
                    summary=r.summary,
                    score=r.reranked_score,
                    rank=i + 1,
                    reranked=True,  # NEW field
                    llm_reason=r.llm_reason  # NEW field
                )
                for i, r in enumerate(reranked)
            ]

        # No reranking: return hybrid results
        for i, r in enumerate(hybrid_results[:limit]):
            r.reranked = False

        return hybrid_results[:limit]
```

---

## 🎛️ Feature Flags

### Configuration

```python
# app/config.py

class Settings(BaseSettings):
    # ... existing settings

    # Reranking configuration
    enable_reranking_default: bool = True
    reranking_candidate_limit: int = 50
    reranking_temperature: float = 0.0

    # A/B testing
    reranking_rollout_percentage: int = 100  # 0-100

    class Config:
        env_file = ".env"
```

### Environment Variables

```bash
# .env

# Reranking
ENABLE_RERANKING_DEFAULT=true
RERANKING_CANDIDATE_LIMIT=50
RERANKING_ROLLOUT_PERCENTAGE=50  # 50% of users get reranking
```

---

## 🔄 Rollout Strategy

### Phase 1: Canary (10%)

```python
import random

async def search_modules(...):
    # Gradual rollout
    enable_reranking = (
        settings.enable_reranking_default and
        random.randint(1, 100) <= settings.reranking_rollout_percentage
    )

    # ... rest of search
```

### Phase 2: A/B Test (50/50)

```python
# Log which variant was used
logger.info(
    "search_request",
    extra={
        "query": query,
        "reranking_enabled": enable_reranking,
        "user_id": user_id  # For consistent bucketing
    }
)
```

### Phase 3: Full Rollout (100%)

```python
# Set in .env
RERANKING_ROLLOUT_PERCENTAGE=100
```

---

## 📊 Response Format

### With Reranking

```json
{
  "modules": [
    {
      "technical_name": "portal_document",
      "name": "Portal Documents",
      "score": 95,
      "rank": 1,
      "reranked": true,
      "llm_reason": "Perfect match for portal + documents + customization",
      "original_rank": 4  // Was #4 before reranking
    }
  ],
  "search_mode": "hybrid",
  "reranking_applied": true,
  "count": 5
}
```

### Without Reranking (Fallback)

```json
{
  "modules": [
    {
      "technical_name": "portal",
      "score": 0.87,
      "rank": 1,
      "reranked": false
    }
  ],
  "reranking_applied": false
}
```

---

## 🧪 Tests

```python
# tests/test_search_integration.py

@pytest.mark.asyncio
async def test_search_with_reranking(db_session):
    """Test búsqueda con reranking."""

    service = SearchService(db_session)

    results = await service.search_modules(
        query="portal documents",
        version="16.0",
        enable_reranking=True
    )

    assert len(results) > 0
    assert results[0].reranked == True
    assert results[0].llm_reason is not None


@pytest.mark.asyncio
async def test_search_without_reranking(db_session):
    """Test búsqueda sin reranking."""

    service = SearchService(db_session)

    results = await service.search_modules(
        query="portal documents",
        version="16.0",
        enable_reranking=False
    )

    assert len(results) > 0
    assert results[0].reranked == False


@pytest.mark.asyncio
async def test_reranking_fallback_on_error(db_session, monkeypatch):
    """Test fallback si reranking falla."""

    # Mock reranking service to fail
    def mock_rerank(*args, **kwargs):
        raise Exception("API error")

    monkeypatch.setattr(RerankingService, 'rerank', mock_rerank)

    service = SearchService(db_session)

    # Should not crash, return hybrid results
    results = await service.search_modules(
        query="test",
        version="16.0",
        enable_reranking=True
    )

    assert len(results) > 0
```

---

## ✅ Criterios de Aceptación

- ✅ Reranking integrado en SearchService
- ✅ Feature flag `enable_reranking` funciona
- ✅ Fallback a hybrid si reranking falla
- ✅ Response incluye metadata de reranking
- ✅ Tests integration passing

---

## 🔗 Siguiente Paso

→ [SPEC-304: Cost Optimization](./SPEC-304-cost-optimization.md)

---

**Estado:** 🔴 Pendiente
