# Quick Start Guide - Fase 4: LLM Reranking

**Tiempo estimado:** 4-6 horas
**Prerequisito:** ✅ Fase 3 completada (Data Enrichment)

---

## 🚀 Inicio Rápido (TL;DR)

```bash
# 1. Implementar RerankingService (usar código de SPEC-301)
# 2. Integrar en SearchService
# 3. Test con queries sample
python scripts/test_reranking.py --limit 10

# 4. Benchmark completo
python scripts/run_benchmark.py --search-mode hybrid --enable-reranking

# 5. Comparar
python scripts/compare_benchmarks.py \
    tests/results/enriched_*.json \
    tests/results/reranked_*.json
```

---

## 📋 Paso a Paso

### Paso 1: Implementar RerankingService (3 horas)

Crear `app/services/reranking_service.py` usando código completo de SPEC-301.

**Key points:**
- Claude Haiku para cost-efficiency
- Temperature = 0 para consistencia
- JSON parsing robusto
- Fallback si API falla

**Test básico:**
```python
service = RerankingService(api_key=settings.anthropic_api_key)

candidates = [
    {'technical_name': 'portal_document', 'name': 'Portal Document', ...},
    {'technical_name': 'portal', 'name': 'Portal', ...}
]

results = await service.rerank(
    query="portal documents",
    candidates=candidates,
    version="16.0"
)

print(results[0].technical_name)  # Should prioritize portal_document
print(results[0].reranked_score)  # e.g., 95
print(results[0].llm_reason)      # e.g., "Perfect match for..."
```

---

### Paso 2: Integrar en SearchService (1 hora)

Modificar `app/services/search_service.py` según SPEC-303.

**Cambios:**
```python
# 1. Añadir import
from app.services.reranking_service import RerankingService

# 2. Init en __init__
self.reranking_service = RerankingService(api_key=settings.anthropic_api_key)

# 3. Modificar search_modules
async def search_modules(
    ...,
    enable_reranking: bool = True  # NEW
):
    # Stage 1: Hybrid (top 50)
    candidates = await self.hybrid_search_service.search(..., limit=50)

    # Stage 2: Reranking (if enabled)
    if enable_reranking:
        return await self.reranking_service.rerank(query, candidates, limit=5)

    return candidates[:5]
```

---

### Paso 3: Testing Manual (30 min)

```python
# scripts/test_reranking.py

async def test():
    test_queries = [
        "portal clientes con documentos personalizados",
        "gestión de suscripciones recurrentes",
        "informes financieros personalizados"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")

        # Without reranking
        results_no_rerank = await search_service.search_modules(
            query, "16.0", enable_reranking=False
        )

        # With reranking
        results_reranked = await search_service.search_modules(
            query, "16.0", enable_reranking=True
        )

        print("Top 3 WITHOUT reranking:")
        for r in results_no_rerank[:3]:
            print(f"  - {r.technical_name}")

        print("Top 3 WITH reranking:")
        for r in results_reranked[:3]:
            print(f"  - {r.technical_name} (score: {r.reranked_score}, reason: {r.llm_reason})")
```

---

### Paso 4: Caching (Opcional, 30 min)

Implementar según SPEC-304 para reducir costos.

**Simple in-memory cache:**
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def _cache_key(query: str, module_ids_tuple):
    return hashlib.md5(f"{query}{module_ids_tuple}".encode()).hexdigest()

async def rerank(self, query, candidates, ...):
    # Check cache
    cache_key = _cache_key(query, tuple(c['id'] for c in candidates))

    if cache_key in self.cache:
        return self.cache[cache_key]

    # Call LLM
    results = await self._rerank_with_llm(...)

    # Save to cache
    self.cache[cache_key] = results

    return results
```

---

### Paso 5: Benchmark (1 hora)

```bash
# Ejecutar benchmark con reranking
python scripts/run_benchmark.py --search-mode hybrid --enable-reranking

# Output esperado:
# [1/20] Query: "facturación electrónica..."
#        WITHOUT reranking: P@3=0.667
#        WITH reranking:    P@3=1.000 ✅ (improved!)
#
# Aggregate: P@3=68.0% (vs 63.0% without reranking)
```

**Comparar:**
```bash
python scripts/compare_benchmarks.py \
    tests/results/enriched_20251122_*.json \
    tests/results/reranked_20251122_*.json

# Output:
# Enriched: P@3 = 63.0%
# Reranked: P@3 = 68.0% (+5.0%)
# ✅ PHASE 4 SUCCESS
```

---

### Paso 6: Cost Analysis (30 min)

```python
# Check costs
stats = reranking_service.get_cost_stats()

print(f"Total requests: {stats['total_requests']}")
print(f"Total cost: ${stats['total_cost_usd']}")
print(f"Avg cost/search: ${stats['avg_cost_per_request']}")

# Expected:
# Total requests: 20
# Total cost: $0.018
# Avg cost/search: $0.0009 ✅
```

**Daily projection:**
```
1,000 searches/day × $0.0009 = $0.90/day
30,000 searches/month = $27/month

With 70% cache hit rate:
$27 × 0.30 = $8/month ✅
```

---

## ✅ Definition of Done

```bash
# Tests
pytest tests/test_reranking_service.py -v
pytest tests/test_phase4_acceptance.py -v

# Benchmark
# P@3 improvement >= 5% ✅
# Cost < $0.001/search ✅

# Commit
git add .
git commit -m "feat: Complete Phase 4 - LLM Reranking"
git tag phase-4-complete
git push origin main --tags
```

---

## 🚨 Troubleshooting

### Error: "JSON parsing failed"

**Solución:**
- LLM a veces añade texto extra fuera del JSON
- Implementar regex para extraer solo el JSON array
- Ver `_parse_llm_response()` en SPEC-301

### Latency > 2s

**Solución:**
- Reducir candidates de 50 a 30
- Implementar caching
- Verificar que Claude Haiku (no Sonnet) está configurado

### Mejora < 3%

**Solución:**
- Tune prompt (probar variantes de SPEC-302)
- Verificar que enrichment (Fase 3) está aplicado
- Analizar queries específicas que no mejoran

### Cost > $0.002/search

**Solución:**
- Implementar caching (70%+ hit rate)
- Reducir max_tokens de 2000 a 1500
- Skip reranking en queries simples

---

## 💡 Tips

1. **Start with 10 queries:** Test con subset antes de full benchmark
2. **Monitor costs:** Check `get_cost_stats()` frecuentemente
3. **Cache early:** Implementar caching desde el inicio
4. **Log LLM reasons:** Útil para debugging y validation
5. **A/B test:** Si dudas, compara con/sin reranking side-by-side

---

## 📊 Expected Results

| Métrica | Fase 3 | Fase 4 | Mejora |
|---------|--------|--------|--------|
| Precision@3 | 63% | 68% | +5% ✅ |
| Precision@5 | 71% | 75% | +4% |
| MRR | 0.68 | 0.73 | +0.05 |
| Latency P95 | 400ms | 1200ms | +800ms |
| Cost/search | $0 | $0.0009 | Acceptable |

---

**Happy reranking! 🚀**
