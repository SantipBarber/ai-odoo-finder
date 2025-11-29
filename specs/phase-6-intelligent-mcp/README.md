# Phase 6: Intelligent MCP Tools 🧠

**Estado:** ⚠️ Parcialmente Implementado (SPEC-602 ✅)
**Prioridad:** 🔥 Alta - Game Changer
**Esfuerzo Estimado:** 3-4 días
**Depende de:** Phase 2 (Hybrid Search) ✅

---

## ✅ SPEC-602 Completado: Flujo Inteligente de Búsqueda

**Estado:** Implementado y testeado  
**Fecha:** Enero 2025

### Documentación SPEC-602
- **[SPEC-602: Flujo Inteligente](SPEC-602-intelligent-mcp-flow.md)** - Especificación completa
- **[Resumen de Implementación](IMPLEMENTATION_SUMMARY.md)** - Detalles técnicos
- **[Guía Rápida](QUICK_REFERENCE.md)** - Para desarrolladores
- **[Resumen Ejecutivo](EXECUTIVE_SUMMARY.md)** - Para stakeholders

### Qué se implementó
- ✅ Servidor MCP standalone para Claude Desktop (`mcp-server/`)
- ✅ Tool description enriquecido con instrucciones inteligentes
- ✅ Formato de respuesta estructurada con niveles de confianza (ALTA/MEDIA/BAJA)
- ✅ Migración 005: `repo_name` en `searchable_text` para mejorar búsqueda por país
- ✅ Testing con 6 casos de uso (100% de éxito)

### Resultados
- 🟢 **Precisión mejorada:** Módulos de localizaciones ahora se encuentran correctamente
- 🟢 **Experiencia mejorada:** Respuestas estructuradas con niveles de confianza
- 🟢 **Integración Claude Desktop:** Búsqueda directa desde conversación

Ver [CHANGELOG.md](../../docs/CHANGELOG.md) para más detalles.

---

## 🎯 Visión

Transformar el MCP de AI-OdooFinder de una **herramienta de búsqueda simple** a un **asistente inteligente conversacional** que entiende el contexto del usuario, puede explorar el ecosistema de módulos, comparar alternativas, y proporcionar recomendaciones expertas.

### Problema Actual (MCP v2.0)

El MCP actual tiene **una sola herramienta**:

```python
@mcp.tool()
async def search_odoo_modules(
    query: str,
    version: str,
    dependencies: Optional[list[str]] = None,
    limit: int = 5
) -> str:
    """Búsqueda básica de módulos"""
```

**Limitaciones:**

1. 🔴 **Parámetros rígidos**: El LLM debe estructurar todo en query+version+deps
2. 🔴 **Una sola pasada**: No puede iterar o refinar la búsqueda
3. 🔴 **Sin contexto conversacional**: Cada búsqueda es independiente
4. 🔴 **Información limitada**: Solo devuelve resultados, sin análisis
5. 🔴 **Sin exploración**: No puede investigar dependencias o relacionados
6. 🔴 **Comparaciones manuales**: El LLM no puede comparar alternativas fácilmente

**Ejemplo de limitación real:**

```
Usuario: "Necesito algo para manejar subscripciones en Odoo 17"

Flujo actual (1 herramienta):
1. Claude ejecuta: search_odoo_modules(query="subscriptions", version="17.0")
2. Devuelve 5 módulos
3. Usuario pregunta: "¿Cuál es mejor entre sale_subscription y contract?"
4. Claude NO PUEDE comparar → Necesita hacer otra búsqueda genérica
```

### Solución Propuesta (MCP v3.0)

**Sistema de herramientas especializadas** que permiten workflows conversacionales:

```python
# 1. Búsqueda principal (mejorada)
@mcp.tool()
async def search_modules(
    description: str,  # ← más flexible que "query"
    odoo_version: str,
    must_have_dependencies: Optional[List[str]] = None,
    preferred_repos: Optional[List[str]] = None,  # ← NUEVO
    exclude_repos: Optional[List[str]] = None,     # ← NUEVO
    min_quality_score: int = 30,                   # ← NUEVO
    max_results: int = 10
) -> str:
    """Búsqueda inteligente con más control"""

# 2. Explorador de ecosistema (NUEVO)
@mcp.tool()
async def explore_module_ecosystem(
    technical_name: str,
    odoo_version: str,
    include_dependents: bool = True,
    include_related: bool = True
) -> str:
    """Analiza dependencias, dependientes, y módulos relacionados"""

# 3. Comparador de módulos (NUEVO)
@mcp.tool()
async def compare_modules(
    module_names: List[str],  # 2-4 módulos
    odoo_version: str,
    comparison_criteria: Optional[List[str]] = None
) -> str:
    """Comparación lado a lado con análisis de calidad"""

# 4. Estadísticas del ecosistema (NUEVO)
@mcp.tool()
async def get_ecosystem_stats(
    scope: str = "overall",  # overall|repository|version
    filter_value: Optional[str] = None
) -> str:
    """Insights y tendencias del ecosistema Odoo"""
```

**Ejemplo mejorado:**

```
Usuario: "Necesito algo para manejar subscripciones en Odoo 17"

Flujo nuevo (4 herramientas):
1. Claude: search_modules(description="subscription management", version="17.0")
   → Devuelve: sale_subscription, contract, subscription_template

2. Usuario: "¿Cuál es mejor entre sale_subscription y contract?"

3. Claude: compare_modules(["sale_subscription", "contract"], "17.0")
   → Devuelve: Tabla comparativa + análisis + recomendación

4. Usuario: "¿Qué dependencias tiene sale_subscription?"

5. Claude: explore_module_ecosystem("sale_subscription", "17.0")
   → Devuelve: deps completas, módulos que dependen de él, relacionados en repo
```

---

## 🎁 Beneficios Clave

### 1. Conversaciones Naturales

**Antes (v2.0):**
```
Usuario: "Busca módulos de inventario"
Claude: search_odoo_modules("inventory", "17.0")
Usuario: "¿Cuál es el más usado?"
Claude: [Tiene que buscar de nuevo, no puede responder]
```

**Después (v3.0):**
```
Usuario: "Busca módulos de inventario"
Claude: search_modules("inventory management", "17.0")
Usuario: "¿Cuál es el más usado?"
Claude: get_ecosystem_stats("repository", "stock-logistics-warehouse")
        → Muestra estadísticas de popularidad
```

### 2. Análisis Profundo

El LLM puede ahora:
- ✅ Explorar dependencias completas antes de recomendar
- ✅ Comparar alternativas objetivamente
- ✅ Entender el contexto del repositorio
- ✅ Validar compatibilidad técnica

### 3. Mejores Recomendaciones

Con más información, Claude puede:
- 🎯 Recomendar basándose en calidad real (no solo similitud)
- 🎯 Advertir sobre dependencias complejas
- 🎯 Sugerir módulos complementarios
- 🎯 Identificar el "stack" completo necesario

### 4. Búsquedas Más Ricas

**Nuevos parámetros permiten:**
- Priorizar repos conocidos: `preferred_repos=["sale-workflow"]`
- Excluir repos problemáticos: `exclude_repos=["deprecated-modules"]`
- Filtrar por calidad mínima: `min_quality_score=60` (producción)
- Búsquedas descriptivas vs queries rígidas

---

## 📊 Comparación de Capacidades

| Capacidad | v2.0 (Actual) | v3.0 (Propuesta) |
|-----------|---------------|------------------|
| **Búsqueda semántica** | ✅ Básica | ✅ Avanzada (más filtros) |
| **Filtrado por deps** | ✅ Simple | ✅ Must-have vs nice-to-have |
| **Filtrado por calidad** | ❌ No | ✅ Score configurable |
| **Priorizar repos** | ❌ No | ✅ Preferred/exclude lists |
| **Explorar dependencias** | ❌ No | ✅ Full dependency tree |
| **Ver dependientes** | ❌ No | ✅ Reverse dependencies |
| **Comparar módulos** | ❌ No | ✅ Side-by-side con análisis |
| **Stats del ecosistema** | ❌ No | ✅ Por repo/version/global |
| **Búsquedas iterativas** | ❌ Una sola pasada | ✅ Conversacionales |
| **Recomendaciones** | ⚠️ Limitadas | ✅ Expertas y contextuales |

---

## 🏗️ Arquitectura

### Diseño de Herramientas

```
┌─────────────────────────────────────────────────────────┐
│                    CLAUDE (LLM)                         │
│  - Entiende intención del usuario                       │
│  - Decide qué herramienta usar                          │
│  - Puede usar múltiples herramientas en secuencia       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              MCP TOOLS (4 herramientas)                 │
│                                                         │
│  1. search_modules()                                    │
│     ├─ Búsqueda principal flexible                      │
│     └─ Parámetros ricos (quality, repos, deps)         │
│                                                         │
│  2. explore_module_ecosystem()                          │
│     ├─ Analiza dependencias completas                   │
│     ├─ Encuentra dependientes (reverse deps)            │
│     └─ Módulos relacionados del mismo repo             │
│                                                         │
│  3. compare_modules()                                   │
│     ├─ Comparación lado a lado                          │
│     ├─ Scoring heurístico                               │
│     └─ Recomendación basada en datos                   │
│                                                         │
│  4. get_ecosystem_stats()                               │
│     ├─ Estadísticas globales                            │
│     ├─ Stats por repositorio                            │
│     └─ Stats por versión                               │
│                                                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              SERVICIOS (Reutilizados)                   │
│  - SearchService (búsqueda híbrida)                     │
│  - Database (SQLAlchemy + pgVector)                     │
│  - EmbeddingService (para semantic search)             │
└─────────────────────────────────────────────────────────┘
```

### Flujo de Decisión del LLM

```
Usuario: "Necesito módulos de CRM para Odoo 17"
    ↓
Claude analiza intención
    ↓
[DECISION 1] ¿Qué herramienta usar?
    → search_modules() ← Búsqueda inicial
    ↓
Claude ejecuta: search_modules("CRM functionality", "17.0")
    ↓
Resultados: crm, crm_lead_score, crm_phonecall (3 módulos)
    ↓
Claude presenta resultados al usuario
    ↓
Usuario: "¿Cuál tiene mejor mantenimiento?"
    ↓
Claude analiza intención
    ↓
[DECISION 2] ¿Qué herramienta usar?
    → compare_modules() ← Comparación
    ↓
Claude ejecuta: compare_modules(["crm", "crm_lead_score"], "17.0")
    ↓
Comparación + análisis de calidad
    ↓
Claude: "crm_lead_score tiene mejor mantenimiento (actualizado hace 1 mes vs 6 meses)"
```

**🔑 Ventaja clave:** El LLM puede crear **workflows inteligentes** combinando herramientas según la conversación.

---

## 🎯 Casos de Uso

### Caso 1: Exploración Inicial

**Usuario:** "Quiero ver qué hay disponible para gestión de almacenes en Odoo 16"

**Workflow:**
1. `get_ecosystem_stats("repository", "stock-logistics-warehouse")` → Contexto
2. `search_modules("warehouse management", "16.0", preferred_repos=["stock-logistics-warehouse"])` → Módulos

**Resultado:** Usuario entiende el ecosistema antes de elegir

---

### Caso 2: Análisis de Dependencias

**Usuario:** "Quiero usar stock_barcode, ¿qué más necesito instalar?"

**Workflow:**
1. `explore_module_ecosystem("stock_barcode", "16.0")` → Dependencias completas
2. Claude muestra: stock, barcodes, base_setup, etc.
3. Claude calcula: "Necesitas instalar 4 módulos adicionales"

**Resultado:** Usuario sabe el alcance real de la instalación

---

### Caso 3: Comparación de Alternativas

**Usuario:** "Tengo que elegir entre sale_subscription y contract para manejar contratos"

**Workflow:**
1. `compare_modules(["sale_subscription", "contract"], "17.0")`
2. Tabla comparativa: stars, deps, última actualización, issues
3. Análisis: sale_subscription más popular, contract más simple
4. Recomendación contextual

**Resultado:** Decisión informada con datos objetivos

---

### Caso 4: Validación de Stack

**Usuario:** "Voy a usar sale_subscription + contract_sale. ¿Son compatibles?"

**Workflow:**
1. `explore_module_ecosystem("sale_subscription", "17.0")`
2. `explore_module_ecosystem("contract_sale", "17.0")`
3. Claude analiza dependencias cruzadas
4. Verifica que ambos dependen de `sale` → ✅ Compatibles

**Resultado:** Validación técnica antes de desarrollar

---

## 📋 Especificaciones

### [SPEC-501: Multi-Tool Architecture](SPEC-501-multi-tool-architecture.md)
- Diseño general del sistema de 4 herramientas
- Comunicación entre herramientas
- Gestión de contexto conversacional

### [SPEC-502: Semantic Search v2](SPEC-502-semantic-search-v2.md)
- `search_modules()` mejorado
- Nuevos parámetros: quality_score, preferred_repos, exclude_repos
- Estrategia de prompting para descripciones ricas

### [SPEC-503: Ecosystem Explorer](SPEC-503-ecosystem-explorer.md)
- `explore_module_ecosystem()` implementación
- Análisis de dependencias (forward + reverse)
- Módulos relacionados del mismo repositorio

### [SPEC-504: Module Comparator](SPEC-504-module-comparator.md)
- `compare_modules()` implementación
- Algoritmo de scoring heurístico
- Generación de recomendaciones

### [SPEC-505: Stats Analyzer](SPEC-505-stats-analyzer.md)
- `get_ecosystem_stats()` implementación
- Agregaciones por repo/versión
- Insights y tendencias

### [SPEC-506: Acceptance Criteria](SPEC-506-acceptance-criteria.md)
- Tests de integración
- Casos de prueba conversacionales
- Métricas de éxito

---

## 🚀 Plan de Implementación

### Fase 1: Fundaciones (1 día)
- [ ] Diseñar arquitectura de 4 herramientas
- [ ] Definir interfaces (type hints + docstrings)
- [ ] Crear funciones auxiliares compartidas
- [ ] Setup de tests

### Fase 2: Implementación Core (2 días)
- [ ] Implementar `search_modules()` v2
- [ ] Implementar `explore_module_ecosystem()`
- [ ] Implementar `compare_modules()`
- [ ] Implementar `get_ecosystem_stats()`

### Fase 3: Refinamiento (1 día)
- [ ] Optimizar formateo de respuestas
- [ ] Implementar scoring heurístico
- [ ] Agregar validaciones robustas
- [ ] Mejorar mensajes de error

### Fase 4: Testing (1 día)
- [ ] Tests unitarios de cada herramienta
- [ ] Tests de integración conversacionales
- [ ] Validación con Claude Desktop
- [ ] Benchmark de calidad de respuestas

---

## 📈 Métricas de Éxito

### Métricas Técnicas
- ✅ 4 herramientas funcionando correctamente
- ✅ <500ms respuesta promedio
- ✅ >95% uptime en producción
- ✅ 0 errores críticos en 100 consultas

### Métricas de UX
- ✅ Claude puede resolver 90% de consultas sin aclaración
- ✅ Usuarios encuentran módulo correcto en <3 interacciones
- ✅ Comparaciones objetivas (no solo opiniones del LLM)
- ✅ Recomendaciones validables con datos

### Métricas de Negocio
- ✅ Aumento en uso del MCP (consultas/día)
- ✅ Reducción de tiempo para encontrar módulo
- ✅ Mayor satisfacción del usuario
- ✅ Diferenciador vs competencia

---

## 🎮 Demo Scenario

**Conversación objetivo:**

```
👤 Usuario: "Necesito gestionar pagos recurrentes en Odoo 17"

🤖 Claude: Voy a buscar módulos de pagos recurrentes para ti.
          [Usa search_modules("recurring payment management", "17.0")]

          Encontré 3 módulos principales:
          1. sale_subscription (⭐ 245 stars) - Gestión completa de suscripciones
          2. contract (⭐ 189 stars) - Contratos con facturación recurrente
          3. subscription_payment (⭐ 67 stars) - Pagos periódicos simplificados

👤 Usuario: "¿Cuál es mejor entre sale_subscription y contract?"

🤖 Claude: Déjame comparar esos dos módulos.
          [Usa compare_modules(["sale_subscription", "contract"], "17.0")]

          📊 Comparación:

          sale_subscription:
          - ⭐ Más popular (245 vs 189 stars)
          - 📦 Más completo (integra con sale, account, payment)
          - ⏰ Actualizado hace 2 días
          - ⚠️ Más complejo (8 dependencias)

          contract:
          - ✅ Más simple (4 dependencias)
          - 🔄 Más flexible para diferentes tipos de contrato
          - ⏰ Actualizado hace 1 semana
          - 📖 Mejor documentación

          Recomendación: sale_subscription si necesitas integración completa
          con ventas y contabilidad. contract si prefieres algo más ligero.

👤 Usuario: "Ok, voy con sale_subscription. ¿Qué dependencias tiene?"

🤖 Claude: Voy a analizar sus dependencias.
          [Usa explore_module_ecosystem("sale_subscription", "17.0")]

          📦 Dependencias de sale_subscription:

          Directas (5):
          - sale (⭐ 450 stars) - Módulo de ventas core
          - account (⭐ 380 stars) - Contabilidad
          - payment (⭐ 210 stars) - Procesamiento de pagos
          - product (core Odoo)
          - portal (core Odoo)

          Necesitarás instalar 3 módulos adicionales además del base de Odoo.

          💡 También puedes considerar:
          - subscription_portal: Para que clientes gestionen sus suscripciones
          - subscription_analytics: Reportes avanzados de suscripciones

👤 Usuario: "Perfecto, gracias!"
```

**🎯 Objetivo logrado:** Usuario encontró módulo correcto, lo comparó objetivamente, validó dependencias, y recibió sugerencias complementarias. Todo en una conversación natural.

---

## 🔗 Próximos Pasos

Después de Phase 6:

1. **Analytics Dashboard**: Dashboard web para visualizar estadísticas
2. **Smart Recommendations**: ML para sugerir módulos basado en stack existente
3. **Dependency Resolver**: Calculador automático de dependencias completas
4. **Quality Predictor**: ML para predecir calidad de módulos nuevos

---

## 📚 Referencias

- [Phase 2: Hybrid Search](../phase-2-hybrid-search/README.md) - Fundación de búsqueda
- [MCP Design v2.0](../../docs/MCP_DESIGN.md) - Arquitectura actual
- [Anthropic MCP Docs](https://modelcontextprotocol.io) - Protocolo MCP
- [Claude Tools Best Practices](https://docs.anthropic.com/claude/docs/tool-use) - Diseño de herramientas

---

**Fecha de creación:** 24 Noviembre 2025
**Autor:** Equipo AI-OdooFinder
**Estado:** 📝 En Spec
**Próxima revisión:** Después de aprobar specs individuales
