# Fase 1: Diagnóstico y Benchmark - Especificaciones Técnicas

**Fecha:** 22 Noviembre 2025
**Proyecto:** AI-OdooFinder
**Fase:** 1 - Diagnóstico y Benchmark
**Duración Estimada:** 1 día
**Prioridad:** Alta (Bloqueante para fases siguientes)

---

## 📋 Objetivo

Establecer un sistema de evaluación cuantitativa de la calidad de búsqueda actual mediante:

1. **Benchmark Suite**: 20 búsquedas representativas con resultados esperados documentados
2. **Métricas Baseline**: Precisión, recall y MRR del sistema actual
3. **Análisis de Patrones**: Identificar tipos de búsquedas que fallan sistemáticamente

---

## 🎯 Entregables

| # | Entregable | Archivo | Criterio de Éxito |
|---|------------|---------|-------------------|
| 1 | Suite de queries de benchmark | `tests/benchmark_queries.json` | 20 queries validadas, 5 categorías cubiertas |
| 2 | Script de benchmark | `scripts/run_benchmark.py` | Ejecuta y calcula 4 métricas automáticamente |
| 3 | Resultado baseline | `tests/results/baseline_YYYYMMDD.json` | Precision@3 < 40% (confirma necesidad mejoras) |
| 4 | Análisis de fallos | `tests/results/failure_analysis.md` | 5 patrones documentados con ejemplos |

---

## 📚 Especificaciones

1. [SPEC-001: Benchmark Queries Dataset](./SPEC-001-benchmark-queries.md)
2. [SPEC-002: Benchmark Execution Script](./SPEC-002-benchmark-script.md)
3. [SPEC-003: Metrics Calculation](./SPEC-003-metrics.md)
4. [SPEC-004: Acceptance Criteria](./SPEC-004-acceptance-criteria.md)

---

## 🔄 Flujo de Trabajo

```mermaid
graph TD
    A[Crear benchmark_queries.json] --> B[Implementar run_benchmark.py]
    B --> C[Ejecutar baseline]
    C --> D[Analizar resultados]
    D --> E{Precision@3 < 40%?}
    E -->|Sí| F[✅ Fase 1 Completada]
    E -->|No| G[⚠️ Revisar queries o sistema]
    F --> H[Documentar patrones de fallo]
    H --> I[Iniciar Fase 2]
```

---

## 🧪 Tests de Validación

### Test 1: Benchmark Queries Válidas
```bash
# Validar que todas las queries son ejecutables
python -m pytest tests/test_benchmark_queries.py::test_all_queries_are_valid
```

**Criterio:** Todas las 20 queries deben tener:
- Campo `query` no vacío
- Campo `version` válido (12.0-19.0)
- Al menos 1 módulo esperado

### Test 2: Script Ejecutable
```bash
# El script debe completarse sin errores
python scripts/run_benchmark.py
```

**Criterio:**
- Sin excepciones
- Genera archivo JSON en `tests/results/`
- Output muestra progreso

### Test 3: Métricas Calculadas
```bash
# Validar que las métricas están presentes
python -m pytest tests/test_benchmark_metrics.py::test_metrics_present
```

**Criterio:** El resultado contiene:
- `aggregate_metrics.precision@3`
- `aggregate_metrics.precision@5`
- `aggregate_metrics.recall@10`
- `aggregate_metrics.mrr`

---

## 📊 Métricas de Éxito (Fase 1)

| Métrica | Target | Justificación |
|---------|--------|---------------|
| Precision@3 | < 40% | Confirma que hay margen de mejora significativo |
| Recall@10 | Cualquier valor | Baseline para comparación futura |
| MRR | Cualquier valor | Baseline para comparación futura |
| Queries ejecutadas | 20/20 | 100% de cobertura del benchmark |
| Tiempo ejecución | < 5 min | Feedback rápido para iteración |

---

## 🚨 Riesgos y Mitigaciones

### Riesgo 1: Queries mal diseñadas (esperados incorrectos)
**Impacto:** Alto - Invalidaría todo el benchmark
**Probabilidad:** Media
**Mitigación:**
- Review manual de queries críticas
- Validar al menos 5 queries manualmente antes de ejecutar
- Incluir queries de diferentes dificultades

### Riesgo 2: Sistema actual ya funciona bien (Precision > 60%)
**Impacto:** Bajo - Sería buena noticia
**Probabilidad:** Baja (según contexto del proyecto)
**Mitigación:**
- Si sucede, ajustar targets de mejora
- Enfocar en casos edge más difíciles

### Riesgo 3: API de embeddings falla durante benchmark
**Impacto:** Medio - Retrasaría la fase
**Probabilidad:** Baja
**Mitigación:**
- Implementar retry logic con backoff
- Cache de embeddings de queries

---

## 🔧 Dependencias Técnicas

### Nuevas Dependencias (si aplica)
Ninguna - Usa stack existente.

### Servicios Externos
- **OpenRouter API**: Para generar embeddings de queries
- **PostgreSQL**: Base de datos con módulos indexados

### Archivos Modificados
Ninguno - Solo crea nuevos archivos.

---

## 📝 Notas de Implementación

### Orden de Implementación Recomendado

1. **Primero:** Crear `benchmark_queries.json` (manual, revisar con cuidado)
2. **Segundo:** Implementar funciones de métricas (unit testeable)
3. **Tercero:** Implementar script de benchmark (orquestador)
4. **Cuarto:** Ejecutar y analizar resultados
5. **Quinto:** Documentar patrones de fallo

### Consideraciones Especiales

- **Queries en español:** Asegurar que el modelo de embeddings maneja bien español
- **Versiones Odoo:** Cubrir al menos 3 versiones diferentes (e.g., 16.0, 17.0, 18.0)
- **Categorías balanceadas:** No todas las queries de la misma área funcional

---

## ✅ Checklist de Implementación

- [ ] Crear estructura de directorios `tests/benchmark_queries.json` y `tests/results/`
- [ ] Implementar `tests/benchmark_queries.json` con 20 queries validadas
- [ ] Implementar `scripts/run_benchmark.py`
- [ ] Implementar funciones de cálculo de métricas
- [ ] Ejecutar benchmark y generar `baseline_YYYYMMDD.json`
- [ ] Analizar resultados y crear `failure_analysis.md`
- [ ] Validar que Precision@3 < 40% (o documentar si es mayor)
- [ ] Documentar 5 patrones de fallo identificados
- [ ] Code review de las queries (al menos 2 personas)
- [ ] Commit y push a repositorio

---

## 🔗 Referencias

- Documento maestro: [docs/SYSTEM_IMPROVEMENTS.md](../../docs/SYSTEM_IMPROVEMENTS.md) - Sección "Fase 1"
- Métricas IR: [Information Retrieval Metrics](https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval))
- Stack actual: FastAPI + PostgreSQL + pgVector + OpenRouter

---

**Estado:** 🔴 Pendiente
**Próximo paso:** Implementar SPEC-001 (Benchmark Queries)
