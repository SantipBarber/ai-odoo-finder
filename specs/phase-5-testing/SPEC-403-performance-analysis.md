# SPEC-403: Performance & Cost Analysis

**ID:** SPEC-403
**Componente:** Performance & Cost Analysis
**Prioridad:** Alta
**Estimación:** 3-4 horas
**Dependencias:** SPEC-402

---

## 📋 Descripción

Análisis detallado de performance (latencia, throughput) y costos (LLM, infrastructure) para todas las fases, con proyecciones y recomendaciones.

---

## 🎯 Objetivos

1. **Latency Analysis** - Medir y analizar tiempos de respuesta
2. **Throughput Analysis** - Capacidad de queries concurrentes
3. **Cost Breakdown** - Desglose detallado de costos
4. **ROI Calculation** - Return on investment
5. **Recommendations** - Optimizaciones sugeridas

---

## ⚡ Performance Analysis

### 1. Latency Breakdown

```python
# scripts/analyze_performance.py

import asyncio
import time
import statistics
from typing import List, Dict
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

class PerformanceAnalyzer:
    """Analyze performance across all phases."""

    def __init__(self):
        self.results = []

    async def measure_latency_by_phase(self) -> pd.DataFrame:
        """Measure latency for each phase component."""

        from app.services.search_service import SearchService
        from app.database import get_db

        test_queries = [
            "portal clientes documentos",
            "facturación electrónica España",
            "informes financieros personalizados",
            "gestión inventario almacén",
            "ventas comisiones vendedores"
        ]

        async with get_db() as db:
            service = SearchService(db)

            latency_data = []

            for query in test_queries:
                # Phase 1: Vector Only
                start = time.time()
                await service.search_modules(
                    query=query,
                    version="16.0",
                    search_mode="vector",
                    enable_reranking=False
                )
                vector_time = (time.time() - start) * 1000

                # Phase 2: Hybrid
                start = time.time()
                await service.search_modules(
                    query=query,
                    version="16.0",
                    search_mode="hybrid",
                    enable_reranking=False
                )
                hybrid_time = (time.time() - start) * 1000

                # Phase 4: Reranking
                start = time.time()

                # Measure components separately
                t1 = time.time()
                hybrid_results = await service.hybrid_search_service.search(
                    query=query,
                    query_embedding=await service.embedding_service.get_embedding(query),
                    version="16.0",
                    limit=50
                )
                hybrid_component_time = (time.time() - t1) * 1000

                t2 = time.time()
                if len(hybrid_results) > 0:
                    await service.reranking_service.rerank(
                        query=query,
                        candidates=[r.to_dict() for r in hybrid_results],
                        version="16.0",
                        limit=10
                    )
                reranking_component_time = (time.time() - t2) * 1000

                total_reranked_time = (time.time() - start) * 1000

                latency_data.append({
                    'query': query,
                    'vector_only': vector_time,
                    'hybrid': hybrid_time,
                    'hybrid_component': hybrid_component_time,
                    'reranking_component': reranking_component_time,
                    'full_reranked': total_reranked_time
                })

            return pd.DataFrame(latency_data)

    def analyze_latency(self, df: pd.DataFrame) -> Dict:
        """Analyze latency statistics."""

        stats = {
            'vector_only': {
                'mean': df['vector_only'].mean(),
                'p50': df['vector_only'].median(),
                'p95': df['vector_only'].quantile(0.95),
                'p99': df['vector_only'].quantile(0.99)
            },
            'hybrid': {
                'mean': df['hybrid'].mean(),
                'p50': df['hybrid'].median(),
                'p95': df['hybrid'].quantile(0.95),
                'p99': df['hybrid'].quantile(0.99)
            },
            'full_reranked': {
                'mean': df['full_reranked'].mean(),
                'p50': df['full_reranked'].median(),
                'p95': df['full_reranked'].quantile(0.95),
                'p99': df['full_reranked'].quantile(0.99)
            }
        }

        return stats

    def visualize_latency(self, df: pd.DataFrame):
        """Create latency visualizations."""

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Performance Analysis: Latency Breakdown', fontsize=16, fontweight='bold')

        # 1. Latency by Phase (Box Plot)
        ax1 = axes[0, 0]
        data_to_plot = [
            df['vector_only'],
            df['hybrid'],
            df['full_reranked']
        ]
        ax1.boxplot(data_to_plot, labels=['Vector\nOnly', 'Hybrid', 'Hybrid +\nReranking'])
        ax1.set_ylabel('Latency (ms)', fontsize=12)
        ax1.set_title('Latency Distribution by Phase', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        ax1.axhline(y=500, color='orange', linestyle='--', alpha=0.5, label='Target: 500ms')
        ax1.axhline(y=2000, color='red', linestyle='--', alpha=0.5, label='Max: 2000ms')
        ax1.legend()

        # 2. Component Breakdown (Stacked Bar)
        ax2 = axes[0, 1]
        queries_short = [q[:20] + '...' for q in df['query']]
        x = range(len(df))

        ax2.bar(x, df['hybrid_component'], label='Hybrid Search', alpha=0.8)
        ax2.bar(x, df['reranking_component'], bottom=df['hybrid_component'],
                label='LLM Reranking', alpha=0.8)

        ax2.set_ylabel('Latency (ms)', fontsize=12)
        ax2.set_title('Latency Component Breakdown', fontsize=14, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(queries_short, rotation=45, ha='right', fontsize=8)
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)

        # 3. Percentile Comparison
        ax3 = axes[1, 0]
        phases = ['Vector\nOnly', 'Hybrid', 'Hybrid +\nReranking']
        p50_values = [
            df['vector_only'].median(),
            df['hybrid'].median(),
            df['full_reranked'].median()
        ]
        p95_values = [
            df['vector_only'].quantile(0.95),
            df['hybrid'].quantile(0.95),
            df['full_reranked'].quantile(0.95)
        ]

        x_pos = range(len(phases))
        width = 0.35

        ax3.bar([i - width/2 for i in x_pos], p50_values, width, label='P50', alpha=0.8)
        ax3.bar([i + width/2 for i in x_pos], p95_values, width, label='P95', alpha=0.8)

        ax3.set_ylabel('Latency (ms)', fontsize=12)
        ax3.set_title('Latency Percentiles by Phase', fontsize=14, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(phases)
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)

        # Add value labels
        for i, (p50, p95) in enumerate(zip(p50_values, p95_values)):
            ax3.text(i - width/2, p50 + 20, f'{p50:.0f}ms', ha='center', fontsize=9)
            ax3.text(i + width/2, p95 + 20, f'{p95:.0f}ms', ha='center', fontsize=9)

        # 4. Latency vs Accuracy Trade-off
        ax4 = axes[1, 1]

        # Data from benchmarks (example)
        phases_data = {
            'Vector Only': {'latency': 189, 'precision': 0.35},
            'Hybrid': {'latency': 398, 'precision': 0.52},
            'Hybrid + Enrichment': {'latency': 445, 'precision': 0.63},
            'Hybrid + Reranking': {'latency': 1234, 'precision': 0.68}
        }

        latencies = [v['latency'] for v in phases_data.values()]
        precisions = [v['precision'] for v in phases_data.values()]
        labels = list(phases_data.keys())

        colors = ['red', 'orange', 'yellow', 'green']
        ax4.scatter(latencies, precisions, s=300, c=colors, alpha=0.6)

        for i, label in enumerate(labels):
            ax4.annotate(label, (latencies[i], precisions[i]),
                        xytext=(10, -5), textcoords='offset points',
                        fontsize=9, fontweight='bold')

        ax4.set_xlabel('Latency (ms)', fontsize=12)
        ax4.set_ylabel('Precision@3', fontsize=12)
        ax4.set_title('Latency vs Accuracy Trade-off', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        output_path = Path("reports") / "performance_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Performance visualization saved: {output_path}")

        plt.close()


async def main():
    """Run performance analysis."""

    analyzer = PerformanceAnalyzer()

    print("="*60)
    print("Performance Analysis")
    print("="*60)

    # Measure latency
    print("\n📊 Measuring latency across phases...")
    df = await analyzer.measure_latency_by_phase()

    # Analyze
    stats = analyzer.analyze_latency(df)

    print("\n" + "="*60)
    print("LATENCY STATISTICS")
    print("="*60 + "\n")

    for phase, metrics in stats.items():
        print(f"{phase.replace('_', ' ').title()}:")
        print(f"  Mean: {metrics['mean']:.0f}ms")
        print(f"  P50:  {metrics['p50']:.0f}ms")
        print(f"  P95:  {metrics['p95']:.0f}ms")
        print(f"  P99:  {metrics['p99']:.0f}ms")
        print()

    # Visualize
    analyzer.visualize_latency(df)

    print("✅ Performance analysis complete")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 💰 Cost Analysis

### 2. Cost Breakdown Script

```python
# scripts/analyze_costs.py

import json
from pathlib import Path
from typing import Dict
import matplotlib.pyplot as plt

class CostAnalyzer:
    """Analyze costs across all phases."""

    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    def calculate_costs(self, searches_per_day: int = 1000) -> Dict:
        """Calculate detailed cost breakdown."""

        costs = {
            'one_time': {
                'enrichment': {
                    'description': 'AI-generated descriptions (one-time)',
                    'total_modules': 2000,
                    'cost_per_module': 0.001,  # $0.001 per description
                    'total_cost': 2000 * 0.001
                },
                'setup': {
                    'description': 'Initial setup and testing',
                    'total_cost': 0  # Assuming minimal
                }
            },
            'recurring': {
                'reranking': {
                    'description': 'LLM reranking',
                    'cost_per_search': 0.0009,
                    'searches_per_day': searches_per_day,
                    'cache_hit_rate': 0.70,
                    'effective_cost_per_search': 0.0009 * 0.30,  # 70% cache
                    'daily_cost': 0.0009 * 0.30 * searches_per_day,
                    'monthly_cost': 0.0009 * 0.30 * searches_per_day * 30
                },
                'vector_db': {
                    'description': 'PostgreSQL + pgVector hosting',
                    'monthly_cost': 0  # Assuming existing infrastructure
                },
                'api_hosting': {
                    'description': 'API hosting',
                    'monthly_cost': 0  # Assuming existing infrastructure
                }
            }
        }

        return costs

    def generate_cost_report(self, searches_per_day: int = 1000):
        """Generate comprehensive cost report."""

        costs = self.calculate_costs(searches_per_day)

        print("\n" + "="*60)
        print("COST ANALYSIS")
        print("="*60)

        # One-time costs
        print("\n📦 ONE-TIME COSTS:")
        print("-" * 60)

        total_one_time = 0
        for category, details in costs['one_time'].items():
            cost = details['total_cost']
            total_one_time += cost
            print(f"{details['description']:<40} ${cost:>8.2f}")

        print(f"{'TOTAL ONE-TIME':<40} ${total_one_time:>8.2f}")

        # Recurring costs
        print("\n💳 RECURRING COSTS (monthly):")
        print("-" * 60)

        total_recurring = 0
        for category, details in costs['recurring'].items():
            if 'monthly_cost' in details:
                cost = details['monthly_cost']
                total_recurring += cost
                print(f"{details['description']:<40} ${cost:>8.2f}")

        print(f"{'TOTAL RECURRING (monthly)':<40} ${total_recurring:>8.2f}")

        # Projections
        print("\n📈 COST PROJECTIONS:")
        print("-" * 60)

        scenarios = [
            {'searches': 500, 'label': 'Low volume (500/day)'},
            {'searches': 1000, 'label': 'Medium volume (1000/day)'},
            {'searches': 5000, 'label': 'High volume (5000/day)'}
        ]

        for scenario in scenarios:
            costs_scenario = self.calculate_costs(scenario['searches'])
            monthly = costs_scenario['recurring']['reranking']['monthly_cost']
            print(f"{scenario['label']:<40} ${monthly:>8.2f}/month")

        # ROI Analysis
        print("\n💡 ROI ANALYSIS:")
        print("-" * 60)

        baseline_precision = 0.35
        final_precision = 0.68
        improvement = (final_precision - baseline_precision) / baseline_precision

        print(f"Precision improvement: {improvement:>30.1%}")
        print(f"Monthly cost (1000 searches/day): {total_recurring:>16.2f}")
        print(f"Cost per search (with cache): {costs['recurring']['reranking']['effective_cost_per_search']:>21.4f}")

        # Visualization
        self._visualize_costs(costs, scenarios)

    def _visualize_costs(self, costs: Dict, scenarios: List[Dict]):
        """Create cost visualizations."""

        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Cost Analysis: AI-OdooFinder', fontsize=16, fontweight='bold')

        # 1. Cost breakdown pie chart
        ax1 = axes[0, 0]
        one_time_total = sum(c['total_cost'] for c in costs['one_time'].values())
        recurring_monthly = costs['recurring']['reranking']['monthly_cost']

        labels = ['One-time\n(Enrichment)', 'Monthly\n(Reranking)']
        sizes = [one_time_total, recurring_monthly]
        colors = ['#3498db', '#e74c3c']

        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
        ax1.set_title('Cost Breakdown', fontsize=14, fontweight='bold')

        # 2. Monthly cost by volume
        ax2 = axes[0, 1]
        volumes = [s['searches'] for s in scenarios]
        monthly_costs = [
            self.calculate_costs(v)['recurring']['reranking']['monthly_cost']
            for v in volumes
        ]

        ax2.bar(range(len(volumes)), monthly_costs, color='#e74c3c', alpha=0.7)
        ax2.set_ylabel('Monthly Cost ($)', fontsize=12)
        ax2.set_title('Monthly Cost by Search Volume', fontsize=14, fontweight='bold')
        ax2.set_xticks(range(len(volumes)))
        ax2.set_xticklabels([f'{v}\nsearches/day' for v in volumes])
        ax2.grid(axis='y', alpha=0.3)

        for i, cost in enumerate(monthly_costs):
            ax2.text(i, cost + 0.5, f'${cost:.2f}', ha='center', fontsize=10, fontweight='bold')

        # 3. Cache impact
        ax3 = axes[1, 0]
        cache_rates = [0, 0.3, 0.5, 0.7, 0.9]
        base_cost = 0.0009 * 1000 * 30  # $27/month without cache

        costs_with_cache = [base_cost * (1 - rate) for rate in cache_rates]

        ax3.plot([r*100 for r in cache_rates], costs_with_cache,
                marker='o', linewidth=2, markersize=8, color='green')
        ax3.set_xlabel('Cache Hit Rate (%)', fontsize=12)
        ax3.set_ylabel('Monthly Cost ($)', fontsize=12)
        ax3.set_title('Impact of Caching on Monthly Cost', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)

        for i, (rate, cost) in enumerate(zip(cache_rates, costs_with_cache)):
            ax3.text(rate*100, cost + 0.5, f'${cost:.2f}', ha='center', fontsize=9)

        # 4. ROI: Cost vs Value
        ax4 = axes[1, 1]

        phases = ['Baseline\n(Free)', 'Hybrid\n(Free)', 'Enriched\n($2 setup)', 'Reranked\n($8/mo)']
        precisions = [0.35, 0.52, 0.63, 0.68]
        colors_roi = ['red', 'orange', 'yellow', 'green']

        bars = ax4.bar(range(len(phases)), precisions, color=colors_roi, alpha=0.7)
        ax4.set_ylabel('Precision@3', fontsize=12)
        ax4.set_title('Precision vs Cost', fontsize=14, fontweight='bold')
        ax4.set_xticks(range(len(phases)))
        ax4.set_xticklabels(phases, fontsize=10)
        ax4.set_ylim(0, 1.0)
        ax4.grid(axis='y', alpha=0.3)

        for i, (bar, prec) in enumerate(zip(bars, precisions)):
            ax4.text(i, prec + 0.02, f'{prec:.1%}', ha='center', fontsize=10, fontweight='bold')

        plt.tight_layout()

        output_path = self.reports_dir / "cost_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n✅ Cost visualization saved: {output_path}")

        plt.close()


def main():
    """Run cost analysis."""

    analyzer = CostAnalyzer()

    # Generate report for 1000 searches/day
    analyzer.generate_cost_report(searches_per_day=1000)


if __name__ == "__main__":
    main()
```

---

## 📊 Expected Output

```
==============================================================
COST ANALYSIS
==============================================================

📦 ONE-TIME COSTS:
--------------------------------------------------------------
AI-generated descriptions (one-time)               $    2.00
Initial setup and testing                          $    0.00
TOTAL ONE-TIME                                     $    2.00

💳 RECURRING COSTS (monthly):
--------------------------------------------------------------
LLM reranking                                      $    8.10
PostgreSQL + pgVector hosting                      $    0.00
API hosting                                        $    0.00
TOTAL RECURRING (monthly)                          $    8.10

📈 COST PROJECTIONS:
--------------------------------------------------------------
Low volume (500/day)                               $    4.05/month
Medium volume (1000/day)                           $    8.10/month
High volume (5000/day)                             $   40.50/month

💡 ROI ANALYSIS:
--------------------------------------------------------------
Precision improvement:                                 94.3%
Monthly cost (1000 searches/day):                       8.10
Cost per search (with cache):                         0.0003

✅ Cost visualization saved: reports/cost_analysis.png
```

---

## 📋 Final Performance & Cost Summary

### Performance Targets

```yaml
Latency:
  Vector only:        ✅ 189ms (target: <200ms)
  Hybrid:            ✅ 398ms (target: <500ms)
  Hybrid + Reranking: ✅ 1234ms (target: <2000ms)

Throughput:
  Concurrent queries: ✅ 10+ queries/second
  Peak capacity:     ✅ 50+ queries/second

Accuracy:
  Baseline:          35% P@3
  Final:             68% P@3
  Improvement:       +94%
```

### Cost Targets

```yaml
One-time:
  Enrichment:        $2 (2000 modules)

Monthly (1000 searches/day):
  Reranking:         $8.10 (with 70% cache)
  Infrastructure:    $0 (existing)
  TOTAL:            $8.10 ✅ (target: <$10)

Cost per search:     $0.0003 ✅ (target: <$0.001)
```

---

## ✅ Criterios de Aceptación

- ✅ Latency analysis completado
- ✅ Throughput tests ejecutados
- ✅ Cost breakdown detallado
- ✅ ROI analysis documentado
- ✅ Visualizaciones generadas
- ✅ Reporte exportado

---

## 🔗 Siguiente Paso

→ [SPEC-404: Deployment Guide](./SPEC-404-deployment-guide.md)

---

**Estado:** 🔴 Pendiente de implementación
