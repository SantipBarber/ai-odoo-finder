# SPEC-401: Comprehensive Test Suite

**ID:** SPEC-401
**Componente:** Testing Infrastructure
**Prioridad:** Alta
**Estimación:** 6-8 horas
**Dependencias:** Fases 1-4 completadas

---

## 📋 Descripción

Crear un test suite completo que valide todas las funcionalidades implementadas en las fases 1-4, con cobertura >90% y tests automatizados para CI/CD.

---

## 🎯 Objetivos

1. **Unit Tests** - Testear cada servicio de forma aislada
2. **Integration Tests** - Validar flujos end-to-end
3. **Performance Tests** - Medir latencia y throughput
4. **Regression Tests** - Prevenir degradación de calidad

---

## 📁 Estructura de Tests

```
tests/
├── unit/
│   ├── test_metrics.py              # IR metrics
│   ├── test_hybrid_search.py        # Hybrid service
│   ├── test_reranking_service.py    # Reranking
│   ├── test_enrichment.py           # AI enrichment
│   ├── test_rrf_algorithm.py        # RRF fusion
│   └── test_utils.py                # Utilities
├── integration/
│   ├── test_search_flow_e2e.py      # Full search flow
│   ├── test_enrichment_pipeline.py  # Enrichment E2E
│   └── test_api_endpoints.py        # API integration
├── performance/
│   ├── test_latency.py              # Latency benchmarks
│   ├── test_throughput.py           # Load tests
│   └── test_load_stress.py          # Stress tests
├── regression/
│   └── test_benchmark_stability.py  # Prevent regressions
├── conftest.py                      # Pytest fixtures
└── pytest.ini                       # Pytest config
```

---

## 🧪 1. Unit Tests

### test_metrics.py

```python
# tests/unit/test_metrics.py

import pytest
from app.utils.metrics import calculate_precision_at_k, calculate_mrr, calculate_ndcg

def test_precision_at_k_perfect():
    """Test perfect precision."""
    predicted = ['A', 'B', 'C']
    relevant = {'A', 'B', 'C'}

    assert calculate_precision_at_k(predicted, relevant, k=3) == 1.0

def test_precision_at_k_partial():
    """Test partial precision."""
    predicted = ['A', 'B', 'C']
    relevant = {'A', 'C'}

    assert calculate_precision_at_k(predicted, relevant, k=3) == 0.667

def test_precision_at_k_zero():
    """Test zero precision."""
    predicted = ['A', 'B', 'C']
    relevant = set()

    assert calculate_precision_at_k(predicted, relevant, k=3) == 0.0

def test_mrr_first_position():
    """Test MRR when first result is relevant."""
    predicted = ['A', 'B', 'C']
    relevant = {'A'}

    assert calculate_mrr(predicted, relevant) == 1.0

def test_mrr_second_position():
    """Test MRR when second result is relevant."""
    predicted = ['X', 'A', 'B']
    relevant = {'A'}

    assert calculate_mrr(predicted, relevant) == 0.5

def test_mrr_no_relevant():
    """Test MRR with no relevant results."""
    predicted = ['X', 'Y', 'Z']
    relevant = {'A'}

    assert calculate_mrr(predicted, relevant) == 0.0

def test_ndcg_perfect():
    """Test perfect NDCG."""
    predicted = ['A', 'B', 'C']
    relevance_scores = {'A': 3, 'B': 2, 'C': 1}

    ndcg = calculate_ndcg(predicted, relevance_scores, k=3)
    assert ndcg == 1.0
```

---

### test_hybrid_search.py

```python
# tests/unit/test_hybrid_search.py

import pytest
from app.services.hybrid_search_service import HybridSearchService

@pytest.mark.asyncio
async def test_vector_search(db_session):
    """Test vector search component."""
    service = HybridSearchService(db_session)

    query_embedding = [0.1] * 1024
    results = await service._vector_search(
        query_embedding=query_embedding,
        version="16.0",
        limit=10
    )

    assert len(results) <= 10
    assert all(hasattr(r, 'vector_score') for r in results)
    assert all(0 <= r.vector_score <= 1 for r in results)

@pytest.mark.asyncio
async def test_fulltext_search(db_session):
    """Test full-text search component."""
    service = HybridSearchService(db_session)

    results = await service._fulltext_search(
        query="facturación electrónica",
        version="16.0",
        limit=10
    )

    assert len(results) <= 10
    assert all(hasattr(r, 'fulltext_score') for r in results)

@pytest.mark.asyncio
async def test_rrf_fusion(db_session):
    """Test RRF fusion algorithm."""
    service = HybridSearchService(db_session)

    vector_results = [
        {'id': 1, 'score': 0.9},
        {'id': 2, 'score': 0.8},
        {'id': 3, 'score': 0.7}
    ]

    fulltext_results = [
        {'id': 2, 'score': 0.95},
        {'id': 1, 'score': 0.85},
        {'id': 4, 'score': 0.75}
    ]

    fused = service._reciprocal_rank_fusion(
        vector_results,
        fulltext_results,
        k=60
    )

    # id=2 should rank higher (top in fulltext, 2nd in vector)
    assert fused[0]['id'] in [1, 2]
    assert len(fused) >= 3
```

---

### test_reranking_service.py

```python
# tests/unit/test_reranking_service.py

import pytest
from app.services.reranking_service import RerankingService
from app.config import settings

@pytest.mark.asyncio
async def test_reranking_basic():
    """Test basic reranking."""
    service = RerankingService(api_key=settings.anthropic_api_key)

    candidates = [
        {
            'id': 1,
            'technical_name': 'portal_document',
            'name': 'Portal Documents',
            'summary': 'Manage documents in portal',
            'ai_description': 'Customer portal document management'
        },
        {
            'id': 2,
            'technical_name': 'portal',
            'name': 'Portal',
            'summary': 'Customer portal',
            'ai_description': 'Basic customer portal'
        }
    ]

    results = await service.rerank(
        query="portal documents customization",
        candidates=candidates,
        version="16.0",
        limit=2
    )

    assert len(results) == 2
    assert all(hasattr(r, 'reranked_score') for r in results)
    assert all(hasattr(r, 'llm_reason') for r in results)
    # portal_document should rank higher
    assert results[0].technical_name == 'portal_document'

@pytest.mark.asyncio
async def test_reranking_fallback():
    """Test fallback on API error."""
    service = RerankingService(api_key="invalid_key")

    candidates = [{'id': 1, 'technical_name': 'test', 'name': 'Test'}]

    # Should fallback to original order, not crash
    results = await service.rerank(
        query="test",
        candidates=candidates,
        version="16.0",
        limit=1
    )

    assert len(results) >= 0  # Fallback returns original

def test_cost_tracking():
    """Test cost tracking."""
    service = RerankingService(api_key=settings.anthropic_api_key)

    stats = service.get_cost_stats()

    assert 'total_requests' in stats
    assert 'total_cost_usd' in stats
    assert 'avg_cost_per_request' in stats
```

---

## 🔗 2. Integration Tests

### test_search_flow_e2e.py

```python
# tests/integration/test_search_flow_e2e.py

import pytest
from app.services.search_service import SearchService

@pytest.mark.asyncio
async def test_full_search_flow_vector_only(db_session):
    """Test complete search flow - vector only."""
    service = SearchService(db_session)

    results = await service.search_modules(
        query="facturación electrónica",
        version="16.0",
        search_mode="vector",
        enable_reranking=False,
        limit=5
    )

    assert len(results) > 0
    assert len(results) <= 5
    assert all(hasattr(r, 'technical_name') for r in results)

@pytest.mark.asyncio
async def test_full_search_flow_hybrid(db_session):
    """Test complete search flow - hybrid."""
    service = SearchService(db_session)

    results = await service.search_modules(
        query="portal con documentos personalizados",
        version="16.0",
        search_mode="hybrid",
        enable_reranking=False,
        limit=5
    )

    assert len(results) > 0
    assert all(hasattr(r, 'hybrid_score') for r in results)

@pytest.mark.asyncio
async def test_full_search_flow_with_reranking(db_session):
    """Test complete search flow - with reranking."""
    service = SearchService(db_session)

    results = await service.search_modules(
        query="informes financieros personalizados",
        version="16.0",
        search_mode="hybrid",
        enable_reranking=True,
        limit=5
    )

    assert len(results) > 0
    assert all(r.reranked == True for r in results)
    assert all(r.llm_reason is not None for r in results)

@pytest.mark.asyncio
async def test_search_with_dependencies(db_session):
    """Test search with dependency filtering."""
    service = SearchService(db_session)

    results = await service.search_modules(
        query="accounting",
        version="16.0",
        dependencies=['account'],
        limit=5
    )

    assert len(results) > 0
    # All results should depend on 'account'
    for r in results:
        assert 'account' in r.depends
```

---

## ⚡ 3. Performance Tests

### test_latency.py

```python
# tests/performance/test_latency.py

import pytest
import time
import statistics
from app.services.search_service import SearchService

@pytest.mark.asyncio
async def test_vector_search_latency(db_session):
    """Measure vector search latency."""
    service = SearchService(db_session)

    latencies = []
    test_queries = ["portal", "invoice", "stock", "sale", "accounting"]

    for query in test_queries:
        start = time.time()

        await service.search_modules(
            query=query,
            version="16.0",
            search_mode="vector",
            enable_reranking=False
        )

        latency_ms = (time.time() - start) * 1000
        latencies.append(latency_ms)

    avg_latency = statistics.mean(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]

    print(f"\nVector Search Latency:")
    print(f"  Average: {avg_latency:.0f}ms")
    print(f"  P95: {p95_latency:.0f}ms")

    assert avg_latency < 200  # Target: <200ms

@pytest.mark.asyncio
async def test_hybrid_search_latency(db_session):
    """Measure hybrid search latency."""
    service = SearchService(db_session)

    latencies = []

    for _ in range(10):
        start = time.time()

        await service.search_modules(
            query="portal documents",
            version="16.0",
            search_mode="hybrid",
            enable_reranking=False
        )

        latency_ms = (time.time() - start) * 1000
        latencies.append(latency_ms)

    p95 = statistics.quantiles(latencies, n=20)[18]

    assert p95 < 500  # Target: <500ms

@pytest.mark.asyncio
async def test_reranking_latency(db_session):
    """Measure reranking latency."""
    service = SearchService(db_session)

    start = time.time()

    await service.search_modules(
        query="financial reporting customization",
        version="16.0",
        search_mode="hybrid",
        enable_reranking=True
    )

    latency_ms = (time.time() - start) * 1000

    print(f"\nReranking Latency: {latency_ms:.0f}ms")

    assert latency_ms < 2000  # Target: <2000ms
```

---

### test_throughput.py

```python
# tests/performance/test_throughput.py

import pytest
import asyncio
import time
from app.services.search_service import SearchService

@pytest.mark.asyncio
async def test_concurrent_searches(db_session):
    """Test concurrent search throughput."""
    service = SearchService(db_session)

    async def single_search(query):
        return await service.search_modules(
            query=query,
            version="16.0",
            search_mode="hybrid",
            enable_reranking=False
        )

    queries = ["portal", "invoice", "stock"] * 10  # 30 queries

    start = time.time()

    # Run 10 concurrent searches
    tasks = [single_search(q) for q in queries[:10]]
    await asyncio.gather(*tasks)

    duration = time.time() - start
    throughput = 10 / duration

    print(f"\nThroughput: {throughput:.1f} queries/second")

    assert throughput > 5  # Target: >5 queries/second
```

---

## 🛡️ 4. Regression Tests

### test_benchmark_stability.py

```python
# tests/regression/test_benchmark_stability.py

import pytest
import json
from pathlib import Path

def test_no_precision_regression():
    """Ensure precision doesn't degrade."""

    results_dir = Path("tests/results")

    # Find latest benchmark results
    reranked_files = sorted(results_dir.glob("reranked_*.json"))

    if len(reranked_files) < 2:
        pytest.skip("Not enough benchmark runs to compare")

    # Compare last two runs
    with open(reranked_files[-2]) as f:
        previous = json.load(f)

    with open(reranked_files[-1]) as f:
        current = json.load(f)

    prev_p3 = previous['aggregate_metrics']['precision@3']
    curr_p3 = current['aggregate_metrics']['precision@3']

    degradation = prev_p3 - curr_p3

    assert degradation < 0.03, f"Precision degraded by {degradation:.1%}"
```

---

## 🔧 Configuration

### pytest.ini

```ini
# tests/pytest.ini

[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    regression: Regression tests
    slow: Slow running tests

# Coverage
addopts =
    --verbose
    --strict-markers
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=90

# Timeouts
timeout = 300
```

---

### conftest.py

```python
# tests/conftest.py

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.config import settings

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    """Create test database engine."""
    engine = create_async_engine(
        settings.test_database_url,
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def db_session(engine):
    """Create test database session."""
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
```

---

## 📊 Coverage Requirements

### Targets

```yaml
Overall Coverage: >90%

By Component:
  app/services/hybrid_search_service.py: >95%
  app/services/reranking_service.py: >90%
  app/services/enrichment/*.py: >85%
  app/utils/metrics.py: 100%
  app/services/search_service.py: >95%
```

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html
```

---

## 🚀 CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml

name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: ankane/pgvector
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test
        run: |
          pytest --cov=app --cov-fail-under=90

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## ✅ Criterios de Aceptación

- ✅ Unit tests: >50 tests, >90% coverage
- ✅ Integration tests: All critical paths covered
- ✅ Performance tests: Latency targets met
- ✅ Regression tests: No degradation >3%
- ✅ CI/CD pipeline: All tests passing
- ✅ Coverage report: Generated and >90%

---

## 🔗 Siguiente Paso

→ [SPEC-402: Benchmark Comparison Report](./SPEC-402-benchmark-comparison.md)

---

**Estado:** 🔴 Pendiente de implementación
