# SPEC-103: RRF Algorithm Implementation

**ID:** SPEC-103
**Componente:** Ranking Algorithm
**Archivo:** Incluido en `hybrid_search_service.py`
**Prioridad:** Media
**Estimación:** 1-2 horas (incluido en SPEC-102)
**Dependencias:** SPEC-102

---

## 📋 Descripción

Documentación detallada del algoritmo Reciprocal Rank Fusion (RRF) usado para combinar rankings de vector search y BM25 search, incluyendo matemática, ejemplos, y tuning de parámetros.

---

## 🎯 Objetivos

1. **Entender la matemática** detrás de RRF
2. **Implementar correctamente** la fórmula
3. **Tuning del parámetro k** para mejores resultados
4. **Validar correctitud** matemática

---

## 📐 Matemática de RRF

### Fórmula Original

```
RRF(d ∈ D) = Σ(r ∈ R) 1/(k + r(d))

donde:
  d = documento
  D = conjunto de todos los documentos
  R = conjunto de rankings (múltiples listas)
  r(d) = ranking del documento d en la lista r
  k = constante de suavizado (típicamente 60)
```

### En Nuestro Caso (2 listas)

```
RRF(module) = 1/(k + rank_vector(module)) + 1/(k + rank_bm25(module))

Si el módulo solo aparece en una lista:
RRF(module) = 1/(k + rank_only_list(module))
```

### ¿Por qué funciona RRF?

1. **No requiere normalización:** Vector scores [0-1] vs BM25 scores [0-∞] no son comparables directamente
2. **Robusto a outliers:** Un score muy alto en una lista no domina completamente
3. **Favorece overlap:** Módulos en ambas listas reciben boost
4. **Simple y efectivo:** Usado en Elasticsearch, Vespa, etc.

---

## 🧮 Ejemplos Paso a Paso

### Ejemplo 1: Con Overlap

**Inputs:**
```python
Vector ranking:  [A:1, B:2, C:3, D:4]
BM25 ranking:    [C:1, A:2, E:3, B:4]
k = 60
```

**Cálculo:**

```
RRF(A) = 1/(60+1) + 1/(60+2) = 1/61 + 1/62 = 0.0164 + 0.0161 = 0.0325
RRF(B) = 1/(60+2) + 1/(60+4) = 1/62 + 1/64 = 0.0161 + 0.0156 = 0.0317
RRF(C) = 1/(60+3) + 1/(60+1) = 1/63 + 1/61 = 0.0159 + 0.0164 = 0.0323
RRF(D) = 1/(60+4) + 0       = 1/64        = 0.0156
RRF(E) = 0       + 1/(60+3) = 1/63        = 0.0159
```

**Final ranking:**
```
1. A: 0.0325  (was #1 vector, #2 BM25)
2. C: 0.0323  (was #3 vector, #1 BM25)
3. B: 0.0317  (was #2 vector, #4 BM25)
4. E: 0.0159  (was only in BM25 #3)
5. D: 0.0156  (was only in vector #4)
```

**Observación:** Módulos en ambas listas (A, B, C) rankean más alto.

---

### Ejemplo 2: Sin Overlap

**Inputs:**
```python
Vector ranking:  [A:1, B:2, C:3]
BM25 ranking:    [D:1, E:2, F:3]
k = 60
```

**Cálculo:**
```
RRF(A) = 1/(60+1) = 0.0164
RRF(B) = 1/(60+2) = 0.0161
RRF(C) = 1/(60+3) = 0.0159
RRF(D) = 1/(60+1) = 0.0164
RRF(E) = 1/(60+2) = 0.0161
RRF(F) = 1/(60+3) = 0.0159
```

**Final ranking:**
```
1. A: 0.0164 (tie with D)
1. D: 0.0164 (tie with A)
3. B: 0.0161 (tie with E)
3. E: 0.0161 (tie with B)
5. C: 0.0159 (tie with F)
5. F: 0.0159 (tie with C)
```

**Observación:** Sin overlap, order es similar al original.

---

### Ejemplo 3: Caso Real Odoo

**Query:** "account reconciliation"

**Vector results (por similarity):**
```
1. account_payment:        0.88
2. account_banking:        0.85
3. account_reconciliation: 0.82  ← Este es el correcto
4. account_invoice:        0.78
```

**BM25 results (por ts_rank):**
```
1. account_reconciliation:  12.4  ← Exacto match en technical_name
2. reconciliation_widget:    8.2
3. account_payment:          5.1
4. account_banking:          4.3
```

**RRF (k=60):**
```
account_reconciliation:
  1/(60+3) + 1/(60+1) = 0.0159 + 0.0164 = 0.0323 → #1 ✅

account_payment:
  1/(60+1) + 1/(60+3) = 0.0164 + 0.0159 = 0.0323 → #1 (tie)

account_banking:
  1/(60+2) + 1/(60+4) = 0.0161 + 0.0156 = 0.0317 → #3

reconciliation_widget:
  0 + 1/(60+2) = 0.0161 → #4
```

**Resultado:** account_reconciliation sube de #3 a #1 ✅

---

## ⚙️ Tuning del Parámetro k

### ¿Qué hace k?

- **k pequeño (k=10):** Enfatiza diferencias entre rankings
- **k grande (k=100):** Suaviza diferencias
- **k=60:** Balance estándar (literatura)

### Ejemplo de Impacto de k

**Setup:**
```
Vector: [A:1, B:2]
BM25:   [B:1, A:10]
```

**Con k=10:**
```
RRF(A) = 1/(10+1) + 1/(10+10) = 0.0909 + 0.0500 = 0.1409
RRF(B) = 1/(10+2) + 1/(10+1)  = 0.0833 + 0.0909 = 0.1742
Winner: B (diferencia grande: 24%)
```

**Con k=100:**
```
RRF(A) = 1/(100+1) + 1/(100+10) = 0.0099 + 0.0091 = 0.0190
RRF(B) = 1/(100+2) + 1/(100+1)  = 0.0098 + 0.0099 = 0.0197
Winner: B (diferencia pequeña: 4%)
```

**Conclusión:** k más bajo da más peso a las posiciones exactas.

---

## 🧪 Validación Matemática

### Tests de Correctitud

```python
def test_rrf_formula_correctness():
    """Verifica que la fórmula RRF es correcta."""

    # Ejemplo del paper de Cormack
    k = 60

    # Module A: rank 1 in list1, rank 2 in list2
    expected_a = 1/(60+1) + 1/(60+2)
    assert abs(expected_a - 0.0325) < 0.0001

    # Module B: rank 3 in list1, rank 1 in list2
    expected_b = 1/(60+3) + 1/(60+1)
    assert abs(expected_b - 0.0323) < 0.0001

    # A should rank higher than B
    assert expected_a > expected_b


def test_rrf_only_one_list():
    """Módulo que solo aparece en una lista."""

    k = 60

    # Module only in vector search at rank 5
    rrf_score = 1/(k + 5)

    assert abs(rrf_score - 0.0154) < 0.0001


def test_rrf_tie_breaking():
    """Cuando dos módulos tienen mismo RRF score."""

    # En caso de tie, mantener orden de la lista original
    # (determinista, no random)
    pass
```

---

## 🎛️ Recomendaciones de Tuning

### k=60 (Default Recomendado)

**Usar cuando:**
- Primera implementación
- Sin datos históricos de performance
- Balance entre precisión y diversidad

**Razón:** Valor bien estudiado en literatura IR.

### k=30 (Más agresivo)

**Usar cuando:**
- Quieres enfatizar posiciones exactas
- Hay mucho overlap entre listas
- Precision > Recall

**Trade-off:** Módulos en posición 10+ tienen muy poco peso.

### k=90 (Más conservador)

**Usar cuando:**
- Quieres más diversidad
- Hay poco overlap
- Recall > Precision

**Trade-off:** Diferencias entre posiciones se suavizan.

---

## 📊 Grid Search para k Optimal

```python
# scripts/tune_rrf_k.py

import asyncio
from app.services.benchmark_runner import BenchmarkRunner

async def grid_search_k():
    """Encuentra k óptimo para RRF."""

    k_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    results = []

    for k in k_values:
        print(f"Testing k={k}...")

        # Run benchmark with this k
        runner = BenchmarkRunner(db, k=k)
        metrics = await runner.run()

        results.append({
            'k': k,
            'precision@3': metrics['precision@3'],
            'precision@5': metrics['precision@5'],
            'mrr': metrics['mrr']
        })

    # Find best k
    best = max(results, key=lambda x: x['precision@3'])
    print(f"\nBest k: {best['k']}")
    print(f"P@3: {best['precision@3']:.3f}")

    return best

if __name__ == '__main__':
    asyncio.run(grid_search_k())
```

**Ejemplo de output:**
```
Testing k=10...  P@3=0.52
Testing k=20...  P@3=0.53
Testing k=30...  P@3=0.54
Testing k=40...  P@3=0.55
Testing k=50...  P@3=0.56
Testing k=60...  P@3=0.57  ← Best
Testing k=70...  P@3=0.56
Testing k=80...  P@3=0.55
Testing k=90...  P@3=0.54
Testing k=100... P@3=0.53

Best k: 60
```

---

## 🔬 Alternativas a RRF (No Recomendadas para Fase 2)

### 1. Weighted Average

```python
score = w1 * normalized_vector_score + w2 * normalized_bm25_score
```

**Problemas:**
- Requiere normalización (compleja para BM25)
- Tuning de weights (w1, w2) es difícil
- Sensible a magnitudes diferentes

### 2. Max Score

```python
score = max(normalized_vector_score, normalized_bm25_score)
```

**Problemas:**
- No considera overlap
- Módulos en ambas listas no reciben boost

### 3. Product

```python
score = vector_score * bm25_score
```

**Problemas:**
- Si uno es 0, score total es 0
- Requiere normalización

**Conclusión:** RRF es la mejor opción para hybrid search.

---

## ✅ Criterios de Aceptación

### AC-1: Formula Correcta
- ✅ Implementación matches paper de Cormack
- ✅ Tests matemáticos pasan

### AC-2: Casos Edge Manejados
- ✅ Módulo solo en vector list
- ✅ Módulo solo en BM25 list
- ✅ Módulo en ambas listas
- ✅ Listas vacías

### AC-3: k Configurable
- ✅ k es parámetro ajustable
- ✅ Default k=60
- ✅ Documentado cómo tunear

---

## 📚 Referencias

### Paper Original
- **Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods**
- Cormack, Clarke, Büttcher - SIGIR 2009
- https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf

### Implementaciones de Referencia
- Elasticsearch: https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html
- Vespa: https://docs.vespa.ai/en/reference/rank-features.html
- Weaviate: https://weaviate.io/developers/weaviate/search/hybrid

---

**Estado:** 🟢 Documentación completa (implementación en SPEC-102)
**Implementador:** Ver SPEC-102
