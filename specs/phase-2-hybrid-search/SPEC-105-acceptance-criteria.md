# SPEC-105: Acceptance Criteria & Testing

**ID:** SPEC-105
**Componente:** Validation & Testing
**Prioridad:** Alta
**Estimación:** 2-3 horas
**Dependencias:** SPEC-101, SPEC-102, SPEC-104

---

## 📋 Descripción

Define los criterios de aceptación completos para la Fase 2, proceso de benchmark, análisis de mejoras, y validación de que la implementación híbrida mejora >15% sobre baseline.

---

## 🎯 Objetivos

1. **Validar mejora:** Precision@3 > baseline + 15%
2. **Performance:** Latencia < 400ms
3. **Quality:** Tests passing, sin regresiones
4. **Go/No-Go:** Decidir si proceder a Fase 3

---

## ✅ Criterios de Aceptación (Success Gate)

### AC-1: Migration Aplicada Exitosamente

```yaml
Requisitos:
  - ✅ Migration 002 aplicada sin errores
  - ✅ Columna searchable_text populated al 100%
  - ✅ Índice GIN creado y funcional
  - ✅ Trigger funciona en INSERT/UPDATE
```

**Validación:**
```sql
-- Test 1: Columna existe
SELECT COUNT(*) FROM information_schema.columns
WHERE table_name = 'odoo_modules' AND column_name = 'searchable_text';
-- Expected: 1

-- Test 2: Todos los registros poblados
SELECT
    COUNT(*) as total,
    COUNT(searchable_text) as populated
FROM odoo_modules;
-- Expected: total = populated

-- Test 3: Índice existe
SELECT indexname FROM pg_indexes
WHERE tablename = 'odoo_modules' AND indexname = 'idx_modules_fulltext';
-- Expected: 1 row
```

---

### AC-2: Hybrid Search Service Implementado

```yaml
Requisitos:
  - ✅ Clase HybridSearchService creada
  - ✅ Métodos _vector_search, _fulltext_search, _rrf implementados
  - ✅ Unit tests passing (>90% coverage)
  - ✅ Integration tests passing
```

**Validación:**
```bash
pytest tests/test_hybrid_search_service.py -v --cov=app/services/hybrid_search_service
# Expected: All tests passed, coverage >90%
```

---

### AC-3: Search Service Integrado

```yaml
Requisitos:
  - ✅ Parámetro search_mode añadido
  - ✅ Los 3 modos funcionan (hybrid, vector, bm25)
  - ✅ Backward compatible
  - ✅ Feature flags configurados
```

**Validación:**
```python
# Test manual
service = SearchService(db)

# Test hybrid
results_hybrid = await service.search_modules(
    query="account reconciliation",
    version="16.0",
    search_mode="hybrid"
)
assert len(results_hybrid) > 0

# Test vector
results_vector = await service.search_modules(
    query="account reconciliation",
    version="16.0",
    search_mode="vector"
)
assert len(results_vector) > 0

# Test BM25
results_bm25 = await service.search_modules(
    query="account reconciliation",
    version="16.0",
    search_mode="bm25"
)
assert len(results_bm25) > 0
```

---

### AC-4: Benchmark Muestra Mejora >15%

```yaml
Requisitos:
  - ✅ Benchmark ejecutado con search_mode="hybrid"
  - ✅ Precision@3 > baseline + 15 puntos porcentuales
  - ✅ Mejora estadísticamente significativa
  - ✅ No regresiones en queries fáciles
```

**Proceso:**

```bash
# 1. Ejecutar benchmark con hybrid search
python scripts/run_benchmark.py --search-mode hybrid

# 2. Comparar con baseline
python scripts/compare_benchmarks.py \
    tests/results/baseline_*.json \
    tests/results/hybrid_*.json

# 3. Validar mejora
```

**Output esperado:**
```
================================================================================
BENCHMARK COMPARISON
================================================================================

Baseline (Fase 1):
  Precision@3:  35.0%
  Precision@5:  42.0%
  MRR:          0.412

Hybrid (Fase 2):
  Precision@3:  52.0%  ✅ (+17.0 pp)
  Precision@5:  58.0%  ✅ (+16.0 pp)
  MRR:          0.524  ✅ (+0.112)

Improvement: 17.0% > 15.0% target ✅ PASSED
================================================================================
```

---

### AC-5: Performance Dentro de Target

```yaml
Requisitos:
  - ✅ Latencia P50 < 300ms
  - ✅ Latencia P95 < 500ms
  - ✅ Latencia P99 < 800ms
  - ✅ No más de 2x latencia de vector solo
```

**Validación:**
```python
# Performance test
import time
import statistics

latencies = []
for query in test_queries:
    start = time.time()
    await service.search_modules(query, "16.0", search_mode="hybrid")
    latency_ms = (time.time() - start) * 1000
    latencies.append(latency_ms)

p50 = statistics.median(latencies)
p95 = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
p99 = statistics.quantiles(latencies, n=100)[98]  # 99th percentile

assert p50 < 300, f"P50 latency {p50}ms > 300ms"
assert p95 < 500, f"P95 latency {p95}ms > 500ms"
assert p99 < 800, f"P99 latency {p99}ms > 800ms"
```

---

## 📊 Benchmark Execution

### Script Modificado

```python
# scripts/run_benchmark.py

import argparse

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--search-mode",
        choices=["vector", "bm25", "hybrid"],
        default="hybrid",
        help="Search mode to benchmark"
    )
    args = parser.parse_args()

    async with get_async_session() as db:
        runner = BenchmarkRunner(db, search_mode=args.search_mode)
        await runner.run()

if __name__ == '__main__':
    asyncio.run(main())
```

### Ejecutar Benchmarks

```bash
# Baseline (ya ejecutado en Fase 1)
# tests/results/baseline_YYYYMMDD.json

# Hybrid search
python scripts/run_benchmark.py --search-mode hybrid
# → tests/results/hybrid_YYYYMMDD.json

# Optional: BM25 solo (para comparación)
python scripts/run_benchmark.py --search-mode bm25
# → tests/results/bm25_YYYYMMDD.json
```

---

## 📈 Comparison Script

### Archivo: `scripts/compare_benchmarks.py`

```python
"""
Compara resultados de dos benchmarks.
"""
import json
import sys
from pathlib import Path


def load_benchmark(filepath: str) -> dict:
    """Carga resultados de benchmark."""
    with open(filepath, 'r') as f:
        return json.load(f)


def compare(baseline_path: str, comparison_path: str):
    """Compara dos benchmarks."""

    baseline = load_benchmark(baseline_path)
    comparison = load_benchmark(comparison_path)

    baseline_metrics = baseline['aggregate_metrics']
    comparison_metrics = comparison['aggregate_metrics']

    print("="*80)
    print("BENCHMARK COMPARISON")
    print("="*80)

    print(f"\nBaseline: {baseline_path}")
    print(f"  Precision@3:  {baseline_metrics['precision@3']:.1%}")
    print(f"  Precision@5:  {baseline_metrics['precision@5']:.1%}")
    print(f"  MRR:          {baseline_metrics['mrr']:.3f}")

    print(f"\nComparison: {comparison_path}")
    print(f"  Precision@3:  {comparison_metrics['precision@3']:.1%}")
    print(f"  Precision@5:  {comparison_metrics['precision@5']:.1%}")
    print(f"  MRR:          {comparison_metrics['mrr']:.3f}")

    # Calculate improvements
    p3_improvement = comparison_metrics['precision@3'] - baseline_metrics['precision@3']
    p5_improvement = comparison_metrics['precision@5'] - baseline_metrics['precision@5']
    mrr_improvement = comparison_metrics['mrr'] - baseline_metrics['mrr']

    print("\n" + "="*80)
    print("IMPROVEMENTS")
    print("="*80)
    print(f"Precision@3:  {p3_improvement:+.1%}  ", end="")
    print("✅ PASS" if p3_improvement >= 0.15 else "❌ FAIL (need +15%)")

    print(f"Precision@5:  {p5_improvement:+.1%}")
    print(f"MRR:          {mrr_improvement:+.3f}")

    # Per difficulty analysis
    print("\n" + "="*80)
    print("BY DIFFICULTY")
    print("="*80)

    for difficulty in ['easy', 'medium', 'hard']:
        baseline_diff = baseline['per_difficulty'][difficulty]
        comparison_diff = comparison['per_difficulty'][difficulty]

        improvement = comparison_diff['precision@3'] - baseline_diff['precision@3']

        print(f"{difficulty.capitalize():6s}: {baseline_diff['precision@3']:.1%} → "
              f"{comparison_diff['precision@3']:.1%} ({improvement:+.1%})")

    # Overall verdict
    print("\n" + "="*80)
    if p3_improvement >= 0.15:
        print("✅ PHASE 2 SUCCESS: Improvement target met (+15%)")
        print("→ Proceed to Phase 3: Data Enrichment")
        return 0
    else:
        print(f"❌ PHASE 2 NEEDS WORK: Only {p3_improvement:.1%} improvement")
        print("→ Tune RRF k parameter or investigate BM25 query performance")
        return 1


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python compare_benchmarks.py <baseline.json> <comparison.json>")
        sys.exit(1)

    sys.exit(compare(sys.argv[1], sys.argv[2]))
```

---

## 🧪 Test Suite Completo

### Archivo: `tests/test_phase2_acceptance.py`

```python
"""
Tests de aceptación para Fase 2.
"""
import pytest
from pathlib import Path
from sqlalchemy import text


class TestPhase2Acceptance:
    """Tests de aceptación para Fase 2."""

    @pytest.mark.asyncio
    async def test_migration_applied(self, db_session):
        """AC-1: Migration aplicada."""

        # Check column exists
        result = await db_session.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'odoo_modules' AND column_name = 'searchable_text'
        """))
        assert result.scalar() == 'searchable_text'

    @pytest.mark.asyncio
    async def test_all_modules_have_searchable_text(self, db_session):
        """AC-1: Todos los módulos poblados."""

        result = await db_session.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(searchable_text) as populated
            FROM odoo_modules
        """))
        row = result.fetchone()

        assert row.total > 0
        assert row.total == row.populated

    @pytest.mark.asyncio
    async def test_gin_index_exists(self, db_session):
        """AC-1: Índice GIN creado."""

        result = await db_session.execute(text("""
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'odoo_modules'
              AND indexname = 'idx_modules_fulltext'
        """))
        assert result.scalar() == 'idx_modules_fulltext'

    @pytest.mark.asyncio
    async def test_hybrid_search_works(self, db_session):
        """AC-2, AC-3: Hybrid search funcional."""

        from app.services.search_service import SearchService

        service = SearchService(db_session)

        results = await service.search_modules(
            query="account reconciliation",
            version="16.0",
            search_mode="hybrid"
        )

        assert len(results) > 0
        assert results[0].score is not None

    @pytest.mark.asyncio
    async def test_all_search_modes_work(self, db_session):
        """AC-3: Los 3 modos funcionan."""

        from app.services.search_service import SearchService

        service = SearchService(db_session)
        query = "account invoice"
        version = "16.0"

        # Test each mode
        for mode in ["vector", "bm25", "hybrid"]:
            results = await service.search_modules(
                query=query,
                version=version,
                search_mode=mode
            )
            assert len(results) > 0, f"Mode '{mode}' returned no results"

    def test_benchmark_results_exist(self):
        """AC-4: Benchmark ejecutado."""

        results_dir = Path("tests/results")
        hybrid_files = list(results_dir.glob("hybrid_*.json"))

        assert len(hybrid_files) > 0, "No hybrid benchmark results found"

    def test_improvement_over_baseline(self):
        """AC-4: Mejora >15% sobre baseline."""

        import json

        results_dir = Path("tests/results")

        # Load most recent of each
        baseline_files = sorted(results_dir.glob("baseline_*.json"))
        hybrid_files = sorted(results_dir.glob("hybrid_*.json"))

        assert len(baseline_files) > 0, "No baseline results"
        assert len(hybrid_files) > 0, "No hybrid results"

        with open(baseline_files[-1]) as f:
            baseline = json.load(f)

        with open(hybrid_files[-1]) as f:
            hybrid = json.load(f)

        baseline_p3 = baseline['aggregate_metrics']['precision@3']
        hybrid_p3 = hybrid['aggregate_metrics']['precision@3']

        improvement = hybrid_p3 - baseline_p3

        assert improvement >= 0.15, \
            f"Improvement {improvement:.1%} < 15% target"
```

---

## 🚦 Go/No-Go Decision

### GO (Proceder a Fase 3) si:

```yaml
✅ Todos los tests de aceptación PASSED
✅ Precision@3 mejora >= 15% sobre baseline
✅ Latencia P95 < 500ms
✅ No regresiones en queries easy
✅ Code review aprobado
```

### NO-GO (Iterar en Fase 2) si:

```yaml
❌ Tests fallan
❌ Mejora < 10% (insuficiente)
❌ Latencia P95 > 1000ms (muy lento)
❌ Regresiones significativas (>5%) en queries easy
```

### Acciones en caso de NO-GO

**Si mejora < 10%:**
1. Tune RRF parameter k (grid search 30-90)
2. Verificar que BM25 está funcionando (check searchable_text)
3. Revisar pesos de campos (A, B, C, D)
4. Considerar custom dictionary en vez de 'english'

**Si latencia > 1000ms:**
1. Verificar que índices están siendo usados (EXPLAIN ANALYZE)
2. Reducir top_candidates de 50 a 30
3. Optimizar queries SQL
4. VACUUM y ANALYZE de BD

**Si regresiones:**
1. Analizar queries específicas que regresaron
2. Ajustar pesos o RRF k
3. Considerar fallback a vector para queries específicas

---

## 📝 Checklist Final de Fase 2

```markdown
## Fase 2 - Checklist de Completitud

### Implementación
- [ ] Migration 002 aplicada a BD
- [ ] HybridSearchService implementado
- [ ] RRF algorithm correcto
- [ ] SearchService integrado
- [ ] Feature flags configurados

### Testing
- [ ] Unit tests passing (hybrid_search_service)
- [ ] Integration tests passing (search_service)
- [ ] Acceptance tests passing (test_phase2_acceptance)
- [ ] Benchmark ejecutado con search_mode="hybrid"

### Resultados
- [ ] tests/results/hybrid_YYYYMMDD.json generado
- [ ] Comparison script ejecutado
- [ ] Precision@3 improvement: ____%  (target: >15%)
- [ ] Latencia P95: _____ms  (target: <500ms)

### Documentación
- [ ] Failure patterns actualizados
- [ ] Mejoras documentadas
- [ ] Learnings capturados

### Aprobaciones
- [ ] Code review completado
- [ ] Benchmark results validados
- [ ] Go/No-Go decision: GO / NO-GO

### Deploy
- [ ] Migration aplicada a producción
- [ ] Feature flag: search_mode_default = "hybrid"
- [ ] Monitoring configurado
```

---

## 🎉 Definición de Done

**Fase 2 está DONE cuando:**

1. ✅ Todos los checkboxes marcados
2. ✅ Tests de aceptación pasan
3. ✅ Mejora >= 15% confirmada
4. ✅ Go/No-Go decision es GO
5. ✅ Commit pushed con tag `phase-2-complete`

```bash
git add .
git commit -m "feat: Complete Phase 2 - Hybrid Search

- Add PostgreSQL full-text search with tsvector + GIN index
- Implement HybridSearchService (Vector + BM25 + RRF)
- Integrate with SearchService via search_mode parameter
- Benchmark results: P@3 improved from 35% to 52% (+17%)
- All acceptance tests passing

Co-Authored-By: Claude <noreply@anthropic.com>"

git tag phase-2-complete
git push origin main --tags
```

---

## 🔗 Siguiente Fase

Una vez Fase 2 completada exitosamente:
→ **Proceder a Fase 3:** Data Enrichment
→ Specs: `specs/phase-3-enrichment/` (próximamente)

---

**Estado:** 🔴 Pendiente de implementación
**Prerequisito:** SPEC-101, SPEC-102, SPEC-104 completados
