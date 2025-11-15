---
name: ai-odoofinder
description: Search for Odoo modules in OCA repositories when users need to find compatible modules by version, functionality, or dependencies
---

# AI-OdooFinder Claude Skill

## 🎯 Cuándo Usar Esta Skill

Invoca esta skill cuando el usuario:
- Busca módulos de Odoo de OCA
- Pregunta por funcionalidades específicas de Odoo
- Necesita módulos compatibles con una versión (16.0, 17.0, 18.0)
- Menciona palabras clave: "módulo Odoo", "OCA", "addon", "extensión Odoo"

**NO invoques** esta skill para:
- Preguntas generales sobre Odoo (usa conocimiento general)
- Módulos propietarios/comerciales (no están en esta base de datos)
- Versiones antiguas (solo 16.0, 17.0, 18.0 disponibles)

---

## ⚠️ INSTRUCCIONES CRÍTICAS

**Estrategia según el entorno:**

### En Claude Code (VSCode Extension):
**SIEMPRE usa la herramienta WebFetch para buscar módulos. NUNCA uses:**
- ❌ bash
- ❌ curl
- ❌ Python scripts
- ❌ Archivos locales
- ❌ Comandos del sistema

**Método correcto:**
1. Construye la URL con los parámetros de búsqueda URL-encoded
2. Usa WebFetch con esa URL
3. Parsea el JSON de respuesta
4. Formatea los resultados para el usuario según las plantillas de este documento

### En Claude Web (claude.ai):
**Debido a restricciones de seguridad, debes pedir al usuario que proporcione la URL:**

1. Identifica los parámetros de búsqueda (query, version, dependencies)
2. Construye la URL completa
3. Presenta al usuario UN MENSAJE como este:

```markdown
Para buscar módulos de [funcionalidad] en Odoo [version]:

🔗 **Haz clic en este enlace y copia el JSON que aparece:**
https://ai-odoo-finder.onrender.com/search?query=[QUERY]&version=[VERSION]&limit=5

📋 Luego pega aquí el resultado y te ayudaré a interpretarlo.

⏱️ **Nota:** La primera búsqueda puede tardar 50-60 segundos si el servicio estaba inactivo.
```

4. Cuando el usuario pegue el JSON, formatéalo según las plantillas de este documento
5. NUNCA intentes usar WebFetch directamente en Claude web - no funcionará

---

## 🎯 Propósito

Ayudar a desarrolladores de Odoo a encontrar módulos compatibles mediante búsqueda inteligente con IA.

Esta skill permite búsquedas en lenguaje natural sobre 991 módulos de OCA (Odoo Community Association) indexados, con filtrado por versión y dependencias.

---

## 🛠️ Herramienta Disponible

### `search_odoo_modules`

Busca módulos de Odoo en repositorios de OCA usando búsqueda híbrida (SQL + semántica con embeddings).

**Endpoint:** `GET https://ai-odoo-finder.onrender.com/search`

**Método de Ejecución:**

```
OBLIGATORIO: Usa WebFetch con la URL completa.

Formato:
WebFetch(
  url="https://ai-odoo-finder.onrender.com/search?query=CONSULTA&version=VERSION&limit=LIMITE",
  prompt="Extract the search results and return the JSON data"
)
```

**Ejemplo Real:**
```
WebFetch(
  url="https://ai-odoo-finder.onrender.com/search?query=inventory+management&version=17.0&limit=5",
  prompt="Extract the complete JSON response with all module results"
)
```

**Nota sobre Cold Start:**
⚠️ El servicio puede estar dormido (Free Tier Render). La primera búsqueda puede tardar 50-60 segundos.
Si WebFetch falla con timeout:
1. Informa al usuario: "El servicio está despertando (~60 segundos)"
2. Espera y reintenta
3. La segunda llamada será instantánea

#### Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `query` | string | ✅ Sí | Consulta en lenguaje natural sobre funcionalidad buscada |
| `version` | string | ✅ Sí | Versión de Odoo: "14.0", "15.0", "16.0", "17.0" o "18.0" |
| `dependencies` | array[string] | ❌ No | Lista de dependencias técnicas requeridas (ej: ["sale", "stock"]) |
| `limit` | integer | ❌ No | Número máximo de resultados (1-50, default: 10) |
| `min_score` | integer | ❌ No | Score mínimo para filtrar resultados (0-100, default: 0) |

#### Request Example

```json
{
  "query": "gestión de suscripciones y pagos recurrentes",
  "version": "17.0",
  "dependencies": ["sale"],
  "limit": 5,
  "min_score": 70
}
```

#### Response Example

```json
{
  "query": "gestión de suscripciones y pagos recurrentes",
  "version": "17.0",
  "dependencies": ["sale"],
  "total_results": 3,
  "results": [
    {
      "id": 584,
      "technical_name": "sale_invoice_frequency",
      "name": "Sale Invoice Frequency",
      "version": "17.0",
      "summary": "Define the invoice frequency for customers",
      "description": "...",
      "depends": ["sale", "account"],
      "author": "Moduon, Odoo Community Association (OCA)",
      "license": "AGPL-3",
      "repo_name": "sale-workflow",
      "repo_url": "https://github.com/OCA/sale-workflow",
      "module_path": "sale_invoice_frequency/__manifest__.py",
      "github_stars": 358,
      "github_issues_open": 326,
      "last_commit_date": "2025-11-06T09:44:25",
      "score": 83,
      "distance": 0.3344
    }
  ]
}
```

---

## 📖 Instrucciones de Uso

### 1. Interpretación de Consultas

Cuando un usuario pregunta sobre módulos de Odoo, debes:

#### Extraer Versión

- **Explícita:** "para v17", "en Odoo 16", "versión 18.0"
- **Implícita:** Si no especifica, preguntar:
  > "¿Para qué versión de Odoo necesitas el módulo? (16.0, 17.0 o 18.0)"

#### Extraer Funcionalidad

Convertir lenguaje natural a query descriptiva:

| Usuario dice | Query a usar |
|--------------|--------------|
| "módulo de inventario" | "gestión de inventario" |
| "algo para proyectos" | "gestión de proyectos y tareas" |
| "facturación electrónica" | "facturación electrónica e-invoicing" |
| "pagos recurrentes" | "suscripciones pagos recurrentes" |

#### Extraer Dependencias

Identificar módulos base mencionados y usar nombres técnicos:

| Usuario menciona | Dependencia técnica |
|------------------|---------------------|
| "que funcione con ventas" | `["sale"]` |
| "integrado con inventario" | `["stock"]` |
| "para contabilidad" | `["account"]` |
| "con compras" | `["purchase"]` |
| "y proyectos" | `["project"]` |

**Módulos técnicos comunes:**
- `sale` (Ventas)
- `account` (Contabilidad)
- `stock` (Inventario/Almacén)
- `purchase` (Compras)
- `project` (Proyectos)
- `mrp` (Fabricación)
- `website` (Sitio Web)
- `crm` (CRM)

---

### 2. Ejemplos de Mapeo

```
Usuario: "Necesito un módulo de inventario para Odoo 17"
→ query: "gestión de inventario almacén"
→ version: "17.0"
→ dependencies: null

---

Usuario: "Busco algo para v16 que maneje pagos recurrentes con ventas"
→ query: "pagos recurrentes suscripciones facturación"
→ version: "16.0"
→ dependencies: ["sale"]

---

Usuario: "Módulo de reportes avanzados para contabilidad en 18.0"
→ query: "reportes avanzados informes analytics"
→ version: "18.0"
→ dependencies: ["account"]
```

---

### 3. Presentación de Resultados

Formatea las respuestas de manera clara y profesional:

```markdown
He encontrado [N] módulos compatibles con Odoo [version]:

1. ⭐ [Nombre] ([score]/100) [Badge si score>70: "✅ Muy recomendado"]
   📦 **Nombre técnico:** `[technical_name]`
   🔗 **Repositorio:** [repo_url]
   📊 [github_stars] estrellas • Actualizado [última_fecha]
   🔗 **Dependencias:** [depends] (máximo 5, el resto indicar "... +N más")

   📝 [summary o description - máximo 150 caracteres]

2. [Siguiente módulo...]
```

#### Badges y Recomendaciones

Añade indicadores según score y metadata:

| Condición | Badge/Nota |
|-----------|------------|
| `score > 80` | "✅ **Muy recomendado**" |
| `score > 70` | "✅ Recomendado" |
| `score < 50` | "⚠️ Relevancia media" |
| `github_stars > 300` | "⭐ Popular en la comunidad" |
| `github_issues_open > 200` | "⚠️ Revisar issues abiertos antes de usar" |
| `last_commit_date < 6 meses` | "🔄 Activamente mantenido" |

---

### 4. Casos Especiales

#### Sin Resultados

```markdown
No encontré módulos que cumplan exactamente con:
- Versión: [version]
- Funcionalidad: [query]
- Dependencias: [depends]

💡 **Sugerencias:**
1. Intenta con una descripción más general
2. Verifica que las dependencias sean correctas
3. Considera otra versión de Odoo (actualmente indexadas: 16.0, 17.0, 18.0)
4. Revisa el [Odoo App Store oficial](https://apps.odoo.com) para módulos propietarios
```

#### Versión No Especificada

```markdown
Para ayudarte mejor, necesito saber para qué versión de Odoo lo necesitas:

- **16.0** (Odoo 16) - 421 módulos disponibles
- **17.0** (Odoo 17) - 264 módulos disponibles
- **18.0** (Odoo 18) - 306 módulos disponibles

¿Cuál estás usando?
```

#### Múltiples Resultados con Scores Similares

```markdown
Encontré varios módulos con funcionalidad similar. Los más relevantes son:

[Lista top 3-5 con scores]

💡 **¿Cómo elegir?**
- Revisa las **dependencias** - elige el que mejor se integre con tus módulos actuales
- Verifica **estrellas y actividad** - módulos más populares suelen estar mejor mantenidos
- Lee la **documentación** en GitHub antes de instalar
```

---

## 📚 Ejemplos de Conversación

### Ejemplo 1: Búsqueda Simple

```
👤 Usuario:
Necesito un módulo para gestionar proyectos en Odoo 17

🤖 Claude:
Te ayudo a buscar módulos de gestión de proyectos para Odoo 17.0

[Usa WebFetch con:
  URL: https://ai-odoo-finder.onrender.com/search?query=gestión+de+proyectos+tareas+planning&version=17.0&limit=5
]

He encontrado 5 módulos compatibles con Odoo 17.0:

1. ⭐ Project Management Enhanced (87/100) ✅ Muy recomendado
   📦 **Nombre técnico:** `project_management`
   🔗 **Repositorio:** https://github.com/OCA/project
   📊 245 estrellas • Actualizado hace 3 días
   🔗 **Dependencias:** project, hr_timesheet

   📝 Gestión avanzada de proyectos con planning, Gantt y reporting

[...]
```

### Ejemplo 2: Con Dependencias

```
👤 Usuario:
Busco algo para Odoo 16 que maneje suscripciones y trabaje con ventas

🤖 Claude:
Perfecto, busco módulos de suscripciones para Odoo 16.0 que se integren con 'sale'.

[Usa WebFetch con:
  URL: https://ai-odoo-finder.onrender.com/search?query=suscripciones+pagos+recurrentes+contratos&version=16.0&dependencies=sale&limit=5
]

He encontrado 3 módulos de suscripciones para Odoo 16.0:

1. ✅ Sale Subscription (89/100) ✅ Muy recomendado
   📦 **Nombre técnico:** `sale_subscription`
   🔗 **Repositorio:** https://github.com/OCA/sale-workflow
   📊 358 estrellas • Actualizado hace 1 semana
   🔗 **Dependencias:** sale, account

   📝 Gestión completa de suscripciones con facturación automática

💡 **Nota:** Todos estos módulos dependen de 'sale' como solicitaste.
```

### Ejemplo 3: Sin Resultados

```
👤 Usuario:
Necesito integración con TikTok para Odoo 18

🤖 Claude:
[Usa WebFetch con:
  URL: https://ai-odoo-finder.onrender.com/search?query=TikTok+integration+social+media&version=18.0&limit=5
]

No encontré módulos específicos de integración con TikTok para Odoo 18.0.

💡 **Sugerencias:**
1. Buscar "social media" de forma más general - puede haber integraciones sociales genéricas
2. Revisar el [Odoo App Store](https://apps.odoo.com) - pueden existir módulos propietarios
3. Considerar desarrollo personalizado si es crítico para tu negocio
4. Buscar integraciones alternativas (Instagram, Facebook) que podrían adaptarse

¿Quieres que busque módulos de redes sociales en general?
```

### Ejemplo 4: Aclarar Versión

```
👤 Usuario:
Necesito un módulo para manejar múltiples almacenes

🤖 Claude:
Para ayudarte mejor, ¿para qué versión de Odoo lo necesitas?

- **16.0** (Odoo 16) - 421 módulos disponibles
- **17.0** (Odoo 17) - 264 módulos disponibles
- **18.0** (Odoo 18) - 306 módulos disponibles

👤 Usuario:
Odoo 17

🤖 Claude (en Claude Code):
[Usa WebFetch con:
  URL: https://ai-odoo-finder.onrender.com/search?query=múltiples+almacenes+gestión+multi-warehouse&version=17.0&limit=5
]

Encontré 4 módulos para gestión de múltiples almacenes en Odoo 17.0:

[Resultados...]
```

### Ejemplo 5: Flujo en Claude Web

```
👤 Usuario (en claude.ai):
Busco módulos de gestión de suscripciones para Odoo 16 que funcionen con ventas

🤖 Claude:
Para buscar módulos de suscripciones para Odoo 16 que se integren con ventas:

🔗 **Haz clic aquí y copia el JSON que aparece:**
https://ai-odoo-finder.onrender.com/search?query=gestión+de+suscripciones+pagos+recurrentes+contratos&version=16.0&limit=5

📋 Luego pega aquí el resultado y te ayudaré a interpretarlo.

⏱️ **Nota:** La primera búsqueda puede tardar 50-60 segundos si el servicio estaba inactivo.

---

👤 Usuario:
{"query":"gestión de suscripciones pagos recurrentes contratos","version":"16.0","total_results":5,"results":[...]}

🤖 Claude:
He encontrado 5 módulos de suscripciones para Odoo 16.0:

1. ⭐ Purchase Invoice Plan (88/100) ✅ Muy recomendado
   📦 **Nombre técnico:** `purchase_invoice_plan`
   🔗 **Repositorio:** https://github.com/OCA/purchase-workflow
   📊 255 estrellas • Actualizado hace 4 días
   🔗 **Dependencias:** purchase_open_qty, purchase_stock

   📝 Add to purchases order, ability to manage future invoice plan

[... más resultados ...]
```

---

## 🎯 Mejores Prácticas

### 1. Siempre Valida la Versión
- Es **crítico** en Odoo - la compatibilidad entre versiones es limitada
- Si el usuario no especifica, **siempre preguntar**

### 2. No Inventes Módulos
- Solo presenta resultados **reales** de la API
- Si no hay resultados, sé honesto y ofrece alternativas

### 3. Contextualiza Dependencias
- Explica **por qué** se necesita una dependencia
- Advierte si un módulo tiene **muchas dependencias** (puede complicar instalación)

### 4. Interpreta Lenguaje Natural
- Los usuarios no conocen nombres técnicos
- "Facturación" → incluye "invoicing", "billing", "facturación electrónica"
- "Inventario" → incluye "stock", "warehouse", "almacén"

### 5. Prioriza por Score
- Muestra primero los de **mayor score**
- Destaca si hay módulos con score >80
- Advierte si todos los resultados tienen score <50

### 6. Proporciona Contexto
- Enlace al **repositorio** para más info
- Menciona **actividad reciente** (mantenimiento)
- Nota sobre **popularidad** (estrellas)

---

## 🔍 Tips para Queries Efectivas

### Amplía la Query con Sinónimos

| Término Original | Sinónimos a Incluir |
|------------------|---------------------|
| "suscripciones" | "recurring, subscription, contract, periodic" |
| "inventario" | "stock, warehouse, almacén, inventory" |
| "reportes" | "reports, analytics, dashboard, informes" |
| "ventas" | "sales, orders, quotation, presupuesto" |

### Contexto es Clave

Mejor: `"gestión de inventario con múltiples almacenes y trazabilidad"`
Que: `"inventario"`

---

## ⚙️ Configuración Técnica

### Endpoint Local (Desarrollo)
```
http://localhost:8989/search
```

### Endpoint Producción (✅ ACTIVO)
```
https://ai-odoo-finder.onrender.com/search
```

### Rate Limits
- No hay límites configurados actualmente
- En producción, considerar rate limiting por IP

### Timeout
- Búsquedas típicamente < 2 segundos
- Si tarda más de 10s, reintentar o reportar error

---

## 📊 Estadísticas Actuales

```
Total módulos indexados: 991
- Odoo 16.0: 421 módulos
- Odoo 17.0: 264 módulos
- Odoo 18.0: 306 módulos

Top repositorios:
1. sale-workflow (321 módulos)
2. purchase-workflow (250 módulos)
3. web (159 módulos)
4. server-tools (151 módulos)
5. account-financial-tools (110 módulos)
```

---

## 🧪 Testing

Para probar la skill, usa WebFetch con esta URL:

```
https://ai-odoo-finder.onrender.com/search?query=reportes+de+ventas&version=17.0&limit=3
```

Respuesta esperada: JSON con resultados rankeados

**Nota:** El primer request puede tardar 50-60 segundos si el servicio estaba dormido (Free Tier).

---

## 🐛 Manejo de Errores

### Si la API no responde
```markdown
⚠️ Lo siento, no puedo conectar con el servicio de búsqueda en este momento.

Por favor:
1. Verifica que el servidor esté corriendo
2. Intenta de nuevo en unos segundos
3. Si el problema persiste, contacta al administrador
```

### Si hay error 400 (Bad Request)
```markdown
⚠️ Parece que hay un problema con los parámetros de búsqueda.

Verifica que:
- La versión sea válida (16.0, 17.0, 18.0)
- La query no esté vacía
- Las dependencias sean nombres de módulos válidos
```

### Si hay error 500 (Server Error)
```markdown
⚠️ Ocurrió un error interno en el servidor.

Intenta:
1. Simplificar tu búsqueda
2. Intentar de nuevo en unos momentos
3. Reportar el error si persiste
```

---

## 🎓 Consideraciones Finales

1. **Siempre valida versión** - Es lo más importante en Odoo
2. **No inventes módulos** - Solo presenta resultados reales
3. **Sé honesto con limitaciones** - Si no hay resultados, dilo
4. **Contextualiza dependencias** - Explica qué significan
5. **Destaca calidad** - Score + estrellas + actividad
6. **Facilita decisión** - Ordena por relevancia, explica diferencias

---

## 📞 Soporte

- **API Docs:** http://localhost:8989/docs (Swagger UI)
- **GitHub:** https://github.com/SantipBarber/ai-odoo-finder
- **Issues:** https://github.com/SantipBarber/ai-odoo-finder/issues

---

<div align="center">

**🤖 Skill creada para maximizar productividad de desarrolladores Odoo**

[Documentación Completa](../README.md) • [Guía Técnica](../docs/TECHNICAL_GUIDE.md) • [API Reference](../docs/API.md)

</div>
