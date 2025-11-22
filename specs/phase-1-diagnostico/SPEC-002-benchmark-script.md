# SPEC-002: Benchmark Execution Script

**ID:** SPEC-002
**Componente:** Benchmark Runner
**Archivo:** `scripts/run_benchmark.py`
**Prioridad:** Alta
**Estimación:** 3-4 horas
**Dependencias:** SPEC-001 (Benchmark Queries)

---

## 📋 Descripción

Implementar un script Python que ejecute todas las queries del benchmark, calcule métricas de información retrieval (IR), y genere un reporte estructurado en JSON con resultados detallados y agregados.

---

## 🎯 Objetivos

1. **Automatización:** Ejecutar las 20 queries sin intervención manual
2. **Métricas estándar:** Calcular Precision@k, Recall@k, MRR
3. **Reporte estructurado:** JSON con resultados detallados y agregados
4. **Trazabilidad:** Timestamp y versionado de resultados
5. **Observabilidad:** Output progresivo durante ejecución

---

## 🏗️ Arquitectura

```
run_benchmark.py
├── main()                           # Entry point
├── BenchmarkRunner
│   ├── __init__(db_session)
│   ├── run()                        # Orquestador principal
│   ├── _load_queries()              # Carga benchmark_queries.json
│   ├── _execute_query()             # Ejecuta 1 query
│   └── _save_results()              # Persiste resultados
├── MetricsCalculator (SPEC-003)
│   ├── precision_at_k()
│   ├── recall_at_k()
│   ├── mrr()
│   └── calculate_all()
└── ReportGenerator
    ├── aggregate_metrics()
    ├── per_category_metrics()
    ├── per_difficulty_metrics()
    └── format_output()
```

---

## 📐 Interfaz y Firma de Funciones

### Clase Principal: BenchmarkRunner

```python
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.services.search_service import SearchService

class BenchmarkRunner:
    """Ejecuta benchmark de búsqueda y genera reporte."""

    def __init__(self, db: AsyncSession):
        """
        Inicializa el runner.

        Args:
            db: Sesión async de base de datos
        """
        self.db = db
        self.search_service = SearchService(db)
        self.metrics_calculator = MetricsCalculator()
        self.report_generator = ReportGenerator()

    async def run(
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

        Raises:
            FileNotFoundError: Si benchmark_queries.json no existe
            ValueError: Si queries están mal formadas
        """
        ...

    def _load_queries(self, filepath: str = "tests/benchmark_queries.json") -> List[Dict]:
        """
        Carga queries desde JSON.

        Returns:
            Lista de queries validadas

        Raises:
            FileNotFoundError: Si archivo no existe
            json.JSONDecodeError: Si JSON inválido
        """
        ...

    async def _execute_query(self, query_data: Dict, limit: int) -> Dict:
        """
        Ejecuta una query individual.

        Args:
            query_data: Objeto query del benchmark
            limit: Número de resultados a retornar

        Returns:
            Dict con:
                - query_id
                - query
                - returned_modules (lista de technical_names)
                - execution_time_ms
                - error (si hubo)
        """
        ...

    def _save_results(
        self,
        results: Dict,
        output_dir: str
    ) -> str:
        """
        Guarda resultados en archivo JSON timestamped.

        Args:
            results: Resultados completos
            output_dir: Directorio destino

        Returns:
            Path del archivo creado
        """
        ...
```

---

## 📊 Estructura del Output

### Archivo: `tests/results/baseline_YYYYMMDD_HHMMSS.json`

```json
{
  "metadata": {
    "timestamp": "2025-11-22T10:30:45Z",
    "total_queries": 20,
    "search_mode": "vector",
    "limit": 10,
    "execution_time_seconds": 45.2
  },
  "aggregate_metrics": {
    "precision@3": 0.35,
    "precision@5": 0.42,
    "recall@10": 0.58,
    "mrr": 0.412
  },
  "per_category": {
    "sales_workflow": {
      "count": 3,
      "precision@3": 0.33,
      "precision@5": 0.40
    },
    "accounting": {
      "count": 3,
      "precision@3": 0.44,
      "precision@5": 0.50
    }
    // ... más categorías
  },
  "per_difficulty": {
    "easy": {
      "count": 5,
      "precision@3": 0.60,
      "precision@5": 0.68
    },
    "medium": {
      "count": 10,
      "precision@3": 0.30,
      "precision@5": 0.38
    },
    "hard": {
      "count": 5,
      "precision@3": 0.13,
      "precision@5": 0.20
    }
  },
  "detailed_results": [
    {
      "query_id": 1,
      "query": "facturación electrónica España",
      "version": "16.0",
      "category": "localization_spain",
      "difficulty": "easy",
      "expected_modules": ["l10n_es_facturae", "l10n_es_aeat"],
      "returned_modules": [
        "l10n_es_facturae",      // ✅ Match
        "l10n_es_aeat",          // ✅ Match
        "l10n_es_vat_book",
        "account_invoice",
        "l10n_es"
      ],
      "metrics": {
        "precision@3": 0.667,   // 2/3 relevantes
        "precision@5": 0.40,    // 2/5 relevantes
        "recall@10": 1.0,       // 2/2 esperados encontrados
        "mrr": 1.0,             // Primer resultado es relevante
        "hits_in_top_3": 2,
        "hits_in_top_5": 2,
        "first_relevant_position": 1
      },
      "execution_time_ms": 234
    }
    // ... 19 queries más
  ]
}
```

---

## 🔍 Lógica de Cálculo de Métricas

### Precision@k

```python
def calculate_precision_at_k(
    retrieved: List[str],
    expected: List[str],
    k: int
) -> float:
    """
    Calcula precision@k: fracción de resultados relevantes en top K.

    Formula: P@k = (# relevantes en top K) / K

    Args:
        retrieved: Lista de módulos retornados (en orden)
        expected: Lista de módulos esperados (ground truth)
        k: Cutoff (típicamente 3 o 5)

    Returns:
        Precision en [0, 1]

    Example:
        >>> calculate_precision_at_k(
        ...     retrieved=["mod1", "mod2", "mod3", "mod4"],
        ...     expected=["mod1", "mod3"],
        ...     k=3
        ... )
        0.667  # 2 de 3 son relevantes
    """
    if not retrieved or k == 0:
        return 0.0

    top_k = retrieved[:k]
    relevant_count = sum(1 for mod in top_k if mod in expected)

    return relevant_count / k
```

### Recall@k

```python
def calculate_recall_at_k(
    retrieved: List[str],
    expected: List[str],
    k: int
) -> float:
    """
    Calcula recall@k: fracción de esperados que están en top K.

    Formula: R@k = (# esperados en top K) / (# total esperados)

    Args:
        retrieved: Lista de módulos retornados
        expected: Lista de módulos esperados
        k: Cutoff

    Returns:
        Recall en [0, 1]

    Example:
        >>> calculate_recall_at_k(
        ...     retrieved=["mod1", "mod2", "mod3"],
        ...     expected=["mod1", "mod3", "mod5"],
        ...     k=3
        ... )
        0.667  # 2 de 3 esperados fueron encontrados
    """
    if not expected:
        return 0.0

    top_k = retrieved[:k]
    found_count = sum(1 for exp in expected if exp in top_k)

    return found_count / len(expected)
```

### Mean Reciprocal Rank (MRR)

```python
def calculate_mrr(
    retrieved: List[str],
    expected: List[str]
) -> float:
    """
    Calcula Mean Reciprocal Rank: inverso del rank del primer relevante.

    Formula: MRR = 1 / (posición primer relevante)

    Args:
        retrieved: Lista de módulos retornados (ordenados)
        expected: Lista de módulos esperados

    Returns:
        MRR en [0, 1]

    Example:
        >>> calculate_mrr(
        ...     retrieved=["mod1", "mod2", "mod3", "mod4"],
        ...     expected=["mod3", "mod5"]
        ... )
        0.333  # Primer relevante en posición 3: 1/3
    """
    for i, module in enumerate(retrieved, start=1):
        if module in expected:
            return 1.0 / i

    return 0.0  # Ningún relevante encontrado
```

---

## 🖥️ Output de Consola

### Durante Ejecución (Verbose Mode)

```
================================================================================
AI-OdooFinder Benchmark Runner
================================================================================

Loading queries from: tests/benchmark_queries.json
✓ Loaded 20 queries successfully

Starting benchmark execution...

[1/20] Query: "facturación electrónica España"
       Version: 16.0 | Category: localization_spain | Difficulty: easy
       Expected: 2 modules
       ✓ Executed in 234ms
       Metrics: P@3=0.667 | P@5=0.40 | R@10=1.0 | MRR=1.0

[2/20] Query: "separar flujos B2B y B2C"
       Version: 16.0 | Category: sales_workflow | Difficulty: medium
       Expected: 3 modules
       ✓ Executed in 189ms
       Metrics: P@3=0.333 | P@5=0.40 | R@10=0.667 | MRR=0.5

...

[20/20] Query: "cross-docking con proveedores"
        Version: 18.0 | Category: inventory | Difficulty: hard
        Expected: 3 modules
        ✓ Executed in 201ms
        Metrics: P@3=0.0 | P@5=0.20 | R@10=0.333 | MRR=0.0

================================================================================
BENCHMARK COMPLETED
================================================================================

Execution Time: 45.2 seconds
Total Queries: 20

AGGREGATE METRICS:
  Precision@3:  35.0%  ████████████░░░░░░░░░░░░
  Precision@5:  42.0%  █████████████░░░░░░░░░░░
  Recall@10:    58.0%  ██████████████████░░░░░░
  Mean MRR:     0.412

BY DIFFICULTY:
  Easy    (5):  P@3=60.0% | P@5=68.0%
  Medium (10):  P@3=30.0% | P@5=38.0%
  Hard    (5):  P@3=13.0% | P@5=20.0%

Results saved to: tests/results/baseline_20251122_103045.json

================================================================================
```

---

## ✅ Criterios de Aceptación

### Criterio 1: Ejecución Completa
- ✅ Ejecuta las 20 queries sin fallos
- ✅ Maneja errores gracefully (timeout, API errors)
- ✅ No crashea si 1-2 queries fallan

### Criterio 2: Métricas Correctas
- ✅ Calcula Precision@3, Precision@5, Recall@10, MRR
- ✅ Métricas agregadas correctamente
- ✅ Métricas por categoría y dificultad

### Criterio 3: Output
- ✅ Genera archivo JSON válido
- ✅ Filename con timestamp: `baseline_YYYYMMDD_HHMMSS.json`
- ✅ Output de consola informativo

### Criterio 4: Performance
- ✅ Completa en < 5 minutos (20 queries × ~10s cada una)
- ✅ No hace queries innecesarias a la BD

---

## 🧪 Tests Unitarios

### Test 1: Metrics Calculation

```python
# tests/test_metrics.py

def test_precision_at_k():
    """Test precision calculation."""

    retrieved = ["mod1", "mod2", "mod3", "mod4"]
    expected = ["mod1", "mod3", "mod5"]

    # Top 3: 2 relevantes (mod1, mod3)
    assert calculate_precision_at_k(retrieved, expected, k=3) == 2/3

    # Top 5: 2 relevantes
    assert calculate_precision_at_k(retrieved, expected, k=5) == 0.4


def test_recall_at_k():
    """Test recall calculation."""

    retrieved = ["mod1", "mod2", "mod3"]
    expected = ["mod1", "mod3", "mod5"]

    # Found 2 out of 3 expected
    assert calculate_recall_at_k(retrieved, expected, k=3) == 2/3


def test_mrr():
    """Test MRR calculation."""

    # First relevant at position 1
    assert calculate_mrr(["mod1", "mod2"], ["mod1"]) == 1.0

    # First relevant at position 3
    assert calculate_mrr(["mod1", "mod2", "mod3"], ["mod3"]) == 1/3

    # No relevant
    assert calculate_mrr(["mod1", "mod2"], ["mod3"]) == 0.0
```

### Test 2: Query Loading

```python
@pytest.mark.asyncio
async def test_load_queries():
    """Test loading benchmark queries."""

    runner = BenchmarkRunner(db_session)
    queries = runner._load_queries("tests/benchmark_queries.json")

    assert len(queries) == 20
    assert all('query' in q for q in queries)
    assert all('expected_modules' in q for q in queries)
```

### Test 3: End-to-End (Sample)

```python
@pytest.mark.asyncio
async def test_benchmark_execution_sample(db_session):
    """Test executing a single query."""

    runner = BenchmarkRunner(db_session)

    query_data = {
        "id": 1,
        "query": "facturación electrónica España",
        "version": "16.0",
        "expected_modules": ["l10n_es_facturae", "l10n_es_aeat"],
        "category": "localization_spain",
        "difficulty": "easy"
    }

    result = await runner._execute_query(query_data, limit=10)

    assert 'query_id' in result
    assert 'returned_modules' in result
    assert 'metrics' in result
    assert len(result['returned_modules']) <= 10
```

---

## 🚨 Manejo de Errores

### Error 1: API Timeout
```python
try:
    results = await search_service.search_modules(...)
except asyncio.TimeoutError:
    logger.warning(f"Query {query_id} timed out")
    # Return partial result with error flag
    return {
        "query_id": query_id,
        "error": "timeout",
        "returned_modules": [],
        "metrics": None
    }
```

### Error 2: Módulo Esperado No Existe
```python
# Validar durante carga de queries
for expected_module in query['expected_modules']:
    exists = await db.execute(
        text("SELECT 1 FROM odoo_modules WHERE technical_name = :name"),
        {"name": expected_module}
    )
    if not exists.scalar():
        logger.error(f"Expected module '{expected_module}' not found in DB")
        # Opcional: Skip query o marcar como inválida
```

### Error 3: Archivo JSON Corrupto
```python
try:
    with open(filepath, 'r') as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in {filepath}: {e}")
    raise ValueError(f"Benchmark queries file is corrupted: {e}")
```

---

## 🚀 Pasos de Implementación

1. **Crear estructura base**
   - Archivo `scripts/run_benchmark.py`
   - Imports necesarios

2. **Implementar MetricsCalculator** (ver SPEC-003)
   - `precision_at_k()`
   - `recall_at_k()`
   - `mrr()`

3. **Implementar BenchmarkRunner**
   - `_load_queries()`
   - `_execute_query()`
   - `_save_results()`

4. **Implementar ReportGenerator**
   - `aggregate_metrics()`
   - `per_category_metrics()`
   - `per_difficulty_metrics()`

5. **Implementar main()**
   - CLI interface
   - Orquestación

6. **Añadir logging y progress**
   - Console output
   - Progress bar (opcional con `tqdm`)

7. **Testing**
   - Unit tests para métricas
   - Integration test con queries de ejemplo

---

## 🔗 Siguiente Paso

Una vez completado este SPEC, proceder a:
→ [SPEC-003: Metrics Calculation](./SPEC-003-metrics.md)

---

**Estado:** 🔴 Pendiente
**Implementador:** TBD
**Revisor:** TBD
