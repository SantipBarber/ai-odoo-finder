# SPEC-001: Benchmark Queries Dataset

**ID:** SPEC-001
**Componente:** Benchmark Suite
**Archivo:** `tests/benchmark_queries.json`
**Prioridad:** Alta
**Estimación:** 2-3 horas

---

## 📋 Descripción

Crear un dataset de 20 búsquedas representativas que cubran casos de uso reales de usuarios buscando módulos Odoo. Cada query debe incluir resultados esperados (ground truth) para evaluar la calidad del sistema de búsqueda.

---

## 🎯 Objetivos

1. **Representatividad:** Cubrir casos de uso reales y diversos
2. **Dificultad balanceada:** Mezcla de queries fáciles, medias y difíciles
3. **Cobertura funcional:** Al menos 5 categorías de Odoo diferentes
4. **Ground truth confiable:** Módulos esperados validados manualmente

---

## 📐 Estructura de Datos

### Schema JSON

```json
{
  "benchmark_queries": [
    {
      "id": 1,
      "query": "string",           // Búsqueda en lenguaje natural
      "version": "string",          // Versión Odoo (e.g., "16.0")
      "expected_modules": [         // Lista de technical_names esperados
        "module_1",
        "module_2",
        "module_3"
      ],
      "category": "string",         // Categoría funcional
      "difficulty": "string",       // "easy", "medium", "hard"
      "notes": "string"             // (Opcional) Contexto adicional
    }
  ],
  "metadata": {
    "created_at": "ISO-8601 timestamp",
    "total_queries": 20,
    "categories": ["category_1", "category_2", ...],
    "difficulty_distribution": {
      "easy": 5,
      "medium": 10,
      "hard": 5
    }
  }
}
```

### Validaciones

| Campo | Tipo | Requerido | Validación |
|-------|------|-----------|------------|
| `id` | integer | ✅ | Único, secuencial 1-20 |
| `query` | string | ✅ | No vacío, longitud 10-200 caracteres |
| `version` | string | ✅ | Formato "XX.0", rango 12.0-19.0 |
| `expected_modules` | array[string] | ✅ | Mínimo 1, máximo 5 módulos |
| `category` | string | ✅ | Enum de categorías válidas |
| `difficulty` | string | ✅ | "easy" | "medium" | "hard" |
| `notes` | string | ❌ | Opcional |

---

## 📊 Distribución de Queries

### Por Categoría (al menos 5 diferentes)

```yaml
Categorías Requeridas:
  - sales_workflow: 3 queries
  - accounting: 3 queries
  - inventory: 3 queries
  - localization_spain: 2 queries
  - portal: 2 queries
  - manufacturing: 2 queries
  - hr: 2 queries
  - website: 2 queries
  - other: 1 query
```

### Por Dificultad

```yaml
Distribución de Dificultad:
  easy: 5 queries    # Búsquedas directas con coincidencias exactas
  medium: 10 queries # Búsquedas semánticas estándar
  hard: 5 queries    # Búsquedas ambiguas o multi-concepto
```

**Criterios de Dificultad:**

- **Easy:** Query contiene términos exactos del `technical_name` o `name` del módulo
  - Ejemplo: "facturación electrónica" → `l10n_es_facturae`

- **Medium:** Query es semántica pero clara, necesita understanding del dominio
  - Ejemplo: "separar flujos B2B y B2C" → `sale_b2b_b2c`

- **Hard:** Query ambigua, multi-concepto o requiere contexto avanzado
  - Ejemplo: "portal clientes con documentos personalizados" → múltiples módulos posibles

### Por Versión Odoo

```yaml
Distribución de Versiones:
  16.0: 10 queries  # Versión más común actualmente
  17.0: 6 queries   # Versión reciente
  18.0: 4 queries   # Versión nueva
```

---

## 🔍 Ejemplos de Queries

### Ejemplo 1: Easy - Localization Spain

```json
{
  "id": 1,
  "query": "facturación electrónica España AEAT",
  "version": "16.0",
  "expected_modules": [
    "l10n_es_facturae",
    "l10n_es_aeat",
    "l10n_es_vat_book"
  ],
  "category": "localization_spain",
  "difficulty": "easy",
  "notes": "Términos muy específicos de localización española"
}
```

**Justificación Easy:**
- Contiene términos exactos: "facturación electrónica", "España", "AEAT"
- Módulos esperados tienen naming claro: `l10n_es_*`

### Ejemplo 2: Medium - Sales Workflow

```json
{
  "id": 2,
  "query": "separar flujos B2B y B2C en ventas",
  "version": "16.0",
  "expected_modules": [
    "sale_b2b_b2c",
    "portal_partner_type",
    "sale_partner_type"
  ],
  "category": "sales_workflow",
  "difficulty": "medium",
  "notes": "Requiere entender conceptos B2B/B2C en contexto Odoo"
}
```

**Justificación Medium:**
- Términos "B2B" y "B2C" no están en todos los módulos explícitamente
- Requiere understanding semántico de separación de flujos

### Ejemplo 3: Hard - Portal + DMS

```json
{
  "id": 3,
  "query": "portal clientes con documentos personalizados",
  "version": "16.0",
  "expected_modules": [
    "portal_document",
    "portal_partner_document",
    "dms_portal"
  ],
  "category": "portal",
  "difficulty": "hard",
  "notes": "Multi-concepto: portal + gestión documental + personalización"
}
```

**Justificación Hard:**
- Combina múltiples conceptos: portal, documentos, personalización
- Varios módulos podrían ser válidos
- Requiere contexto de integración entre módulos

---

## 📝 Template de Queries

### Sales & CRM

```json
// EASY
{
  "id": X,
  "query": "descuentos automáticos por volumen",
  "version": "16.0",
  "expected_modules": ["sale_discount_volume", "product_pricelist_volume"],
  "category": "sales_pricing",
  "difficulty": "easy"
}

// MEDIUM
{
  "id": X,
  "query": "workflow aprobación presupuestos",
  "version": "17.0",
  "expected_modules": ["sale_order_approval", "sale_order_validation"],
  "category": "sales_workflow",
  "difficulty": "medium"
}

// HARD
{
  "id": X,
  "query": "integrar tienda online con gestión de stock y envíos",
  "version": "16.0",
  "expected_modules": ["website_sale_stock", "delivery_integration", "website_sale_delivery"],
  "category": "website",
  "difficulty": "hard"
}
```

### Accounting & Finance

```json
// EASY
{
  "id": X,
  "query": "conciliación bancaria automática",
  "version": "16.0",
  "expected_modules": ["account_bank_reconciliation", "account_reconciliation_widget"],
  "category": "accounting",
  "difficulty": "easy"
}

// MEDIUM
{
  "id": X,
  "query": "informes financieros personalizados",
  "version": "17.0",
  "expected_modules": ["account_financial_report", "mis_builder"],
  "category": "accounting",
  "difficulty": "medium"
}
```

### Inventory & Logistics

```json
// EASY
{
  "id": X,
  "query": "trazabilidad de lotes y números de serie",
  "version": "17.0",
  "expected_modules": ["stock_production_lot", "product_expiry", "stock_lot_traceability"],
  "category": "inventory",
  "difficulty": "easy"
}

// MEDIUM
{
  "id": X,
  "query": "gestión de kits y productos compuestos",
  "version": "16.0",
  "expected_modules": ["mrp_bom", "sale_product_set", "product_pack"],
  "category": "inventory",
  "difficulty": "medium"
}

// HARD
{
  "id": X,
  "query": "cross-docking con proveedores y rutas automáticas",
  "version": "18.0",
  "expected_modules": ["stock_dropshipping", "stock_route", "purchase_stock"],
  "category": "inventory",
  "difficulty": "hard"
}
```

---

## ✅ Criterios de Aceptación

### Criterio 1: Completitud
- ✅ Exactamente 20 queries definidas
- ✅ Todos los campos requeridos presentes
- ✅ Metadata completa

### Criterio 2: Distribución
- ✅ Al menos 5 categorías diferentes cubiertas
- ✅ Distribución de dificultad: 5 easy, 10 medium, 5 hard
- ✅ Al menos 3 versiones Odoo diferentes

### Criterio 3: Validación de Expected Modules
- ✅ Todos los módulos en `expected_modules` existen en la BD
- ✅ Todos los módulos pertenecen a la versión especificada
- ✅ Al menos 1 módulo esperado por query

### Criterio 4: Calidad de Queries
- ✅ Queries en lenguaje natural (no technical_names)
- ✅ Queries representativas de uso real
- ✅ Sin duplicados

---

## 🧪 Tests de Validación

### Test 1: Schema Validation

```python
# tests/test_benchmark_queries.py

import json
import pytest
from pathlib import Path

def test_benchmark_queries_schema():
    """Valida que el schema JSON es correcto."""

    with open('tests/benchmark_queries.json', 'r') as f:
        data = json.load(f)

    # Check top-level keys
    assert 'benchmark_queries' in data
    assert 'metadata' in data

    # Check metadata
    metadata = data['metadata']
    assert metadata['total_queries'] == 20
    assert 'created_at' in metadata
    assert 'categories' in metadata
    assert 'difficulty_distribution' in metadata

    # Check queries count
    queries = data['benchmark_queries']
    assert len(queries) == 20

    # Check each query has required fields
    for query in queries:
        assert 'id' in query
        assert 'query' in query
        assert 'version' in query
        assert 'expected_modules' in query
        assert 'category' in query
        assert 'difficulty' in query

        # Validate types
        assert isinstance(query['id'], int)
        assert isinstance(query['query'], str)
        assert isinstance(query['version'], str)
        assert isinstance(query['expected_modules'], list)
        assert len(query['expected_modules']) >= 1
        assert query['difficulty'] in ['easy', 'medium', 'hard']
```

### Test 2: Expected Modules Exist in DB

```python
@pytest.mark.asyncio
async def test_expected_modules_exist_in_db(db_session):
    """Valida que todos los módulos esperados existen en la BD."""

    with open('tests/benchmark_queries.json', 'r') as f:
        data = json.load(f)

    for query_data in data['benchmark_queries']:
        for module_name in query_data['expected_modules']:
            # Check module exists
            result = await db_session.execute(
                text("SELECT COUNT(*) FROM odoo_modules WHERE technical_name = :name"),
                {"name": module_name}
            )
            count = result.scalar()

            assert count > 0, f"Module '{module_name}' not found in DB (query {query_data['id']})"
```

### Test 3: Distribution Validation

```python
def test_benchmark_distribution():
    """Valida que la distribución de queries es correcta."""

    with open('tests/benchmark_queries.json', 'r') as f:
        data = json.load(f)

    queries = data['benchmark_queries']

    # Count by difficulty
    difficulty_counts = {'easy': 0, 'medium': 0, 'hard': 0}
    for query in queries:
        difficulty_counts[query['difficulty']] += 1

    assert difficulty_counts['easy'] == 5
    assert difficulty_counts['medium'] == 10
    assert difficulty_counts['hard'] == 5

    # Count categories
    categories = set(q['category'] for q in queries)
    assert len(categories) >= 5, "Should have at least 5 different categories"

    # Count versions
    versions = set(q['version'] for q in queries)
    assert len(versions) >= 3, "Should have at least 3 different Odoo versions"
```

---

## 📚 Recursos

### Referencias para Crear Queries

1. **OCA GitHub:** Browse módulos populares en https://github.com/OCA
2. **Odoo Documentation:** Casos de uso comunes en https://www.odoo.com/documentation
3. **Real user queries:** Si hay logs de búsquedas previas, usarlas como inspiración

### Módulos Comunes por Categoría

**Sales:**
- `sale_order_approval`, `sale_discount`, `sale_quotation_template`

**Accounting:**
- `account_financial_report`, `account_bank_reconciliation`, `mis_builder`

**Inventory:**
- `stock_production_lot`, `product_expiry`, `stock_warehouse`

**Localization ES:**
- `l10n_es_facturae`, `l10n_es_aeat`, `l10n_es_vat_book`

**Manufacturing:**
- `mrp_bom`, `mrp_workorder`, `mrp_subcontracting`

---

## 🚀 Pasos de Implementación

1. **Crear archivo base** `tests/benchmark_queries.json` con estructura
2. **Definir metadata** con categorías y distribución objetivo
3. **Crear 5 queries EASY** con términos exactos
4. **Crear 10 queries MEDIUM** con búsquedas semánticas
5. **Crear 5 queries HARD** con multi-concepto
6. **Validar módulos esperados** contra BD (query SQL)
7. **Ejecutar tests de validación**
8. **Review manual** con al menos 1 persona adicional

---

## 🔗 Siguiente Paso

Una vez completado este SPEC, proceder a:
→ [SPEC-002: Benchmark Execution Script](./SPEC-002-benchmark-script.md)

---

**Estado:** 🔴 Pendiente
**Implementador:** TBD
**Revisor:** TBD
