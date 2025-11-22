# Quick Start Guide - Fase 2: Hybrid Search

**Tiempo estimado:** 6-8 horas
**Prioridad:** Implementar en orden (1 → 2 → 3 → 4 → 5)
**Prerequisito:** ✅ Fase 1 completada

---

## 🚀 Inicio Rápido (TL;DR)

```bash
# 1. Backup BD
pg_dump ai_odoo_finder > backup_before_phase2.sql

# 2. Aplicar migration
psql ai_odoo_finder < migrations/002_add_fulltext_search.sql

# 3. Implementar HybridSearchService
# Ver SPEC-102

# 4. Integrar en SearchService
# Ver SPEC-104

# 5. Ejecutar benchmark
python scripts/run_benchmark.py --search-mode hybrid

# 6. Comparar resultados
python scripts/compare_benchmarks.py \
    tests/results/baseline_*.json \
    tests/results/hybrid_*.json
```

---

## 📋 Checklist de Implementación

### Paso 1: Preparación y Backup (15 min)

```bash
# 1. Crear branch
git checkout -b phase-2-hybrid-search

# 2. CRÍTICO: Backup de BD
pg_dump -h localhost -U postgres ai_odoo_finder > \
    backups/before_phase2_$(date +%Y%m%d_%H%M%S).sql

# 3. Verificar que Fase 1 está completa
ls tests/results/baseline_*.json  # Debe existir
```

**Checklist:**
- [ ] Branch creado
- [ ] Backup de BD realizado
- [ ] Baseline de Fase 1 disponible

---

### Paso 2: Database Migration (1 hora)

**Objetivo:** Añadir full-text search a PostgreSQL

#### 2.1 Crear Migration SQL

```bash
# Copiar template desde SPEC-101
mkdir -p migrations
```

Crear archivo `migrations/002_add_fulltext_search.sql` con el contenido de SPEC-101.

#### 2.2 Testing en Desarrollo

```bash
# Aplicar en BD de desarrollo PRIMERO
psql -h localhost -U postgres ai_odoo_finder_dev < \
    migrations/002_add_fulltext_search.sql

# Verificar que funcionó
psql -h localhost -U postgres ai_odoo_finder_dev -c "
    SELECT COUNT(*) FROM odoo_modules WHERE searchable_text IS NOT NULL;
"
# Debe retornar el total de módulos
```

#### 2.3 Validar Full-Text Search

```sql
-- Test query
SELECT technical_name,
       ts_rank_cd(searchable_text, query) as rank
FROM odoo_modules,
     plainto_tsquery('english', 'account reconciliation') query
WHERE searchable_text @@ query
  AND version = '16.0'
ORDER BY rank DESC
LIMIT 10;
```

**Debe retornar:** Resultados ordenados por relevancia

#### 2.4 Aplicar a Producción

```bash
# Solo si test en dev fue exitoso
psql -h localhost -U postgres ai_odoo_finder < \
    migrations/002_add_fulltext_search.sql
```

**Checklist:**
- [ ] Migration SQL creada
- [ ] Aplicada en dev sin errores
- [ ] Full-text search validada
- [ ] Aplicada en producción
- [ ] searchable_text 100% poblado

---

### Paso 3: Implementar HybridSearchService (3 horas)

**Archivo:** `app/services/hybrid_search_service.py`

#### 3.1 Crear Estructura Base

```bash
touch app/services/hybrid_search_service.py
```

#### 3.2 Copiar Código de SPEC-102

Ver SPEC-102 para implementación completa de:
- Clase `SearchResult` (dataclass)
- Clase `HybridSearchService`
- Métodos: `search()`, `_vector_search()`, `_fulltext_search()`, `_reciprocal_rank_fusion()`

**Puntos clave:**
1. Vector search usa `embedding <=> :embedding`
2. BM25 usa `searchable_text @@ plainto_tsquery()`
3. RRF formula: `1/(k + rank)` con k=60

#### 3.3 Tests Unitarios

```bash
touch tests/test_hybrid_search_service.py
```

Implementar al menos:
- `test_vector_search_returns_results`
- `test_fulltext_search_returns_results`
- `test_rrf_basic`
- `test_rrf_no_overlap`
- `test_search_combines_both_methods`

```bash
# Ejecutar tests
pytest tests/test_hybrid_search_service.py -v --cov
```

**Checklist:**
- [ ] `hybrid_search_service.py` creado
- [ ] SearchResult dataclass implementada
- [ ] HybridSearchService implementada
- [ ] RRF correcto matemáticamente
- [ ] Tests unitarios passing (>90% coverage)

---

### Paso 4: Integrar en SearchService (1.5 horas)

**Archivo:** `app/services/search_service.py` (modificar existente)

#### 4.1 Modificar SearchService

```python
# Añadir import
from app.services.hybrid_search_service import HybridSearchService

# Modificar __init__
def __init__(self, db: AsyncSession):
    self.db = db
    self.embedding_service = EmbeddingService()
    self.hybrid_search_service = HybridSearchService(db)  # NEW

# Añadir parámetro search_mode
async def search_modules(
    self,
    query: str,
    version: str,
    dependencies: Optional[List[str]] = None,
    limit: int = 5,
    search_mode: str = "hybrid"  # NEW
):
    # ... routing logic (ver SPEC-104)
```

#### 4.2 Implementar Routing

Ver SPEC-104 para implementación completa de:
- `_hybrid_search()`
- `_vector_search()`
- `_bm25_search()`

#### 4.3 Tests de Integración

```python
# tests/test_search_service_integration.py

@pytest.mark.asyncio
async def test_search_mode_hybrid(db_session):
    service = SearchService(db_session)

    results = await service.search_modules(
        query="account reconciliation",
        version="16.0",
        search_mode="hybrid"
    )

    assert len(results) > 0
    assert results[0].score is not None
```

**Checklist:**
- [ ] SearchService modificado
- [ ] search_mode parámetro añadido
- [ ] Los 3 modos funcionan (hybrid, vector, bm25)
- [ ] Integration tests passing
- [ ] Backward compatible (sin search_mode funciona)

---

### Paso 5: Benchmark y Validación (2 horas)

#### 5.1 Modificar Script de Benchmark

```python
# scripts/run_benchmark.py

# Añadir argumento
parser.add_argument(
    "--search-mode",
    choices=["vector", "bm25", "hybrid"],
    default="hybrid"
)

# Pasar a BenchmarkRunner
runner = BenchmarkRunner(db, search_mode=args.search_mode)
```

#### 5.2 Ejecutar Benchmark

```bash
# Ejecutar con hybrid search
python scripts/run_benchmark.py --search-mode hybrid

# Output esperado:
# → tests/results/hybrid_20251122_HHMMSS.json
```

#### 5.3 Crear Script de Comparación

Ver SPEC-105 para `scripts/compare_benchmarks.py` completo.

#### 5.4 Comparar Resultados

```bash
python scripts/compare_benchmarks.py \
    tests/results/baseline_20251122_*.json \
    tests/results/hybrid_20251122_*.json
```

**Output esperado:**
```
================================================================================
BENCHMARK COMPARISON
================================================================================

Baseline:  P@3 = 35.0%
Hybrid:    P@3 = 52.0%  (+17.0%)

✅ PHASE 2 SUCCESS: Improvement target met (+15%)
```

**Checklist:**
- [ ] Benchmark script modificado
- [ ] Benchmark ejecutado sin errores
- [ ] Archivo hybrid_*.json generado
- [ ] Script de comparación creado
- [ ] Mejora >= 15% confirmada

---

### Paso 6: Tests de Aceptación (30 min)

```bash
# Ejecutar suite completa
pytest tests/test_phase2_acceptance.py -v
```

**Todos deben pasar:**
- `test_migration_applied`
- `test_all_modules_have_searchable_text`
- `test_gin_index_exists`
- `test_hybrid_search_works`
- `test_all_search_modes_work`
- `test_improvement_over_baseline`

**Checklist:**
- [ ] Todos los tests de aceptación PASSED
- [ ] No regresiones identificadas
- [ ] Latencia aceptable (<500ms P95)

---

## ✅ Definition of Done

```bash
# Verificar que TODO está completo
pytest tests/test_phase2_acceptance.py -v  # ✅ All passed
ls tests/results/hybrid_*.json             # ✅ Exists
python scripts/compare_benchmarks.py ...   # ✅ Improvement >15%

# Commit y tag
git add .
git commit -m "feat: Complete Phase 2 - Hybrid Search

- Add full-text search with tsvector + GIN
- Implement HybridSearchService with RRF
- Integrate into SearchService
- P@3 improved from 35% to 52% (+17%)

Co-Authored-By: Claude <noreply@anthropic.com>"

git tag phase-2-complete
git push origin main --tags
```

---

## 🚨 Troubleshooting

### Error: "column searchable_text does not exist"

**Causa:** Migration no aplicada

**Solución:**
```bash
psql ai_odoo_finder < migrations/002_add_fulltext_search.sql
```

### Error: "query doesn't use GIN index"

**Causa:** Query planner no usa índice

**Solución:**
```sql
ANALYZE odoo_modules;

-- Verificar con EXPLAIN
EXPLAIN ANALYZE
SELECT * FROM odoo_modules
WHERE searchable_text @@ plainto_tsquery('english', 'test');
```

### Mejora < 15%

**Causa:** RRF k subóptimo o BM25 no funciona bien

**Solución:**
```bash
# Tune k parameter
python scripts/tune_rrf_k.py  # Grid search k=30-90

# Verificar BM25 funciona
psql ai_odoo_finder -c "
    SELECT COUNT(*) FROM odoo_modules
    WHERE searchable_text @@ plainto_tsquery('english', 'account');
"
# Debe retornar > 0
```

### Latencia > 500ms

**Causa:** Índices no optimizados

**Solución:**
```sql
-- Rebuild índices
REINDEX INDEX idx_modules_fulltext;
VACUUM ANALYZE odoo_modules;

-- Verificar query plan
EXPLAIN ANALYZE [tu query]
```

---

## 🎯 Métricas de Éxito

Al completar Fase 2 deberías tener:

| Métrica | Baseline | Target | Real |
|---------|----------|--------|------|
| Precision@3 | ~35% | >50% | __% |
| Precision@5 | ~42% | >54% | __% |
| MRR | ~0.41 | >0.50 | ____ |
| Latencia P95 | ~200ms | <500ms | ___ms |

---

## 📞 Ayuda

**¿Bloqueado? Revisa:**
1. [SPEC-101](./SPEC-101-database-migration.md) - Migration
2. [SPEC-102](./SPEC-102-hybrid-search-service.md) - Hybrid Service
3. [SPEC-104](./SPEC-104-search-integration.md) - Integration
4. [SPEC-105](./SPEC-105-acceptance-criteria.md) - Acceptance

---

## 🎉 Próximos Pasos

Una vez Fase 2 completa:
→ **Proceder a Fase 3:** Data Enrichment
→ AI descriptions, functional tags, keywords

**Happy coding! 🚀**
