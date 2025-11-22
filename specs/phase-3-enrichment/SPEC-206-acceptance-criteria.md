# SPEC-206: Acceptance Criteria & Testing

**ID:** SPEC-206
**Componente:** Validation & Testing
**Prioridad:** Alta
**Estimación:** 2 horas
**Dependencias:** SPEC-201, SPEC-202, SPEC-203, SPEC-204, SPEC-205

---

## 📋 Descripción

Criterios de aceptación completos para Fase 3, validación de enrichment, benchmark con datos enriquecidos, y Go/No-Go decision.

---

## ✅ Criterios de Aceptación

### AC-1: Schema Migration Aplicada

```yaml
Requisitos:
  - ✅ Migration 003 aplicada
  - ✅ 4 columnas nuevas creadas
  - ✅ 3 índices GIN creados
  - ✅ Trigger actualizado
```

**Validación:**
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name = 'odoo_modules'
  AND column_name IN ('ai_description', 'functional_tags', 'keywords', 'enrichment_metadata');
-- Expected: 4 rows
```

---

### AC-2: Enrichment Ejecutado

```yaml
Requisitos:
  - ✅ Pipeline ejecutado sin errores
  - ✅ >80% de módulos sin README enriquecidos
  - ✅ Todos los módulos tienen tags
  - ✅ Todos los módulos tienen keywords
```

**Validación:**
```sql
-- Count enrichment coverage
SELECT
    COUNT(*) as total_modules,
    COUNT(ai_description) FILTER (WHERE readme IS NULL OR LENGTH(readme) < 500) as enriched,
    COUNT(functional_tags) FILTER (WHERE array_length(functional_tags, 1) >= 2) as has_tags,
    COUNT(keywords) FILTER (WHERE array_length(keywords, 1) >= 5) as has_keywords
FROM odoo_modules;

-- Expected:
-- enriched / (modules without good README) > 0.80
-- has_tags = total_modules
-- has_keywords = total_modules
```

---

### AC-3: AI Descriptions Quality

```yaml
Requisitos:
  - ✅ Promedio >200 palabras por descripción
  - ✅ Sin markdown formatting
  - ✅ Contenido relevante (menciona funcionalidad)
```

**Validación:**
```python
def test_ai_descriptions_quality():
    """Valida calidad de descripciones generadas."""

    query = "SELECT ai_description FROM odoo_modules WHERE ai_description IS NOT NULL LIMIT 20"
    descriptions = db.execute(query).fetchall()

    for desc in descriptions:
        text = desc[0]

        # Length check
        word_count = len(text.split())
        assert word_count >= 100, "Description too short"

        # No markdown
        assert '##' not in text
        assert '**' not in text

        # Has meaningful content
        assert any(kw in text.lower() for kw in ['module', 'odoo', 'functionality', 'provides'])
```

---

### AC-4: Tags Assigned

```yaml
Requisitos:
  - ✅ 100% de módulos tienen 2+ tags
  - ✅ Tags son válidos (están en taxonomy)
  - ✅ Distribución razonable (no todos el mismo tag)
```

**Validación:**
```sql
-- Check tag coverage
SELECT
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE array_length(functional_tags, 1) >= 2) as has_min_tags,
    ROUND(100.0 * COUNT(*) FILTER (WHERE array_length(functional_tags, 1) >= 2) / COUNT(*), 1) as percentage
FROM odoo_modules;

-- Expected: percentage > 95%

-- Check tag distribution
SELECT tag, COUNT(*) as count
FROM odoo_modules, unnest(functional_tags) as tag
GROUP BY tag
ORDER BY count DESC
LIMIT 10;

-- Expected: Variety of tags (not all modules with same tag)
```

---

### AC-5: Keywords Extracted

```yaml
Requisitos:
  - ✅ Promedio 8-12 keywords por módulo
  - ✅ Keywords relevantes (no stopwords)
  - ✅ Include domain terms
```

**Validación:**
```sql
-- Average keywords per module
SELECT
    AVG(array_length(keywords, 1)) as avg_keywords,
    MIN(array_length(keywords, 1)) as min_keywords,
    MAX(array_length(keywords, 1)) as max_keywords
FROM odoo_modules
WHERE keywords IS NOT NULL;

-- Expected: avg_keywords between 8-12

-- Check domain keywords present
SELECT keyword, COUNT(*) as frequency
FROM odoo_modules, unnest(keywords) as keyword
WHERE keyword IN ('invoice', 'sale', 'stock', 'accounting', 'b2b', 'api')
GROUP BY keyword;

-- Expected: Common domain terms present
```

---

### AC-6: Embeddings Regenerated

```yaml
Requisitos:
  - ✅ Embeddings actualizados para módulos enriquecidos
  - ✅ Embeddings incluyen enriched data
```

**Validación:**
```sql
-- Check embeddings not null
SELECT COUNT(*) FROM odoo_modules WHERE embedding IS NULL;
-- Expected: 0

-- Check embeddings dimension
SELECT array_length(embedding, 1) FROM odoo_modules LIMIT 1;
-- Expected: 1024
```

---

### AC-7: Benchmark Muestra Mejora >10%

```yaml
Requisitos:
  - ✅ Benchmark ejecutado post-enrichment
  - ✅ Precision@3 > baseline Fase 2 + 10%
  - ✅ Mejoras especialmente en queries con sinónimos
```

**Proceso:**
```bash
# Ejecutar benchmark
python scripts/run_benchmark.py --search-mode hybrid

# Comparar con Fase 2
python scripts/compare_benchmarks.py \
    tests/results/hybrid_*.json \
    tests/results/enriched_*.json
```

**Output esperado:**
```
Hybrid (Fase 2):    P@3 = 52.0%
Enriched (Fase 3):  P@3 = 63.0%  (+11.0%)

✅ PHASE 3 SUCCESS: Improvement target met (+10%)
```

---

## 🧪 Test Suite Completo

```python
# tests/test_phase3_acceptance.py

class TestPhase3Acceptance:
    """Tests de aceptación para Fase 3."""

    @pytest.mark.asyncio
    async def test_schema_changes_applied(self, db_session):
        """AC-1: Schema actualizado."""

        columns = await db_session.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'odoo_modules'
              AND column_name IN ('ai_description', 'functional_tags', 'keywords', 'enrichment_metadata')
        """))

        assert len(columns.fetchall()) == 4

    @pytest.mark.asyncio
    async def test_enrichment_coverage(self, db_session):
        """AC-2: Cobertura de enrichment."""

        stats = await db_session.execute(text("""
            SELECT
                COUNT(*) as total,
                COUNT(ai_description) FILTER (WHERE readme IS NULL OR LENGTH(readme) < 500) as enriched,
                COUNT(*) FILTER (WHERE readme IS NULL OR LENGTH(readme) < 500) as needing_enrichment
            FROM odoo_modules
        """))

        row = stats.fetchone()

        # At least 80% of modules needing enrichment should be enriched
        coverage = row.enriched / row.needing_enrichment if row.needing_enrichment > 0 else 0
        assert coverage >= 0.80, f"Enrichment coverage {coverage:.1%} < 80%"

    @pytest.mark.asyncio
    async def test_all_modules_have_tags(self, db_session):
        """AC-4: Todos tienen tags."""

        result = await db_session.execute(text("""
            SELECT COUNT(*) FROM odoo_modules
            WHERE functional_tags IS NULL OR array_length(functional_tags, 1) < 2
        """))

        count_without_tags = result.scalar()
        assert count_without_tags < 100, f"{count_without_tags} modules without enough tags"

    @pytest.mark.asyncio
    async def test_keywords_quality(self, db_session):
        """AC-5: Keywords válidos."""

        result = await db_session.execute(text("""
            SELECT AVG(array_length(keywords, 1)) FROM odoo_modules WHERE keywords IS NOT NULL
        """))

        avg_keywords = result.scalar()
        assert 6 <= avg_keywords <= 15, f"Average keywords {avg_keywords} out of range [6-15]"

    def test_benchmark_improvement(self):
        """AC-7: Benchmark mejora >10%."""

        import json

        results_dir = Path("tests/results")

        hybrid_files = sorted(results_dir.glob("hybrid_*.json"))
        enriched_files = sorted(results_dir.glob("enriched_*.json"))

        assert len(enriched_files) > 0, "No enriched benchmark results"

        with open(hybrid_files[-1]) as f:
            hybrid = json.load(f)

        with open(enriched_files[-1]) as f:
            enriched = json.load(f)

        hybrid_p3 = hybrid['aggregate_metrics']['precision@3']
        enriched_p3 = enriched['aggregate_metrics']['precision@3']

        improvement = enriched_p3 - hybrid_p3

        assert improvement >= 0.10, \
            f"Improvement {improvement:.1%} < 10% target"
```

---

## 🚦 Go/No-Go Decision

### GO (Proceder a Fase 4) si:

```yaml
✅ Todos los tests de aceptación PASSED
✅ Precision@3 mejora >= 10% sobre Fase 2
✅ >80% de módulos enriquecidos
✅ Costo de API < $10
✅ Code review aprobado
```

### NO-GO (Iterar en Fase 3) si:

```yaml
❌ Mejora < 5% (insuficiente)
❌ AI descriptions de baja calidad
❌ Tags incorrectos (>20% de módulos)
❌ Costo > $20 (fuera de presupuesto)
```

---

## 📝 Checklist Final

```markdown
## Fase 3 - Checklist de Completitud

### Implementación
- [ ] Migration 003 aplicada
- [ ] AIDescriptionService implementado
- [ ] TaggingService implementado
- [ ] KeywordService implementado
- [ ] Enrichment Pipeline implementado

### Execution
- [ ] Pipeline ejecutado (full o dry-run validado)
- [ ] AI descriptions generadas (>80% success)
- [ ] Tags asignados (100% de módulos)
- [ ] Keywords extraídos (promedio 8-12)
- [ ] Embeddings regenerados

### Testing
- [ ] Unit tests passing
- [ ] Acceptance tests passing
- [ ] Benchmark ejecutado
- [ ] Mejora >= 10% confirmada

### Costs
- [ ] API costs < $10
- [ ] Budget tracking document updated

### Documentation
- [ ] Enrichment report generado
- [ ] Sample descriptions reviewed
- [ ] Learnings capturados
```

---

## 🎉 Definition of Done

```bash
# Verificar TODO completo
pytest tests/test_phase3_acceptance.py -v  # ✅ All passed
ls tests/results/enriched_*.json           # ✅ Exists
python scripts/compare_benchmarks.py ...   # ✅ Improvement >10%

# Commit
git add .
git commit -m "feat: Complete Phase 3 - Data Enrichment

- Add AI descriptions with Claude Haiku (1000+ modules)
- Implement functional tagging system
- Extract keywords with TF-IDF
- Regenerate embeddings with enriched data
- P@3 improved from 52% to 63% (+11%)

Co-Authored-By: Claude <noreply@anthropic.com>"

git tag phase-3-complete
git push origin main --tags
```

---

## 🔗 Siguiente Fase

Una vez Fase 3 completada:
→ **Proceder a Fase 4:** LLM Reranking
→ Specs: `specs/phase-4-reranking/`

---

**Estado:** 🔴 Pendiente de implementación
