# SPEC-600: Intelligent Search Strategy

**Estado:** 📝 Draft
**Prioridad:** 🔥 Crítica
**Autor:** Equipo AI-OdooFinder

---

## El Problema Real

No es un problema de **ranking** (rerankers), es un problema de **información y entendimiento**:

### 1. Datos Pobres en el Origen

```python
# Ejemplo actual de un módulo enriquecido
{
    "technical_name": "l10n_es_aeat_mod303",
    "ai_description": "This module extends Odoo functionality...",  # GENÉRICO
    "keywords": ["tax", "spain", "vat"]  # INSUFICIENTES
}

# Lo que debería ser
{
    "technical_name": "l10n_es_aeat_mod303",
    "ai_description": "Módulo para la generación automática del Modelo 303 de declaración
                       trimestral de IVA para la Agencia Tributaria Española (AEAT).
                       Calcula automáticamente las casillas del formulario basándose en
                       las facturas registradas y permite exportar en formato BOE.",
    "keywords": [
        "modelo 303", "IVA trimestral", "AEAT", "agencia tributaria",
        "declaración IVA", "BOE", "impuestos España", "VAT quarterly",
        "Spanish tax return", "formulario fiscal"
    ]
}
```

### 2. El Embedding Solo Refleja lo que Tiene

```
┌─────────────────────────────────────────────────────────────┐
│  EMBEDDING = f(name + summary + ai_description + keywords)  │
│                                                             │
│  Si ai_description = "generic ERP module..."                │
│  → El embedding será genérico                               │
│  → No importa qué tan bueno sea el modelo de embeddings     │
└─────────────────────────────────────────────────────────────┘
```

### 3. El Usuario Pregunta de Forma Natural

```
Usuario: "Necesito generar el modelo 303 de hacienda"
                    ↓
Search actual: vector_search("modelo 303 hacienda")
                    ↓
Resultado: Módulos con embeddings genéricos no matchean bien
```

---

## La Solución Integral

No añadir complejidad (rerankers), sino **mejorar la cadena completa**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                    ESTRATEGIA DE BÚSQUEDA INTELIGENTE                  │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  1. MEJORAR DATOS EN ORIGEN                                            │
│     └─ Enriquecimiento profundo con análisis de código                 │
│     └─ Keywords funcionales, no técnicos                               │
│     └─ Descripciones que responden a "¿qué problema resuelve?"         │
│                                                                        │
│  2. QUERY EXPANSION EN CLIENTE (LLM)                                   │
│     └─ El LLM que llama al MCP reformula la query                      │
│     └─ Añade sinónimos, términos técnicos, traducciones                │
│     └─ Tool descriptions que guían a Claude                            │
│                                                                        │
│  3. BÚSQUEDA MULTI-ESTRATEGIA                                          │
│     └─ Primero: búsqueda específica (high precision)                   │
│     └─ Si falla: búsqueda amplia (high recall)                         │
│     └─ Fallback: sugerir categorías relacionadas                       │
│                                                                        │
│  4. RESPUESTA INTELIGENTE                                              │
│     └─ Si encuentra: mostrar con confianza                             │
│     └─ Si aproximado: explicar limitaciones                            │
│     └─ Si nada: guiar al usuario hacia alternativas                    │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Componente 1: Enriquecimiento Profundo

### 1.1 Análisis de Código (¿Tenemos el código?)

**Pregunta clave:** ¿Podemos analizar el código fuente de los módulos?

Si tenemos acceso al código (manifest.py, models/, views/):

```python
# Extraer información del código
def analyze_module_code(module_path: str) -> dict:
    """
    Analiza código fuente para extraer:
    - Modelos definidos (class X(models.Model))
    - Campos relevantes
    - Vistas (forms, trees, kanban)
    - Wizards
    - Reports
    - Acciones automatizadas
    """

    # Ejemplo: l10n_es_aeat_mod303
    return {
        "models": ["l10n.es.aeat.mod303.report"],
        "inherits": ["l10n.es.aeat.report"],
        "wizards": ["l10n.es.aeat.mod303.export.boe"],
        "reports": ["l10n_es_aeat_mod303_report"],
        "fields_added": ["casilla_01", "casilla_02", ...],
        "cron_jobs": [],
        "computed_summary": "Generates Spanish VAT quarterly declaration (Model 303)"
    }
```

**Si NO tenemos el código**, usar solo manifest + README más agresivamente.

### 1.2 Prompt de Enriquecimiento Mejorado

```markdown
Eres un experto en Odoo. Analiza este módulo y genera:

1. DESCRIPCIÓN FUNCIONAL (3-4 oraciones):
   - ¿Qué PROBLEMA DE NEGOCIO resuelve?
   - ¿Para qué TIPO DE EMPRESA es útil?
   - ¿Qué FLUJO DE TRABAJO automatiza?

2. KEYWORDS DE BÚSQUEDA (10-15 términos):
   - Términos que un USUARIO buscaría (no desarrollador)
   - En ESPAÑOL e INGLÉS
   - Incluir SINÓNIMOS y VARIACIONES
   - Incluir CONTEXTO DE USO (ej: "declaración trimestral", no solo "tax")

3. CASOS DE USO (2-3 ejemplos):
   - "Cuando necesitas..."
   - "Útil si tu empresa..."

MÓDULO:
- technical_name: {technical_name}
- name: {name}
- summary: {summary}
- depends: {depends}
- readme: {readme}
```

### 1.3 Regenerar Embeddings con Datos Mejorados

Una vez mejorado el enriquecimiento:

```python
def build_enhanced_embedding_text(module):
    """
    Construye texto optimizado para embedding.
    Orden de importancia para el modelo de embeddings.
    """
    parts = []

    # 1. Problema que resuelve (más importante)
    if module.problem_solved:
        parts.append(f"Solves: {module.problem_solved}")

    # 2. Keywords funcionales (alta densidad semántica)
    if module.keywords:
        parts.append(f"Keywords: {' '.join(module.keywords)}")

    # 3. Casos de uso
    if module.use_cases:
        parts.append(f"Use cases: {' '.join(module.use_cases)}")

    # 4. Descripción funcional
    if module.ai_description:
        parts.append(module.ai_description)

    # 5. Nombre y summary como contexto
    parts.append(f"{module.name}. {module.summary}")

    return " | ".join(parts)
```

---

## Componente 2: Query Expansion en Cliente

### 2.1 Tool Description que Guía a Claude

```python
@mcp.tool()
async def search_odoo_modules(
    expanded_query: str,
    odoo_version: str,
    ...
) -> str:
    """
    Busca módulos de Odoo en el ecosistema OCA.

    IMPORTANTE - EXPANSIÓN DE QUERY:
    Antes de llamar a esta herramienta, EXPANDE la query del usuario:

    1. Añade SINÓNIMOS y TÉRMINOS RELACIONADOS
    2. Incluye TRADUCCIONES (español/inglés)
    3. Añade TÉRMINOS TÉCNICOS de Odoo si aplican
    4. Considera el CONTEXTO EMPRESARIAL

    EJEMPLOS DE EXPANSIÓN:

    Usuario dice: "facturación electrónica España"
    Tu envías: "factura electrónica facturae e-factura electronic invoice
                Spain AEAT BOE XML digital invoice firma electrónica"

    Usuario dice: "control de inventario"
    Tu envías: "inventory control stock management warehouse gestión almacén
                control inventario stock levels ubicaciones locations"

    Usuario dice: "nóminas"
    Tu envías: "payroll nóminas salarios payslip HR recursos humanos
                employee salary IRPF cotizaciones seguridad social"

    Args:
        expanded_query: Query EXPANDIDA con sinónimos y términos relacionados
        odoo_version: Versión de Odoo (ej: "16.0", "17.0")
    """
```

### 2.2 Sistema de Prompts para el MCP

El MCP devuelve no solo resultados, sino **contexto para Claude**:

```json
{
  "results": [...],
  "search_context": {
    "query_understood_as": "Spanish electronic invoicing for tax authority",
    "related_categories": ["localization", "accounting", "tax"],
    "if_not_found_suggest": "Try searching for 'l10n_es' modules or 'AEAT'"
  }
}
```

---

## Componente 3: Búsqueda Multi-Estrategia

### 3.1 Cascada de Búsqueda

```python
async def intelligent_search(query: str, version: str) -> SearchResult:
    """
    Búsqueda en cascada con fallbacks inteligentes.
    """

    # Nivel 1: Búsqueda exacta/específica (high precision)
    results = await search_hybrid(
        query=query,
        version=version,
        limit=5,
        min_score=70  # Solo resultados muy relevantes
    )

    if results and results[0].score > 80:
        return SearchResult(
            results=results,
            confidence="high",
            message="Found modules that match your needs"
        )

    # Nivel 2: Búsqueda amplia (high recall)
    results = await search_hybrid(
        query=query,
        version=version,
        limit=10,
        min_score=40  # Más permisivo
    )

    if results:
        return SearchResult(
            results=results,
            confidence="medium",
            message="Found potentially related modules. Review if they match your use case."
        )

    # Nivel 3: Sugerencias por categoría
    categories = extract_categories_from_query(query)
    suggestions = await get_modules_by_category(categories, version)

    return SearchResult(
        results=suggestions,
        confidence="low",
        message="No exact match found. Here are modules in related categories.",
        alternative_queries=generate_alternative_queries(query)
    )
```

### 3.2 Detección de Intención

```python
def classify_search_intent(query: str) -> SearchIntent:
    """
    Clasifica qué tipo de búsqueda necesita el usuario.
    """
    intents = {
        "specific_module": r"módulo|module|l10n_|stock_|sale_",
        "functionality": r"necesito|quiero|busco|gestionar|manejar",
        "problem": r"cómo|como|problema|issue|error",
        "comparison": r"mejor|diferencia|vs|comparar|alternativa",
        "exploration": r"qué hay|opciones|disponible|listar"
    }

    # Retorna intent + confidence
```

---

## Componente 4: Respuesta Inteligente

### 4.1 Formateo Contextual de Respuestas

```python
def format_search_response(results: SearchResult) -> str:
    """
    Formatea respuesta según confianza y contexto.
    """

    if results.confidence == "high":
        return f"""
        ✅ Encontré {len(results.results)} módulos que cubren tu necesidad:

        {format_modules(results.results)}

        El más recomendado es **{results.results[0].name}** porque:
        - {results.results[0].ai_description}
        """

    elif results.confidence == "medium":
        return f"""
        🔍 Encontré módulos relacionados, pero revisa si se ajustan a tu caso:

        {format_modules(results.results)}

        💡 Si ninguno encaja, intenta ser más específico sobre:
        - ¿Qué proceso de negocio quieres automatizar?
        - ¿Para qué país/localización?
        """

    else:  # low
        return f"""
        ⚠️ No encontré módulos exactos para "{results.original_query}"

        Esto puede significar:
        1. No existe un módulo OCA para esto (podrías desarrollarlo)
        2. La funcionalidad está en Odoo Enterprise
        3. Necesitas combinar varios módulos

        📂 Módulos en categorías relacionadas:
        {format_modules(results.results)}

        🔄 Intenta buscar con estos términos alternativos:
        {format_alternatives(results.alternative_queries)}
        """
```

### 4.2 Guía al Usuario

Cuando no hay resultados, **ayudar activamente**:

```markdown
No encontré un módulo específico para "dashboard de KPIs ejecutivo".

📊 **Sobre reportes en Odoo:**
Odoo se enfoca más en procesos operativos que en BI avanzado.
Para dashboards ejecutivos, considera:

1. **Odoo Enterprise** tiene dashboards nativos
2. **Integración externa**: Metabase, Grafana, Power BI conectados a Odoo
3. **Módulos OCA disponibles**:
   - `mis_builder` - Constructor de informes financieros
   - `bi_sql_editor` - Queries SQL personalizadas
   - `base_report_creator` - Reports dinámicos

¿Quieres que busque alguna de estas alternativas?
```

---

## Métricas de Éxito

### Antes (con reranker brute-force)
- P@3: 27.8%
- Latencia: +6s/query
- Costo: GPU/RAM para modelo 4B

### Objetivo (búsqueda inteligente)
- P@3: >50%
- Latencia: <500ms
- Costo: Solo embeddings API (ya pagamos)

### Cómo Medimos
1. **Benchmark expandido**: 50+ queries reales
2. **User studies**: ¿El desarrollador encuentra lo que busca?
3. **Fallback quality**: Cuando no hay match exacto, ¿las sugerencias son útiles?

---

## Plan de Implementación

### Fase 6.A: Mejorar Datos (2-3 días)
1. [ ] Nuevo prompt de enriquecimiento más agresivo
2. [ ] Re-enriquecer módulos con descripción genérica
3. [ ] Regenerar embeddings con texto optimizado
4. [ ] Benchmark para medir mejora

### Fase 6.B: Query Expansion (1 día)
1. [ ] Actualizar tool descriptions del MCP
2. [ ] Añadir ejemplos de expansión en docs
3. [ ] Test con Claude Desktop

### Fase 6.C: Multi-Estrategia (2 días)
1. [ ] Implementar cascada de búsqueda
2. [ ] Clasificador de intención
3. [ ] Respuestas contextuales
4. [ ] Fallbacks inteligentes

### Fase 6.D: Validación (1 día)
1. [ ] Benchmark completo
2. [ ] Test con usuarios reales
3. [ ] Ajustes finales

---

## Conclusión

**No necesitamos más potencia de cómputo, necesitamos más inteligencia en el diseño:**

1. **Datos ricos** → Embeddings útiles
2. **Query expansion** → Mejor matching
3. **Multi-estrategia** → Siempre hay respuesta útil
4. **Guía contextual** → El usuario siempre sabe qué hacer

El reranker de 4B queda como **opción premium** para casos extremos, no como requisito base.