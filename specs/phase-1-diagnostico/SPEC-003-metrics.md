# SPEC-003: Metrics Calculation

**ID:** SPEC-003
**Componente:** Metrics Calculator
**Archivo:** `app/metrics/benchmark_metrics.py`
**Prioridad:** Alta
**Estimación:** 2 horas
**Dependencias:** SPEC-001

---

## 📋 Descripción

Implementar módulo de cálculo de métricas estándar de Information Retrieval (IR) para evaluar la calidad de los resultados de búsqueda. Este módulo es reutilizable para todas las fases del proyecto.

---

## 🎯 Objetivos

1. **Métricas estándar IR:** Implementar Precision, Recall, MRR, NDCG
2. **Testeable:** Unit tests exhaustivos con casos edge
3. **Reutilizable:** Módulo independiente usado en todas las fases
4. **Documentado:** Docstrings con fórmulas matemáticas

---

## 📐 API del Módulo

### Ubicación

```
app/
└── metrics/
    ├── __init__.py
    └── benchmark_metrics.py
```

### Clase Principal

```python
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class IRMetrics:
    """Resultado de cálculo de métricas IR."""

    precision_at_3: float
    precision_at_5: float
    recall_at_10: float
    mrr: float
    ndcg_at_10: Optional[float] = None
    hits_in_top_3: int = 0
    hits_in_top_5: int = 0
    first_relevant_position: Optional[int] = None


class MetricsCalculator:
    """Calcula métricas de Information Retrieval."""

    @staticmethod
    def calculate_all(
        retrieved: List[str],
        expected: List[str]
    ) -> IRMetrics:
        """
        Calcula todas las métricas IR para un resultado de búsqueda.

        Args:
            retrieved: Lista de módulos retornados (en orden de relevancia)
            expected: Lista de módulos esperados (ground truth)

        Returns:
            IRMetrics con todas las métricas calculadas

        Example:
            >>> calc = MetricsCalculator()
            >>> metrics = calc.calculate_all(
            ...     retrieved=["mod1", "mod2", "mod3", "mod4", "mod5"],
            ...     expected=["mod1", "mod3", "mod6"]
            ... )
            >>> metrics.precision_at_3
            0.667
            >>> metrics.mrr
            1.0
        """
        return IRMetrics(
            precision_at_3=MetricsCalculator.precision_at_k(retrieved, expected, k=3),
            precision_at_5=MetricsCalculator.precision_at_k(retrieved, expected, k=5),
            recall_at_10=MetricsCalculator.recall_at_k(retrieved, expected, k=10),
            mrr=MetricsCalculator.mrr(retrieved, expected),
            hits_in_top_3=MetricsCalculator.count_hits(retrieved[:3], expected),
            hits_in_top_5=MetricsCalculator.count_hits(retrieved[:5], expected),
            first_relevant_position=MetricsCalculator.first_relevant_position(retrieved, expected)
        )

    @staticmethod
    def precision_at_k(
        retrieved: List[str],
        expected: List[str],
        k: int
    ) -> float:
        """
        Calcula Precision@k.

        Formula: P@k = |{relevant documents} ∩ {retrieved documents@k}| / k

        Mide: ¿Qué fracción de los resultados retornados son relevantes?

        Args:
            retrieved: Documentos retornados (ordenados por score)
            expected: Documentos relevantes (ground truth)
            k: Cutoff para evaluación

        Returns:
            Precision en [0, 1]
        """
        ...

    @staticmethod
    def recall_at_k(
        retrieved: List[str],
        expected: List[str],
        k: int
    ) -> float:
        """
        Calcula Recall@k.

        Formula: R@k = |{relevant documents} ∩ {retrieved documents@k}| / |{relevant documents}|

        Mide: ¿Qué fracción de los documentos relevantes fueron retornados?

        Args:
            retrieved: Documentos retornados
            expected: Documentos relevantes
            k: Cutoff para evaluación

        Returns:
            Recall en [0, 1]
        """
        ...

    @staticmethod
    def mrr(retrieved: List[str], expected: List[str]) -> float:
        """
        Calcula Mean Reciprocal Rank.

        Formula: MRR = 1 / rank_first_relevant

        Mide: ¿Qué tan arriba aparece el primer resultado relevante?

        Args:
            retrieved: Documentos retornados (ordenados)
            expected: Documentos relevantes

        Returns:
            MRR en [0, 1]
        """
        ...

    @staticmethod
    def count_hits(retrieved: List[str], expected: List[str]) -> int:
        """
        Cuenta cuántos documentos relevantes hay en retrieved.

        Args:
            retrieved: Documentos retornados
            expected: Documentos relevantes

        Returns:
            Número de hits
        """
        return sum(1 for doc in retrieved if doc in expected)

    @staticmethod
    def first_relevant_position(
        retrieved: List[str],
        expected: List[str]
    ) -> Optional[int]:
        """
        Encuentra la posición (1-indexed) del primer documento relevante.

        Args:
            retrieved: Documentos retornados
            expected: Documentos relevantes

        Returns:
            Posición (1-based) o None si no hay relevantes
        """
        for i, doc in enumerate(retrieved, start=1):
            if doc in expected:
                return i
        return None
```

---

## 📊 Fórmulas Matemáticas

### Precision@k

```
P@k = (Número de documentos relevantes en top K) / K

Ejemplo:
  Retrieved: [A, B, C, D, E]
  Expected:  [A, C, F]
  P@3 = 2/3 = 0.667  (A y C son relevantes)
  P@5 = 2/5 = 0.40
```

### Recall@k

```
R@k = (Número de documentos relevantes encontrados en top K) / (Total de documentos relevantes)

Ejemplo:
  Retrieved: [A, B, C, D, E]
  Expected:  [A, C, F]
  R@5 = 2/3 = 0.667  (Encontramos A y C, pero falta F)
```

### Mean Reciprocal Rank (MRR)

```
MRR = 1 / (Posición del primer documento relevante)

Ejemplo 1:
  Retrieved: [A, B, C]
  Expected:  [A]
  MRR = 1/1 = 1.0  (Primer resultado es relevante)

Ejemplo 2:
  Retrieved: [A, B, C, D]
  Expected:  [C]
  MRR = 1/3 = 0.333  (Primer relevante en posición 3)

Ejemplo 3:
  Retrieved: [A, B, C]
  Expected:  [D]
  MRR = 0.0  (Ningún relevante encontrado)
```

### Normalized Discounted Cumulative Gain (NDCG@k) - Opcional

```
DCG@k = Σ(i=1 to k) [rel_i / log2(i + 1)]
IDCG@k = DCG@k del ranking ideal
NDCG@k = DCG@k / IDCG@k

Nota: NDCG es útil cuando hay niveles de relevancia (1, 2, 3...)
      En nuestro caso: relevancia binaria (0 o 1)
      → NDCG no es crítico para Fase 1, pero puede añadirse en Fase 5
```

---

## 🧪 Test Cases

### Test Suite Exhaustiva

```python
# tests/test_benchmark_metrics.py

import pytest
from app.metrics.benchmark_metrics import MetricsCalculator, IRMetrics


class TestPrecisionAtK:
    """Tests para Precision@k."""

    def test_perfect_precision(self):
        """Todos los resultados son relevantes."""
        retrieved = ["A", "B", "C"]
        expected = ["A", "B", "C", "D"]

        assert MetricsCalculator.precision_at_k(retrieved, expected, k=3) == 1.0

    def test_zero_precision(self):
        """Ningún resultado es relevante."""
        retrieved = ["A", "B", "C"]
        expected = ["D", "E", "F"]

        assert MetricsCalculator.precision_at_k(retrieved, expected, k=3) == 0.0

    def test_partial_precision(self):
        """Algunos resultados son relevantes."""
        retrieved = ["A", "B", "C", "D", "E"]
        expected = ["A", "C", "F"]

        assert MetricsCalculator.precision_at_k(retrieved, expected, k=3) == 2/3
        assert MetricsCalculator.precision_at_k(retrieved, expected, k=5) == 2/5

    def test_empty_retrieved(self):
        """Lista retrieved vacía."""
        assert MetricsCalculator.precision_at_k([], ["A"], k=3) == 0.0

    def test_empty_expected(self):
        """Lista expected vacía."""
        assert MetricsCalculator.precision_at_k(["A"], [], k=3) == 0.0

    def test_k_larger_than_retrieved(self):
        """k mayor que len(retrieved)."""
        retrieved = ["A", "B"]
        expected = ["A"]

        # Debería usar len(retrieved) como denominador cuando k > len
        # O retornar precisión basada en k de todas formas
        # Decisión de diseño: usar k como denominador siempre
        assert MetricsCalculator.precision_at_k(retrieved, expected, k=5) == 1/5


class TestRecallAtK:
    """Tests para Recall@k."""

    def test_perfect_recall(self):
        """Todos los esperados son encontrados."""
        retrieved = ["A", "B", "C", "D"]
        expected = ["A", "B"]

        assert MetricsCalculator.recall_at_k(retrieved, expected, k=4) == 1.0

    def test_zero_recall(self):
        """Ningún esperado es encontrado."""
        retrieved = ["A", "B", "C"]
        expected = ["D", "E"]

        assert MetricsCalculator.recall_at_k(retrieved, expected, k=3) == 0.0

    def test_partial_recall(self):
        """Algunos esperados son encontrados."""
        retrieved = ["A", "B", "C"]
        expected = ["A", "C", "D", "E"]

        assert MetricsCalculator.recall_at_k(retrieved, expected, k=3) == 2/4

    def test_empty_expected(self):
        """No hay esperados."""
        assert MetricsCalculator.recall_at_k(["A"], [], k=3) == 0.0


class TestMRR:
    """Tests para Mean Reciprocal Rank."""

    def test_first_result_relevant(self):
        """Primer resultado es relevante."""
        assert MetricsCalculator.mrr(["A", "B"], ["A"]) == 1.0

    def test_second_result_relevant(self):
        """Segundo resultado es relevante."""
        assert MetricsCalculator.mrr(["A", "B"], ["B"]) == 1/2

    def test_third_result_relevant(self):
        """Tercer resultado es relevante."""
        assert MetricsCalculator.mrr(["A", "B", "C"], ["C"]) == 1/3

    def test_no_relevant(self):
        """Ningún resultado relevante."""
        assert MetricsCalculator.mrr(["A", "B"], ["C"]) == 0.0

    def test_multiple_relevant(self):
        """Múltiples relevantes: debe usar el primero."""
        retrieved = ["A", "B", "C", "D"]
        expected = ["B", "D"]

        # Primer relevante es B en posición 2
        assert MetricsCalculator.mrr(retrieved, expected) == 1/2

    def test_empty_retrieved(self):
        """Lista retrieved vacía."""
        assert MetricsCalculator.mrr([], ["A"]) == 0.0


class TestCalculateAll:
    """Tests para cálculo agregado."""

    def test_calculate_all_comprehensive(self):
        """Test completo de todas las métricas."""
        retrieved = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        expected = ["A", "C", "F", "K"]

        metrics = MetricsCalculator.calculate_all(retrieved, expected)

        # Precision@3: A, C son relevantes → 2/3
        assert metrics.precision_at_3 == 2/3

        # Precision@5: A, C son relevantes → 2/5
        assert metrics.precision_at_5 == 2/5

        # Recall@10: A, C, F encontrados (3), K no (1) → 3/4
        assert metrics.recall_at_10 == 3/4

        # MRR: Primer relevante es A en posición 1
        assert metrics.mrr == 1.0

        # Hits
        assert metrics.hits_in_top_3 == 2
        assert metrics.hits_in_top_5 == 2

        # First relevant position
        assert metrics.first_relevant_position == 1

    def test_calculate_all_no_results(self):
        """Cuando no hay resultados relevantes."""
        metrics = MetricsCalculator.calculate_all(
            retrieved=["A", "B", "C"],
            expected=["D", "E"]
        )

        assert metrics.precision_at_3 == 0.0
        assert metrics.precision_at_5 == 0.0
        assert metrics.recall_at_10 == 0.0
        assert metrics.mrr == 0.0
        assert metrics.hits_in_top_3 == 0
        assert metrics.first_relevant_position is None


class TestEdgeCases:
    """Tests de casos edge."""

    def test_case_sensitivity(self):
        """Módulos deben compararse case-sensitive."""
        retrieved = ["module_A", "module_b"]
        expected = ["module_a", "module_B"]

        # No debería haber matches (case-sensitive)
        assert MetricsCalculator.precision_at_k(retrieved, expected, k=2) == 0.0

    def test_duplicates_in_retrieved(self):
        """Duplicados en retrieved (no debería pasar, pero manejar)."""
        retrieved = ["A", "A", "B"]
        expected = ["A"]

        # Cada A cuenta como hit individual
        # Precision@3 = 2/3 (ambos A's son relevantes)
        assert MetricsCalculator.precision_at_k(retrieved, expected, k=3) == 2/3

    def test_duplicates_in_expected(self):
        """Duplicados en expected (no debería pasar)."""
        retrieved = ["A", "B"]
        expected = ["A", "A"]

        # Debería deduplicar expected automáticamente
        # O contar como único
        # Decisión: expected es un set conceptualmente
        # Implementar deduplicación
        pass
```

---

## 📈 Agregación de Métricas

### Clase ReportAggregator

```python
from typing import List, Dict
from statistics import mean, median

class ReportAggregator:
    """Agrega métricas de múltiples queries."""

    @staticmethod
    def aggregate_metrics(results: List[IRMetrics]) -> Dict:
        """
        Calcula promedios de métricas.

        Args:
            results: Lista de IRMetrics de cada query

        Returns:
            Dict con métricas promediadas
        """
        return {
            "precision@3": mean(r.precision_at_3 for r in results),
            "precision@5": mean(r.precision_at_5 for r in results),
            "recall@10": mean(r.recall_at_10 for r in results),
            "mrr": mean(r.mrr for r in results),
            "median_precision@3": median(r.precision_at_3 for r in results),
            "median_mrr": median(r.mrr for r in results)
        }

    @staticmethod
    def group_by_category(
        detailed_results: List[Dict],
        metric_field: str
    ) -> Dict[str, float]:
        """
        Agrupa métricas por categoría.

        Args:
            detailed_results: Resultados detallados con campo 'category'
            metric_field: Campo a agregar (e.g., 'precision@3')

        Returns:
            Dict {category: avg_metric}
        """
        from collections import defaultdict

        category_results = defaultdict(list)

        for result in detailed_results:
            category = result['category']
            metric_value = result['metrics'][metric_field]
            category_results[category].append(metric_value)

        return {
            category: mean(values)
            for category, values in category_results.items()
        }

    @staticmethod
    def group_by_difficulty(
        detailed_results: List[Dict]
    ) -> Dict[str, Dict]:
        """
        Agrupa métricas por dificultad.

        Args:
            detailed_results: Resultados detallados con campo 'difficulty'

        Returns:
            Dict {difficulty: {metrics}}
        """
        from collections import defaultdict

        difficulty_results = defaultdict(list)

        for result in detailed_results:
            difficulty = result['difficulty']
            difficulty_results[difficulty].append(result['metrics'])

        return {
            difficulty: {
                'count': len(metrics_list),
                'precision@3': mean(m['precision@3'] for m in metrics_list),
                'precision@5': mean(m['precision@5'] for m in metrics_list),
                'mrr': mean(m['mrr'] for m in metrics_list)
            }
            for difficulty, metrics_list in difficulty_results.items()
        }
```

---

## ✅ Criterios de Aceptación

### Criterio 1: Implementación Completa
- ✅ Todas las funciones implementadas con docstrings
- ✅ Type hints completos
- ✅ Fórmulas matemáticas documentadas

### Criterio 2: Tests Passing
- ✅ Al menos 20 unit tests
- ✅ Cobertura de código > 95%
- ✅ Todos los edge cases cubiertos

### Criterio 3: Validación Matemática
- ✅ Fórmulas verificadas contra literatura IR
- ✅ Resultados manuales coinciden con implementación

### Criterio 4: Performance
- ✅ Cálculo de métricas < 1ms por query
- ✅ No hay operaciones O(n²) innecesarias

---

## 🔗 Referencias

### Papers y Literatura

1. **Precision and Recall**
   - Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to information retrieval. Cambridge university press.
   - Chapter 8: Evaluation in information retrieval

2. **Mean Reciprocal Rank (MRR)**
   - Voorhees, E. M. (1999). The TREC-8 Question Answering Track Report. TREC.

3. **NDCG**
   - Järvelin, K., & Kekäläinen, J. (2002). Cumulated gain-based evaluation of IR techniques. ACM Transactions on Information Systems.

### Recursos Online

- https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)
- https://scikit-learn.org/stable/modules/model_evaluation.html#ranking-metrics

---

## 🚀 Pasos de Implementación

1. **Crear estructura**
   - `app/metrics/__init__.py`
   - `app/metrics/benchmark_metrics.py`

2. **Implementar funciones base**
   - `precision_at_k()`
   - `recall_at_k()`
   - `mrr()`

3. **Implementar IRMetrics dataclass**

4. **Implementar calculate_all()**

5. **Implementar ReportAggregator**

6. **Escribir tests**
   - Tests unitarios para cada función
   - Tests de integración

7. **Documentación**
   - Docstrings con ejemplos
   - README del módulo

---

## 🔗 Siguiente Paso

Una vez completado este SPEC, proceder a:
→ [SPEC-004: Acceptance Criteria](./SPEC-004-acceptance-criteria.md)

---

**Estado:** 🔴 Pendiente
**Implementador:** TBD
**Revisor:** TBD
