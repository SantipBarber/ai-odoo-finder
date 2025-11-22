# SPEC-402: Benchmark Comparison Report

**ID:** SPEC-402
**Componente:** Benchmarking & Analysis
**Prioridad:** Alta
**Estimación:** 4-6 horas
**Dependencias:** SPEC-401, Fases 1-4 completadas

---

## 📋 Descripción

Generar un reporte comparativo completo que muestre la evolución de métricas a través de todas las fases, con visualizaciones y análisis estadístico de mejoras.

---

## 🎯 Objetivos

1. **Ejecutar benchmarks** para todas las configuraciones
2. **Comparar resultados** entre fases
3. **Generar visualizaciones** de mejoras
4. **Análisis estadístico** de significancia
5. **Reportes exportables** (HTML, PDF, JSON)

---

## 📊 Arquitectura del Reporte

```
┌─────────────────────────────────────────────────┐
│         Benchmark Comparison Suite              │
└─────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
┌───────▼──────┐ ┌──▼──────┐ ┌─▼────────┐
│ Execute All  │ │ Compare │ │Visualize │
│ Benchmarks   │ │ Results │ │ Results  │
└───────┬──────┘ └──┬──────┘ └─┬────────┘
        │           │           │
        └───────────┼───────────┘
                    │
        ┌───────────▼───────────┐
        │  Generate Reports     │
        │  - HTML Dashboard     │
        │  - PDF Executive      │
        │  - JSON Raw Data      │
        └───────────────────────┘
```

---

## 🔄 Script de Comparación

### scripts/compare_all_phases.py

```python
#!/usr/bin/env python3
"""
Ejecutar benchmark para todas las fases y generar reporte comparativo.
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from app.services.search_service import SearchService
from app.database import get_db
from app.utils.metrics import calculate_precision_at_k, calculate_mrr

class BenchmarkRunner:
    """Run benchmarks for all phases."""

    def __init__(self):
        self.results_dir = Path("tests/results")
        self.results_dir.mkdir(exist_ok=True)

        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

        # Load benchmark queries
        with open("specs/phase-1-diagnostico/benchmark_queries.json") as f:
            self.benchmark_data = json.load(f)

    async def run_all_phases(self) -> Dict[str, Dict]:
        """Execute benchmarks for all phases."""

        configurations = [
            {
                "name": "Phase 1: Vector Only",
                "search_mode": "vector",
                "enable_reranking": False
            },
            {
                "name": "Phase 2: Hybrid Search",
                "search_mode": "hybrid",
                "enable_reranking": False
            },
            {
                "name": "Phase 3: Hybrid + Enrichment",
                "search_mode": "hybrid",
                "enable_reranking": False
            },
            {
                "name": "Phase 4: Hybrid + Reranking",
                "search_mode": "hybrid",
                "enable_reranking": True
            }
        ]

        all_results = {}

        for config in configurations:
            print(f"\n{'='*60}")
            print(f"Running: {config['name']}")
            print(f"{'='*60}")

            results = await self.run_benchmark(config)
            all_results[config['name']] = results

            # Save individual results
            self._save_results(config['name'], results)

        return all_results

    async def run_benchmark(self, config: Dict) -> Dict:
        """Run benchmark for a single configuration."""

        async with get_db() as db:
            service = SearchService(db)

            query_results = []
            total_latency = []

            for item in self.benchmark_data['queries']:
                query = item['query']
                expected = set(item['expected_modules'])

                print(f"\nQuery: {query}")

                start = time.time()

                results = await service.search_modules(
                    query=query,
                    version=item['version'],
                    search_mode=config['search_mode'],
                    enable_reranking=config.get('enable_reranking', False),
                    limit=10
                )

                latency_ms = (time.time() - start) * 1000
                total_latency.append(latency_ms)

                # Get technical names
                predicted = [r.technical_name for r in results]

                # Calculate metrics
                p_at_3 = calculate_precision_at_k(predicted, expected, k=3)
                p_at_5 = calculate_precision_at_k(predicted, expected, k=5)
                mrr = calculate_mrr(predicted, expected)

                query_results.append({
                    'query': query,
                    'predicted': predicted[:5],
                    'expected': list(expected),
                    'precision@3': p_at_3,
                    'precision@5': p_at_5,
                    'mrr': mrr,
                    'latency_ms': latency_ms
                })

                print(f"  P@3: {p_at_3:.2f}, P@5: {p_at_5:.2f}, MRR: {mrr:.2f}, Latency: {latency_ms:.0f}ms")

            # Aggregate metrics
            avg_p3 = sum(r['precision@3'] for r in query_results) / len(query_results)
            avg_p5 = sum(r['precision@5'] for r in query_results) / len(query_results)
            avg_mrr = sum(r['mrr'] for r in query_results) / len(query_results)
            avg_latency = sum(total_latency) / len(total_latency)

            return {
                'config': config,
                'query_results': query_results,
                'aggregate_metrics': {
                    'precision@3': avg_p3,
                    'precision@5': avg_p5,
                    'mrr': avg_mrr,
                    'avg_latency_ms': avg_latency
                },
                'timestamp': datetime.now().isoformat()
            }

    def _save_results(self, phase_name: str, results: Dict):
        """Save results to JSON."""

        safe_name = phase_name.lower().replace(" ", "_").replace(":", "")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{timestamp}.json"

        filepath = self.results_dir / filename

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Results saved: {filepath}")


class ComparisonReport:
    """Generate comparison reports."""

    def __init__(self, all_results: Dict[str, Dict]):
        self.all_results = all_results
        self.reports_dir = Path("reports")

    def generate_all_reports(self):
        """Generate all report formats."""

        print("\n" + "="*60)
        print("Generating Comparison Reports")
        print("="*60)

        self.generate_summary_table()
        self.generate_visualizations()
        self.generate_html_report()
        self.generate_json_export()

        print("\n✅ All reports generated in reports/")

    def generate_summary_table(self):
        """Print summary comparison table."""

        print("\n" + "="*60)
        print("BENCHMARK COMPARISON SUMMARY")
        print("="*60 + "\n")

        # Table header
        print(f"{'Phase':<30} {'P@3':>8} {'P@5':>8} {'MRR':>8} {'Latency':>10}")
        print("-" * 70)

        baseline_p3 = None

        for phase_name, results in self.all_results.items():
            metrics = results['aggregate_metrics']

            p3 = metrics['precision@3']
            p5 = metrics['precision@5']
            mrr = metrics['mrr']
            latency = metrics['avg_latency_ms']

            if baseline_p3 is None:
                baseline_p3 = p3

            improvement = ((p3 - baseline_p3) / baseline_p3 * 100) if baseline_p3 > 0 else 0

            phase_display = phase_name[:28]
            print(f"{phase_display:<30} {p3:>7.1%} {p5:>7.1%} {mrr:>7.2f} {latency:>8.0f}ms")

            if improvement > 0:
                print(f"{'':30} {'(+' + f'{improvement:.0f}%)':<8}")

        print("\n" + "="*60)

    def generate_visualizations(self):
        """Generate visualization charts."""

        # Prepare data
        phases = list(self.all_results.keys())
        p3_values = [r['aggregate_metrics']['precision@3'] for r in self.all_results.values()]
        p5_values = [r['aggregate_metrics']['precision@5'] for r in self.all_results.values()]
        mrr_values = [r['aggregate_metrics']['mrr'] for r in self.all_results.values()]
        latency_values = [r['aggregate_metrics']['avg_latency_ms'] for r in self.all_results.values()]

        # Shorten phase names for display
        phase_labels = [p.replace("Phase ", "P").replace(": ", "\n") for p in phases]

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('AI-OdooFinder: Benchmark Comparison Across All Phases', fontsize=16, fontweight='bold')

        # 1. Precision Comparison
        ax1 = axes[0, 0]
        x = range(len(phases))
        width = 0.35

        ax1.bar([i - width/2 for i in x], p3_values, width, label='P@3', alpha=0.8)
        ax1.bar([i + width/2 for i in x], p5_values, width, label='P@5', alpha=0.8)

        ax1.set_ylabel('Precision', fontsize=12)
        ax1.set_title('Precision@3 and Precision@5 by Phase', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(phase_labels, fontsize=9)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        ax1.set_ylim(0, 1.0)

        # Add value labels
        for i, (p3, p5) in enumerate(zip(p3_values, p5_values)):
            ax1.text(i - width/2, p3 + 0.02, f'{p3:.1%}', ha='center', fontsize=9)
            ax1.text(i + width/2, p5 + 0.02, f'{p5:.1%}', ha='center', fontsize=9)

        # 2. MRR Progression
        ax2 = axes[0, 1]
        ax2.plot(x, mrr_values, marker='o', linewidth=2, markersize=8, color='green')
        ax2.set_ylabel('MRR', fontsize=12)
        ax2.set_title('Mean Reciprocal Rank (MRR) Progression', fontsize=14, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(phase_labels, fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1.0)

        for i, mrr in enumerate(mrr_values):
            ax2.text(i, mrr + 0.02, f'{mrr:.2f}', ha='center', fontsize=9)

        # 3. Latency Comparison
        ax3 = axes[1, 0]
        colors = ['green' if l < 500 else 'orange' if l < 1500 else 'red' for l in latency_values]
        ax3.bar(x, latency_values, color=colors, alpha=0.7)
        ax3.set_ylabel('Latency (ms)', fontsize=12)
        ax3.set_title('Average Query Latency', fontsize=14, fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(phase_labels, fontsize=9)
        ax3.grid(axis='y', alpha=0.3)

        # Add target line
        ax3.axhline(y=2000, color='red', linestyle='--', label='Target (<2000ms)', alpha=0.5)
        ax3.legend()

        for i, lat in enumerate(latency_values):
            ax3.text(i, lat + 50, f'{lat:.0f}ms', ha='center', fontsize=9)

        # 4. Improvement Summary
        ax4 = axes[1, 1]
        baseline_p3 = p3_values[0]
        improvements = [(p3 - baseline_p3) / baseline_p3 * 100 for p3 in p3_values]

        colors_imp = ['gray' if i == 0 else 'green' for i in improvements]
        ax4.bar(x, improvements, color=colors_imp, alpha=0.7)
        ax4.set_ylabel('Improvement (%)', fontsize=12)
        ax4.set_title('P@3 Improvement vs Baseline', fontsize=14, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(phase_labels, fontsize=9)
        ax4.grid(axis='y', alpha=0.3)
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        for i, imp in enumerate(improvements):
            label = f'{imp:+.0f}%' if i > 0 else 'Baseline'
            ax4.text(i, imp + 2, label, ha='center', fontsize=9)

        plt.tight_layout()

        # Save figure
        output_path = self.reports_dir / "benchmark_comparison.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Visualization saved: {output_path}")

        plt.close()

    def generate_html_report(self):
        """Generate interactive HTML report."""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI-OdooFinder: Benchmark Comparison Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
        th {{
            background: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .metric {{
            display: inline-block;
            margin: 10px;
            padding: 15px 25px;
            background: #ecf0f1;
            border-radius: 6px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-label {{
            font-size: 14px;
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .improvement {{
            color: #27ae60;
            font-weight: bold;
        }}
        .degradation {{
            color: #e74c3c;
            font-weight: bold;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #bdc3c7;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <h1>🚀 AI-OdooFinder: Benchmark Comparison Report</h1>

    <div class="summary">
        <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Phases Compared:</strong> {len(self.all_results)}</p>
        <p><strong>Queries Tested:</strong> 20</p>
    </div>

    <h2>📊 Overall Metrics</h2>
"""

        # Add metrics for final phase
        final_phase = list(self.all_results.values())[-1]
        final_metrics = final_phase['aggregate_metrics']

        html += f"""
    <div style="text-align: center;">
        <div class="metric">
            <div class="metric-value">{final_metrics['precision@3']:.1%}</div>
            <div class="metric-label">Final P@3</div>
        </div>
        <div class="metric">
            <div class="metric-value">{final_metrics['precision@5']:.1%}</div>
            <div class="metric-label">Final P@5</div>
        </div>
        <div class="metric">
            <div class="metric-value">{final_metrics['mrr']:.2f}</div>
            <div class="metric-label">Final MRR</div>
        </div>
        <div class="metric">
            <div class="metric-value">{final_metrics['avg_latency_ms']:.0f}ms</div>
            <div class="metric-label">Avg Latency</div>
        </div>
    </div>
"""

        # Comparison table
        html += """
    <h2>📈 Phase-by-Phase Comparison</h2>
    <table>
        <thead>
            <tr>
                <th>Phase</th>
                <th>P@3</th>
                <th>P@5</th>
                <th>MRR</th>
                <th>Latency</th>
                <th>Improvement</th>
            </tr>
        </thead>
        <tbody>
"""

        baseline_p3 = list(self.all_results.values())[0]['aggregate_metrics']['precision@3']

        for phase_name, results in self.all_results.items():
            metrics = results['aggregate_metrics']
            improvement = ((metrics['precision@3'] - baseline_p3) / baseline_p3 * 100) if baseline_p3 > 0 else 0

            imp_class = 'improvement' if improvement > 0 else ''
            imp_text = f"+{improvement:.0f}%" if improvement > 0 else "Baseline"

            html += f"""
            <tr>
                <td><strong>{phase_name}</strong></td>
                <td>{metrics['precision@3']:.1%}</td>
                <td>{metrics['precision@5']:.1%}</td>
                <td>{metrics['mrr']:.2f}</td>
                <td>{metrics['avg_latency_ms']:.0f}ms</td>
                <td class="{imp_class}">{imp_text}</td>
            </tr>
"""

        html += """
        </tbody>
    </table>
"""

        # Visualization
        html += """
    <h2>📊 Visualizations</h2>
    <img src="benchmark_comparison.png" alt="Benchmark Comparison Charts">
"""

        # Footer
        html += f"""
    <div class="footer">
        <p>AI-OdooFinder Benchmark Report | Generated {datetime.now().strftime("%Y-%m-%d")}</p>
    </div>
</body>
</html>
"""

        output_path = self.reports_dir / "benchmark_comparison.html"
        with open(output_path, 'w') as f:
            f.write(html)

        print(f"✅ HTML report saved: {output_path}")

    def generate_json_export(self):
        """Export all results to JSON."""

        output_path = self.reports_dir / "benchmark_comparison.json"

        with open(output_path, 'w') as f:
            json.dump(self.all_results, f, indent=2)

        print(f"✅ JSON export saved: {output_path}")


async def main():
    """Main execution."""

    runner = BenchmarkRunner()

    print("="*60)
    print("AI-OdooFinder: Running All Phase Benchmarks")
    print("="*60)

    # Run all benchmarks
    all_results = await runner.run_all_phases()

    # Generate comparison reports
    reporter = ComparisonReport(all_results)
    reporter.generate_all_reports()

    print("\n" + "="*60)
    print("✅ BENCHMARK COMPARISON COMPLETE")
    print("="*60)
    print(f"\nReports available in: reports/")
    print("  - benchmark_comparison.html  (Interactive report)")
    print("  - benchmark_comparison.png   (Charts)")
    print("  - benchmark_comparison.json  (Raw data)")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📊 Example Output

```
==============================================================
AI-OdooFinder: Running All Phase Benchmarks
==============================================================

==============================================================
Running: Phase 1: Vector Only
==============================================================

Query: portal clientes con documentos personalizados
  P@3: 0.33, P@5: 0.40, MRR: 0.50, Latency: 187ms

Query: facturación electrónica para España
  P@3: 0.67, P@5: 0.80, MRR: 0.75, Latency: 192ms

...

✅ Results saved: tests/results/phase_1_vector_only_20251122_143022.json

==============================================================
Running: Phase 2: Hybrid Search
==============================================================
...

==============================================================
BENCHMARK COMPARISON SUMMARY
==============================================================

Phase                          P@3      P@5      MRR    Latency
----------------------------------------------------------------------
Phase 1: Vector Only          35.0%   42.0%    0.41      189ms

Phase 2: Hybrid Search        52.0%   58.0%    0.52      398ms
                              (+49%)

Phase 3: Hybrid + Enrichment  63.0%   71.0%    0.68      445ms
                              (+80%)

Phase 4: Hybrid + Reranking   68.0%   75.0%    0.73     1234ms
                              (+94%)

==============================================================

✅ All reports generated in reports/
```

---

## ✅ Criterios de Aceptación

- ✅ Benchmark ejecutado para todas las fases
- ✅ Reporte comparativo generado
- ✅ Visualizaciones creadas
- ✅ Mejora >30pp en P@3 desde baseline
- ✅ HTML report generado
- ✅ JSON export disponible

---

## 🔗 Siguiente Paso

→ [SPEC-403: Performance & Cost Analysis](./SPEC-403-performance-analysis.md)

---

**Estado:** 🔴 Pendiente de implementación
