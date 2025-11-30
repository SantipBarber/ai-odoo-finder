"""
Information Retrieval metrics calculation.

Implements standard IR metrics to evaluate search quality:
- Precision@k: Fraction of relevant results in top K
- Recall@k: Fraction of expected results found in top K
- MRR: Mean Reciprocal Rank - position of first relevant result
"""

from collections import defaultdict
from dataclasses import dataclass
from statistics import mean, median
from typing import Dict, List, Optional


@dataclass
class IRMetrics:
    """IR metrics calculation result."""

    precision_at_3: float
    precision_at_5: float
    recall_at_10: float
    mrr: float
    ndcg_at_10: Optional[float] = None
    hits_in_top_3: int = 0
    hits_in_top_5: int = 0
    first_relevant_position: Optional[int] = None


class MetricsCalculator:
    """Calculate Information Retrieval metrics."""

    @staticmethod
    def precision_at_k(retrieved: List[str], expected: List[str], k: int) -> float:
        """
        Calculate Precision@k.

        Formula: P@k = |{relevant docs} ∩ {retrieved docs@k}| / k
        Measures: What fraction of returned results are relevant?
        """
        if not retrieved or k == 0:
            return 0.0

        top_k = retrieved[:k]
        relevant_count = sum(1 for mod in top_k if mod in expected)

        return relevant_count / k

    @staticmethod
    def recall_at_k(retrieved: List[str], expected: List[str], k: int) -> float:
        """
        Calculate Recall@k.

        Formula: R@k = |{relevant docs} ∩ {retrieved docs@k}| / |{relevant docs}|
        Measures: What fraction of relevant documents were returned?
        """
        if not expected:
            return 0.0

        top_k = retrieved[:k]
        found_count = sum(1 for exp in expected if exp in top_k)

        return found_count / len(expected)

    @staticmethod
    def mrr(retrieved: List[str], expected: List[str]) -> float:
        """
        Calculate Mean Reciprocal Rank.

        Formula: MRR = 1 / rank_first_relevant
        Measures: How high does the first relevant result appear?
        """
        for i, module in enumerate(retrieved, start=1):
            if module in expected:
                return 1.0 / i

        return 0.0

    @staticmethod
    def count_hits(retrieved: List[str], expected: List[str]) -> int:
        """Count how many relevant documents are in retrieved."""
        return sum(1 for doc in retrieved if doc in expected)

    @staticmethod
    def first_relevant_position(retrieved: List[str], expected: List[str]) -> Optional[int]:
        """Find position (1-indexed) of first relevant document."""
        for i, doc in enumerate(retrieved, start=1):
            if doc in expected:
                return i
        return None

    @staticmethod
    def calculate_all(retrieved: List[str], expected: List[str]) -> IRMetrics:
        """Calculate all IR metrics for a search result."""
        return IRMetrics(
            precision_at_3=MetricsCalculator.precision_at_k(retrieved, expected, k=3),
            precision_at_5=MetricsCalculator.precision_at_k(retrieved, expected, k=5),
            recall_at_10=MetricsCalculator.recall_at_k(retrieved, expected, k=10),
            mrr=MetricsCalculator.mrr(retrieved, expected),
            hits_in_top_3=MetricsCalculator.count_hits(retrieved[:3], expected),
            hits_in_top_5=MetricsCalculator.count_hits(retrieved[:5], expected),
            first_relevant_position=MetricsCalculator.first_relevant_position(retrieved, expected),
        )


class ReportAggregator:
    """Aggregate metrics from multiple queries."""

    @staticmethod
    def aggregate_metrics(results: List[IRMetrics]) -> Dict:
        """Calculate average metrics across queries."""
        if not results:
            return {
                "precision@3": 0.0,
                "precision@5": 0.0,
                "recall@10": 0.0,
                "mrr": 0.0,
                "median_precision@3": 0.0,
                "median_mrr": 0.0,
            }

        return {
            "precision@3": mean(r.precision_at_3 for r in results),
            "precision@5": mean(r.precision_at_5 for r in results),
            "recall@10": mean(r.recall_at_10 for r in results),
            "mrr": mean(r.mrr for r in results),
            "median_precision@3": median(r.precision_at_3 for r in results),
            "median_mrr": median(r.mrr for r in results),
        }

    @staticmethod
    def group_by_category(detailed_results: List[Dict], metric_field: str) -> Dict[str, float]:
        """Group metrics by category."""
        category_results = defaultdict(list)

        for result in detailed_results:
            category = result["category"]
            metric_value = result["metrics"][metric_field]
            category_results[category].append(metric_value)

        return {category: mean(values) for category, values in category_results.items()}

    @staticmethod
    def group_by_difficulty(detailed_results: List[Dict]) -> Dict[str, Dict]:
        """Group metrics by difficulty level."""
        difficulty_results = defaultdict(list)

        for result in detailed_results:
            difficulty = result["difficulty"]
            difficulty_results[difficulty].append(result["metrics"])

        return {
            difficulty: {
                "count": len(metrics_list),
                "precision@3": mean(m["precision@3"] for m in metrics_list),
                "precision@5": mean(m["precision@5"] for m in metrics_list),
                "recall@10": mean(m["recall@10"] for m in metrics_list),
                "mrr": mean(m["mrr"] for m in metrics_list),
            }
            for difficulty, metrics_list in difficulty_results.items()
        }
