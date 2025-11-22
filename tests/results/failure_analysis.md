# Análisis de Patrones de Fallo - Baseline

**Fecha:** 2025-11-22
**Versión Benchmark:** 1.0
**Archivo Resultados:** [baseline_20251122_181454.json](baseline_20251122_181454.json)

---

## 📊 Resumen Ejecutivo

El benchmark baseline reveló un **fallo total del sistema** con métricas en 0%:

- **Precision@3:** 0.0% (0/20 queries con resultados relevantes)
- **Precision@5:** 0.0%
- **Recall@10:** 0.0%
- **MRR:** 0.000

**Conclusión crítica:** El sistema NO encontró NINGUNO de los módulos esperados en las 20 queries de prueba. Esto indica problemas fundamentales que deben ser abordados en las siguientes fases.

---

## 🔍 Patrones de Fallo Identificados

### Patrón 1: Desconexión Total con Expected Modules

**Descripción:**
El sistema retorna módulos relacionados temáticamente pero NO encuentra ninguno de los módulos específicos esperados.

**Frecuencia:** 20/20 queries (100%)

**Ejemplo 1:**
```json
Query: "facturación electrónica España AEAT"
Expected: ["l10n_es_facturae", "l10n_es_aeat"]
Returned: [
  "account_fiscal_position_vat_check",
  "account_move_name_sequence",
  "account_fiscal_year_auto_create"
]
```

**Ejemplo 2:**
```json
Query: "separar flujos B2B y B2C en ventas"
Expected: ["sale_b2b_b2c", "portal_partner_type", "sale_partner_type"]
Returned: [
  "sale_automatic_workflow_job",
  "partner_sale_pivot",
  "sale_invoice_blocking"
]
```

**Análisis:**
- El sistema encuentra módulos de las categorías correctas (accounting, sales)
- Pero NO encuentra los módulos específicos esperados
- **Hipótesis principal:** Los `expected_modules` del benchmark NO existen en la base de datos real
- **Hipótesis secundaria:** La búsqueda vectorial no está funcionando correctamente

**Mejora Propuesta:**
1. **CRÍTICO - Fase 0:** Validar que todos los `expected_modules` existen en la BD antes de continuar
2. **Fase 2:** Si los módulos existen, mejorar embeddings y reranking para priorizar matches exactos

---

### Patrón 2: Pérdida de Especificidad Geográfica/Localización

**Descripción:**
Queries con términos específicos de localización (España, AEAT, IVA) retornan módulos genéricos internacionales.

**Frecuencia:** 2/20 queries (10%) - todas las de localización española

**Ejemplo:**
```json
Query: "libro de IVA España"
Expected: ["l10n_es_vat_book", "l10n_es_aeat_mod303"]
Returned: [
  "account_move_line_tax_editable",
  "account_fiscal_position_vat_check",
  ...
]
```

**Análisis:**
- El embedding no prioriza términos como "España", "AEAT", "l10n_es"
- Retorna módulos genéricos de IVA/VAT sin considerar localización
- Posible problema: Embeddings en inglés no capturan bien contexto español

**Mejora Propuesta:**
- **Fase 2:** Implementar boost de localización (multiplicar score si `technical_name` contiene `l10n_XX`)
- **Fase 3:** Query expansion para mapear "España" → "l10n_es", "AEAT" → "aeat"
- **Fase 4:** Usar modelo multilingüe optimizado para español

**Frecuencia estimada en producción:** ~15% de queries (usuarios españoles buscando módulos locales)

---

### Patrón 3: No Reconocimiento de Acrónimos/Términos Técnicos

**Descripción:**
Búsquedas con acrónimos específicos (B2B, B2C, DMS, MRP) no encuentran módulos que los contienen.

**Frecuencia:** 4/20 queries (20%)

**Ejemplo 1:**
```json
Query: "separar flujos B2B y B2C en ventas"
Expected: ["sale_b2b_b2c", ...]
Returned: ["sale_automatic_workflow_job", "partner_sale_pivot", ...]
```

**Ejemplo 2:**
```json
Query: "gestión documental DMS con etiquetas"
Expected: ["dms", "document_tag", "dms_category"]
Returned: ["sale_order_note_template", "account_dashboard_banner", ...]
```

**Análisis:**
- El embedding vectorial no asocia "B2B/B2C" con `sale_b2b_b2c`
- "DMS" no se mapea a módulos con `dms` en technical_name
- El modelo de embeddings no entiende acrónimos del dominio Odoo

**Mejora Propuesta:**
- **Fase 2:** Boost por keyword matching exacto (si query contiene "b2b" y module contiene "b2b", +bonus)
- **Fase 3:** Diccionario de expansión de acrónimos:
  - DMS → Document Management System
  - MRP → Manufacturing Resource Planning
  - B2B → Business to Business
- **Fase 4:** Fine-tuning del modelo de embeddings con ejemplos de Odoo

**Frecuencia estimada:** ~25% de queries (usuarios técnicos usan acrónimos)

---

### Patrón 4: Incapacidad para Búsquedas Multi-Concepto

**Descripción:**
Queries que combinan múltiples conceptos retornan módulos de solo uno de ellos.

**Frecuencia:** 3/20 queries (15%)

**Ejemplo:**
```json
Query: "integrar tienda online con gestión de stock y envíos"
Expected: ["website_sale_stock", "delivery_integration", "website_sale_delivery"]
Returned: ["sale_order_note_template", "account_dashboard_banner", "portal_sale_order_search"]
```

**Análisis:**
- Query combina: ecommerce + inventario + logística
- Sistema retorna módulos genéricos de sales
- No captura la intersección de múltiples dominios

**Mejora Propuesta:**
- **Fase 2:** Query decomposition - dividir en sub-queries y combinar resultados
- **Fase 3:** Graph-based ranking usando dependencias de módulos
- **Fase 4:** LLM-based reranking que entienda requisitos multi-dominio

**Frecuencia estimada:** ~20% de queries (requisitos complejos de integración)

---

### Patrón 5: No Diferenciación por Versión de Odoo

**Descripción:**
El sistema retorna módulos sin considerar la versión especificada en la query.

**Frecuencia:** No medible con datos actuales (pero observado en logs)

**Ejemplo:**
```
Query version=18.0 puede retornar módulos de 16.0, 17.0, 18.0 mezclados
```

**Análisis:**
- El filtro de versión se aplica ANTES de la búsqueda vectorial (correcto)
- Pero algunos módulos pueden existir en múltiples versiones
- No hay preferencia por versiones más recientes

**Mejora Propuesta:**
- **Fase 2:** Verificar que filtrado por versión funciona correctamente
- **Fase 3:** Boost leve por versión exacta (vs versiones compatibles)

**Frecuencia estimada:** ~10% de queries (cuando hay módulos cross-version)

---

## 🚨 Hallazgo Crítico: Validación de Ground Truth

### Problema Fundamental Detectado

**Antes de continuar con mejoras, es CRÍTICO validar que los `expected_modules` existen en la base de datos.**

#### Acción Requerida

Ejecutar validación SQL contra la BD:

```sql
-- Verificar existencia de todos los expected_modules
WITH expected AS (
  SELECT unnest(ARRAY[
    'l10n_es_facturae', 'l10n_es_aeat',
    'sale_b2b_b2c', 'portal_partner_type', 'sale_partner_type',
    'portal_document', 'portal_partner_document', 'dms_portal',
    'stock_production_lot', 'product_expiry', 'stock_lot_traceability',
    -- ... incluir todos los 49 expected_modules del benchmark
  ]) AS module_name
)
SELECT
  e.module_name,
  om.technical_name,
  om.version,
  CASE
    WHEN om.technical_name IS NULL THEN '❌ NOT FOUND'
    ELSE '✅ EXISTS'
  END as status
FROM expected e
LEFT JOIN odoo_modules om ON e.module_name = om.technical_name
ORDER BY status DESC, e.module_name;
```

#### Posibles Resultados

**Escenario A: Módulos NO existen (>80% missing)**
- Los `expected_modules` son ejemplos ficticios
- **Acción:** Reemplazar con módulos reales de la BD antes de continuar Fase 2
- **Impacto:** Benchmark actual NO es válido como baseline

**Escenario B: Módulos existen (>50% found)**
- El sistema de búsqueda está fundamentalmente roto
- **Acción:** Debugging profundo de embeddings, vectores, y search_service
- **Impacto:** Problemas graves en implementación actual

---

## 📈 Proyección de Mejora

Asumiendo que se valida/corrige el ground truth:

| Fase | Mejoras Implementadas | Precision@3 Esperada | Recall@10 Esperada |
|------|----------------------|---------------------|-------------------|
| **Baseline (actual)** | Solo búsqueda vectorial | 0.0% | 0.0% |
| **Fase 2** | Hybrid search + keyword boost | 25-35% | 40-50% |
| **Fase 3** | Query expansion + reranking | 45-55% | 60-70% |
| **Fase 4** | LLM reranking + fine-tuning | 60-70% | 75-85% |

**Meta final:** Precision@3 > 60%, Recall@10 > 75%

---

## ✅ Conclusiones y Próximos Pasos

### Conclusiones

1. **El sistema actual NO funciona** - 0% de acierto indica problema fundamental
2. **Validación de ground truth es URGENTE** - antes de cualquier mejora
3. **Si los módulos existen:** El problema está en embeddings/búsqueda vectorial
4. **Si los módulos NO existen:** El benchmark necesita reconstrucción completa

### Próximos Pasos (en orden)

#### Paso 1: Validación (CRÍTICO - hacer AHORA)
- [ ] Ejecutar query SQL de validación de expected_modules
- [ ] Documentar % de módulos encontrados vs missing
- [ ] Si <50% existen: Recrear benchmark_queries.json con módulos reales

#### Paso 2: Debugging (si módulos existen)
- [ ] Verificar que embeddings se generaron correctamente en BD
- [ ] Hacer búsqueda manual de 2-3 queries y analizar vectores
- [ ] Revisar logs de search_service para detectar errores

#### Paso 3: Baseline Válido
- [ ] Re-ejecutar benchmark con datos corregidos
- [ ] Obtener baseline real (esperado: 15-25% Precision@3)
- [ ] Usar como referencia para Fase 2

#### Paso 4: Iniciar Fase 2
- [ ] Implementar mejoras de hybrid search
- [ ] Solo cuando tengamos baseline válido

---

## 📎 Referencias

- [SPEC-001: Benchmark Queries](../../specs/phase-1-diagnostico/SPEC-001-benchmark-queries.md)
- [SPEC-002: Benchmark Script](../../specs/phase-1-diagnostico/SPEC-002-benchmark-script.md)
- [SPEC-003: Metrics Module](../../specs/phase-1-diagnostico/SPEC-003-metrics.md)
- [Baseline Results JSON](baseline_20251122_181454.json)

---

**Generado automáticamente el:** 2025-11-22 18:14:54
**Por:** AI-OdooFinder Benchmark Runner v1.0
