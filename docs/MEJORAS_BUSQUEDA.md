# 🚀 Plan de Mejoras - Sistema de Búsqueda

**Fecha:** 19 Noviembre 2025
**Contexto:** MCP funcionando, pero búsqueda mejorable
**Objetivo:** Aumentar precisión y relevancia de resultados

---

## 📊 Diagnóstico Actual

### Estado de la Búsqueda

**Funcionamiento técnico:** ✅ Operativo
**Precisión de resultados:** ⚠️ Mejorable
**Cobertura de módulos:** ⚠️ Solo OCA (2,508 módulos)

### Datos Vectoriales Actuales

**Información indexada por módulo:**
- ✅ `technical_name`: Nombre técnico del módulo
- ✅ `name`: Nombre legible
- ✅ `summary`: Resumen breve
- ✅ `description`: Descripción (cuando existe)
- ✅ `depends`: Lista de dependencias
- ✅ `author`: Autor/organización
- ✅ `version`: Versión de Odoo
- ✅ README content (cuando existe - 60% de módulos)

**Metadata adicional:**
- ✅ GitHub stars
- ✅ Issues abiertas
- ✅ Fecha último commit
- ✅ Licencia
- ✅ Repositorio origen

### Problemas Identificados

1. **Búsquedas poco afinadas**: Los resultados no siempre son los más relevantes
2. **Queries directas al MCP**: Sin optimización ni enriquecimiento previo
3. **Cobertura limitada**: Solo módulos OCA (falta Odoo App Store oficial)
4. **Falta de contexto**: Las búsquedas son literales, sin análisis semántico previo

---

## 🎯 Propuestas de Mejora

### Propuesta 1: Skill Inteligente como Intermediario

**Concepto:**
```
Usuario → Skill (análisis) → MCP (búsqueda optimizada) → Resultados
```

**Flujo propuesto:**

1. **Usuario escribe query natural** en Claude Web
   - Ejemplo: "Necesito separar flujos de venta B2B y B2C en Odoo 16"

2. **Skill analiza y enriquece**:
   - Extrae conceptos clave: "separar", "flujos", "B2B", "B2C", "venta"
   - Identifica versión: "16.0"
   - Infiere dependencias probables: `["sale", "account"]`
   - Genera query optimizada: "separate business customer workflows sale order types B2B B2C wholesale retail"
   - Define límite apropiado según complejidad

3. **Skill invoca MCP** con parámetros enriquecidos:
   ```json
   {
     "query": "separate business customer workflows sale order types B2B B2C wholesale retail",
     "version": "16.0",
     "dependencies": ["sale"],
     "limit": 10
   }
   ```

4. **MCP busca** con query optimizada

5. **Skill post-procesa resultados**:
   - Filtra por relevancia real
   - Agrupa por categoría funcional
   - Explica por qué cada módulo es relevante
   - Sugiere combinaciones de módulos

**Beneficios:**
- ✅ Búsquedas más precisas
- ✅ Mejor UX (usuario escribe natural, sistema optimiza)
- ✅ Resultados más relevantes
- ✅ Contexto y explicaciones

**Implementación:**
- Crear/actualizar `docs/Claude_Skill.md` con lógica de análisis
- Definir prompts para extracción de conceptos
- Plantillas de optimización de queries
- Post-procesamiento de resultados

---

### Propuesta 2: Enriquecer Datos Vectoriales

**Análisis necesario:**
1. Revisar calidad de embeddings actuales
2. Evaluar si README es suficiente o necesitamos más contexto
3. Considerar añadir:
   - Tags/categorías funcionales (ventas, compras, inventario, etc.)
   - Casos de uso comunes
   - Relaciones entre módulos (módulos similares, alternativas)
   - Popularidad relativa (descargas, forks)

**Acción inmediata:**
- [ ] Query SQL para analizar módulos con/sin README
- [ ] Revisar 10-20 búsquedas reales y analizar fallos
- [ ] Identificar qué información falta para mejorar precisión

**Mejoras de datos:**
- Generar descripciones enriquecidas con IA para módulos sin README
- Extraer keywords/tags del código fuente
- Análizar dependencias inversas (qué módulos dependen de este)

---

### Propuesta 3: Integrar Odoo App Store

**Estado actual:** Sprint 4 (planificado, no iniciado)
**Prioridad:** 🔴 Alta (aumentar cobertura)

**Módulos a añadir:**
- Módulos oficiales de Odoo SA
- Módulos comerciales/enterprise
- Partners certificados

**Impacto esperado:**
- Pasar de ~2,500 módulos a ~5,000-7,000 módulos
- Cubrir módulos enterprise que no están en OCA
- Mejor cobertura para casos de uso comerciales

**Siguiente paso:**
- Investigar estructura de apps.odoo.com
- Decidir: scraping vs API no oficial
- Diseñar esquema de BD para módulos store

---

### Propuesta 4: Queries MCP Más Ricas

**Actual:**
```json
{
  "query": "inventory",
  "version": "17.0",
  "limit": 5
}
```

**Mejorado:**
```json
{
  "query": "inventory management stock tracking warehouse operations",
  "version": "17.0",
  "dependencies": ["stock"],
  "limit": 10,
  "context": {
    "use_case": "Small business needs inventory tracking",
    "existing_modules": ["sale", "purchase"],
    "priority": "ease_of_use"
  }
}
```

**Requiere:**
- Actualizar schema del tool MCP
- Implementar filtros adicionales en SearchService
- Skill que genere este contexto enriquecido

---

## 📋 Plan de Implementación

### Fase 1: Diagnóstico (1 día) ⏳ PRÓXIMO

**Objetivos:**
- Analizar calidad de búsqueda actual
- Revisar datos vectoriales
- Identificar gaps específicos

**Tareas:**
- [ ] Hacer 20 búsquedas de prueba y evaluar resultados
- [ ] Query BD: análisis de cobertura de README
- [ ] Revisar scores de búsquedas reales
- [ ] Documentar casos donde la búsqueda falla

**Entregable:** Reporte de diagnóstico con casos específicos

---

### Fase 2: Skill Inteligente (2-3 días)

**Objetivo:** Implementar Skill como intermediario

**Tareas:**
- [ ] Diseñar lógica de análisis de queries
- [ ] Crear prompts de extracción de conceptos
- [ ] Implementar template de optimización de queries
- [ ] Definir post-procesamiento de resultados
- [ ] Actualizar `docs/Claude_Skill.md` con nuevo flujo
- [ ] Testing en Claude Web

**Entregable:** Skill funcional que optimiza búsquedas vía MCP

---

### Fase 3: Enriquecimiento de Datos (3-4 días)

**Objetivo:** Mejorar calidad de embeddings

**Tareas:**
- [ ] Generar descripciones IA para módulos sin README
- [ ] Extraer keywords del código fuente
- [ ] Categorizar módulos funcionalmente (tags)
- [ ] Re-generar embeddings con nueva información
- [ ] Re-indexar base de datos vectorial

**Entregable:** BD vectorial enriquecida, mejores embeddings

---

### Fase 4: Integración Odoo App Store (1-2 semanas)

**Objetivo:** Añadir módulos oficiales/comerciales

**Tareas:**
- [ ] Investigar apps.odoo.com (estructura, anti-scraping)
- [ ] Implementar scraper o usar API no oficial
- [ ] Crear tabla `odoo_store_modules` en BD
- [ ] Pipeline ETL para módulos store
- [ ] Generar embeddings para módulos store
- [ ] Actualizar SearchService para incluir ambas fuentes
- [ ] Testing y validación

**Entregable:** Sistema con ~5,000-7,000 módulos indexados

---

### Fase 5: MCP v2 - Queries Enriquecidas (2-3 días)

**Objetivo:** Soportar búsquedas con contexto

**Tareas:**
- [ ] Actualizar schema de `search_odoo_modules` tool
- [ ] Implementar filtros de contexto en SearchService
- [ ] Actualizar Skill para generar contexto enriquecido
- [ ] Testing con casos reales

**Entregable:** MCP v2 con soporte de contexto

---

## 🎯 Priorización

### Sprint Actual (Esta Semana)
1. ✅ **Fase 4 del Sprint 2**: Documentación MCP
2. 🔴 **Fase 1**: Diagnóstico de búsqueda (1 día)

### Sprint Próximo (Semana 23-29 Nov)
3. 🟠 **Fase 2**: Skill Inteligente (2-3 días)
4. 🟡 **Fase 3**: Enriquecimiento de datos (3-4 días)

### Sprints Futuros (Diciembre)
5. 🟢 **Fase 4**: Odoo App Store (1-2 semanas)
6. 🔵 **Fase 5**: MCP v2 (2-3 días)

---

## 📐 Arquitectura Propuesta

### Flujo Actual (Básico)
```
Claude Web → MCP → SearchService → PostgreSQL/pgVector → Resultados
```

### Flujo Mejorado (con Skill)
```
Usuario escribe query natural
    ↓
Claude Web con Skill.md cargado
    ↓
Skill analiza y enriquece query
    ↓
Skill invoca MCP con parámetros optimizados
    ↓
MCP → SearchService → PostgreSQL/pgVector
    ↓
SearchService aplica filtros contextuales
    ↓
Resultados vuelven a Skill
    ↓
Skill post-procesa y formatea
    ↓
Usuario recibe resultados enriquecidos
```

### Componentes Nuevos

**1. Skill Inteligente** (`docs/Claude_Skill.md`)
- Análisis de intención del usuario
- Extracción de conceptos clave
- Optimización de queries
- Post-procesamiento de resultados

**2. Base de Datos Enriquecida**
- Tags funcionales
- Categorías
- Descripciones generadas por IA
- Keywords extraídos

**3. SearchService v2**
- Filtros contextuales
- Soporte multi-fuente (OCA + Store)
- Ranking mejorado

**4. MCP v2** (`mcp_tools.py`)
- Schema extendido con contexto
- Soporte de filtros avanzados

---

## 🔬 Casos de Uso a Optimizar

### Caso 1: Búsqueda funcional compleja
**Query usuario:** "Necesito separar flujos B2B y B2C en ventas"

**Actual:** Resultados genéricos de "sale"

**Mejorado con Skill:**
- Identifica conceptos: separación, flujos, tipos de cliente
- Query optimizada: "sale order type B2B B2C customer workflow separation"
- Resultados: `sale_order_type`, `sale_partner_type`, etc.

---

### Caso 2: Búsqueda por caso de uso
**Query usuario:** "Gestión de almacenes multi-ubicación con trazabilidad"

**Actual:** Resultados muy amplios de "stock"

**Mejorado con Skill:**
- Identifica requisitos: multi-warehouse, lot tracking
- Dependencies: `["stock"]`
- Query optimizada: "multi warehouse location management lot serial tracking"
- Filtra por: repos populares, actualizados recientemente

---

### Caso 3: Búsqueda con contexto empresarial
**Query usuario:** "Somos una PYME de distribución, necesitamos facturación electrónica en España"

**Actual:** No usa contexto geográfico ni de industria

**Mejorado con Skill:**
- Extrae: país (España), industria (distribución), tamaño (PYME)
- Query: "electronic invoice Spain TicketBAI SII AEAT l10n_es"
- Context: `{ "country": "ES", "industry": "distribution" }`
- Prioriza módulos de localización española

---

## 💡 Ideas Adicionales

### A. Sistema de Feedback
- Permitir al usuario indicar si el resultado fue útil
- Ajustar embeddings/ranking basado en feedback
- A/B testing de queries optimizadas vs directas

### B. Caché Inteligente
- Cachear búsquedas frecuentes
- Pre-computar resultados para queries comunes
- Sugerencias automáticas basadas en historial

### C. Búsqueda por Similitud
- "Módulos similares a X"
- "Alternativas a X"
- "Qué otros módulos usan los que usan X"

### D. Análisis de Compatibilidad
- Verificar compatibilidad entre módulos antes de recomendar
- Detectar conflictos conocidos
- Sugerir orden de instalación

---

## ✅ Criterios de Éxito

### Métricas Objetivo

**Precisión de búsqueda:**
- Actual: ~70% de relevancia en top 5
- Objetivo: >85% de relevancia en top 5

**Cobertura:**
- Actual: 2,508 módulos (solo OCA)
- Objetivo: >5,000 módulos (OCA + Store)

**Satisfacción:**
- Usuario encuentra módulo relevante en primera búsqueda: >80%
- Necesita refinar búsqueda: <20%

**Performance:**
- Tiempo respuesta: <3 segundos
- Skill overhead: <1 segundo

---

## 📝 Próximos Pasos Inmediatos

### Esta Sesión
1. ✅ Documentar bug fix trailing slash
2. ✅ Crear plan de mejoras (este documento)
3. ⏳ Definir estructura de Skill inteligente

### Próxima Sesión
1. Fase 1: Diagnóstico de búsqueda (queries reales, análisis)
2. Comenzar Fase 2: Diseño de Skill inteligente
3. Prototipo de optimización de queries

---

**Última actualización:** 19 Nov 2025, 23:45 UTC
**Estado:** Plan aprobado, pendiente inicio Fase 1
**Decisión requerida:** Priorizar Skill vs Odoo Store vs Enriquecimiento de datos
