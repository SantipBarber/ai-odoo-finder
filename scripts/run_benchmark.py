#!/usr/bin/env python
"""
Script de ejecución de benchmark de búsqueda.

Este script ejecuta todas las queries del benchmark, calcula métricas IR
y genera un reporte estructurado con resultados detallados y agregados.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from statistics import mean

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.database import SessionLocal
from backend.app.services.search_service import SearchService
from backend.app.metrics.benchmark_metrics import MetricsCalculator, ReportAggregator


class BenchmarkRunner:
    """Ejecuta benchmark de búsqueda y genera reporte."""

    def __init__(self, db_session, search_mode: str = "hybrid"):
        """
        Inicializa el runner.

        Args:
            db_session: Sesión de base de datos
            search_mode: Modo de búsqueda ("vector", "bm25", "hybrid")
        """
        self.db = db_session
        self.search_service = SearchService(db_session)
        self.metrics_calculator = MetricsCalculator()
        self.report_aggregator = ReportAggregator()
        self.search_mode = search_mode

    def run(
        self,
        output_dir: str = "tests/results",
        limit: int = 10,
        verbose: bool = True
    ) -> Dict:
        """
        Ejecuta el benchmark completo.

        Args:
            output_dir: Directorio donde guardar resultados
            limit: Número de resultados a retornar por query (para calcular recall@10)
            verbose: Si True, imprime progreso

        Returns:
            Dict con resultados completos del benchmark
        """
        if verbose:
            print("=" * 80)
            print("AI-OdooFinder Benchmark Runner")
            print("=" * 80)

        start_time = datetime.now()

        # Load queries
        queries = self._load_queries()
        if verbose:
            print(f"\n✓ Loaded {len(queries)} queries successfully\n")
            print("Starting benchmark execution...\n")

        # Execute benchmark
        results = []
        for i, query_data in enumerate(queries, 1):
            if verbose:
                print(f"[{i}/{len(queries)}] Query: \"{query_data['query']}\"")
                print(f"       Version: {query_data['version']} | "
                      f"Category: {query_data['category']} | "
                      f"Difficulty: {query_data['difficulty']}")
                print(f"       Expected: {len(query_data['expected_modules'])} modules")

            result = self._execute_query(query_data, limit)
            results.append(result)

            # Print quick metrics
            if verbose and not result.get('error'):
                metrics = result['metrics']
                print(f"       ✓ Executed in {result['execution_time_ms']:.0f}ms")
                print(f"       Metrics: P@3={metrics['precision@3']:.3f} | "
                      f"R@10={metrics['recall@10']:.3f} | MRR={metrics['mrr']:.3f}\n")
            elif verbose:
                print(f"       ✗ Error: {result.get('error')}\n")

        # Generate report
        execution_time = (datetime.now() - start_time).total_seconds()
        report = self._generate_report(results, execution_time)

        # Save results
        output_path = self._save_results(report, output_dir)

        # Print summary
        if verbose:
            self._print_summary(report, output_path, execution_time)

        return report

    def _load_queries(self, filepath: str = "tests/benchmark_queries.json") -> List[Dict]:
        """
        Carga queries desde JSON.

        Returns:
            Lista de queries validadas

        Raises:
            FileNotFoundError: Si archivo no existe
            json.JSONDecodeError: Si JSON inválido
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data["benchmark_queries"]
        except FileNotFoundError:
            print(f"ERROR: Archivo {filepath} no encontrado")
            raise
        except json.JSONDecodeError as e:
            print(f"ERROR: JSON inválido en {filepath}: {e}")
            raise

    def _execute_query(self, query_data: Dict, limit: int) -> Dict:
        """
        Ejecuta una query individual.

        Args:
            query_data: Objeto query del benchmark
            limit: Número de resultados a retornar

        Returns:
            Dict con resultados y métricas
        """
        start_time = datetime.now()

        try:
            # Execute search
            search_results = self.search_service.search(
                query=query_data['query'],
                version=query_data['version'],
                limit=limit,
                search_mode=self.search_mode
            )

            # Extract module technical names
            returned_modules = [r['technical_name'] for r in search_results]

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
                'execution_time_ms': execution_time,
                'error': None
            }

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            print(f"       ERROR executing query {query_data['id']}: {e}")

            return {
                'query_id': query_data['id'],
                'query': query_data['query'],
                'version': query_data['version'],
                'category': query_data['category'],
                'difficulty': query_data['difficulty'],
                'expected_modules': query_data['expected_modules'],
                'returned_modules': [],
                'metrics': {
                    'precision@3': 0.0,
                    'precision@5': 0.0,
                    'recall@10': 0.0,
                    'mrr': 0.0,
                    'hits_in_top_3': 0,
                    'hits_in_top_5': 0,
                    'first_relevant_position': None
                },
                'execution_time_ms': execution_time,
                'error': str(e)
            }

    def _generate_report(self, results: List[Dict], execution_time: float) -> Dict:
        """
        Genera reporte agregado.

        Args:
            results: Lista de resultados detallados
            execution_time: Tiempo total de ejecución en segundos

        Returns:
            Dict con reporte completo
        """
        # Filter out errors for metric calculation
        valid_results = [r for r in results if not r.get('error')]

        if not valid_results:
            print("WARNING: No valid results to aggregate")
            aggregate = {
                'precision@3': 0.0,
                'precision@5': 0.0,
                'recall@10': 0.0,
                'mrr': 0.0
            }
            per_category = {}
            per_difficulty = {}
        else:
            # Aggregate metrics
            aggregate = {
                'precision@3': mean(r['metrics']['precision@3'] for r in valid_results),
                'precision@5': mean(r['metrics']['precision@5'] for r in valid_results),
                'recall@10': mean(r['metrics']['recall@10'] for r in valid_results),
                'mrr': mean(r['metrics']['mrr'] for r in valid_results)
            }

            # Per category metrics
            per_category = self.report_aggregator.group_by_difficulty(valid_results)

            # Per difficulty metrics
            per_difficulty = self.report_aggregator.group_by_difficulty(valid_results)

        return {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_queries': len(results),
                'valid_queries': len(valid_results),
                'failed_queries': len(results) - len(valid_results),
                'search_mode': self.search_mode,
                'limit': 10,
                'execution_time_seconds': execution_time
            },
            'aggregate_metrics': aggregate,
            'per_difficulty': per_difficulty,
            'detailed_results': results
        }

    def _save_results(self, report: Dict, output_dir: str) -> str:
        """
        Guarda resultados en archivo JSON timestamped.

        Args:
            report: Reporte completo
            output_dir: Directorio destino

        Returns:
            Path del archivo creado
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.search_mode}_{timestamp}.json"
        filepath = Path(output_dir) / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def _print_summary(self, report: Dict, output_path: str, execution_time: float):
        """
        Imprime resumen en consola.

        Args:
            report: Reporte completo
            output_path: Ruta del archivo guardado
            execution_time: Tiempo de ejecución en segundos
        """
        metrics = report['aggregate_metrics']
        metadata = report['metadata']

        print("\n" + "=" * 80)
        print("BENCHMARK COMPLETED")
        print("=" * 80)
        print(f"\nExecution Time: {execution_time:.1f} seconds")
        print(f"Total Queries: {metadata['total_queries']}")
        print(f"Valid Queries: {metadata['valid_queries']}")
        if metadata['failed_queries'] > 0:
            print(f"Failed Queries: {metadata['failed_queries']}")

        print(f"\nAGGREGATE METRICS:")
        print(f"  Precision@3:  {metrics['precision@3']:.1%}  {'█' * int(metrics['precision@3'] * 24)}{'░' * (24 - int(metrics['precision@3'] * 24))}")
        print(f"  Precision@5:  {metrics['precision@5']:.1%}  {'█' * int(metrics['precision@5'] * 24)}{'░' * (24 - int(metrics['precision@5'] * 24))}")
        print(f"  Recall@10:    {metrics['recall@10']:.1%}  {'█' * int(metrics['recall@10'] * 24)}{'░' * (24 - int(metrics['recall@10'] * 24))}")
        print(f"  Mean MRR:     {metrics['mrr']:.3f}")

        # Per difficulty breakdown
        if 'per_difficulty' in report and report['per_difficulty']:
            print(f"\nBY DIFFICULTY:")
            for difficulty in ['easy', 'medium', 'hard']:
                if difficulty in report['per_difficulty']:
                    d = report['per_difficulty'][difficulty]
                    print(f"  {difficulty.capitalize():6} ({d['count']:2}):  "
                          f"P@3={d['precision@3']:.1%} | P@5={d['precision@5']:.1%}")

        print(f"\nResults saved to: {output_path}")
        print("=" * 80)


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description='Run search benchmark with specified search mode'
    )
    parser.add_argument(
        '--search-mode',
        choices=['vector', 'bm25', 'hybrid'],
        default='hybrid',
        help='Search mode to benchmark (default: hybrid)'
    )
    args = parser.parse_args()

    print(f"\n🚀 Starting benchmark with search_mode={args.search_mode}...\n")

    db = SessionLocal()
    try:
        runner = BenchmarkRunner(db, search_mode=args.search_mode)
        report = runner.run(verbose=True)

        # Return exit code based on success
        if report['metadata']['failed_queries'] == 0:
            print("\n✅ Benchmark completed successfully!")
            return 0
        else:
            print(f"\n⚠️  Benchmark completed with {report['metadata']['failed_queries']} failures")
            return 1

    except Exception as e:
        print(f"\n❌ Benchmark failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == '__main__':
    sys.exit(main())
