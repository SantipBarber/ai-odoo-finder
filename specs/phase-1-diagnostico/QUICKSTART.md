# Quick Start Guide - Fase 1: Diagnóstico

**Tiempo estimado:** 4-6 horas
**Prioridad:** Implementar en orden (1 → 2 → 3 → 4)

---

## 🚀 Inicio Rápido (TL;DR)

```bash
# 1. Crear estructura de directorios
mkdir -p tests/results app/metrics

# 2. Implementar queries de benchmark
cp specs/phase-1-diagnostico/benchmark_queries_example.json tests/benchmark_queries.json
# Editar y validar expected_modules contra tu BD

# 3. Implementar módulo de métricas
# Seguir: specs/phase-1-diagnostico/SPEC-003-metrics.md

# 4. Implementar script de benchmark
# Seguir: specs/phase-1-diagnostico/SPEC-002-benchmark-script.md

# 5. Ejecutar benchmark
python scripts/run_benchmark.py

# 6. Analizar resultados y crear failure_analysis.md
cat tests/results/baseline_*.json | jq '.aggregate_metrics'
```

---

## 📋 Checklist de Implementación

### Paso 1: Preparación (15 min)

```bash
# Crear estructura de directorios
mkdir -p tests/results
mkdir -p app/metrics
mkdir -p scripts

# Copiar ejemplo de queries
cp specs/phase-1-diagnostico/benchmark_queries_example.json \
   tests/benchmark_queries.json
```

**Checklist:**
- [ ] Directorios creados
- [ ] Archivo `tests/benchmark_queries.json` existe
- [ ] Git branch creado: `git checkout -b phase-1-diagnostico`

---

### Paso 2: Validar Queries de Benchmark (1-2 horas)

**Objetivo:** Asegurar que todos los `expected_modules` existen en tu BD.

#### Script de Validación SQL

```sql
-- Validar módulos del ejemplo contra tu BD
WITH expected_modules AS (
  SELECT unnest(ARRAY[
    'l10n_es_facturae', 'l10n_es_aeat',
    'sale_b2b_b2c', 'portal_partner_type',
    'portal_document', 'dms_portal'
    -- ... añadir todos los expected_modules del JSON
  ]) AS module_name
)
SELECT
  em.module_name,
  om.technical_name,
  om.version,
  CASE
    WHEN om.technical_name IS NULL THEN '❌ NOT FOUND'
    ELSE '✅ EXISTS'
  END as status
FROM expected_modules em
LEFT JOIN odoo_modules om ON em.module_name = om.technical_name
ORDER BY status, em.module_name;
```

#### Proceso de Ajuste

1. **Ejecuta la query SQL** para ver qué módulos no existen
2. **Para módulos faltantes:**
   - Busca alternativas similares en tu BD
   - O elimina de expected_modules si no hay equivalente
3. **Ajusta el JSON** con módulos válidos
4. **Re-ejecuta validación** hasta que todos sean ✅

**Checklist:**
- [ ] Todos los expected_modules validados contra BD
- [ ] Al menos 15 queries con expected_modules válidos
- [ ] Distribución: 5 easy, 10 medium, 5 hard mantenida

---

### Paso 3: Implementar Módulo de Métricas (1 hora)

**Archivo:** `app/metrics/benchmark_metrics.py`

#### Template Inicial

```python
"""
Módulo de cálculo de métricas de Information Retrieval.
"""
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class IRMetrics:
    """Resultado de métricas IR."""
    precision_at_3: float
    precision_at_5: float
    recall_at_10: float
    mrr: float
    hits_in_top_3: int = 0
    hits_in_top_5: int = 0
    first_relevant_position: Optional[int] = None


class MetricsCalculator:
    """Calcula métricas de Information Retrieval."""

    @staticmethod
    def precision_at_k(retrieved: List[str], expected: List[str], k: int) -> float:
        """Calcula Precision@k."""
        if not retrieved or k == 0:
            return 0.0

        top_k = retrieved[:k]
        relevant_count = sum(1 for mod in top_k if mod in expected)
        return relevant_count / k

    @staticmethod
    def recall_at_k(retrieved: List[str], expected: List[str], k: int) -> float:
        """Calcula Recall@k."""
        if not expected:
            return 0.0

        top_k = retrieved[:k]
        found_count = sum(1 for exp in expected if exp in top_k)
        return found_count / len(expected)

    @staticmethod
    def mrr(retrieved: List[str], expected: List[str]) -> float:
        """Calcula Mean Reciprocal Rank."""
        for i, module in enumerate(retrieved, start=1):
            if module in expected:
                return 1.0 / i
        return 0.0

    @staticmethod
    def calculate_all(retrieved: List[str], expected: List[str]) -> IRMetrics:
        """Calcula todas las métricas."""
        return IRMetrics(
            precision_at_3=MetricsCalculator.precision_at_k(retrieved, expected, k=3),
            precision_at_5=MetricsCalculator.precision_at_k(retrieved, expected, k=5),
            recall_at_10=MetricsCalculator.recall_at_k(retrieved, expected, k=10),
            mrr=MetricsCalculator.mrr(retrieved, expected),
            hits_in_top_3=sum(1 for m in retrieved[:3] if m in expected),
            hits_in_top_5=sum(1 for m in retrieved[:5] if m in expected),
            first_relevant_position=next(
                (i for i, m in enumerate(retrieved, 1) if m in expected),
                None
            )
        )
```

#### Tests Unitarios

```python
# tests/test_benchmark_metrics.py
import pytest
from app.metrics.benchmark_metrics import MetricsCalculator

def test_precision_at_k():
    retrieved = ["A", "B", "C"]
    expected = ["A", "C"]

    assert MetricsCalculator.precision_at_k(retrieved, expected, k=3) == 2/3

def test_recall_at_k():
    retrieved = ["A", "B", "C"]
    expected = ["A", "C", "D"]

    assert MetricsCalculator.recall_at_k(retrieved, expected, k=3) == 2/3

def test_mrr():
    assert MetricsCalculator.mrr(["A", "B"], ["A"]) == 1.0
    assert MetricsCalculator.mrr(["A", "B", "C"], ["C"]) == 1/3
```

**Checklist:**
- [ ] `app/metrics/benchmark_metrics.py` implementado
- [ ] `app/metrics/__init__.py` creado
- [ ] Tests unitarios en `tests/test_benchmark_metrics.py`
- [ ] Tests pasan: `pytest tests/test_benchmark_metrics.py -v`

---

### Paso 4: Implementar Script de Benchmark (2 horas)

**Archivo:** `scripts/run_benchmark.py`

#### Template Inicial

```python
"""
Script de ejecución de benchmark.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from sqlalchemy import text
from app.database import get_async_session
from app.services.search_service import SearchService
from app.metrics.benchmark_metrics import MetricsCalculator


class BenchmarkRunner:
    """Ejecuta benchmark de búsqueda."""

    def __init__(self, db_session):
        self.db = db_session
        self.search_service = SearchService(db_session)
        self.metrics_calculator = MetricsCalculator()

    async def run(self, output_dir: str = "tests/results") -> Dict:
        """Ejecuta benchmark completo."""

        print("="*80)
        print("AI-OdooFinder Benchmark Runner")
        print("="*80)

        # Load queries
        queries = self._load_queries()
        print(f"\n✓ Loaded {len(queries)} queries")

        # Execute benchmark
        results = []
        for i, query_data in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Query: \"{query_data['query']}\"")

            result = await self._execute_query(query_data)
            results.append(result)

            # Print quick metrics
            metrics = result['metrics']
            print(f"       Metrics: P@3={metrics['precision@3']:.3f} | "
                  f"R@10={metrics['recall@10']:.3f} | MRR={metrics['mrr']:.3f}")

        # Generate report
        report = self._generate_report(results)

        # Save results
        output_path = self._save_results(report, output_dir)

        # Print summary
        self._print_summary(report, output_path)

        return report

    def _load_queries(self) -> List[Dict]:
        """Carga queries desde JSON."""
        with open("tests/benchmark_queries.json", "r") as f:
            data = json.load(f)
        return data["benchmark_queries"]

    async def _execute_query(self, query_data: Dict) -> Dict:
        """Ejecuta una query individual."""
        start_time = datetime.now()

        # Execute search
        search_results = await self.search_service.search_modules(
            query=query_data['query'],
            version=query_data['version'],
            limit=10
        )

        # Extract module names
        returned_modules = [r.technical_name for r in search_results]

        # Calculate metrics
        metrics = self.metrics_calculator.calculate_all(
            retrieved=returned_modules,
            expected=query_data['expected_modules']
        )

        execution_time = (datetime.now() - start_time).total_seconds() * 1000

        return {
            'query_id': query_data['id'],
            'query': query_data['query'],
            'version': query_data['version'],
            'category': query_data['category'],
            'difficulty': query_data['difficulty'],
            'expected_modules': query_data['expected_modules'],
            'returned_modules': returned_modules,
            'metrics': {
                'precision@3': metrics.precision_at_3,
                'precision@5': metrics.precision_at_5,
                'recall@10': metrics.recall_at_10,
                'mrr': metrics.mrr,
                'hits_in_top_3': metrics.hits_in_top_3,
                'hits_in_top_5': metrics.hits_in_top_5,
                'first_relevant_position': metrics.first_relevant_position
            },
            'execution_time_ms': execution_time
        }

    def _generate_report(self, results: List[Dict]) -> Dict:
        """Genera reporte agregado."""
        from statistics import mean

        # Aggregate metrics
        aggregate = {
            'precision@3': mean(r['metrics']['precision@3'] for r in results),
            'precision@5': mean(r['metrics']['precision@5'] for r in results),
            'recall@10': mean(r['metrics']['recall@10'] for r in results),
            'mrr': mean(r['metrics']['mrr'] for r in results)
        }

        # TODO: Add per_category and per_difficulty aggregation

        return {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_queries': len(results),
                'search_mode': 'vector'
            },
            'aggregate_metrics': aggregate,
            'detailed_results': results
        }

    def _save_results(self, report: Dict, output_dir: str) -> str:
        """Guarda resultados en JSON."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"baseline_{timestamp}.json"
        filepath = Path(output_dir) / filename

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        return str(filepath)

    def _print_summary(self, report: Dict, output_path: str):
        """Imprime resumen en consola."""
        metrics = report['aggregate_metrics']

        print("\n" + "="*80)
        print("BENCHMARK COMPLETED")
        print("="*80)
        print(f"\nAGGREGATE METRICS:")
        print(f"  Precision@3:  {metrics['precision@3']:.1%}")
        print(f"  Precision@5:  {metrics['precision@5']:.1%}")
        print(f"  Recall@10:    {metrics['recall@10']:.1%}")
        print(f"  Mean MRR:     {metrics['mrr']:.3f}")
        print(f"\nResults saved to: {output_path}")
        print("="*80)


async def main():
    """Entry point."""
    async with get_async_session() as db:
        runner = BenchmarkRunner(db)
        await runner.run()


if __name__ == '__main__':
    asyncio.run(main())
```

**Checklist:**
- [ ] `scripts/run_benchmark.py` implementado
- [ ] Script ejecutable: `python scripts/run_benchmark.py`
- [ ] Genera archivo en `tests/results/baseline_YYYYMMDD_HHMMSS.json`
- [ ] Output de consola informativo

---

### Paso 5: Ejecutar y Analizar (1 hora)

#### Ejecutar Benchmark

```bash
python scripts/run_benchmark.py
```

**Output esperado:**
```
================================================================================
AI-OdooFinder Benchmark Runner
================================================================================

✓ Loaded 20 queries

[1/20] Query: "facturación electrónica España AEAT"
       Metrics: P@3=0.667 | R@10=1.000 | MRR=1.000
...
================================================================================
BENCHMARK COMPLETED
================================================================================

AGGREGATE METRICS:
  Precision@3:  35.0%
  Precision@5:  42.0%
  Recall@10:    58.0%
  Mean MRR:     0.412

Results saved to: tests/results/baseline_20251122_103045.json
```

#### Analizar Resultados

```bash
# Ver métricas agregadas
cat tests/results/baseline_*.json | jq '.aggregate_metrics'

# Ver queries con peor performance
cat tests/results/baseline_*.json | \
  jq '.detailed_results | sort_by(.metrics["precision@3"]) | .[0:5]'

# Ver distribución por dificultad
cat tests/results/baseline_*.json | jq '.per_difficulty'
```

**Checklist:**
- [ ] Benchmark ejecutado sin errores
- [ ] Archivo JSON generado
- [ ] Precision@3 < 45% (confirma necesidad de mejoras)
- [ ] Diferencia clara entre easy/medium/hard

---

### Paso 6: Failure Analysis (1 hora)

Crear archivo `tests/results/failure_analysis.md` documentando:

1. **5 patrones de fallo identificados**
2. **Para cada patrón:**
   - Descripción del problema
   - Ejemplo concreto de query
   - Análisis de por qué falla
   - Hipótesis de mejora

**Template:**
```markdown
# Análisis de Patrones de Fallo - Baseline

## Patrón 1: [Nombre del patrón]

### Descripción
[Qué tipo de búsquedas fallan]

### Ejemplo
Query: "[query específica]"
Expected: [módulos esperados]
Returned: [módulos retornados]

### Análisis
[Por qué falló]

### Mejora Propuesta
- Fase X: [qué mejora ayudaría]

### Frecuencia
X/20 queries (XX%)
```

**Checklist:**
- [ ] `failure_analysis.md` creado
- [ ] 5+ patrones documentados
- [ ] Cada patrón mapea a fase de mejora
- [ ] Proyección de mejora estimada

---

## ✅ Definition of Done

**Fase 1 está completa cuando:**

```bash
# Todos estos comandos pasan
pytest tests/test_benchmark_metrics.py -v
pytest tests/test_phase1_acceptance.py -v
python scripts/run_benchmark.py  # Exit code 0

# Y todos estos archivos existen
ls tests/benchmark_queries.json
ls tests/results/baseline_*.json
ls tests/results/failure_analysis.md
ls app/metrics/benchmark_metrics.py
ls scripts/run_benchmark.py
```

---

## 🚨 Troubleshooting

### Error: "Module not found in database"

**Causa:** Expected module no existe en tu BD

**Solución:**
```sql
-- Buscar alternativas
SELECT technical_name, name, summary
FROM odoo_modules
WHERE technical_name ILIKE '%keyword%'
  AND version = '16.0'
LIMIT 10;
```

### Error: "Search service timeout"

**Causa:** API de embeddings lenta

**Solución:**
- Aumentar timeout en search_service
- Usar cache de embeddings para queries
- Implementar retry logic

### Precision@3 muy alta (>60%)

**Causa:** Sistema ya funciona bien o queries muy fáciles

**Solución:**
- Añadir queries más difíciles
- Validar que expected_modules son correctos
- Ajustar targets de mejora al alza

### Precision@3 muy baja (<10%)

**Causa:** Sistema roto o expected_modules incorrectos

**Solución:**
- Validar embeddings se generan correctamente
- Revisar expected_modules manualmente
- Ejecutar búsqueda manual de 2-3 queries

---

## 📞 Ayuda

**¿Bloqueado? Revisa:**
1. [SPEC-001](./SPEC-001-benchmark-queries.md) - Queries
2. [SPEC-002](./SPEC-002-benchmark-script.md) - Script
3. [SPEC-003](./SPEC-003-metrics.md) - Métricas
4. [SPEC-004](./SPEC-004-acceptance-criteria.md) - Criterios

**¿Aún bloqueado?**
- Crea issue en GitHub con tag `phase-1`
- Incluye output de error completo
- Adjunta `benchmark_queries.json` si relevante

---

## 🎉 Próximos Pasos

Una vez Fase 1 completa:

```bash
# Commit y tag
git add .
git commit -m "feat: Complete Phase 1 - Diagnostic & Benchmark"
git tag phase-1-complete
git push origin main --tags

# Proceder a Fase 2
cd specs/phase-2-hybrid-search
cat README.md
```

---

**Happy coding! 🚀**
