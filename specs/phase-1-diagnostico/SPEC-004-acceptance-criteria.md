# SPEC-004: Acceptance Criteria & Validation

**ID:** SPEC-004
**Componente:** Validation & Acceptance
**Prioridad:** Alta
**Estimación:** 1 hora
**Dependencias:** SPEC-001, SPEC-002, SPEC-003

---

## 📋 Descripción

Define los criterios de aceptación completos para la Fase 1, checklist de validación, y proceso de análisis de patrones de fallo que determinan si la fase se completó exitosamente y si el sistema está listo para las mejoras de Fase 2.

---

## 🎯 Objetivo

Establecer criterios claros y medibles que determinen:

1. **Success Gate:** ¿La Fase 1 está completa?
2. **Go/No-Go Decision:** ¿Procedemos a Fase 2?
3. **Failure Patterns:** ¿Qué tipos de búsquedas fallan?

---

## ✅ Criterios de Aceptación (Success Gate)

### AC-1: Benchmark Suite Completo

**Criterio:**
```yaml
Requisitos:
  - ✅ Archivo tests/benchmark_queries.json existe
  - ✅ Contiene exactamente 20 queries
  - ✅ Todas las queries tienen campos requeridos
  - ✅ Al menos 5 categorías diferentes
  - ✅ Distribución: 5 easy, 10 medium, 5 hard
  - ✅ Al menos 3 versiones Odoo
  - ✅ Todos los expected_modules existen en BD
```

**Validación:**
```bash
python -m pytest tests/test_benchmark_queries.py::test_benchmark_suite_complete -v
```

**Resultado esperado:** PASSED

---

### AC-2: Script Ejecutable

**Criterio:**
```yaml
Requisitos:
  - ✅ scripts/run_benchmark.py existe y es ejecutable
  - ✅ Se ejecuta sin errores con las 20 queries
  - ✅ Genera archivo JSON en tests/results/
  - ✅ Tiempo de ejecución < 5 minutos
  - ✅ Maneja errores gracefully (no crashes)
```

**Validación:**
```bash
time python scripts/run_benchmark.py
echo $?  # Debe ser 0 (exit code success)
ls tests/results/baseline_*.json  # Debe existir
```

**Resultado esperado:** Exit code 0, archivo creado

---

### AC-3: Métricas Calculadas

**Criterio:**
```yaml
Requisitos:
  - ✅ Archivo results JSON contiene aggregate_metrics
  - ✅ Métricas presentes: precision@3, precision@5, recall@10, mrr
  - ✅ Todas las métricas en rango [0, 1]
  - ✅ Métricas por categoría calculadas
  - ✅ Métricas por dificultad calculadas
  - ✅ Detailed results con 20 entries
```

**Validación:**
```bash
python -m pytest tests/test_benchmark_results.py::test_metrics_present -v
```

**Resultado esperado:** PASSED

---

### AC-4: Baseline Documentado

**Criterio:**
```yaml
Requisitos:
  - ✅ Precision@3 baseline documentado
  - ✅ Valor esperado: < 40% (confirma necesidad mejoras)
  - ✅ Diferencia por dificultad clara (easy > medium > hard)
  - ✅ Al menos 1 categoría con P@3 > 50%
  - ✅ Al menos 1 categoría con P@3 < 30%
```

**Validación:** Manual review del archivo JSON

**Resultado esperado:**
```json
{
  "aggregate_metrics": {
    "precision@3": 0.25-0.40  // Rango esperado
  },
  "per_difficulty": {
    "easy": {"precision@3": 0.50-0.70},
    "medium": {"precision@3": 0.20-0.40},
    "hard": {"precision@3": 0.05-0.20}
  }
}
```

---

### AC-5: Patrones de Fallo Identificados

**Criterio:**
```yaml
Requisitos:
  - ✅ Documento tests/results/failure_analysis.md existe
  - ✅ Documenta al menos 5 patrones de fallo
  - ✅ Cada patrón incluye:
      - Descripción del problema
      - Ejemplo de query que falla
      - Módulo esperado vs retornado
      - Hipótesis de por qué falla
      - Propuesta de mejora
```

**Validación:** Manual review del documento

**Resultado esperado:** Ver template abajo

---

## 📊 Failure Analysis Template

### Archivo: `tests/results/failure_analysis.md`

```markdown
# Análisis de Patrones de Fallo - Fase 1 Baseline

**Fecha:** 2025-11-22
**Benchmark:** baseline_20251122_103045.json
**Precision@3 Global:** 35.0%

---

## Patrón 1: Búsquedas Multi-Concepto

### Descripción
Queries que combinan múltiples conceptos funcionales (e.g., "portal + documentos")
fallan porque el embedding promedia los conceptos y pierde especificidad.

### Ejemplo
```yaml
Query: "portal clientes con documentos personalizados"
Expected: ["portal_document", "dms_portal"]
Returned: ["portal", "website_portal", "customer_portal"]
```

### Análisis
- Vector embedding captura "portal" fuertemente
- "Documentos personalizados" se diluye en el embedding
- Módulos genéricos de portal rankean más alto

### Hipótesis de Mejora
- **Hybrid Search (Fase 2):** BM25 puede capturar "document" como keyword
- **Reranking (Fase 4):** LLM puede entender la combinación de conceptos

### Frecuencia
4/20 queries (20%)

---

## Patrón 2: Sinónimos y Terminología Específica

### Descripción
Queries usando términos de negocio (e.g., "B2B", "trazabilidad") no matchean
con technical_names (e.g., "sale_partner_type", "stock_lot").

### Ejemplo
```yaml
Query: "separar flujos B2B y B2C"
Expected: ["sale_b2b_b2c", "portal_partner_type"]
Returned: ["sale_order_type", "sale_workflow", "crm_business_type"]
```

### Análisis
- Embedding de "B2B" no es semánticamente cercano a "partner_type"
- README/summary no usan explícitamente "B2B" y "B2C"

### Hipótesis de Mejora
- **Enrichment (Fase 3):** Añadir tags "B2B", "B2C" a módulos relevantes
- **Terminology table (Fase 3):** Mapear sinónimos comunes

### Frecuencia
5/20 queries (25%)

---

## Patrón 3: Módulos Sin README

### Descripción
Módulos con solo technical_name y summary corto tienen embeddings pobres
y no rankean bien para búsquedas semánticas.

### Ejemplo
```yaml
Query: "informes financieros personalizados"
Expected: ["mis_builder", "account_financial_report"]
Returned: ["account_report", "account_invoice_report", "base_report"]

Nota: "mis_builder" no tiene README, solo summary: "Management Information System"
```

### Análisis
- 40% de módulos no tienen README indexado
- Embeddings basados solo en summary (1-2 líneas) son débiles
- Queries específicas no matchean con summaries genéricos

### Hipótesis de Mejora
- **AI Descriptions (Fase 3):** Generar descripciones con Claude para módulos sin README
- **Functional Tags (Fase 3):** Añadir contexto estructurado

### Frecuencia
6/20 queries (30%)

---

## Patrón 4: Coincidencias Exactas vs Semánticas

### Descripción
Queries con términos exactos del technical_name (e.g., "facturación electrónica" → "l10n_es_facturae")
funcionan bien, pero el sistema no prioriza coincidencias exactas sobre semánticas.

### Ejemplo - FALLA
```yaml
Query: "account reconciliation"
Expected: ["account_reconciliation_widget"]
Returned: ["account_payment", "account_banking", "account_reconciliation_widget"]

Posición del esperado: #3 (debería ser #1)
```

### Análisis
- El término "reconciliation" aparece en technical_name exacto
- Pero otros módulos con embeddings similares rankean más alto
- No hay boost para keyword exact matches

### Hipótesis de Mejora
- **Hybrid Search (Fase 2):** BM25 dará boost a exact matches
- **RRF fusion (Fase 2):** Combinará señales de vector + keyword

### Frecuencia
3/20 queries (15%)

---

## Patrón 5: Versión Específica con Pocas Opciones

### Descripción
Queries para versiones nuevas (18.0, 19.0) tienen menos módulos indexados,
resultando en matches de menor calidad.

### Ejemplo
```yaml
Query: "gestión de suscripciones recurrentes"
Version: 18.0
Expected: ["sale_subscription", "contract_recurring"]
Returned: ["sale_order", "account_invoice_recurring", "sale_payment"]

Nota: solo 150 módulos en v18.0 vs 800 en v16.0
```

### Análisis
- Menos datos en versiones nuevas → embeddings menos representativos
- Módulos genéricos dominan por falta de opciones específicas

### Hipótesis de Mejora
- **Data Quality (Fase 3):** Asegurar cobertura consistente en todas las versiones
- **Considerar App Store scraping** si OCA coverage es insuficiente

### Frecuencia
2/20 queries (10%)

---

## Resumen de Patrones

| Patrón | Frecuencia | Mejora Propuesta | Fase |
|--------|------------|------------------|------|
| Multi-concepto | 20% | Hybrid + Reranking | 2, 4 |
| Sinónimos | 25% | Enrichment + Terminology | 3 |
| Sin README | 30% | AI Descriptions | 3 |
| Exact matches | 15% | Hybrid Search (BM25) | 2 |
| Versiones nuevas | 10% | Data coverage | 3 |

**Total queries afectadas:** 16/20 (80%)

---

## Recomendaciones

### Prioridad 1: Data Enrichment (Fase 3)
- Impacta 55% de fallos (Sinónimos + Sin README)
- Bajo costo de implementación
- Base sólida para otras mejoras

### Prioridad 2: Hybrid Search (Fase 2)
- Impacta 35% de fallos (Exact matches + Multi-concepto)
- Mejora incremental clara
- Prerequisito para Reranking

### Prioridad 3: Reranking (Fase 4)
- Impacta 20% de fallos (Multi-concepto)
- Mayor costo (LLM calls)
- Pulido final después de 2 y 3

---

## Métricas de Mejora Proyectadas

Basado en patrones identificados:

| Fase | Precision@3 Proyectada | Mejora |
|------|------------------------|--------|
| Baseline (actual) | 35% | - |
| + Hybrid Search | 50% | +15% |
| + Enrichment | 65% | +15% |
| + Reranking | 72% | +7% |

**Target Final:** >70% Precision@3
```

---

## 🧪 Tests de Validación

### Test Suite: `tests/test_phase1_acceptance.py`

```python
"""
Tests de aceptación para Fase 1.
"""
import json
import pytest
from pathlib import Path


class TestPhase1Acceptance:
    """Tests de aceptación para Fase 1."""

    def test_benchmark_queries_exists(self):
        """AC-1: Archivo de queries existe."""
        assert Path("tests/benchmark_queries.json").exists()

    def test_benchmark_queries_count(self):
        """AC-1: Exactamente 20 queries."""
        with open("tests/benchmark_queries.json") as f:
            data = json.load(f)

        assert len(data["benchmark_queries"]) == 20

    def test_benchmark_categories_coverage(self):
        """AC-1: Al menos 5 categorías."""
        with open("tests/benchmark_queries.json") as f:
            data = json.load(f)

        categories = set(q["category"] for q in data["benchmark_queries"])
        assert len(categories) >= 5

    def test_benchmark_difficulty_distribution(self):
        """AC-1: Distribución correcta de dificultad."""
        with open("tests/benchmark_queries.json") as f:
            data = json.load(f)

        difficulty_counts = {
            "easy": 0,
            "medium": 0,
            "hard": 0
        }

        for query in data["benchmark_queries"]:
            difficulty_counts[query["difficulty"]] += 1

        assert difficulty_counts["easy"] == 5
        assert difficulty_counts["medium"] == 10
        assert difficulty_counts["hard"] == 5

    def test_baseline_results_exists(self):
        """AC-2: Archivo de resultados baseline existe."""
        results_dir = Path("tests/results")
        baseline_files = list(results_dir.glob("baseline_*.json"))

        assert len(baseline_files) > 0, "No baseline results found"

    def test_baseline_metrics_present(self):
        """AC-3: Métricas presentes en resultados."""
        results_dir = Path("tests/results")
        baseline_files = sorted(results_dir.glob("baseline_*.json"))

        assert len(baseline_files) > 0

        # Load most recent baseline
        with open(baseline_files[-1]) as f:
            results = json.load(f)

        # Check aggregate metrics
        assert "aggregate_metrics" in results
        metrics = results["aggregate_metrics"]

        assert "precision@3" in metrics
        assert "precision@5" in metrics
        assert "recall@10" in metrics
        assert "mrr" in metrics

        # Check metrics are in valid range
        assert 0 <= metrics["precision@3"] <= 1
        assert 0 <= metrics["precision@5"] <= 1
        assert 0 <= metrics["recall@10"] <= 1
        assert 0 <= metrics["mrr"] <= 1

    def test_baseline_confirms_improvement_needed(self):
        """AC-4: Baseline confirma necesidad de mejoras (P@3 < 40%)."""
        results_dir = Path("tests/results")
        baseline_files = sorted(results_dir.glob("baseline_*.json"))

        with open(baseline_files[-1]) as f:
            results = json.load(f)

        precision_at_3 = results["aggregate_metrics"]["precision@3"]

        # Expected: precision is low enough to justify improvements
        # But not TOO low (would indicate broken system)
        assert 0.15 <= precision_at_3 <= 0.45, \
            f"Precision@3 ({precision_at_3:.2%}) outside expected range"

    def test_difficulty_gradient_exists(self):
        """AC-4: Easy > Medium > Hard en precision."""
        results_dir = Path("tests/results")
        baseline_files = sorted(results_dir.glob("baseline_*.json"))

        with open(baseline_files[-1]) as f:
            results = json.load(f)

        per_diff = results["per_difficulty"]

        easy_p3 = per_diff["easy"]["precision@3"]
        medium_p3 = per_diff["medium"]["precision@3"]
        hard_p3 = per_diff["hard"]["precision@3"]

        assert easy_p3 >= medium_p3, "Easy should have >= precision than medium"
        assert medium_p3 >= hard_p3, "Medium should have >= precision than hard"

    def test_failure_analysis_exists(self):
        """AC-5: Documento de análisis de fallos existe."""
        failure_analysis = Path("tests/results/failure_analysis.md")
        assert failure_analysis.exists()

    def test_failure_analysis_has_patterns(self):
        """AC-5: Análisis documenta al menos 5 patrones."""
        failure_analysis = Path("tests/results/failure_analysis.md")

        with open(failure_analysis) as f:
            content = f.read()

        # Count pattern headers (## Patrón N:)
        import re
        patterns = re.findall(r"## Patrón \d+:", content)

        assert len(patterns) >= 5, \
            f"Expected at least 5 patterns, found {len(patterns)}"

    def test_detailed_results_count(self):
        """AC-3: Resultados detallados para las 20 queries."""
        results_dir = Path("tests/results")
        baseline_files = sorted(results_dir.glob("baseline_*.json"))

        with open(baseline_files[-1]) as f:
            results = json.load(f)

        assert "detailed_results" in results
        assert len(results["detailed_results"]) == 20
```

---

## 🚦 Go/No-Go Decision

### Criterios para Proceder a Fase 2

```yaml
GO (Proceder a Fase 2) si:
  - ✅ Todos los tests de aceptación PASSED
  - ✅ Precision@3 baseline < 45%
  - ✅ Al menos 5 patrones de fallo documentados
  - ✅ Patrones de fallo mapean a mejoras de Fases 2-4
  - ✅ Team review aprueba benchmark queries

NO-GO (Revisar Fase 1) si:
  - ❌ Tests de aceptación fallan
  - ❌ Precision@3 baseline > 60% (sistema ya funciona bien)
  - ❌ Precision@3 baseline < 10% (sistema roto, revisar implementación)
  - ❌ Queries no son representativas
  - ❌ Expected modules incorrectos
```

### Acciones en caso de NO-GO

**Si P@3 > 60%:**
- ✅ Sistema funciona mejor de lo esperado
- 🔄 Ajustar targets de mejora (objetivo 80%)
- 🔄 Crear queries más difíciles si es necesario
- ✅ Proceder con Fases 2-4 como "optimización"

**Si P@3 < 10%:**
- ❌ Revisar implementación de búsqueda actual
- ❌ Validar que embeddings se están generando correctamente
- ❌ Revisar que expected_modules son correctos
- ⏸️ NO proceder a Fase 2 hasta resolver

**Si tests fallan:**
- ❌ Revisar implementación según spec
- ❌ Corregir bugs identificados
- 🔄 Re-ejecutar tests

---

## 📝 Checklist Final de Fase 1

```markdown
## Fase 1 - Checklist de Completitud

### Archivos Creados
- [ ] tests/benchmark_queries.json
- [ ] tests/results/ (directorio)
- [ ] tests/results/baseline_YYYYMMDD_HHMMSS.json
- [ ] tests/results/failure_analysis.md
- [ ] scripts/run_benchmark.py
- [ ] app/metrics/benchmark_metrics.py
- [ ] tests/test_benchmark_queries.py
- [ ] tests/test_benchmark_metrics.py
- [ ] tests/test_phase1_acceptance.py

### Tests Ejecutados
- [ ] pytest tests/test_benchmark_queries.py -v (PASSED)
- [ ] pytest tests/test_benchmark_metrics.py -v (PASSED)
- [ ] pytest tests/test_phase1_acceptance.py -v (PASSED)
- [ ] python scripts/run_benchmark.py (EXIT 0)

### Métricas Documentadas
- [ ] Precision@3 baseline: ____%
- [ ] Precision@5 baseline: ____%
- [ ] Recall@10 baseline: ____%
- [ ] MRR baseline: _____
- [ ] Tiempo de ejecución: _____ segundos

### Análisis Completado
- [ ] 5+ patrones de fallo identificados
- [ ] Cada patrón incluye ejemplo y hipótesis
- [ ] Patrones mapeados a fases de mejora
- [ ] Proyección de mejoras documentada

### Aprobaciones
- [ ] Code review completado
- [ ] Queries validadas por experto Odoo
- [ ] Métricas baseline aprobadas
- [ ] Go/No-Go decision: GO / NO-GO

### Documentación
- [ ] README de Fase 1 actualizado con resultados
- [ ] Learnings documentados
- [ ] Próximos pasos definidos
```

---

## 🎉 Definición de Done

**Fase 1 está DONE cuando:**

1. ✅ Todos los checkboxes del checklist están marcados
2. ✅ Todos los tests de aceptación pasan
3. ✅ Go/No-Go decision es GO
4. ✅ Failure analysis completado y revisado
5. ✅ Commit pushed a repositorio con tag `phase-1-complete`

**Output final:**
```bash
git add .
git commit -m "feat: Complete Phase 1 - Diagnostic & Benchmark

- Add 20 benchmark queries covering 5 categories
- Implement benchmark runner with IR metrics
- Baseline results: P@3=35%, P@5=42%, MRR=0.412
- Document 5 failure patterns for improvement
- All acceptance tests passing

Co-Authored-By: Claude <noreply@anthropic.com>"

git tag phase-1-complete
git push origin main --tags
```

---

## 🔗 Siguiente Fase

Una vez Fase 1 completada exitosamente:
→ **Proceder a Fase 2:** Hybrid Search (BM25 + Vector)
→ Specs: `specs/phase-2-hybrid-search/`

---

**Estado:** 🔴 Pendiente
**Implementador:** TBD
**Revisor:** TBD
