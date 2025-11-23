# AI-OdooFinder - Especificaciones Técnicas

**Proyecto:** AI-OdooFinder Search Improvements
**Metodología:** Spec-Driven Development
**Fecha Inicio:** 22 Noviembre 2025

---

## 📚 Estructura de Especificaciones

Este directorio contiene todas las especificaciones técnicas para implementar las mejoras del sistema de búsqueda, organizadas por fases incrementales.

```
specs/
├── README.md                          # Este archivo
├── phase-1-diagnostico/              # Fase 1: Benchmark y Diagnóstico ✅
│   ├── README.md                     # Overview de Fase 1
│   ├── QUICKSTART.md                 # Guía de inicio rápido
│   ├── SPEC-001-benchmark-queries.md # Dataset de queries
│   ├── SPEC-002-benchmark-script.md  # Script de ejecución
│   ├── SPEC-003-metrics.md           # Cálculo de métricas
│   ├── SPEC-004-acceptance-criteria.md # Criterios de éxito
│   └── benchmark_queries_example.json # Template de queries
├── phase-2-hybrid-search/            # Fase 2: BM25 + Vector ✅
│   ├── README.md                     # Overview de Fase 2
│   ├── QUICKSTART.md                 # Guía de inicio rápido
│   ├── SPEC-101-database-migration.md # Migration SQL
│   ├── SPEC-102-hybrid-search-service.md # Servicio híbrido
│   ├── SPEC-103-rrf-algorithm.md     # Algoritmo RRF
│   ├── SPEC-104-search-integration.md # Integración
│   └── SPEC-105-acceptance-criteria.md # Criterios de éxito
├── phase-3-enrichment/               # Fase 3: Enriquecimiento [PRÓXIMAMENTE]
├── phase-4-reranking/                # Fase 4: LLM Reranking [PRÓXIMAMENTE]
└── phase-5-testing/                  # Fase 5: Testing Final [PRÓXIMAMENTE]
```

---

## 🎯 Roadmap de Implementación

### ✅ Fase 1: Diagnóstico y Benchmark (Día 1)
**Estado:** 🟢 Specs completas
**Objetivo:** Establecer baseline y patrones de fallo
**Specs:**
- [SPEC-001: Benchmark Queries](./phase-1-diagnostico/SPEC-001-benchmark-queries.md)
- [SPEC-002: Benchmark Script](./phase-1-diagnostico/SPEC-002-benchmark-script.md)
- [SPEC-003: Metrics Calculation](./phase-1-diagnostico/SPEC-003-metrics.md)
- [SPEC-004: Acceptance Criteria](./phase-1-diagnostico/SPEC-004-acceptance-criteria.md)

**Entregables:**
- ✅ 20 queries de benchmark validadas
- ✅ Baseline metrics (P@3, P@5, Recall, MRR)
- ✅ Análisis de 5+ patrones de fallo

**Criterio de éxito:** P@3 < 40% (confirma necesidad de mejoras)

---

### ✅ Fase 2: Hybrid Search (Días 2-3) - COMPLETADA
**Estado:** 🟢 COMPLETADA
**Objetivo:** Combinar vector similarity + BM25 full-text con RRF
**Specs:**
- [SPEC-101: Database Migration](./phase-2-hybrid-search/SPEC-101-database-migration.md)
- [SPEC-102: Hybrid Search Service](./phase-2-hybrid-search/SPEC-102-hybrid-search-service.md)
- [SPEC-103: RRF Algorithm](./phase-2-hybrid-search/SPEC-103-rrf-algorithm.md)
- [SPEC-104: Search Integration](./phase-2-hybrid-search/SPEC-104-search-integration.md)
- [SPEC-105: Acceptance Criteria](./phase-2-hybrid-search/SPEC-105-acceptance-criteria.md)

**Entregables:**
- ✅ PostgreSQL full-text search con tsvector + GIN
- ✅ HybridSearchService implementado
- ✅ Reciprocal Rank Fusion (RRF) funcional
- ✅ Integration en SearchService
- ✅ Tests de aceptación pasando (7/8)
- ✅ Validación manual exitosa (70% relevancia)
- ✅ Migración a psycopg3 completada

**Nota:** Benchmark cuantitativo pendiente de datos completos (Fase 3)

---

### 🔜 Fase 3: Data Enrichment (Días 4-6)
**Estado:** 🔵 Pendiente de specs
**Objetivo:** Añadir tags funcionales, AI descriptions, keywords

**Mejora esperada:** +10-15% adicional en Precision@3

---

### 🔜 Fase 4: LLM Reranking (Días 8-10)
**Estado:** 🔵 Pendiente de specs
**Objetivo:** Reordenar top 50 con Claude Haiku

**Mejora esperada:** +5-10% adicional en Precision@3

---

### 🔜 Fase 5: Testing & Validation (Días 11-14)
**Estado:** 🔵 Pendiente de specs
**Objetivo:** Test suite completo, reportes comparativos

**Entregable:** Reporte final con comparativa de todas las fases

---

## 🚀 Cómo Usar Estas Specs

### Para Implementadores

1. **Lee el README de la fase** para entender el contexto y objetivos
2. **Sigue las specs en orden** (SPEC-001, SPEC-002, etc.)
3. **Implementa según la firma de funciones** definida en cada spec
4. **Ejecuta los tests de validación** incluidos en cada spec
5. **Completa el checklist de acceptance criteria** antes de marcar como done

### Para Reviewers

1. **Verifica que la implementación sigue la spec** (firmas, estructura)
2. **Ejecuta los tests de validación** definidos
3. **Valida los criterios de aceptación** de SPEC-004
4. **Revisa casos edge** documentados en tests

### Para Product Owners

1. **Revisa el README de cada fase** para entender entregables
2. **Valida los criterios de éxito** en SPEC-004
3. **Aprueba las queries de benchmark** (especialmente importante para Fase 1)
4. **Revisa el failure analysis** para priorizar mejoras

---

## 📊 Métricas de Éxito del Proyecto

### Objetivos Mínimos

| Métrica | Baseline (Fase 1) | Target Final (Fase 5) | Mejora |
|---------|-------------------|-----------------------|--------|
| Precision@3 | ~35% | >60% | +25% |
| Precision@5 | ~42% | >70% | +28% |
| MRR | ~0.41 | >0.60 | +0.19 |
| Latencia | ~200ms | <2s | Aceptable |

### Objetivos Stretch

| Métrica | Target Stretch |
|---------|----------------|
| Precision@3 | >70% |
| Precision@5 | >80% |
| MRR | >0.70 |

---

## 🛠️ Stack Técnico

```yaml
Backend:
  - Python 3.14
  - FastAPI
  - SQLAlchemy 2.0

Database:
  - PostgreSQL 17
  - pgVector extension

APIs:
  - OpenRouter (embeddings: Qwen3-Embedding-4B)
  - Anthropic Claude (reranking, descriptions)

Testing:
  - pytest
  - pytest-asyncio

Metrics:
  - Custom IR metrics module
  - Precision, Recall, MRR, NDCG
```

---

## 📝 Convenciones de Especificaciones

### Estructura de Cada Spec

Todas las specs siguen este formato estándar:

```markdown
# SPEC-XXX: Título

**ID:** SPEC-XXX
**Componente:** Nombre del componente
**Archivo:** Path del archivo a crear
**Prioridad:** Alta/Media/Baja
**Estimación:** X horas
**Dependencias:** SPEC-YYY, SPEC-ZZZ

## 📋 Descripción
[Qué hace este componente]

## 🎯 Objetivos
[Objetivos medibles]

## 📐 Interfaz y API
[Firmas de funciones, schemas]

## ✅ Criterios de Aceptación
[Checklist de requisitos]

## 🧪 Tests de Validación
[Tests incluidos en la spec]

## 🚀 Pasos de Implementación
[Orden recomendado]
```

### IDs de Specs

```
SPEC-001 a SPEC-099: Fase 1
SPEC-100 a SPEC-199: Fase 2
SPEC-200 a SPEC-299: Fase 3
SPEC-300 a SPEC-399: Fase 4
SPEC-400 a SPEC-499: Fase 5
```

---

## 🔍 Glosario

**Precision@k:** Fracción de resultados relevantes en top K retornados

**Recall@k:** Fracción de resultados esperados encontrados en top K

**MRR:** Mean Reciprocal Rank - Inverso de la posición del primer resultado relevante

**RRF:** Reciprocal Rank Fusion - Método para combinar rankings

**BM25:** Best Matching 25 - Algoritmo de ranking basado en TF-IDF

**Ground Truth:** Resultados esperados correctos (expected_modules)

**Embedding:** Vector denso que representa semánticamente un texto

**Reranking:** Re-ordenar resultados usando un modelo más sofisticado

---

## 📚 Referencias

### Documentos del Proyecto
- [SYSTEM_IMPROVEMENTS.md](../docs/SYSTEM_IMPROVEMENTS.md) - Plan maestro de mejoras

### Literatura Técnica
- Manning et al. - Introduction to Information Retrieval
- Cormack et al. - Reciprocal Rank Fusion (SIGIR 2009)
- Pinecone - Hybrid Search Guide

---

## 🤝 Contribución

### Añadir Nueva Spec

1. Crea archivo en la carpeta de fase correspondiente
2. Sigue el template de estructura de spec
3. Añade entry en el README de la fase
4. Actualiza este README con el nuevo componente

### Modificar Spec Existente

1. Usa versionado en el header (e.g., "v1.1")
2. Documenta cambios en sección "Changelog"
3. Notifica a implementadores y reviewers

---

## 📞 Contacto

**Proyecto Lead:** TBD
**Tech Lead:** TBD
**Maintainers:** TBD

---

## ⚖️ Licencia

Especificaciones internas del proyecto AI-OdooFinder.

---

**Última actualización:** 23 Noviembre 2025
**Versión specs:** 1.1
**Fase actual:** Fase 2 completada ✅ | Próxima: Fase 3 - Data Enrichment
