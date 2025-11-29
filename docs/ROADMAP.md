# 🗺️ Hoja de Ruta AI-OdooFinder - Plan de Implementación

**Versión:** 3.0 (Fase 6: MCP Inteligente Completada)
**Fecha:** Enero 2025
**Objetivo:** Sistema de búsqueda inteligente de módulos Odoo con IA

---

## 🎯 FASE ACTUAL: Fase 6 Completada - MCP Inteligente

**Estado Actual del Proyecto:**
- ✅ MVP Funcional desplegado en Render
- ✅ API REST funcionando con FastAPI
- ✅ Base de datos Neon con pgVector
- ✅ Claude Skill funcional (Web copy-paste + Code nativo)
- ✅ **15,881 módulos indexados** (v12.0 - v19.0, 8 versiones) 🎉
- ✅ **14,869 módulos con README completo** (93.6%)
- ✅ **15,881 módulos con AI enrichment** (100%)
- ✅ GitHub Actions ETL funcionando correctamente
- ✅ Sprint 1: Limpieza de documentación completado
- ✅ Sprint 3: Multi-versión completado
- ✅ **Fase 6: MCP Inteligente completada** 🎉
  - ✅ Servidor MCP standalone para Claude Desktop
  - ✅ Tool description enriquecido con instrucciones inteligentes
  - ✅ Formato de respuesta estructurada con niveles de confianza
  - ✅ Migración 005: repo_name en searchable_text
  - ✅ Testing con 6 casos de uso (100% éxito)
- ❌ Módulos propios no soportados (Sprint 5 pendiente)

---

## 📋 PLAN DE TRABAJO INMEDIATO

### SPRINT 1: Limpieza y Corrección ✅ COMPLETADO

**Completado:** 15 Noviembre 2025
**Resultado:** Documentación limpia y organizada, 8 archivos eliminados, PROJECT_SUMMARY.md creado

#### ✅ Tarea 1.1: Corregir GitHub Actions ETL
**Problema:** El job nocturno falla con `ModuleNotFoundError: No module named 'sqlalchemy'`

**Solución:**
- [ ] Agregar step de instalación de dependencias en `.github/workflows/etl.yml`
- [ ] Configurar variables de entorno necesarias (DATABASE_URL, etc.)
- [ ] Decidir si queremos mantener el ETL automático o deshabilitarlo
- [ ] Documentar el propósito del ETL automático

**Archivos a modificar:**
- `.github/workflows/etl.yml`

**Tiempo estimado:** 2 horas

---

#### ✅ Tarea 1.2: Auditoría y Limpieza de Documentación
**Objetivo:** Identificar documentos desactualizados, duplicados o innecesarios

**Documentos a revisar:**

**MANTENER Y ACTUALIZAR:**
- ✅ `README.md` - Documento principal
- ✅ `docs/ROADMAP.md` - Este documento (actualizar con nuevo plan)
- ✅ `docs/TECHNICAL_GUIDE.md` - Guía técnica
- ✅ `docs/API.md` - Referencia de API
- ✅ `docs/QUICKSTART.md` - Guía rápida
- ✅ `claude-skill/README.md` - Guía de la skill
- ✅ `claude-skill/ai-odoofinder-skill/Skill.md` - Definición de la skill

**REVISAR Y POSIBLEMENTE ELIMINAR:**
- ⚠️ `docs/CREATED_FILES.md` - Posible documento temporal
- ⚠️ `docs/GALLERY.md` - ¿Tiene contenido útil?
- ⚠️ `docs/BRANDING.md` - ¿Es necesario para el proyecto?
- ⚠️ `docs/NEXT_STEPS.md` - Posible duplicado del ROADMAP
- ⚠️ `claude-skill/prompts.md` - Contenido mínimo
- ⚠️ `claude-skill/examples.md` - Contenido mínimo
- ⚠️ `CONTRIBUTING.md` (raíz) - Duplicado de `docs/CONTRIBUTING.md`

**Acciones:**
- [ ] Revisar cada documento marcado con ⚠️
- [ ] Eliminar duplicados innecesarios
- [ ] Consolidar información útil
- [ ] Actualizar INDEX.md con la nueva estructura

**Tiempo estimado:** 3-4 horas

---

#### ✅ Tarea 1.3: Actualizar Documentación Clave

**Documentos a actualizar:**

1. **README.md**
   - [ ] Actualizar estadísticas de módulos (991 total)
   - [ ] Añadir nota sobre Claude Skill (funciona diferente en Web vs Code)
   - [ ] Actualizar roadmap con nuevas features planeadas

2. **docs/TECHNICAL_GUIDE.md**
   - [ ] Documentar arquitectura actual
   - [ ] Explicar cómo funciona la búsqueda híbrida
   - [ ] Añadir diagramas si es posible

3. **docs/API.md**
   - [ ] Documentar endpoint `/search` GET y POST
   - [ ] Ejemplos de requests/responses actualizados
   - [ ] Parámetros disponibles

4. **claude-skill/README.md**
   - [ ] Ya actualizado con diferencias Web vs Code
   - [ ] Revisar que esté completo

**Tiempo estimado:** 4-5 horas

---

### SPRINT 2: Implementación MCP (1-2 semanas)

#### 🚀 Tarea 2.1: Investigación y Setup MCP
**Objetivo:** Implementar servidor MCP para que la skill funcione nativamente en Claude Web

**Recursos:**
- Documentación MCP: https://modelcontextprotocol.io
- Ejemplos de servidores MCP
- Claude Code MCP integration

**Pasos:**
- [ ] Estudiar protocolo MCP y arquitectura
- [ ] Diseñar estructura del servidor MCP
- [ ] Configurar proyecto MCP (Node.js o Python)
- [ ] Implementar herramienta `search_odoo_modules` en MCP
- [ ] Testing local con Claude Desktop
- [ ] Documentar instalación para usuarios

**Entregables:**
- [ ] Servidor MCP funcional en `/mcp-server/`
- [ ] Documentación de instalación
- [ ] README específico para MCP

**Tiempo estimado:** 5-7 días

---

#### 🚀 Tarea 2.2: Integración y Testing
- [ ] Probar servidor MCP con Claude Desktop
- [ ] Probar con Claude Web (si es posible)
- [ ] Crear ejemplos de uso
- [ ] Actualizar Skill.md con instrucciones MCP
- [ ] Video tutorial (opcional)

**Tiempo estimado:** 2-3 días

---

### SPRINT 3: Expansión de Versiones ✅ COMPLETADO

**Completado:** 15 Noviembre 2025
**Resultado:** 2,508 módulos indexados en 8 versiones (v12.0 - v19.0)

#### 📦 Tarea 3.1: Soporte Multi-Versión (v12 - v19) ✅
**Objetivo:** Ampliar cobertura de versiones de Odoo

**Versiones a añadir:**
- v12.0 (LTS antigua)
- v13.0
- v14.0
- v15.0
- v19.0 (actual)

**Cambios necesarios:**

1. **Base de datos:**
   - [ ] No requiere cambios (campo `version` ya es string)

2. **ETL Script:**
   - [ ] Actualizar `scripts/etl_oca_modules.py`
   - [ ] Añadir versiones 12.0, 13.0, 14.0, 15.0, 19.0 a `ODOO_VERSIONS`
   - [ ] Probar que GitHub API tenga ramas para estas versiones

3. **API:**
   - [ ] Actualizar validación de versiones en schemas
   - [ ] Documentar nuevas versiones en API.md

4. **Skill:**
   - [ ] Actualizar Skill.md con nuevas versiones disponibles
   - [ ] Actualizar estadísticas de módulos por versión

**Pasos de implementación:**
- [ ] Modificar `ODOO_VERSIONS` en ETL
- [ ] Ejecutar ETL para nuevas versiones
- [ ] Verificar indexación correcta
- [ ] Actualizar documentación
- [ ] Testing con búsquedas multi-versión

**Tiempo estimado:** 3-4 días

**Estimación de módulos:**
- v12.0: ~150-200 módulos
- v13.0: ~200-250 módulos
- v14.0: ~250-300 módulos
- v15.0: ~300-350 módulos
- v19.0: ~100-150 módulos (nueva, crecerá)
- **Total nuevo:** ~1000-1250 módulos adicionales
- **Gran total:** ~2000-2250 módulos

---

### SPRINT 4: Integración Odoo App Store (2 semanas)

#### 🏪 Tarea 4.1: Scraping Odoo App Store
**Objetivo:** Añadir módulos oficiales y de terceros del Odoo App Store

**Desafíos:**
- Odoo App Store no tiene API pública oficial
- Requiere scraping o acceso con cuenta

**Opciones de implementación:**

**Opción A: Scraping (Recomendada para MVP)**
- [ ] Investigar estructura HTML de apps.odoo.com
- [ ] Implementar scraper con BeautifulSoup/Scrapy
- [ ] Extraer: nombre, descripción, versión, autor, precio
- [ ] Manejar paginación y rate limiting
- [ ] Almacenar en tabla separada `odoo_store_modules`

**Opción B: API no oficial**
- [ ] Investigar si existe API no documentada
- [ ] Reverse engineering de la web app

**Opción C: Manual curado**
- [ ] Lista manual de módulos comerciales populares
- [ ] Actualización mensual manual

**Implementación:**

1. **Nuevo script:** `scripts/scrape_odoo_store.py`
```python
# Estructura básica
def scrape_odoo_store(version: str, category: str = None):
    # Scraping lógica
    pass

def parse_module_page(url: str):
    # Extraer info del módulo
    pass
```

2. **Nueva tabla en DB:**
```python
class OdooStoreModule(Base):
    __tablename__ = "odoo_store_modules"
    # Similar a OdooModule pero con campos adicionales:
    # - price (Decimal)
    # - is_commercial (Boolean)
    # - rating (Float)
    # - downloads (Integer)
    # - store_url (String)
```

3. **Actualizar servicio de búsqueda:**
- [ ] Modificar `search_service.py` para buscar en ambas tablas
- [ ] Añadir filtro `source` (oca, store, custom)
- [ ] Combinar resultados y rankear

**Tiempo estimado:** 7-10 días

---

#### 🏪 Tarea 4.2: Testing y Documentación
- [ ] Probar scraping en diferentes categorías
- [ ] Verificar calidad de datos extraídos
- [ ] Documentar limitaciones (módulos de pago, etc.)
- [ ] Actualizar API docs con nuevo parámetro `source`
- [ ] Actualizar Skill.md con info sobre Odoo Store

**Tiempo estimado:** 2-3 días

---

### SPRINT 5: Módulos Propios/Custom (1 semana)

#### 🏢 Tarea 5.1: Soporte para Módulos Propios
**Objetivo:** Permitir indexar módulos desarrollados internamente

**Flujo de trabajo:**

1. **Usuario crea README del módulo custom:**
```markdown
# my_custom_module

**Versión:** 17.0
**Dependencias:** sale, stock
**Autor:** Mi Empresa

Descripción detallada del módulo...

## Características
- Feature 1
- Feature 2
```

2. **Usuario ejecuta script de indexación:**
```bash
python scripts/index_custom_module.py \
  --path /path/to/my_custom_module \
  --company "Mi Empresa"
```

3. **Script genera embedding y guarda en Neon**

**Implementación:**

**Script:** `scripts/index_custom_module.py`
```python
def index_custom_module(
    module_path: str,
    company: str,
    version: str = "17.0"
):
    # 1. Leer __manifest__.py
    # 2. Leer README.md si existe
    # 3. Generar embedding
    # 4. Guardar en custom_modules table
```

**Nueva tabla:**
```python
class CustomModule(Base):
    __tablename__ = "custom_modules"
    # Similar a OdooModule
    # Campos adicionales:
    # - company (String) - Empresa propietaria
    # - is_private (Boolean) - Si es privado
    # - custom_tags (ARRAY) - Tags custom
```

**Actualizar búsqueda:**
- [ ] Añadir parámetro `include_custom` (bool)
- [ ] Filtrar por empresa si es necesario
- [ ] Combinar resultados de las 3 fuentes

**Seguridad:**
- [ ] Autenticación para módulos privados
- [ ] Filtrado por tenant/empresa
- [ ] No mostrar módulos privados en búsquedas públicas

**Pasos:**
- [ ] Crear script `index_custom_module.py`
- [ ] Crear tabla `custom_modules`
- [ ] Modificar servicio de búsqueda
- [ ] Implementar autenticación básica
- [ ] Documentar proceso en docs/CUSTOM_MODULES.md
- [ ] Testing con módulos reales

**Tiempo estimado:** 5-6 días

---

#### 🏢 Tarea 5.2: UI/CLI para Gestión Custom
- [ ] Crear comando CLI para gestión
- [ ] Implementar endpoints API para CRUD custom modules
- [ ] Documentar best practices
- [ ] Ejemplo completo end-to-end

**Tiempo estimado:** 2-3 días

---

## 📊 RESUMEN DEL PLAN

### Timeline General

```
SPRINT 1: Limpieza y Corrección          [Semana 1]
├─ Tarea 1.1: Fix GitHub Actions         [2h]
├─ Tarea 1.2: Auditoría docs             [4h]
└─ Tarea 1.3: Actualizar docs            [5h]

SPRINT 2: MCP                            [Semanas 2-3]
├─ Tarea 2.1: Implementar MCP            [5-7 días]
└─ Tarea 2.2: Testing MCP                [2-3 días]

SPRINT 3: Multi-versión                  [Semana 4]
└─ Tarea 3.1: v12-v19                    [3-4 días]

SPRINT 4: Odoo Store                     [Semanas 5-6]
├─ Tarea 4.1: Scraping                   [7-10 días]
└─ Tarea 4.2: Testing/Docs               [2-3 días]

SPRINT 5: Módulos Custom                 [Semana 7]
├─ Tarea 5.1: Core implementation        [5-6 días]
└─ Tarea 5.2: UI/CLI                     [2-3 días]
```

**Total estimado:** 7-8 semanas

---

## ✅ CHECKLIST DE TAREAS

### SPRINT 1: Limpieza ✨
- [ ] Corregir GitHub Actions ETL
- [ ] Auditar documentación
- [ ] Eliminar documentos duplicados/innecesarios
- [ ] Actualizar README.md
- [ ] Actualizar TECHNICAL_GUIDE.md
- [ ] Actualizar API.md
- [ ] Actualizar INDEX.md

### SPRINT 2: MCP 🔌
- [ ] Investigar protocolo MCP
- [ ] Configurar proyecto MCP
- [ ] Implementar servidor MCP
- [ ] Implementar tool `search_odoo_modules`
- [ ] Testing con Claude Desktop
- [ ] Documentar instalación MCP
- [ ] Actualizar Skill.md con instrucciones MCP
- [ ] Video/guía de instalación

### SPRINT 3: Multi-versión 📦
- [ ] Actualizar ETL para v12-v19
- [ ] Ejecutar ETL para nuevas versiones
- [ ] Actualizar validación de API
- [ ] Actualizar documentación
- [ ] Testing búsquedas multi-versión
- [ ] Actualizar estadísticas en docs

### SPRINT 4: Odoo Store 🏪
- [ ] Investigar estructura Odoo App Store
- [ ] Implementar scraper
- [ ] Crear tabla `odoo_store_modules`
- [ ] Probar scraping
- [ ] Integrar en servicio de búsqueda
- [ ] Añadir filtro `source` en API
- [ ] Testing con datos reales
- [ ] Documentar limitaciones
- [ ] Actualizar API docs
- [ ] Actualizar Skill.md

### SPRINT 5: Módulos Custom 🏢
- [ ] Diseñar flujo de indexación custom
- [ ] Crear script `index_custom_module.py`
- [ ] Crear tabla `custom_modules`
- [ ] Implementar autenticación
- [ ] Modificar servicio de búsqueda
- [ ] Testing con módulos reales
- [ ] Crear docs/CUSTOM_MODULES.md
- [ ] Implementar CLI management
- [ ] Crear endpoints API CRUD
- [ ] Ejemplo end-to-end

---

## 🎯 OBJETIVOS DEL PLAN

### Al finalizar este roadmap tendremos:

**Cobertura:**
- ✅ 2000-2500 módulos indexados
- ✅ 8 versiones de Odoo (v12-v19)
- ✅ Módulos OCA + Odoo Store + Custom

**Funcionalidad:**
- ✅ MCP implementado (búsqueda nativa en Claude)
- ✅ Búsqueda multi-fuente (OCA, Store, Custom)
- ✅ Soporte para módulos privados/empresariales

**Documentación:**
- ✅ Docs actualizados y sin duplicados
- ✅ Guías de instalación MCP
- ✅ Guía de módulos custom
- ✅ API completa documentada

**Automatización:**
- ✅ GitHub Actions funcionando correctamente
- ✅ ETL automático (opcional)
- ✅ CI/CD mejorado

---

---

## 📋 Resumen Ejecutivo

### Qué Vamos a Construir

Un asistente de IA conversacional que ayuda a desarrolladores de Odoo a encontrar módulos compatibles mediante:
- **Búsqueda Híbrida:** Filtrado SQL + Búsqueda semántica (RAG)
- **Interfaz:** Claude Skill (conversacional, sin UI que desarrollar)
- **Embeddings:** Qwen3-Embedding (open source, eficiente)

### Stack Tecnológico

```yaml
Backend & Datos:
  - Neon Postgres Serverless (con pgVector)
  - FastAPI en Render.com (API REST)
  - OpenRouter + Qwen3-Embedding-4B
  - SQLAlchemy + Alembic

Interfaz:
  - Claude Skill (conversacional en claude.ai)
  - Sin UI web en MVP

Integración:
  - GitHub API (repositorios OCA)
  - ~500-1000 módulos de Odoo indexados
```

### Timeline

**MVP:** 4-6 semanas  
**Beta pública:** 8-10 semanas  
**Producción:** 12 semanas

---

## 🎯 FASE 0: Setup y Validación Técnica

**Duración:** 1-2 semanas  
**Objetivo:** Verificar viabilidad antes de desarrollar

### Semana 1: Configuración Base

#### 1.1 Entorno de Desarrollo

```bash
# Crear proyecto
mkdir ai-odoofinder
cd ai-odoofinder

# Entorno virtual Python
python3.10 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Dependencias básicas
pip install fastapi uvicorn sqlalchemy psycopg2-binary pgvector httpx python-dotenv
```

#### 1.2 Configurar Qwen3-Embedding

**Modelos disponibles:**
- `Qwen/Qwen3-Embedding-4B` (ligero, rápido)
- `Qwen/Qwen3-Embedding-4B` (mejor calidad)

**Opción A: Via OpenRouter (Recomendado para MVP)**
```python
# embedding_service.py
import openai

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="tu_openrouter_key"
)

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="qwen/qwen3-embedding-8b",  # O 4b
        input=text
    )
    return response.data[0].embedding
```

**Opción B: Local con Ollama (Si prefieres)**
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull qwen3-embedding-8b

# Usar en Python
import ollama
embedding = ollama.embeddings(
    model='qwen3-embedding-8b',
    prompt='texto para embedding'
)
```

#### 1.3 Test de Embeddings

```python
# scripts/test_embeddings.py
def test_qwen_embeddings():
    """Verificar que Qwen3-Embedding funciona"""
    
    texts = [
        "módulo de gestión de inventario",
        "gestión de almacén y stock",
        "módulo de ventas y facturación"
    ]
    
    embeddings = [get_embedding(text) for text in texts]
    
    # Verificar dimensiones
    assert len(embeddings[0]) == 4096  # Qwen3-8B
    # O 2048 para Qwen3-4B
    
    # Test similitud
    from sklearn.metrics.pairwise import cosine_similarity
    similarity_matrix = cosine_similarity(embeddings)
    
    # Los dos primeros deberían ser más similares
    assert similarity_matrix[0][1] > similarity_matrix[0][2]
    
    print("✅ Embeddings funcionando correctamente")
    print(f"Dimensión: {len(embeddings[0])}")
    print(f"Similitud 1-2: {similarity_matrix[0][1]:.3f}")

if __name__ == "__main__":
    test_qwen_embeddings()
```

#### 1.4 Explorar GitHub API de OCA

```python
# scripts/explore_oca.py
import requests

GITHUB_TOKEN = "tu_token_aqui"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def list_oca_repos():
    """Listar repositorios de OCA"""
    url = "https://api.github.com/orgs/OCA/repos"
    response = requests.get(url, headers=HEADERS, params={"per_page": 100})
    response.raise_for_status()
    
    repos = response.json()
    print(f"Total repos encontrados: {len(repos)}")
    
    # Mostrar algunos
    for repo in repos[:10]:
        print(f"- {repo['name']}: {repo['description'][:50]}...")
    
    return repos

def get_repo_branches(repo_name: str):
    """Obtener ramas de un repo"""
    url = f"https://api.github.com/repos/OCA/{repo_name}/branches"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    branches = response.json()
    odoo_versions = [b['name'] for b in branches if b['name'] in ['16.0', '17.0', '18.0']]
    
    print(f"Ramas Odoo en {repo_name}: {odoo_versions}")
    return odoo_versions

def find_manifests(repo_name: str, branch: str):
    """Encontrar manifiestos en una rama"""
    url = f"https://api.github.com/repos/OCA/{repo_name}/git/trees/{branch}"
    response = requests.get(url, headers=HEADERS, params={"recursive": "1"})
    response.raise_for_status()
    
    tree = response.json().get("tree", [])
    manifests = [item["path"] for item in tree if item["path"].endswith("__manifest__.py")]
    
    print(f"Manifiestos en {repo_name}/{branch}: {len(manifests)}")
    return manifests

def parse_manifest_example():
    """Parsear un manifiesto de ejemplo"""
    # Ejemplo: server-tools/base_technical_features/__manifest__.py
    url = "https://raw.githubusercontent.com/OCA/server-tools/17.0/base_technical_features/__manifest__.py"
    response = requests.get(url)
    response.raise_for_status()
    
    import ast
    manifest = ast.literal_eval(response.text)
    
    print("\n📦 Ejemplo de manifiesto parseado:")
    print(f"Nombre: {manifest.get('name')}")
    print(f"Versión: {manifest.get('version')}")
    print(f"Dependencias: {manifest.get('depends')}")
    print(f"Autor: {manifest.get('author')}")
    print(f"Licencia: {manifest.get('license')}")
    
    return manifest

if __name__ == "__main__":
    print("🔍 Explorando GitHub API de OCA...\n")
    
    # 1. Listar repos
    repos = list_oca_repos()
    
    # 2. Probar con un repo
    print("\n📂 Explorando repo 'server-tools':")
    branches = get_repo_branches("server-tools")
    
    # 3. Encontrar manifiestos
    if "17.0" in branches:
        manifests = find_manifests("server-tools", "17.0")
    
    # 4. Parsear ejemplo
    parse_manifest_example()
    
    print("\n✅ Exploración completada!")
```

### Semana 2: Decisión GO/NO-GO

#### Calcular Costos

```python
# scripts/estimate_costs.py

# Datos a indexar
ESTIMATED_MODULES = 800  # Aproximado de OCA
AVG_TEXT_LENGTH = 500    # Chars por módulo (description + README)

# Costos Qwen3-Embedding en OpenRouter
# (Verificar precios actuales en openrouter.ai)
COST_PER_1M_TOKENS = 0.02  # USD (estimado, verificar)

total_tokens = (ESTIMATED_MODULES * AVG_TEXT_LENGTH) / 4  # Aprox tokens
cost_embeddings = (total_tokens / 1_000_000) * COST_PER_1M_TOKENS

print(f"📊 Estimación de Costos MVP:")
print(f"Módulos a indexar: {ESTIMATED_MODULES}")
print(f"Tokens estimados: {total_tokens:,.0f}")
print(f"Costo embeddings inicial: ${cost_embeddings:.2f}")
print(f"Costo mensual (re-indexado): ${cost_embeddings:.2f}")
print(f"\n💡 Total estimado MVP: ${cost_embeddings * 2:.2f} (inicial + 1 mes)")
```

#### Checklist Decisión

- [ ] ✅ Qwen3-Embedding funciona correctamente
- [ ] ✅ GitHub API responde y puedo parsear manifiestos
- [ ] ✅ Costos son asumibles (<$50 USD para MVP)
- [ ] ✅ Tiempo estimado realista (4-6 semanas)
- [ ] ✅ Tengo acceso a OpenRouter (o Ollama local)

**🚦 Decisión:** Si todos ✅ → Continuar a Fase 1

---

## 🚀 FASE 1: MVP Funcional

**Duración:** 2-3 semanas  
**Objetivo:** Sistema end-to-end con 100-200 módulos

### Semana 3: Backend Base

#### 3.1 Estructura del Proyecto

```
ai-odoofinder/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configuración
│   │   ├── database.py          # DB connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── embedding_service.py  # Qwen3-Embedding
│   │   │   ├── github_service.py     # GitHub API
│   │   │   └── search_service.py     # Búsqueda híbrida
│   │   └── api/
│   │       └── endpoints/
│   │           └── search.py    # Endpoints API
│   ├── tests/
│   └── requirements.txt
├── scripts/
│   └── etl_oca_modules.py       # ETL pipeline
├── claude-skill/
│   └── SKILL.md                 # Claude Skill definition
├── .env.example
├── .gitignore
└── README.md
```

#### 3.2 Configuración de Neon

**Crear cuenta y proyecto:**
```bash
# 1. Ir a https://neon.com y crear cuenta
# 2. Crear nuevo proyecto: "ai-odoofinder"
# 3. Seleccionar región más cercana
# 4. Copiar connection string
```

**Habilitar pgVector:**
```sql
-- En Neon SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar instalación
SELECT * FROM pg_extension WHERE extname = 'vector';
```

**Variables de entorno (.env):**
```bash
# Neon Database
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require

# OpenRouter
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# GitHub
GITHUB_TOKEN=ghp_xxxxx
```

**Ventajas de Neon para este proyecto:**
- ✅ Scale-to-zero: Solo pagas cuando se usa
- ✅ Provisioning instantáneo: 300ms vs varios minutos
- ✅ Branching: Crear copias de BD para testing
- ✅ pgVector optimizado para IA
- ✅ Free tier generoso: 0.5GB storage + 191 compute hours/mes

#### 3.3 Modelos de Datos

```python
# backend/app/models.py
from sqlalchemy import Column, Integer, String, ARRAY, DateTime, Text
from pgvector.sqlalchemy import Vector
from datetime import datetime

class OdooModule(Base):
    __tablename__ = "odoo_modules"
    
    # Identificadores
    id = Column(Integer, primary_key=True)
    technical_name = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    
    # Metadata Odoo
    version = Column(String, nullable=False, index=True)  # "16.0", "17.0", "18.0"
    depends = Column(ARRAY(String), default=[])
    author = Column(String)
    license = Column(String)
    
    # GitHub info
    repo_name = Column(String, nullable=False)  # "server-tools"
    repo_url = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    
    # Contenido
    description = Column(Text)
    summary = Column(Text)
    
    # Metadata calidad
    github_stars = Column(Integer, default=0)
    github_issues_open = Column(Integer, default=0)
    last_commit_date = Column(DateTime)
    
    # Embedding (4096 dims para Qwen3-8B, 2048 para 4B)
    embedding = Column(Vector(4096))  # O 2048 según modelo
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índice único
    __table_args__ = (
        Index('idx_tech_name_version', 'technical_name', 'version', unique=True),
    )
```

#### 3.3 Configuración Base de Datos

```bash
# Crear base de datos
createdb ai_odoofinder

# Instalar extensión pgVector
psql ai_odoofinder -c "CREATE EXTENSION vector;"

# Verificar
psql ai_odoofinder -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

```python
# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/ai_odoofinder")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear tablas
def init_db():
    Base.metadata.create_all(bind=engine)
```

#### 3.4 API FastAPI

```python
# backend/app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import get_db, init_db
from .api.endpoints import search

app = FastAPI(
    title="AI-OdooFinder API",
    description="AI-powered Odoo module discovery",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup
@app.on_event("startup")
def on_startup():
    init_db()

# Routes
app.include_router(search.router, prefix="/api/v1", tags=["search"])

@app.get("/")
def root():
    return {
        "message": "AI-OdooFinder API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
```

```python
# backend/app/api/endpoints/search.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ...database import get_db
from ...schemas import SearchRequest, SearchResponse
from ...services.search_service import SearchService

router = APIRouter()

@router.post("/search", response_model=List[SearchResponse])
async def search_modules(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Buscar módulos de Odoo usando búsqueda híbrida.
    
    - **query**: Descripción de funcionalidad (ej: "gestión de inventario")
    - **version**: Versión de Odoo ("16.0", "17.0", "18.0")
    - **depends**: Lista opcional de dependencias requeridas
    - **limit**: Número máximo de resultados (default: 5)
    """
    service = SearchService(db)
    results = await service.search(
        query=request.query,
        version=request.version,
        depends=request.depends,
        limit=request.limit
    )
    return results
```

### Semana 4: ETL Pipeline

#### 4.1 Script de Ingesta

```python
# scripts/etl_oca_modules.py
import requests
import ast
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, engine
from backend.app.models import Base, OdooModule
from backend.app.services.embedding_service import get_embedding

# Config
GITHUB_TOKEN = "tu_token"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
TARGET_REPOS = ["server-tools", "web", "sale-workflow"]  # MVP: 3 repos
ODOO_VERSIONS = ["16.0", "17.0", "18.0"]

def get_repo_metadata(repo_name: str):
    """Obtener stars, issues, etc."""
    url = f"https://api.github.com/repos/OCA/{repo_name}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    data = response.json()
    return {
        "stars": data["stargazers_count"],
        "open_issues": data["open_issues_count"],
        "last_push": datetime.fromisoformat(data["pushed_at"].replace("Z", "+00:00"))
    }

def find_manifests(repo_name: str, branch: str):
    """Encontrar manifiestos en rama"""
    url = f"https://api.github.com/repos/OCA/{repo_name}/git/trees/{branch}"
    response = requests.get(url, headers=HEADERS, params={"recursive": "1"})
    response.raise_for_status()
    
    tree = response.json().get("tree", [])
    return [item["path"] for item in tree if item["path"].endswith("__manifest__.py")]

def fetch_file(repo_name: str, branch: str, path: str):
    """Descargar archivo"""
    url = f"https://raw.githubusercontent.com/OCA/{repo_name}/{branch}/{path}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def process_module(db: Session, repo_name: str, branch: str, manifest_path: str, repo_metadata: dict):
    """Procesar un módulo"""
    
    # Extraer nombre técnico
    folder = manifest_path.rsplit("/", 1)[0]
    technical_name = folder.split("/")[-1]
    
    print(f"📦 Procesando: {repo_name}/{branch}/{technical_name}")
    
    # Descargar manifiesto
    manifest_content = fetch_file(repo_name, branch, manifest_path)
    manifest = ast.literal_eval(manifest_content)
    
    # Intentar descargar README
    readme_content = ""
    try:
        readme_path = f"{folder}/README.md"
        readme_content = fetch_file(repo_name, branch, readme_path)
    except:
        print(f"  ⚠️  No README found")
    
    # Preparar texto para embedding
    embedding_text = " ".join([
        manifest.get("name", ""),
        manifest.get("summary", ""),
        manifest.get("description", ""),
        readme_content[:1000]  # Primeros 1000 chars del README
    ])
    
    # Generar embedding con Qwen3
    print(f"  🧠 Generando embedding...")
    embedding = get_embedding(embedding_text)
    
    # Verificar si existe
    existing = db.query(OdooModule).filter(
        OdooModule.technical_name == technical_name,
        OdooModule.version == branch
    ).first()
    
    if existing:
        print(f"  ♻️  Actualizando módulo existente")
        # Actualizar
        existing.name = manifest.get("name", technical_name)
        existing.depends = manifest.get("depends", [])
        existing.description = manifest.get("description", "")
        existing.summary = manifest.get("summary", "")
        existing.embedding = embedding
        existing.github_stars = repo_metadata["stars"]
        existing.github_issues_open = repo_metadata["open_issues"]
        existing.last_commit_date = repo_metadata["last_push"]
        existing.updated_at = datetime.utcnow()
    else:
        print(f"  ✨ Creando nuevo módulo")
        # Crear
        module = OdooModule(
            technical_name=technical_name,
            name=manifest.get("name", technical_name),
            version=branch,
            depends=manifest.get("depends", []),
            author=manifest.get("author", ""),
            license=manifest.get("license", ""),
            repo_name=repo_name,
            repo_url=f"https://github.com/OCA/{repo_name}",
            branch=branch,
            description=manifest.get("description", ""),
            summary=manifest.get("summary", ""),
            embedding=embedding,
            github_stars=repo_metadata["stars"],
            github_issues_open=repo_metadata["open_issues"],
            last_commit_date=repo_metadata["last_push"]
        )
        db.add(module)
    
    db.commit()
    print(f"  ✅ Completado")

def main():
    """Pipeline ETL principal"""
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        for repo_name in TARGET_REPOS:
            print(f"\n{'='*60}")
            print(f"📂 Repositorio: {repo_name}")
            print(f"{'='*60}")
            
            # Metadata del repo
            repo_metadata = get_repo_metadata(repo_name)
            print(f"⭐ Stars: {repo_metadata['stars']}")
            
            for version in ODOO_VERSIONS:
                print(f"\n  🔖 Versión: {version}")
                
                try:
                    manifests = find_manifests(repo_name, version)
                    print(f"  📦 Módulos encontrados: {len(manifests)}")
                    
                    for manifest_path in manifests:
                        try:
                            process_module(db, repo_name, version, manifest_path, repo_metadata)
                        except Exception as e:
                            print(f"  ❌ Error: {e}")
                            continue
                            
                except Exception as e:
                    print(f"  ❌ Error en versión {version}: {e}")
                    continue
        
        # Resumen
        total = db.query(OdooModule).count()
        print(f"\n{'='*60}")
        print(f"✅ ETL Completado!")
        print(f"📊 Total módulos indexados: {total}")
        print(f"{'='*60}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
```

#### 4.2 Servicio de Embeddings

```python
# backend/app/services/embedding_service.py
import openai
import os

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

EMBEDDING_MODEL = "qwen/qwen3-embedding-8b"  # O 4b

def get_embedding(text: str) -> list[float]:
    """
    Generar embedding usando Qwen3-Embedding.
    
    Args:
        text: Texto para generar embedding
        
    Returns:
        Vector de 4096 dimensiones (8B) o 2048 (4B)
    """
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generar embeddings para múltiples textos"""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]
```

### Semana 5: Búsqueda Híbrida

#### 5.1 Servicio de Búsqueda

```python
# backend/app/services/search_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models import OdooModule
from .embedding_service import get_embedding
from typing import List, Optional
from datetime import datetime, timedelta

class SearchService:
    def __init__(self, db: Session):
        self.db = db
    
    async def search(
        self,
        query: str,
        version: str,
        depends: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[dict]:
        """
        Búsqueda híbrida: SQL filtering + Vector similarity
        
        Paso 1: Filtrado determinista (SQL)
        Paso 2: Búsqueda semántica (Vector)
        Paso 3: Scoring de calidad
        Paso 4: Ordenar y retornar
        """
        
        # PASO 1: Filtrado determinista
        base_query = self.db.query(OdooModule).filter(
            OdooModule.version == version
        )
        
        # Filtrar por dependencias si se especifican
        if depends:
            for dep in depends:
                base_query = base_query.filter(
                    OdooModule.depends.contains([dep])
                )
        
        # Obtener IDs de candidatos
        candidates = base_query.all()
        candidate_ids = [m.id for m in candidates]
        
        if not candidate_ids:
            return []
        
        print(f"📊 Candidatos tras filtro SQL: {len(candidate_ids)}")
        
        # PASO 2: Búsqueda semántica
        query_embedding = get_embedding(query)
        
        # Búsqueda vectorial en candidatos
        # Usando pgvector cosine distance
        results = self.db.query(
            OdooModule,
            OdooModule.embedding.cosine_distance(query_embedding).label("distance")
        ).filter(
            OdooModule.id.in_(candidate_ids)
        ).order_by(
            "distance"
        ).limit(limit * 2).all()  # 2x para poder filtrar después
        
        print(f"🔍 Resultados tras búsqueda vectorial: {len(results)}")
        
        # PASO 3: Scoring y formateo
        formatted_results = []
        for module, distance in results:
            quality_score = self._calculate_quality_score(module)
            
            formatted_results.append({
                "id": module.id,
                "name": module.name,
                "technical_name": module.technical_name,
                "version": module.version,
                "description": module.description,
                "summary": module.summary,
                "repo_url": module.repo_url,
                "repo_name": module.repo_name,
                "depends": module.depends,
                "author": module.author,
                "license": module.license,
                "similarity_score": round(1 - distance, 3),  # 0-1
                "quality_score": quality_score,  # 0-100
                "github_stars": module.github_stars,
                "github_issues_open": module.github_issues_open,
                "last_commit_date": module.last_commit_date.isoformat() if module.last_commit_date else None
            })
        
        # PASO 4: Ordenar por score combinado y limitar
        formatted_results.sort(
            key=lambda x: (x["similarity_score"] * 0.7 + x["quality_score"]/100 * 0.3),
            reverse=True
        )
        
        return formatted_results[:limit]
    
    def _calculate_quality_score(self, module: OdooModule) -> float:
        """
        Calcular score de calidad (0-100)
        
        Basado en:
        - GitHub stars (40 puntos max)
        - Actividad reciente (40 puntos max)
        - Ratio de issues (20 puntos max)
        """
        score = 0.0
        
        # Stars (máximo 40 puntos)
        # 1 star = 4 puntos, cap en 40
        score += min(module.github_stars * 4, 40)
        
        # Actividad reciente (máximo 40 puntos)
        if module.last_commit_date:
            days_ago = (datetime.utcnow() - module.last_commit_date).days
            if days_ago < 30:
                score += 40
            elif days_ago < 90:
                score += 30
            elif days_ago < 180:
                score += 20
            elif days_ago < 365:
                score += 10
        
        # Issues (máximo 20 puntos)
        if module.github_issues_open < 5:
            score += 20
        elif module.github_issues_open < 15:
            score += 10
        elif module.github_issues_open < 30:
            score += 5
        
        return round(min(score, 100), 1)
```

#### 5.2 Schemas Pydantic

```python
# backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SearchRequest(BaseModel):
    query: str = Field(..., description="Descripción de funcionalidad buscada")
    version: str = Field(..., description="Versión de Odoo (16.0, 17.0, 18.0)")
    depends: Optional[List[str]] = Field(default=None, description="Dependencias requeridas")
    limit: int = Field(default=5, ge=1, le=20, description="Máximo de resultados")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "gestión de inventario y almacén",
                "version": "17.0",
                "depends": ["stock"],
                "limit": 5
            }
        }

class SearchResponse(BaseModel):
    id: int
    name: str
    technical_name: str
    version: str
    description: Optional[str]
    summary: Optional[str]
    repo_url: str
    repo_name: str
    depends: List[str]
    author: Optional[str]
    license: Optional[str]
    similarity_score: float = Field(..., description="Similitud semántica (0-1)")
    quality_score: float = Field(..., description="Score de calidad (0-100)")
    github_stars: int
    github_issues_open: int
    last_commit_date: Optional[str]
    
    class Config:
        from_attributes = True
```

#### 5.3 Testing

```python
# backend/tests/test_search.py
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_search_basic():
    response = client.post("/api/v1/search", json={
        "query": "gestión de inventario",
        "version": "17.0",
        "limit": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 3

def test_search_with_depends():
    response = client.post("/api/v1/search", json={
        "query": "ventas",
        "version": "17.0",
        "depends": ["sale"],
        "limit": 5
    })
    assert response.status_code == 200
    data = response.json()
    
    # Todos deben tener 'sale' en depends
    for module in data:
        assert "sale" in module["depends"]

def test_search_empty_version():
    response = client.post("/api/v1/search", json={
        "query": "test",
        "version": "99.0"
    })
    assert response.status_code == 200
    assert len(response.json()) == 0
```

---

## 🤖 FASE 1.5: Claude Skill

**Duración:** 1 semana (paralelo a Semana 5)  
**Objetivo:** Interfaz conversacional funcionando

### Claude Skill Setup

#### 1. Crear Proyecto en Claude

1. Ve a [claude.ai](https://claude.ai)
2. Crea nuevo proyecto: "AI-OdooFinder"
3. Añade archivos a Project Knowledge:
   - README.md
   - docs/TECHNICAL_GUIDE.md
   - PROJECT_STRUCTURE.md

#### 2. Configurar SKILL.md

```markdown
# AI-OdooFinder Skill

## Propósito
Ayudar a desarrolladores de Odoo a encontrar módulos compatibles usando búsqueda inteligente con IA.

## Herramienta Disponible

### search_odoo_modules

Busca módulos de Odoo en repositorios de OCA usando búsqueda híbrida (SQL + semántica).

**Endpoint:** `POST https://tu-api.render.com/api/v1/search`

**Parámetros:**
- `query` (string, requerido): Descripción de funcionalidad en lenguaje natural
  - Ejemplos: "gestión de inventario", "reportes de ventas", "integración WhatsApp"
- `version` (string, requerido): Versión de Odoo
  - Valores: "16.0", "17.0", "18.0"
- `depends` (array, opcional): Dependencias requeridas
  - Ejemplos: ["sale"], ["stock", "purchase"]
- `limit` (integer, opcional): Máximo resultados (default: 5)

**Request Example:**
```json
{
  "query": "gestión de suscripciones y pagos recurrentes",
  "version": "17.0",
  "depends": ["sale"],
  "limit": 5
}
```

**Response Example:**
```json
[
  {
    "name": "Sale Subscription",
    "technical_name": "sale_subscription",
    "version": "17.0",
    "description": "Manage recurring subscriptions...",
    "repo_url": "https://github.com/OCA/sale-workflow",
    "depends": ["sale", "account"],
    "similarity_score": 0.892,
    "quality_score": 85.5,
    "github_stars": 245,
    "last_commit_date": "2024-01-15T10:30:00"
  }
]
```

## Instrucciones de Uso

### 1. Interpretación de Consultas

Cuando un usuario pregunta sobre módulos de Odoo:

**Extraer versión:**
- Explícita: "para v17", "en Odoo 16", "versión 18"
- Si no se especifica, preguntar: "¿Para qué versión de Odoo? (16.0, 17.0 o 18.0)"

**Extraer funcionalidad:**
- Usuario: "módulo de inventario" → query: "gestión de inventario"
- Usuario: "algo para proyectos" → query: "gestión de proyectos"
- Usuario: "facturación electrónica" → query: "facturación electrónica"

**Extraer dependencias:**
- Explícitas: "que funcione con sale", "integrado con stock"
- Mapear a nombres técnicos: sale, account, stock, purchase, project, etc.

### 2. Llamada a la Herramienta

```
Usuario: "Necesito un módulo de inventario para Odoo 17"

Claude llama:
{
  "query": "gestión de inventario",
  "version": "17.0"
}

---

Usuario: "Busco algo para v16 que maneje pagos recurrentes con ventas"

Claude llama:
{
  "query": "pagos recurrentes suscripciones",
  "version": "16.0",
  "depends": ["sale"]
}
```

### 3. Presentación de Resultados

Formatea la respuesta de manera clara y útil:

```
He encontrado [N] módulos compatibles con Odoo [version]:

1. ⭐ [Nombre] ([quality_score]/100) ✅ Muy recomendado
   📦 Nombre técnico: [technical_name]
   🔗 Repositorio: [repo_url]
   📊 [github_stars] estrellas • Actualizado [last_commit_date]
   🔗 Dependencias: [depends]
   📝 [description resumida]
   
2. [Siguiente módulo...]
```

**Recomendaciones:**
- Si quality_score > 70: Añadir "✅ Muy recomendado"
- Si quality_score < 40: Añadir "⚠️ Poco mantenido, verificar antes de usar"
- Si similarity_score < 0.5: Mencionar "Relevancia media"

### 4. Casos Especiales

**Sin resultados:**
```
No encontré módulos que cumplan exactamente con:
- Versión: [version]
- Funcionalidad: [query]
- Dependencias: [depends]

Sugerencias:
1. Intenta con descripción más general
2. Verifica las dependencias
3. Considera otra versión de Odoo
```

**Versión no especificada:**
```
Para ayudarte mejor, ¿para qué versión de Odoo necesitas el módulo?
- 16.0 (Odoo 16)
- 17.0 (Odoo 17)
- 18.0 (Odoo 18)
```

## Ejemplos de Conversación

### Ejemplo 1: Búsqueda Simple
```
Usuario: Necesito un módulo para gestionar proyectos en Odoo 17

Claude: Te ayudo a buscar módulos de gestión de proyectos para Odoo 17.0

[Llama a search_odoo_modules]

He encontrado 5 módulos compatibles:

1. ⭐ Project (95/100) ✅ Muy recomendado
   📦 project
   🔗 https://github.com/odoo/odoo
   ...
```

### Ejemplo 2: Con Dependencias
```
Usuario: Busco algo para Odoo 16 que maneje suscripciones y trabaje con ventas

Claude: Perfecto, busco módulos de suscripciones para Odoo 16.0 que 
        dependan de 'sale'.

[Llama con depends=["sale"]]

He encontrado 3 módulos:
...
```

### Ejemplo 3: Sin Resultados
```
Usuario: Necesito integración con TikTok para Odoo 18

Claude: [Llama a search_odoo_modules]

No encontré módulos específicos de TikTok para Odoo 18.0.

Esto puede deberse a que es una integración muy específica que aún 
no existe en OCA.

Sugerencias:
1. Buscar "social media" de forma más general
2. Revisar Odoo App Store oficial
3. Considerar desarrollo personalizado
```

## Testing

Para probar la skill:

```bash
curl -X POST https://tu-api.com/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "reportes de ventas",
    "version": "17.0",
    "limit": 3
  }'
```

## Consideraciones

1. **Siempre valida la versión** - Es crítico en Odoo
2. **No inventes módulos** - Solo presenta resultados reales
3. **Sé honesto sobre limitaciones** - Si no hay resultados, dilo
4. **Contextualiza dependencias** - Explica por qué se requieren
5. **Prioriza calidad** - Destaca módulos con score alto
```

#### 3. Deploy API (Para que Claude pueda acceder)

**Configuración en Render.com:**
```bash
# 1. Crear cuenta en https://render.com
# 2. Conectar tu repositorio de GitHub
# 3. Crear Web Service con estos parámetros:

Build Command: pip install -r requirements.txt
Start Command: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT

Environment Variables:
  DATABASE_URL: [Tu Neon connection string]
  OPENROUTER_API_KEY: [Tu OpenRouter key]
  GITHUB_TOKEN: [Tu GitHub token]
```

**Render se encarga de:**
- ✅ Build automático en cada push
- ✅ SSL/HTTPS automático
- ✅ Health checks
- ✅ Logs centralizados

**Obtendrás URL pública:**
```
https://ai-odoofinder.onrender.com
```

**Alternativas a Render:**
- Railway.app (similar, un poco más caro)
- Fly.io (más control, más complejo)
- Vercel (solo para Python con limitaciones)

**¿Por qué Render + Neon y no solo Neon Data API?**

El Neon Data API es solo para operaciones CRUD básicas (GET/POST/PATCH/DELETE).
Nuestro caso requiere:
- ✅ Generar embeddings on-the-fly con Qwen3
- ✅ Búsqueda híbrida (SQL + vectorial)
- ✅ Scoring y ranking personalizado
- ✅ Lógica de negocio compleja

Por eso necesitamos FastAPI custom en Render conectándose a Neon.

#### 4. Probar Claude Skill

En Claude.ai, probar:
```
"Hola, necesito un módulo para Odoo 17 que gestione inventario y almacenes"
```

Claude debería:
1. Reconocer la intención
2. Llamar a tu API automáticamente
3. Formatear resultados bonitos
4. Permitir refinar búsqueda

---

## ✅ Checklist MVP Completado

- [ ] PostgreSQL + pgVector configurado
- [ ] Qwen3-Embedding funcionando
- [ ] API FastAPI deployada y accesible
- [ ] ETL procesa 100-200 módulos (3 repos OCA)
- [ ] Búsqueda híbrida retorna resultados relevantes
- [ ] Claude Skill configurada en claude.ai
- [ ] Tests básicos pasan
- [ ] Documentación actualizada
- [ ] Primera búsqueda end-to-end exitosa

---

## 🚀 FASE 2: Producción

**Duración:** 1-2 meses  
**Objetivo:** Sistema robusto con 500+ módulos

### Mes 1: Expansión

#### Objetivos:
1. **ETL completo de OCA**
   - Indexar TODOS los repos (~20-30 repos)
   - ~500-1000 módulos totales
   - Automatizar con GitHub Actions (cada 24h)

2. **Optimizaciones**
   - Caché con Redis (búsquedas frecuentes)
   - Índices optimizados en PostgreSQL
   - Rate limiting en API

3. **Scoring avanzado**
   - Considerar más factores
   - Pesos ajustados por testing
   - Feedback de usuarios

#### Tareas:

**1. ETL Automatizado**
```yaml
# .github/workflows/etl.yml
name: ETL Daily Update

on:
  schedule:
    - cron: '0 2 * * *'  # Cada día a las 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  etl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run ETL
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          GITHUB_TOKEN: ${{ secrets.GH_TOKEN }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_KEY }}
        run: python scripts/etl_oca_modules.py --all-repos
```

**2. Caché con Redis**
```python
# backend/app/services/cache_service.py
import redis
import json
from typing import Optional

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

def get_cached_search(query: str, version: str) -> Optional[list]:
    """Obtener búsqueda cacheada"""
    key = f"search:{version}:{query}"
    cached = redis_client.get(key)
    return json.loads(cached) if cached else None

def cache_search(query: str, version: str, results: list):
    """Cachear resultados"""
    key = f"search:{version}:{query}"
    redis_client.setex(
        key,
        3600,  # 1 hora
        json.dumps(results)
    )
```

**3. Análisis de Dependencias**
```python
# backend/app/services/dependency_service.py
class DependencyAnalyzer:
    def check_compatibility(self, module: OdooModule) -> dict:
        """
        Verificar que dependencias:
        1. Existen en la versión correcta
        2. No tienen conflictos
        3. Están disponibles
        """
        missing = []
        conflicts = []
        
        for dep in module.depends:
            dep_module = self.db.query(OdooModule).filter(
                OdooModule.technical_name == dep,
                OdooModule.version == module.version
            ).first()
            
            if not dep_module:
                missing.append(dep)
        
        return {
            "compatible": len(missing) == 0,
            "missing_dependencies": missing,
            "conflicts": conflicts,
            "installation_order": self._resolve_order(module)
        }
```

### Mes 2: Features Avanzadas

#### Objetivos:
1. **GitHub Webhooks** - Actualización automática
2. **Métricas** - Prometheus + Grafana
3. **CLI** (Opcional) - Para power users
4. **Documentación completa** - API + guías

---

## ⚠️ Riesgos y Mitigación

### Riesgos Técnicos:
- **Rate limits de GitHub API** → Usar token personal + caché
- **Costos de embeddings** → Monitorear uso, considerar Ollama local
- **Calidad de búsqueda** → A/B testing con diferentes modelos

### Riesgos de Proyecto:
- **Mantenimiento OCA** → ETL automatizado diario
- **Escalabilidad** → Plan de migración a infra pagada

---

## 📊 Métricas de Éxito

### MVP (Semana 6):
- ✅ 100-200 módulos indexados
- ✅ API responde en <500ms
- ✅ Claude Skill funcional
- ✅ 5 búsquedas de prueba exitosas
- ✅ 3 usuarios beta

### Beta (Semana 10):
- ✅ 500+ módulos indexados
- ✅ 20+ usuarios activos
- ✅ 50+ búsquedas/día
- ✅ <5% errores

### Producción (Semana 12):
- ✅ 1000+ módulos
- ✅ 100+ usuarios
- ✅ 200+ búsquedas/día
- ✅ <1% errores
- ✅ Documentación completa

---

## 💰 Presupuesto Estimado

### Costos Iniciales (Setup):
- Qwen3 embeddings (indexado inicial): $5-10 USD
- GitHub API: Gratis (5000 requests/hora)
- PostgreSQL: Gratis (Render free tier)
- Hosting API: Gratis (Render free tier)

### Costos Mensuales:
- Re-indexado (1x/día): ~$2 USD/mes
- Hosting: $0-7 USD/mes (Render)
- Database: $0-7 USD/mes (Render)
- OpenRouter (búsquedas): ~$5 USD/mes (100 búsquedas/día)

**Total MVP:** ~$20-30 USD inicial + $10-15 USD/mes

---

## 🎯 Próximos Pasos INMEDIATOS

### Esta Semana:
1. ✅ Subir repositorio a GitHub
2. ✅ Añadir docs a Project Knowledge en Claude
3. ✅ Crear issue para Fase 0

### Semana Próxima (Fase 0):
1. Setup entorno Python
2. Probar Qwen3-Embedding
3. Explorar GitHub API
4. Estimar costos reales
5. Decisión GO/NO-GO

---

## 📞 Soporte

### Recursos:
- **Qwen3-Embedding:** https://github.com/QwenLM/Qwen3-Embedding
- **OpenRouter:** https://openrouter.ai/docs
- **GitHub API:** https://docs.github.com/en/rest
- **FastAPI:** https://fastapi.tiangolo.com
- **pgVector:** https://github.com/pgvector/pgvector

### Comunidad:
- GitHub Issues: Para bugs y features
- Discord: [Crear server si hay interés]
- Documentación: docs/TECHNICAL_GUIDE.md

---

## 📋 Apéndice: Decisiones de Arquitectura

### ¿Por qué Qwen3 en lugar de OpenAI?
- Open source y más económico
- Rendimiento comparable
- Flexibilidad (local u OpenRouter)

### ¿Por qué Claude Skill y no UI web?
- Desarrollo más rápido
- UX conversacional superior
- Cero frontend que mantener

---

<div align="center">

**🚀 ¡Listo para comenzar! 🚀**

**Siguiente paso:** Abrir nuevo chat en Claude proyecto y decir:  
*"Hola Claude, vamos a empezar con la Fase 0 de AI-OdooFinder"*

</div>
