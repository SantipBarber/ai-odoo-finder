"""
Tests unitarios para el módulo de métricas de benchmark.
"""
import sys
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from backend.app.metrics.benchmark_metrics import MetricsCalculator, IRMetrics, ReportAggregator


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

        # Usa k como denominador siempre
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
        assert MetricsCalculator.mrr(["A", "B", "C"], ["C"]) == pytest.approx(1/3)

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


class TestCountHits:
    """Tests para count_hits."""

    def test_count_hits_all_match(self):
        """Todos los retrieved son relevantes."""
        retrieved = ["A", "B", "C"]
        expected = ["A", "B", "C", "D"]

        assert MetricsCalculator.count_hits(retrieved, expected) == 3

    def test_count_hits_partial(self):
        """Algunos retrieved son relevantes."""
        retrieved = ["A", "B", "C"]
        expected = ["A", "C"]

        assert MetricsCalculator.count_hits(retrieved, expected) == 2

    def test_count_hits_none(self):
        """Ningún retrieved es relevante."""
        retrieved = ["A", "B"]
        expected = ["C", "D"]

        assert MetricsCalculator.count_hits(retrieved, expected) == 0


class TestFirstRelevantPosition:
    """Tests para first_relevant_position."""

    def test_first_position(self):
        """Primer resultado es relevante."""
        retrieved = ["A", "B", "C"]
        expected = ["A"]

        assert MetricsCalculator.first_relevant_position(retrieved, expected) == 1

    def test_middle_position(self):
        """Resultado relevante en medio."""
        retrieved = ["A", "B", "C", "D"]
        expected = ["C"]

        assert MetricsCalculator.first_relevant_position(retrieved, expected) == 3

    def test_no_relevant(self):
        """Sin resultados relevantes."""
        retrieved = ["A", "B", "C"]
        expected = ["D"]

        assert MetricsCalculator.first_relevant_position(retrieved, expected) is None


class TestCalculateAll:
    """Tests para cálculo agregado."""

    def test_calculate_all_comprehensive(self):
        """Test completo de todas las métricas."""
        retrieved = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        expected = ["A", "C", "F", "K"]

        metrics = MetricsCalculator.calculate_all(retrieved, expected)

        # Precision@3: A, C son relevantes → 2/3
        assert metrics.precision_at_3 == pytest.approx(2/3)

        # Precision@5: A, C son relevantes → 2/5
        assert metrics.precision_at_5 == pytest.approx(2/5)

        # Recall@10: A, C, F encontrados (3), K no (1) → 3/4
        assert metrics.recall_at_10 == pytest.approx(3/4)

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
        """Duplicados en retrieved."""
        retrieved = ["A", "A", "B"]
        expected = ["A"]

        # Cada A cuenta como hit individual
        assert MetricsCalculator.precision_at_k(retrieved, expected, k=3) == pytest.approx(2/3)


class TestReportAggregator:
    """Tests para ReportAggregator."""

    def test_aggregate_metrics(self):
        """Test de agregación de métricas."""
        results = [
            IRMetrics(precision_at_3=0.67, precision_at_5=0.6, recall_at_10=0.8, mrr=1.0),
            IRMetrics(precision_at_3=0.33, precision_at_5=0.4, recall_at_10=0.5, mrr=0.5),
            IRMetrics(precision_at_3=0.0, precision_at_5=0.2, recall_at_10=0.3, mrr=0.0)
        ]

        agg = ReportAggregator.aggregate_metrics(results)

        assert agg["precision@3"] == pytest.approx((0.67 + 0.33 + 0.0) / 3)
        assert agg["mrr"] == pytest.approx((1.0 + 0.5 + 0.0) / 3)

    def test_aggregate_metrics_empty(self):
        """Test con lista vacía."""
        agg = ReportAggregator.aggregate_metrics([])

        assert agg["precision@3"] == 0.0
        assert agg["mrr"] == 0.0

    def test_group_by_difficulty(self):
        """Test de agrupación por dificultad."""
        detailed_results = [
            {
                "difficulty": "easy",
                "metrics": {"precision@3": 0.67, "precision@5": 0.6, "recall@10": 0.8, "mrr": 1.0}
            },
            {
                "difficulty": "easy",
                "metrics": {"precision@3": 0.33, "precision@5": 0.4, "recall@10": 0.5, "mrr": 0.5}
            },
            {
                "difficulty": "hard",
                "metrics": {"precision@3": 0.0, "precision@5": 0.2, "recall@10": 0.3, "mrr": 0.0}
            }
        ]

        grouped = ReportAggregator.group_by_difficulty(detailed_results)

        assert grouped["easy"]["count"] == 2
        assert grouped["easy"]["precision@3"] == pytest.approx((0.67 + 0.33) / 2)
        assert grouped["hard"]["count"] == 1
        assert grouped["hard"]["precision@3"] == 0.0
