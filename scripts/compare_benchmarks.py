"""
Compara resultados de dos benchmarks.

Usage:
    python compare_benchmarks.py <baseline.json> <comparison.json>
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

    baseline_mode = baseline['metadata'].get('search_mode', 'vector')
    comparison_mode = comparison['metadata'].get('search_mode', 'hybrid')

    print("="*80)
    print("BENCHMARK COMPARISON")
    print("="*80)

    print(f"\nBaseline ({baseline_mode}): {baseline_path}")
    print(f"  Precision@3:  {baseline_metrics['precision@3']:.1%}")
    print(f"  Precision@5:  {baseline_metrics['precision@5']:.1%}")
    print(f"  MRR:          {baseline_metrics['mrr']:.3f}")

    print(f"\nComparison ({comparison_mode}): {comparison_path}")
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
        if difficulty in baseline.get('per_difficulty', {}) and \
           difficulty in comparison.get('per_difficulty', {}):
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
