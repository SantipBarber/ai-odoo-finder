"""
Módulo de cálculo de métricas de Information Retrieval.

Este módulo implementa métricas estándar de IR para evaluar la calidad
de los resultados de búsqueda:
- Precision@k: Fracción de resultados relevantes en top K
- Recall@k: Fracción de esperados encontrados en top K
- MRR: Mean Reciprocal Rank - posición del primer resultado relevante
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from statistics import mean, median
from collections import defaultdict


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

        Example:
            >>> MetricsCalculator.precision_at_k(
            ...     retrieved=["A", "B", "C"],
            ...     expected=["A", "C"],
            ...     k=3
            ... )
            0.667
        """
        if not retrieved or k == 0:
            return 0.0

        top_k = retrieved[:k]
        relevant_count = sum(1 for mod in top_k if mod in expected)

        return relevant_count / k

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

        Example:
            >>> MetricsCalculator.recall_at_k(
            ...     retrieved=["A", "B", "C"],
            ...     expected=["A", "C", "D"],
            ...     k=3
            ... )
            0.667
        """
        if not expected:
            return 0.0

        top_k = retrieved[:k]
        found_count = sum(1 for exp in expected if exp in top_k)

        return found_count / len(expected)

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

        Example:
            >>> MetricsCalculator.mrr(
            ...     retrieved=["A", "B", "C"],
            ...     expected=["C"]
            ... )
            0.333
        """
        for i, module in enumerate(retrieved, start=1):
            if module in expected:
                return 1.0 / i

        return 0.0

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
            >>> metrics = MetricsCalculator.calculate_all(
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
        if not results:
            return {
                "precision@3": 0.0,
                "precision@5": 0.0,
                "recall@10": 0.0,
                "mrr": 0.0,
                "median_precision@3": 0.0,
                "median_mrr": 0.0
            }

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
        difficulty_results = defaultdict(list)

        for result in detailed_results:
            difficulty = result['difficulty']
            difficulty_results[difficulty].append(result['metrics'])

        return {
            difficulty: {
                'count': len(metrics_list),
                'precision@3': mean(m['precision@3'] for m in metrics_list),
                'precision@5': mean(m['precision@5'] for m in metrics_list),
                'recall@10': mean(m['recall@10'] for m in metrics_list),
                'mrr': mean(m['mrr'] for m in metrics_list)
            }
            for difficulty, metrics_list in difficulty_results.items()
        }
