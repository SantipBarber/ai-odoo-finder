# SPEC-602: Flujo Inteligente de Búsqueda MCP

**Estado:** ✅ Implementado
**Prioridad:** 🔥 Alta  
**Dependencias:** SPEC-601 (completada)  
**Fecha:** 2025-11-29

---

## Contexto

Después de completar SPEC-601 (extracción de descripciones limpias y regeneración de embeddings), los resultados del benchmark mejoraron significativamente:

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Precision@3 | 16.7% | 41.7% | +150% |
| Precision@5 | 13.3% | 30.0% | +126% |
| MRR | 0.546 | 0.687 | +26% |

Sin embargo, para alcanzar el objetivo de >50% en P@3 y ofrecer una experiencia realmente útil, necesitamos un **flujo inteligente** que aproveche la capacidad del LLM cliente para mejorar las queries.

---

## Decisión: No Usar Skill Externa

### Análisis

| Aspecto | Skill (archivo externo) | Tool Description (en código) |
|---------|------------------------|------------------------------|
| **Mantenimiento** | Hay que actualizar archivo separado | Todo en un lugar |
| **Consistencia** | Puede desincronizarse | Siempre actualizado |
| **Flexibilidad** | Muy detallado (600+ líneas) | Más conciso |
| **Carga en contexto** | Grande | Pequeño |

### Decisión Final

**Usar Tool Description enriquecido** dentro del código MCP.

NO necesitamos:
- Skill externa separada
- Documentación extensa en el contexto del LLM

---

## Problema Actual

```
┌─────────────────────────────────────────────────────────────────┐
│                      FLUJO ACTUAL (Simple)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Usuario: "Necesito facturación electrónica"                     │
│                        │                                         │
│                        ▼                                         │
│  Claude: search_odoo_modules(                                    │
│            query="facturación electrónica",  ← Query literal     │
│            version="16.0"                                        │
│          )                                                       │
│                        │                                         │
│                        ▼                                         │
│  MCP: Búsqueda semántica directa                                │
│                        │                                         │
│                        ▼                                         │
│  Resultados: Puede que no encuentre lo mejor                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

PROBLEMAS:
1. La query es literal, sin expansión de términos
2. No se aclara el contexto (¿qué país? ¿qué tipo?)
3. No hay guía sobre qué hacer si no hay resultados exactos
4. No hay confirmación con el usuario
```

---

## Propuesta: Flujo Inteligente en 4 Fases

```
┌─────────────────────────────────────────────────────────────────┐
│                   FLUJO PROPUESTO (Inteligente)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FASE 1: CLARIFICACIÓN (LLM ↔ Usuario)                          │
│  ─────────────────────────────────────                          │
│  Usuario: "Necesito facturación electrónica"                     │
│                        │                                         │
│                        ▼                                         │
│  LLM: "Para encontrar el módulo más adecuado:                   │
│        - ¿Para qué país/localización?                           │
│        - ¿Qué estándar? (Facturae, CFDI, UBL...)               │
│        - ¿Necesitas firma electrónica?                          │
│        - ¿Versión de Odoo?"                                     │
│                        │                                         │
│                        ▼                                         │
│  Usuario: "España, para administración pública, Odoo 16"         │
│                                                                  │
│  FASE 2: EXPANSIÓN DE QUERY (LLM interno)                       │
│  ─────────────────────────────────────────                      │
│  LLM construye query expandida:                                  │
│    "factura electrónica facturae España FACE                     │
│     administración pública e-factura XML firma                   │
│     electronic invoice Spain government"                         │
│                        │                                         │
│                        ▼                                         │
│  search_odoo_modules(query=<expandida>, version="16.0")          │
│                                                                  │
│  FASE 3: PRESENTACIÓN INTELIGENTE (MCP → LLM → Usuario)         │
│  ─────────────────────────────────────────────────────          │
│  MCP devuelve resultados estructurados                          │
│  LLM presenta al usuario:                                        │
│    ✅ RECOMENDADO: l10n_es_facturae_face                         │
│       "Este módulo permite enviar facturas electrónicas          │
│        en formato Facturae a FACe (administraciones públicas)"   │
│    📋 ALTERNATIVAS: l10n_es_facturae, ...                        │
│                                                                  │
│  FASE 4: CONFIRMACIÓN (LLM ↔ Usuario) ← NUEVO                   │
│  ─────────────────────────────────────                          │
│  LLM: "¿Este módulo cubre lo que necesitas?                     │
│        Si no, puedo buscar algo más específico."                │
│                        │                                         │
│        ┌───────────────┼───────────────┐                        │
│        ▼               ▼               ▼                        │
│     "Sí, es         "No, necesito    "Tengo una                 │
│      perfecto"       algo diferente"  pregunta"                 │
│        │               │               │                        │
│        ▼               ▼               ▼                        │
│     [FIN]          [VOLVER A       [RESPONDER                   │
│                     FASE 1]         Y CONTINUAR]                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Fase 1: Clarificación Inteligente

### Cuándo Pedir Aclaraciones

El LLM debe pedir aclaraciones cuando la query es:

| Tipo de Query | Ejemplo | Aclaración Necesaria |
|---------------|---------|---------------------|
| **Genérica** | "facturación" | País, tipo, estándar |
| **Ambigua** | "gestión de inventario" | ¿Warehouse? ¿Multi-location? ¿Barcodes? |
| **Sin versión** | "módulo de nóminas" | Versión de Odoo |
| **Multi-dominio** | "CRM con e-commerce" | Prioridad, alcance |

### Cuándo NO Pedir Aclaraciones

| Tipo de Query | Ejemplo | Acción |
|---------------|---------|--------|
| **Específica** | "modelo 303 AEAT España 16.0" | Buscar directamente |
| **Técnica** | "l10n_es_facturae" | Buscar por nombre técnico |
| **Con contexto** | "DMS para gestionar documentos en 17.0" | Buscar directamente |

### Preguntas de Clarificación por Categoría

```python
CLARIFICATION_PROMPTS = {
    "localization": [
        "¿Para qué país o región?",
        "¿Qué regulaciones fiscales específicas?",
        "¿Necesitas reportes para alguna autoridad fiscal?"
    ],
    "accounting": [
        "¿Qué tipo de reportes necesitas?",
        "¿Multi-empresa o single company?",
        "¿Integración con algún sistema externo?"
    ],
    "inventory": [
        "¿Necesitas gestión de múltiples almacenes?",
        "¿Trazabilidad por lotes o números de serie?",
        "¿Integración con códigos de barras?"
    ],
    "sales": [
        "¿B2B, B2C o ambos?",
        "¿E-commerce integrado?",
        "¿Gestión de suscripciones?"
    ],
    "hr": [
        "¿Qué país para nóminas/contratos?",
        "¿Gestión de gastos incluida?",
        "¿Control de asistencia?"
    ]
}
```

---

## Fase 2: Expansión de Query

### Estrategia de Expansión

El LLM debe expandir la query del usuario siguiendo estas reglas:

```markdown
## INSTRUCCIONES PARA EXPANSIÓN DE QUERY

Antes de llamar a search_odoo_modules, EXPANDE la query del usuario:

1. **Añade sinónimos en español e inglés**
   - "factura" → "factura invoice billing"
   - "inventario" → "inventario inventory stock warehouse"

2. **Añade términos técnicos de Odoo**
   - "ventas" → "ventas sales sale_order quotation"
   - "compras" → "compras purchase procurement"

3. **Añade contexto del dominio**
   - Si es España: "España Spain ES l10n_es AEAT"
   - Si es México: "México Mexico MX l10n_mx SAT CFDI"

4. **Añade términos funcionales**
   - "factura electrónica" → "factura electrónica e-invoice 
     electronic invoice digital XML firma signature"

5. **NO añadas ruido**
   - Evita términos demasiado genéricos como "module" o "odoo"
   - Evita repeticiones excesivas
   - Máximo 30-40 palabras en la query expandida
```

### Ejemplos de Expansión

| Query Usuario | Query Expandida |
|--------------|-----------------|
| "facturación electrónica España" | "factura electrónica facturae Spain España AEAT FACE e-invoice electronic invoice XML firma digital signature administración pública government" |
| "control de inventario con códigos de barras" | "inventory control stock warehouse barcode scanning gestión inventario almacén código barras trazabilidad tracking location ubicación" |
| "gestión de suscripciones y pagos recurrentes" | "subscription recurring payment suscripción pago recurrente billing facturación periódica contract contrato renewal renovación" |

---

## Fase 3: Respuesta Estructurada del MCP

### Formato de Respuesta MCP (JSON-RPC 2.0)

Según la especificación MCP, las herramientas devuelven resultados en formato JSON-RPC:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Contenido de la respuesta aquí"
      }
    ],
    "isError": false
  }
}
```

El campo `content` es un array que puede contener:
- `text`: Contenido textual
- `image`: Imágenes en base64
- `resource`: Recursos embebidos con URI

### Estructura del Contenido de Respuesta

Aunque MCP usa JSON-RPC, el contenido `text` será interpretado por el LLM cliente (Claude, GPT, Gemini, etc.). Por lo tanto, devolvemos **texto estructurado** que el LLM puede parsear e interpretar:

```markdown
# 🎯 Resultados de Búsqueda

## Confianza: ALTA | MEDIA | BAJA

### ✅ RECOMENDADO (score >= 80)
**Módulo:** l10n_es_facturae_face
**Nombre:** Facturae + FACe
**Score:** 92/100
**Descripción:** Este módulo permite enviar facturas electrónicas 
                 en formato Facturae 3.2.x a la plataforma FACe 
                 del gobierno español para facturación a 
                 administraciones públicas.
**Repositorio:** l10n-spain
**GitHub:** https://github.com/OCA/l10n-spain/tree/16.0/l10n_es_facturae_face
**Dependencias:** l10n_es_facturae, base

### 📋 ALTERNATIVAS
1. **l10n_es_facturae** (Score: 85)
   Facturae básico sin integración FACe
   
2. **l10n_es_facturae_igic** (Score: 78)
   Variante para Canarias con IGIC

### 💡 INFORMACIÓN ADICIONAL
- Todos estos módulos requieren certificado digital para firma
- Documentación: [link]
```

### Niveles de Confianza

| Nivel | Criterio | Acción del LLM |
|-------|----------|----------------|
| **ALTA** | Score >= 80, módulo específico encontrado | Recomendar directamente |
| **MEDIA** | Score 50-79, varios candidatos | Presentar opciones, pedir confirmación |
| **BAJA** | Score < 50, solo aproximaciones | Explicar limitaciones, ofrecer alternativas |
| **NINGUNA** | Sin resultados relevantes | Explicar que no existe, sugerir desarrollo |

---

## Fase 4: Confirmación y Bucle Iterativo

### Flujo de Confirmación

```
LLM presenta resultado
        │
        ▼
"¿Este módulo cubre tu necesidad?"
        │
        ├─── "Sí" ────────────► FIN (éxito)
        │
        ├─── "No, necesito X" ─► VOLVER A FASE 1
        │                        (con contexto adicional)
        │
        ├─── "Casi, pero falta Y" ► FASE 3.5: Solución Parcial
        │
        └─── "Tengo dudas sobre Z" ► Responder y continuar
```

### Respuestas del LLM según Confirmación

#### Si el usuario confirma (Sí)
```markdown
Perfecto. Para instalar `l10n_es_facturae_face`:

1. Ve a Aplicaciones en Odoo
2. Busca "facturae face"
3. Instala el módulo

O vía terminal:
```
pip install odoo-addon-l10n_es_facturae_face
```

¿Necesitas ayuda con la configuración?
```

#### Si el usuario niega (No, necesito algo diferente)
```markdown
Entendido. Para encontrar algo más adecuado:
- ¿Qué funcionalidad específica te falta en este módulo?
- ¿O buscas algo completamente diferente?

[VOLVER A FASE 1 con nuevo contexto]
```

#### Si es solución parcial (Casi, pero falta Y)
```markdown
El módulo `X` cubre el 70% de tu necesidad. 
Para la funcionalidad que falta (Y), tienes opciones:

1. **Módulo adicional**: `módulo_complementario` añade Y
   
2. **Extensión custom**: Podrías heredar de X y añadir:
   ```python
   class MiExtension(models.Model):
       _inherit = 'modelo.base'
       
       campo_nuevo = fields.Char('Campo para Y')
   ```

¿Quieres que te ayude a diseñar la extensión?
```

---

## Manejo de Casos Especiales

### Caso 1: No Existe Módulo

```markdown
❌ **No encontré un módulo OCA para [funcionalidad]**

Esto puede significar:
1. **No existe en OCA** - Es una oportunidad de contribuir
2. **Está en Odoo Enterprise** - La funcionalidad X está incluida en Enterprise
3. **Nombre diferente** - ¿Quizás buscas [alternativa similar]?

### Opciones:
1. **Desarrollar módulo custom** basándote en:
   - `base_module` como punto de partida
   - Estructura sugerida: [snippet]

2. **Considerar Odoo Enterprise** si el presupuesto lo permite

3. **Buscar en otros repositorios**:
   - Odoo Apps Store: https://apps.odoo.com
   - GitHub (no-OCA): buscar "odoo [funcionalidad]"

¿Te ayudo a diseñar un módulo custom?
```

### Caso 2: Solución Parcial

```markdown
⚠️ **Encontré módulos que cubren PARCIALMENTE tu necesidad**

**Lo que necesitas:** Gestión de suscripciones con facturación 
                      automática y pausas

**Lo que existe:**

| Módulo | Tiene | No tiene |
|--------|-------|----------|
| `contract` | ✅ Contratos recurrentes | ❌ Pausas |
|            | ✅ Facturación automática |  |
| `subscription_oca` | ✅ Suscripciones | ❌ Menos flexible |

### Recomendación:
Usa `contract` y extiéndelo para añadir pausas:

```python
class ContractContract(models.Model):
    _inherit = 'contract.contract'
    
    is_paused = fields.Boolean('Pausado')
    pause_date = fields.Date('Fecha de pausa')
    
    def action_pause(self):
        self.write({
            'is_paused': True, 
            'pause_date': fields.Date.today()
        })
```

¿Quieres que desarrollemos este módulo de extensión juntos?
```

### Caso 3: Múltiples Buenos Resultados

```markdown
✅ **Encontré varios módulos excelentes**

La elección depende de tu caso específico:

| Módulo | Mejor para | Score |
|--------|-----------|-------|
| `dms` | Gestión documental completa, carpetas, permisos | 92 |
| `document_knowledge` | Integración con Odoo Knowledge | 85 |
| `attachment_preview` | Solo previsualización de adjuntos | 78 |

### Mi recomendación:
- **DMS completo** → `dms`
- **Ya usas Knowledge** → `document_knowledge`  
- **Solo ver adjuntos** → `attachment_preview` (más ligero)

¿Cuál se ajusta mejor a tu situación?
```

---

## Implementación del Tool Description

### Nuevo Tool Description Completo

```python
@mcp.tool()
async def search_odoo_modules(
    query: Annotated[str, """
        Query de búsqueda para módulos Odoo.
        
        ⚠️ IMPORTANTE - LEE ANTES DE LLAMAR:
        
        1. SI LA QUERY ES GENÉRICA O AMBIGUA:
           Pide aclaraciones al usuario ANTES de llamar:
           - ¿País/localización? (España, México, Francia...)
           - ¿Versión de Odoo?
           - ¿Funcionalidad específica?
           
        2. UNA VEZ TENGAS CONTEXTO, EXPANDE LA QUERY:
           Añade sinónimos en español e inglés, términos técnicos
           de Odoo, y contexto de localización.
           
           Ejemplo:
           Usuario: "facturación electrónica España"
           Tu query: "factura electrónica facturae Spain AEAT 
                     FACE e-invoice XML firma digital"
           
        3. MÁXIMO 30-40 PALABRAS en la query expandida
    """],
    version: Annotated[str, """
        Versión de Odoo (12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0).
        Si el usuario no especifica, pregunta o usa 16.0 como default.
    """],
    dependencies: Annotated[Optional[list[str]], """
        Lista opcional de dependencias requeridas.
        Útil para filtrar módulos que extiendan módulos específicos.
    """] = None,
    limit: Annotated[int, """
        Número máximo de resultados (default: 5, max: 20).
        Usa 5 para búsquedas específicas, 10 para exploratorias.
    """] = 5,
) -> str:
    """
    Busca módulos de Odoo en el ecosistema OCA (15,000+ módulos).
    
    FLUJO RECOMENDADO:
    
    1. CLARIFICA si es necesario
       Pide al usuario: país, versión, funcionalidad específica
    
    2. EXPANDE la query
       Añade sinónimos (ES/EN), términos técnicos, contexto
    
    3. INTERPRETA los resultados
       - Score >= 80: Alta confianza → recomienda directamente
       - Score 50-79: Media → presenta opciones
       - Score < 50: Baja → menciona limitaciones
    
    4. CONFIRMA con el usuario
       "¿Este módulo cubre tu necesidad?"
       Si no → iterar con más contexto
    
    5. Si NO HAY resultados buenos:
       - Sugiere módulos parciales
       - Indica si existe en Odoo Enterprise
       - Ofrece guía para desarrollo custom
    
    ⛔ NUNCA inventes módulos que no existen
    ⛔ NUNCA asumas la versión de Odoo
    ⛔ NUNCA ignores cuando el usuario dice "no es lo que busco"
    
    Devuelve resultados con:
    - Módulo recomendado (si existe)
    - Alternativas relevantes
    - Nivel de confianza
    - Links a GitHub
    """
```

---

## Compatibilidad con Diferentes LLMs

### Clientes MCP Soportados

El MCP es compatible con cualquier cliente que implemente el protocolo:

| LLM | Cliente MCP | Notas |
|-----|-------------|-------|
| Claude | Claude Desktop, Claude Code | Soporte nativo |
| ChatGPT | Vía plugins/custom | Requiere wrapper |
| Gemini | Vía extensiones | Requiere wrapper |
| Otros | Cualquier cliente JSON-RPC | Estándar abierto |

### Formato de Respuesta Universal

La respuesta del MCP es texto estructurado que cualquier LLM puede interpretar:

```
# Título claro
## Secciones con encabezados
- Listas con bullets
**Negrita** para énfasis
`código` para términos técnicos
[links](url) para referencias
```

---

## Métricas de Éxito

| Métrica | Actual | Objetivo |
|---------|--------|----------|
| Precision@3 | 41.7% | >60% |
| MRR | 0.687 | >0.80 |
| Queries sin resultado útil | ~20% | <10% |
| Confirmación positiva del usuario | - | >80% |
| Iteraciones promedio hasta éxito | - | <2 |

---

## Plan de Implementación

### Fase 1: Mejorar Tool Description (2-3 horas)
- [x] Actualizar `mcp_tools.py` con nuevo tool description
- [x] Añadir instrucciones de clarificación
- [x] Añadir ejemplos de expansión de query
- [x] Crear servidor MCP standalone en `mcp-server/`

### Fase 2: Mejorar Formato de Respuesta (3-4 horas)
- [x] Modificar `_format_results_for_claude()` → `_format_results_intelligent()`
- [x] Añadir clasificación de confianza (ALTA/MEDIA/BAJA)
- [x] Añadir sección de alternativas estructurada
- [x] Añadir guía para casos sin resultados
- [x] Añadir sección de soluciones parciales
- [x] **EXTRA:** Migración 005 - Añadir `repo_name` a `searchable_text`

### Fase 3: Testing con LLM (2-3 horas)
- [x] Probar flujo de clarificación
- [x] Probar expansión de queries
- [x] Probar manejo de casos especiales
- [x] Probar bucle de confirmación
- [x] Ajustar según resultados

#### Resultados del Testing (Claude Desktop + Haiku 4.5)

| Consulta | Resultado | Módulos Encontrados |
|----------|-----------|---------------------|
| Facturae España (Odoo 16) | ✅ | `l10n_es_facturae_face`, `l10n_es_facturae_igic` |
| CFDI México (Odoo 17) | ✅ | `l10n_mx_cfdi`, `l10n_mx_cfdi_account` |
| Suscripciones (Odoo 16) | ✅ | `contract`, `subscription_oca` |
| DMS + OCR (Odoo 17) | ✅ | `dms`, `dms_storage` |
| AEAT mod303 (Odoo 16) | ✅ | `l10n_es_aeat_mod303` |
| Delivery carriers (Odoo 17) | ✅ | `delivery_price_method`, `product_packaging_dimension` |

### Fase 4: Benchmark y Validación (1-2 horas)
- [x] Ejecutar benchmark con nuevo flujo
- [x] Comparar métricas antes/después
- [x] Documentar mejoras → `docs/CHANGELOG.md`
- [x] Ajustes finales

---

## Próximos Pasos

1. ✅ **Revisar y aprobar** este diseño
2. ✅ **Implementar** Fase 1: Tool Description
3. ✅ **Implementar** Fase 2: Formato de respuesta
4. ✅ **Crear** servidor MCP standalone (`mcp-server/`)
5. ✅ **Migración 005:** Añadir `repo_name` a full-text search
6. ✅ **Testing** con Claude Desktop (6 consultas verificadas)
7. ✅ **Documentar** cambios en `docs/CHANGELOG.md`

## Archivos Modificados/Creados

### Nuevos
- `mcp-server/pyproject.toml`
- `mcp-server/README.md`
- `mcp-server/src/ai_odoofinder_mcp/__init__.py`
- `mcp-server/src/ai_odoofinder_mcp/server.py`
- `backend/migrations/005_add_repo_name_to_searchable_text.sql`
- `docs/CHANGELOG.md`

### Modificados
- `backend/app/mcp_tools.py` - Tool description enriquecido + formato respuesta

---

## Referencias

- [MCP Specification - Tools](https://modelcontextprotocol.io/specification/2024-11-05/server/tools)
- [JSON-RPC 2.0](https://www.jsonrpc.org/specification)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- SPEC-600: Intelligent Search Strategy
- SPEC-601: Rich Content Extraction (completada)