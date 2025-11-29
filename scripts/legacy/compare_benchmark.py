#!/usr/bin/env python
"""
Script de comparación de benchmarks - Fase 5
Compara resultados de diferentes modos de búsqueda y genera reporte.
"""

import json
import sys
from datetime import datetime
from glob import glob
from pathlib import Path
from statistics import mean, median, stdev

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_latest_results(results_dir: str = "tests/results") -> dict:
    """Carga los resultados más recientes de cada modo."""
    results = {}

    for mode in ["vector", "hybrid", "bm25"]:
        files = sorted(glob(f"{results_dir}/{mode}_*.json"), reverse=True)
        if files:
            with open(files[0]) as f:
                results[mode] = json.load(f)
                results[mode]["_filepath"] = files[0]

    return results


def calculate_latency_percentiles(latencies: list) -> dict:
    """Calcula percentiles de latencia."""
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)

    return {
        "min": min(latencies),
        "p25": sorted_lat[int(n * 0.25)],
        "p50": median(latencies),
        "p75": sorted_lat[int(n * 0.75)],
        "p95": sorted_lat[min(int(n * 0.95), n-1)],
        "p99": sorted_lat[min(int(n * 0.99), n-1)],
        "max": max(latencies),
        "avg": mean(latencies),
        "stdev": stdev(latencies) if n > 1 else 0
    }


def generate_comparison_report(results: dict) -> str:
    """Genera reporte de comparación en formato markdown."""

    report = []
    report.append("# AI-OdooFinder Benchmark Comparison Report")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Modes compared:** {', '.join(results.keys())}")

    # Summary table
    report.append("\n## Summary Metrics\n")
    report.append("| Metric | " + " | ".join(results.keys()) + " |")
    report.append("|--------|" + "|".join(["--------"] * len(results)) + "|")

    metrics = ["precision@3", "precision@5", "recall@10", "mrr"]
    for metric in metrics:
        row = f"| {metric} |"
        for mode, data in results.items():
            val = data["aggregate_metrics"][metric]
            if metric != "mrr":
                row += f" {val:.1%} |"
            else:
                row += f" {val:.3f} |"
        report.append(row)

    # Latency comparison
    report.append("\n## Latency Analysis\n")
    report.append("| Percentile | " + " | ".join(results.keys()) + " |")
    report.append("|------------|" + "|".join(["--------"] * len(results)) + "|")

    percentiles = {}
    for mode, data in results.items():
        latencies = [r["execution_time_ms"] for r in data["detailed_results"]]
        percentiles[mode] = calculate_latency_percentiles(latencies)

    for p in ["min", "p25", "p50", "p75", "p95", "p99", "max", "avg"]:
        row = f"| {p.upper()} |"
        for mode in results.keys():
            row += f" {percentiles[mode][p]:.0f}ms |"
        report.append(row)

    # Per-query comparison
    report.append("\n## Per-Query Results\n")

    # Get queries from first result set
    first_mode = list(results.keys())[0]
    queries = {r["query_id"]: r for r in results[first_mode]["detailed_results"]}

    header = "| ID | Query | Version |"
    for mode in results.keys():
        header += f" {mode} P@3 |"
    header += " MRR |"
    report.append(header)

    separator = "|---|-------|---------|"
    for _ in results.keys():
        separator += "---------|"
    separator += "------|"
    report.append(separator)

    for qid in sorted(queries.keys()):
        q = queries[qid]
        row = f"| {qid} | {q['query'][:30]}... | {q['version']} |"

        for mode in results.keys():
            mode_result = next(r for r in results[mode]["detailed_results"] if r["query_id"] == qid)
            p3 = mode_result["metrics"]["precision@3"]
            row += f" {p3:.0%} |"

        # MRR from first mode
        mrr = q["metrics"]["mrr"]
        row += f" {mrr:.2f} |"
        report.append(row)

    # Conclusions
    report.append("\n## Conclusions\n")

    modes = list(results.keys())
    if len(modes) >= 2:
        m1, m2 = modes[0], modes[1]
        p3_1 = results[m1]["aggregate_metrics"]["precision@3"]
        p3_2 = results[m2]["aggregate_metrics"]["precision@3"]

        if p3_1 == p3_2:
            report.append(f"- **{m1.upper()}** and **{m2.upper()}** produce identical precision results")

            lat1 = mean([r["execution_time_ms"] for r in results[m1]["detailed_results"]])
            lat2 = mean([r["execution_time_ms"] for r in results[m2]["detailed_results"]])

            if lat2 < lat1:
                improvement = (lat1 - lat2) / lat1 * 100
                report.append(f"- **{m2.upper()}** is {improvement:.1f}% faster on average")
            elif lat1 < lat2:
                improvement = (lat2 - lat1) / lat2 * 100
                report.append(f"- **{m1.upper()}** is {improvement:.1f}% faster on average")
        else:
            if p3_2 > p3_1:
                improvement = (p3_2 - p3_1) / p3_1 * 100
                report.append(f"- **{m2.upper()}** improves P@3 by {improvement:.1f}% vs {m1.upper()}")
            else:
                degradation = (p3_1 - p3_2) / p3_1 * 100
                report.append(f"- **{m1.upper()}** is {degradation:.1f}% better in P@3 vs {m2.upper()}")

    # Overall assessment
    best_mode = max(results.keys(), key=lambda m: results[m]["aggregate_metrics"]["precision@3"])
    best_p3 = results[best_mode]["aggregate_metrics"]["precision@3"]
    best_mrr = results[best_mode]["aggregate_metrics"]["mrr"]

    report.append(f"\n### Overall Assessment\n")
    report.append(f"- Best mode: **{best_mode.upper()}**")
    report.append(f"- P@3: {best_p3:.1%}")
    report.append(f"- MRR: {best_mrr:.3f}")
    report.append(f"- Recall@10: {results[best_mode]['aggregate_metrics']['recall@10']:.1%}")

    return "\n".join(report)


def main():
    print("=" * 70)
    print("AI-OdooFinder Benchmark Comparison")
    print("=" * 70)

    results = load_latest_results()

    if not results:
        print("❌ No benchmark results found in tests/results/")
        return 1

    print(f"\n✓ Loaded results for: {', '.join(results.keys())}")

    # Generate report
    report = generate_comparison_report(results)

    # Save report
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"benchmark_comparison_{timestamp}.md"

    with open(report_file, "w") as f:
        f.write(report)

    print(f"\n✓ Report saved to: {report_file}")

    # Print summary to console
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for mode, data in results.items():
        m = data["aggregate_metrics"]
        print(f"\n{mode.upper()}:")
        print(f"  P@3: {m['precision@3']:.1%} | P@5: {m['precision@5']:.1%} | MRR: {m['mrr']:.3f}")

    print("\n" + "=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
