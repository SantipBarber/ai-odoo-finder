# Changelog

Todos los cambios notables en AI-OdooFinder serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2025-01-XX

### 🚀 Fase 6: MCP Inteligente (SPEC-602)

Esta versión implementa el flujo inteligente de búsqueda MCP según SPEC-602.

### Added

#### Servidor MCP Local para Claude Desktop
- **Nuevo directorio `mcp-server/`** con servidor MCP standalone
  - `mcp-server/src/ai_odoofinder_mcp/server.py` - Servidor principal
  - `mcp-server/pyproject.toml` - Configuración del paquete
  - `mcp-server/README.md` - Instrucciones de instalación

#### Tool Description Enriquecido
- **Instrucciones de clarificación inteligente** en el parámetro `query`:
  - Cuándo pedir aclaraciones (queries genéricas, ambiguas, sin versión)
  - Cuándo NO pedir aclaraciones (queries específicas, nombres técnicos)
  
- **Instrucciones de construcción de query**:
  - Regla crítica para localizaciones: usar prefijo `l10n_XX_` como término principal
  - Ejemplos específicos para España, México, Argentina, Francia, Italia, etc.
  - Guía de sinónimos ES/EN para búsquedas no localizadas

#### Formato de Respuesta Estructurada
- **Niveles de confianza**: 🟢 ALTA (≥80), 🟡 MEDIA (50-79), 🟠 BAJA (<50), 🔴 NINGUNA
- **Secciones diferenciadas**:
  - ✅ RECOMENDADO: Módulos con score ≥80, formato detallado
  - 📋 ALTERNATIVAS: Módulos con score <80, formato resumido
- **Guía contextual** según nivel de confianza
- **Instrucciones para el LLM** sobre cómo presentar resultados

#### Migración de Base de Datos
- **`backend/migrations/005_add_repo_name_to_searchable_text.sql`**
  - Añade `repo_name` al campo `searchable_text` (tsvector)
  - Mejora búsqueda de localizaciones por nombre de país
  - Ejemplo: buscar "Spain" ahora encuentra módulos de `l10n-spain`

### Changed

- **`backend/app/mcp_tools.py`**: 
  - Actualizado `QUERY_DESCRIPTION` con instrucciones inteligentes
  - Nueva función `_format_results_intelligent()` con niveles de confianza
  - Nueva función `_calculate_confidence()` 
  - Nueva función `_format_module_detailed()` para recomendados
  - Nueva función `_format_module_summary()` para alternativas
  - Nueva función `_get_confidence_guidance()` con guías contextuales
  - Nueva función `_get_llm_instructions()` con instrucciones para el LLM
  - Nueva función `_format_no_results()` para casos sin resultados

### Fixed

- **Búsqueda de localizaciones**: Antes, buscar "facturae Spain" no encontraba `l10n_es_facturae` porque:
  - La descripción del módulo está en español
  - El campo `repo_name` (l10n-spain) no estaba indexado en BM25
  - Ahora `repo_name` se incluye en `searchable_text` con peso B

### Metrics

Resultados del testing con Claude Desktop:

| Consulta | Resultado | Módulos encontrados correctamente |
|----------|-----------|-----------------------------------|
| Facturae España (Odoo 16) | ✅ | `l10n_es_facturae_face`, `l10n_es_facturae_igic` |
| CFDI México (Odoo 17) | ✅ | `l10n_mx_cfdi`, `l10n_mx_cfdi_account` |
| Suscripciones (Odoo 16) | ✅ | `contract`, `subscription_oca` |
| DMS + OCR (Odoo 17) | ✅ | `dms`, `dms_storage` |
| AEAT mod303 (Odoo 16) | ✅ | `l10n_es_aeat_mod303` |
| Delivery carriers (Odoo 17) | ✅ | `delivery_price_method`, `product_packaging_dimension` |

---

## [1.0.0] - 2025-11-XX

### Fase 5: Search Quality & Testing

#### Added
- Benchmark suite para evaluar calidad de búsqueda
- Scripts de comparación de benchmarks
- Casos de prueba para localizaciones

#### Metrics
- Precision@3: 41.7%
- Precision@5: 30.0%
- MRR: 0.687

---

## [0.9.0] - 2025-11-XX

### Fase 4: Data Enrichment

#### Added
- Campo `ai_description` con descripciones generadas por IA
- Campo `keywords` con palabras clave extraídas
- Campo `functional_tags` con categorías funcionales
- Migración 004: Full-text search con campos de enrichment

#### Metrics
- 15,881 módulos enriquecidos (100%)

---

## [0.8.0] - 2025-11-XX

### Fase 3: Hybrid Search

#### Added
- Búsqueda híbrida (Vector + BM25)
- Reciprocal Rank Fusion (RRF)
- Campo `searchable_text` (tsvector)
- Índice GIN para full-text search

---

## [0.7.0] - 2025-11-XX

### Fase 2: Vector Search

#### Added
- Embeddings con Qwen3-Embedding-4B
- Índice HNSW para búsqueda vectorial
- pgVector integration

---

## [0.6.0] - 2025-11-XX

### Fase 1: ETL & Data Ingestion

#### Added
- ETL pipeline para módulos OCA
- Integración con GitHub API
- 15,881 módulos indexados de 176 repositorios
- Soporte para versiones 12.0 a 19.0

---

## Cómo Usar Este Changelog

- **Added**: Nuevas funcionalidades
- **Changed**: Cambios en funcionalidades existentes
- **Deprecated**: Funcionalidades que serán eliminadas
- **Removed**: Funcionalidades eliminadas
- **Fixed**: Corrección de bugs
- **Security**: Vulnerabilidades corregidas
- **Metrics**: Métricas de rendimiento/calidad