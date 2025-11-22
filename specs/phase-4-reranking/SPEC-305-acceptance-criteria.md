# SPEC-305: Acceptance Criteria & Testing

**ID:** SPEC-305
**Componente:** Validation & Testing
**Prioridad:** Alta
**Estimación:** 2 horas
**Dependencias:** SPEC-301, SPEC-302, SPEC-303, SPEC-304

---

## 📋 Descripción

Criterios de aceptación completos para Fase 4, benchmark con reranking, análisis de mejoras, y Go/No-Go decision.

---

## ✅ Criterios de Aceptación

### AC-1: Reranking Service Implementado

```yaml
Requisitos:
  - ✅ RerankingService creado
  - ✅ Prompt V3 implementado
  - ✅ JSON parsing robusto
  - ✅ Error handling con fallback
  - ✅ Cost tracking funcional
```

**Validación:**
```python
service = RerankingService(api_key="...")

candidates = [...]  # 10 test modules
results = await service.rerank("test query", candidates)

assert len(results) > 0
assert all(hasattr(r, 'reranked_score') for r in results)
assert service.get_cost_stats()['total_requests'] > 0
```

---

### AC-2: Integration Completa

```yaml
Requisitos:
  - ✅ SearchService integrado
  - ✅ Feature flag `enable_reranking` funciona
  - ✅ Fallback a hybrid si reranking falla
  - ✅ Response incluye metadata
```

**Validación:**
```bash
# Con reranking
curl -X POST /api/search \
  -d '{"query": "portal documents", "version": "16.0", "enable_reranking": true}'

# Response debe incluir:
# "reranking_applied": true
# "modules[0].llm_reason": "..."
```

---

### AC-3: Benchmark Muestra Mejora >5%

```yaml
Requisitos:
  - ✅ Benchmark ejecutado con reranking
  - ✅ Precision@3 > baseline Fase 3 + 5%
  - ✅ MRR mejora significativamente
  - ✅ No regresiones en queries fáciles
```

**Proceso:**
```bash
# Ejecutar benchmark
python scripts/run_benchmark.py --search-mode hybrid --enable-reranking

# Comparar
python scripts/compare_benchmarks.py \
    tests/results/enriched_*.json \
    tests/results/reranked_*.json
```

**Output esperado:**
```
Enriched (Fase 3):  P@3 = 63.0%
Reranked (Fase 4):  P@3 = 68.0%  (+5.0%)

✅ PHASE 4 SUCCESS: Improvement target met (+5%)
```

---

### AC-4: Cost Under Budget

```yaml
Requisitos:
  - ✅ Cost per search < $0.001
  - ✅ Daily cost < $5 (con 1000 searches)
  - ✅ Cache hit rate > 50%
  - ✅ Budget monitoring activo
```

**Validación:**
```python
stats = cost_tracker.get_stats()

assert stats['avg_cost_per_search'] < 0.001
assert stats['cache_hit_rate'] > 0.5

# Check daily budget
daily_cost = get_daily_cost()
assert daily_cost < 5.0
```

---

### AC-5: Latency Acceptable

```yaml
Requisitos:
  - ✅ P50 latency < 800ms (hybrid + reranking)
  - ✅ P95 latency < 1500ms
  - ✅ P99 latency < 2500ms
```

**Validación:**
```python
latencies = []
for query in test_queries:
    start = time.time()
    await search_service.search_modules(query, "16.0", enable_reranking=True)
    latencies.append((time.time() - start) * 1000)

p50 = statistics.median(latencies)
p95 = statistics.quantiles(latencies, n=20)[18]

assert p50 < 800
assert p95 < 1500
```

---

## 🧪 Test Suite Completo

```python
# tests/test_phase4_acceptance.py

class TestPhase4Acceptance:
    """Tests de aceptación para Fase 4."""

    @pytest.mark.asyncio
    async def test_reranking_service_works(self):
        """AC-1: Servicio funcional."""

        service = RerankingService(api_key=settings.anthropic_api_key)

        candidates = [
            {'technical_name': 'test1', 'name': 'Test 1', 'summary': 'Test'},
            {'technical_name': 'test2', 'name': 'Test 2', 'summary': 'Test'}
        ]

        results = await service.rerank("test query", candidates, limit=2)

        assert len(results) == 2
        assert all(r.reranked_score > 0 for r in results)

    @pytest.mark.asyncio
    async def test_integration_with_search(self, db_session):
        """AC-2: Integración completa."""

        service = SearchService(db_session)

        results = await service.search_modules(
            query="portal documents",
            version="16.0",
            enable_reranking=True
        )

        assert len(results) > 0
        assert results[0].reranked == True

    @pytest.mark.asyncio
    async def test_fallback_on_error(self, db_session, monkeypatch):
        """AC-2: Fallback funciona."""

        def mock_rerank(*args, **kwargs):
            raise Exception("API error")

        monkeypatch.setattr(RerankingService, 'rerank', mock_rerank)

        service = SearchService(db_session)

        # Should not crash
        results = await service.search_modules(
            query="test",
            version="16.0",
            enable_reranking=True
        )

        assert len(results) > 0
        # Should have fallen back to hybrid results
        assert results[0].reranked == False

    def test_benchmark_improvement(self):
        """AC-3: Benchmark mejora >5%."""

        import json

        enriched_files = sorted(Path("tests/results").glob("enriched_*.json"))
        reranked_files = sorted(Path("tests/results").glob("reranked_*.json"))

        assert len(reranked_files) > 0

        with open(enriched_files[-1]) as f:
            enriched = json.load(f)

        with open(reranked_files[-1]) as f:
            reranked = json.load(f)

        enriched_p3 = enriched['aggregate_metrics']['precision@3']
        reranked_p3 = reranked['aggregate_metrics']['precision@3']

        improvement = reranked_p3 - enriched_p3

        assert improvement >= 0.05, f"Improvement {improvement:.1%} < 5%"

    def test_cost_under_budget(self):
        """AC-4: Costos bajo presupuesto."""

        stats = cost_tracker.get_stats()

        assert stats['avg_cost_per_search'] < 0.001

    @pytest.mark.asyncio
    async def test_latency_acceptable(self, db_session):
        """AC-5: Latencia aceptable."""

        service = SearchService(db_session)

        latencies = []

        for query in ["portal", "invoice", "stock", "sale", "account"]:
            start = time.time()

            await service.search_modules(
                query=query,
                version="16.0",
                enable_reranking=True
            )

            latency_ms = (time.time() - start) * 1000
            latencies.append(latency_ms)

        avg_latency = sum(latencies) / len(latencies)

        assert avg_latency < 1000, f"Avg latency {avg_latency}ms > 1000ms"
```

---

## 🚦 Go/No-Go Decision

### GO (Proceder a Fase 5) si:

```yaml
✅ Todos los tests de aceptación PASSED
✅ Precision@3 mejora >= 5% sobre Fase 3
✅ Cost per search < $0.001
✅ Latency P95 < 1500ms
✅ No regresiones (queries fáciles mantienen precision)
✅ Code review aprobado
```

### NO-GO (Revisar Fase 4) si:

```yaml
❌ Mejora < 3% (ROI cuestionable)
❌ Cost per search > $0.002 (demasiado caro)
❌ Latency P95 > 2500ms (UX inaceptable)
❌ Regresiones > 5% en queries easy
```

### Acciones en caso de NO-GO

**Si mejora < 3%:**
1. Tune prompt (probar variantes)
2. Aumentar candidates de 30 a 50
3. Ajustar score ranges
4. Si no mejora → **SKIP Fase 4**, usar solo Fase 3

**Si cost > $0.002:**
1. Implementar caching agresivo
2. Reducir candidates a 20
3. Smart reranking (skip simple queries)
4. Considerar batch processing

**Si latency > 2500ms:**
1. Reducir candidates a 20-30
2. Parallel processing de módulos
3. Cache más agresivo
4. Considerar async reranking

---

## 📝 Checklist Final

```markdown
## Fase 4 - Checklist de Completitud

### Implementación
- [ ] RerankingService implementado
- [ ] Prompt V3 optimizado
- [ ] SearchService integrado
- [ ] Feature flag configurado
- [ ] Caching implementado
- [ ] Cost tracking implementado

### Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Acceptance tests passing
- [ ] Benchmark ejecutado

### Resultados
- [ ] Precision@3 improvement: ____%  (target: >5%)
- [ ] Cost per search: $_____  (target: <$0.001)
- [ ] Latency P95: _____ms  (target: <1500ms)
- [ ] Cache hit rate: ____%  (target: >50%)

### Costs Analysis
- [ ] Daily cost projection: $_____
- [ ] Monthly cost projection: $_____
- [ ] ROI analysis documented

### Documentation
- [ ] Cost analysis report
- [ ] Performance analysis
- [ ] Learnings documented
```

---

## 🎉 Definition of Done

```bash
# Verificar TODO completo
pytest tests/test_phase4_acceptance.py -v  # ✅ All passed
ls tests/results/reranked_*.json           # ✅ Exists

# Commit
git add .
git commit -m "feat: Complete Phase 4 - LLM Reranking

- Implement two-stage retrieval with Claude Haiku
- Add intelligent reranking with optimized prompts
- Integrate caching for cost optimization
- P@3 improved from 63% to 68% (+5%)
- Cost: $0.0008 per search (with 70% cache hit rate)

Co-Authored-By: Claude <noreply@anthropic.com>"

git tag phase-4-complete
git push origin main --tags
```

---

## 🔗 Siguiente Fase

Una vez Fase 4 completada:
→ **Proceder a Fase 5:** Testing & Validation
→ Specs: `specs/phase-5-testing/`

---

**Estado:** 🔴 Pendiente de implementación
