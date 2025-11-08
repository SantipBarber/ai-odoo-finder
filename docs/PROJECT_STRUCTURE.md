# 📁 Estructura del Proyecto AI-OdooFinder

```
ai-odoofinder/
│
├── 📄 README.md                          # README principal (comercial)
├── 📄 LICENSE                            # Licencia MIT
├── 📄 CONTRIBUTING.md                    # Guía de contribución
├── 📄 .gitignore                         # Archivos ignorados por git
├── 📄 .env.example                       # Template de variables de entorno
├── 📄 requirements.txt                   # Dependencias Python (producción)
├── 📄 requirements-dev.txt               # Dependencias de desarrollo
├── 📄 docker-compose.yml                 # Configuración Docker
├── 📄 Dockerfile                         # Imagen Docker del backend
├── 📄 pyproject.toml                     # Configuración del proyecto Python
│
├── 📂 docs/                              # 📚 Documentación
│   ├── TECHNICAL_GUIDE.md                # Guía técnica completa
│   ├── API.md                            # Documentación de API
│   ├── ARCHITECTURE.md                   # Diagrama de arquitectura
│   ├── DEPLOYMENT.md                     # Guía de deployment
│   └── CHANGELOG.md                      # Registro de cambios
│
├── 📂 backend/                           # 🐍 Backend FastAPI
│   ├── 📄 __init__.py
│   │
│   ├── 📂 app/                           # Aplicación principal
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py                    # Entry point de FastAPI
│   │   ├── 📄 config.py                  # Configuración general
│   │   ├── 📄 database.py                # Conexión a base de datos
│   │   ├── 📄 models.py                  # Modelos SQLAlchemy
│   │   ├── 📄 schemas.py                 # Schemas Pydantic
│   │   │
│   │   ├── 📂 api/                       # 🔌 Endpoints de API
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 deps.py                # Dependencias compartidas
│   │   │   └── 📂 endpoints/
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 search.py          # Endpoint de búsqueda
│   │   │       ├── 📄 modules.py         # CRUD de módulos
│   │   │       ├── 📄 health.py          # Health checks
│   │   │       └── 📄 webhooks.py        # GitHub webhooks
│   │   │
│   │   ├── 📂 services/                  # 🔧 Lógica de negocio
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 search_service.py      # Servicio de búsqueda híbrida
│   │   │   ├── 📄 embedding_service.py   # Generación de embeddings
│   │   │   ├── 📄 github_service.py      # Interacción con GitHub API
│   │   │   ├── 📄 scoring_service.py     # Cálculo de scores de calidad
│   │   │   └── 📄 cache_service.py       # Gestión de caché
│   │   │
│   │   ├── 📂 core/                      # ⚙️ Funcionalidad core
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 security.py            # Autenticación/autorización
│   │   │   ├── 📄 logging.py             # Configuración de logging
│   │   │   └── 📄 exceptions.py          # Excepciones personalizadas
│   │   │
│   │   └── 📂 utils/                     # 🛠️ Utilidades
│   │       ├── 📄 __init__.py
│   │       ├── 📄 validators.py          # Validadores
│   │       ├── 📄 parsers.py             # Parsers (manifests, etc)
│   │       └── 📄 helpers.py             # Funciones helper
│   │
│   └── 📂 tests/                         # 🧪 Tests
│       ├── 📄 __init__.py
│       ├── 📄 conftest.py                # Configuración pytest
│       ├── 📂 unit/                      # Tests unitarios
│       │   ├── 📄 test_search_service.py
│       │   ├── 📄 test_embedding_service.py
│       │   └── 📄 test_scoring.py
│       ├── 📂 integration/               # Tests de integración
│       │   ├── 📄 test_api_search.py
│       │   └── 📄 test_github_api.py
│       └── 📂 e2e/                       # Tests end-to-end
│           └── 📄 test_full_flow.py
│
├── 📂 scripts/                           # 🔄 Scripts de utilidad
│   ├── 📄 etl_oca_modules.py             # ETL principal
│   ├── 📄 update_embeddings.py           # Actualizar embeddings
│   ├── 📄 setup_database.py              # Setup inicial de DB
│   ├── 📄 migrate_data.py                # Migraciones de datos
│   └── 📄 benchmark.py                   # Benchmarking
│
├── 📂 claude-skill/                      # 🤖 Claude Skill
│   ├── 📄 SKILL.md                       # Definición de la skill
│   ├── 📄 examples.md                    # Ejemplos de uso
│   └── 📄 prompts.md                     # Prompts optimizados
│
├── 📂 frontend/                          # 🎨 Frontend (Opcional - Fase 2)
│   ├── 📄 package.json
│   ├── 📄 tsconfig.json
│   ├── 📄 next.config.js
│   │
│   ├── 📂 src/
│   │   ├── 📂 app/                       # Next.js App Router
│   │   │   ├── 📄 layout.tsx
│   │   │   ├── 📄 page.tsx
│   │   │   └── 📂 search/
│   │   │       └── 📄 page.tsx
│   │   │
│   │   ├── 📂 components/                # Componentes React
│   │   │   ├── 📄 SearchBar.tsx
│   │   │   ├── 📄 ModuleCard.tsx
│   │   │   ├── 📄 FilterPanel.tsx
│   │   │   └── 📄 ResultsList.tsx
│   │   │
│   │   ├── 📂 lib/                       # Utilidades frontend
│   │   │   ├── 📄 api.ts
│   │   │   └── 📄 utils.ts
│   │   │
│   │   └── 📂 styles/                    # Estilos
│   │       └── 📄 globals.css
│   │
│   └── 📂 public/                        # Assets estáticos
│       ├── 📄 logo.svg
│       └── 📄 favicon.ico
│
├── 📂 alembic/                           # 🔄 Migraciones de DB
│   ├── 📄 env.py
│   ├── 📄 script.py.mako
│   └── 📂 versions/
│       └── 📄 001_initial_schema.py
│
├── 📂 .github/                           # ⚙️ GitHub Actions
│   ├── 📂 workflows/
│   │   ├── 📄 ci.yml                     # CI/CD pipeline
│   │   ├── 📄 tests.yml                  # Tests automatizados
│   │   ├── 📄 deploy.yml                 # Deployment
│   │   └── 📄 etl.yml                    # ETL scheduler
│   │
│   ├── 📂 ISSUE_TEMPLATE/
│   │   ├── 📄 bug_report.md
│   │   └── 📄 feature_request.md
│   │
│   └── 📄 pull_request_template.md
│
├── 📂 logs/                              # 📊 Logs (git ignored)
│   └── 📄 .gitkeep
│
└── 📂 data/                              # 💾 Data (git ignored)
    ├── 📂 cache/
    └── 📂 temp/
```

---

## 📋 Descripción de Directorios Principales

### `/backend`
Contiene toda la lógica del servidor FastAPI, servicios, modelos y tests.

**Archivos clave:**
- `main.py`: Punto de entrada de la aplicación
- `models.py`: Definición de tablas de base de datos
- `services/search_service.py`: Lógica de búsqueda híbrida

### `/scripts`
Scripts de utilidad para ETL, mantenimiento y operaciones batch.

**Archivos clave:**
- `etl_oca_modules.py`: Pipeline de ingesta de datos de OCA

### `/claude-skill`
Definición de la Claude Skill para integración con Anthropic.

**Archivos clave:**
- `SKILL.md`: Instrucciones para Claude sobre cómo usar la herramienta

### `/docs`
Documentación técnica completa del proyecto.

**Archivos clave:**
- `TECHNICAL_GUIDE.md`: Guía de implementación detallada
- `API.md`: Referencia de endpoints

### `/frontend` (Opcional - Fase 2)
Aplicación web Next.js para interfaz de usuario visual.

### `/.github`
Configuración de GitHub Actions para CI/CD, templates de issues y PRs.

---

## 🔑 Archivos de Configuración Importantes

| Archivo | Propósito |
|---------|-----------|
| `.env.example` | Template de variables de entorno |
| `requirements.txt` | Dependencias Python de producción |
| `requirements-dev.txt` | Dependencias de desarrollo (pytest, black, etc) |
| `docker-compose.yml` | Orquestación de servicios Docker |
| `pyproject.toml` | Configuración de herramientas Python (black, mypy) |
| `alembic.ini` | Configuración de Alembic para migraciones |

---

## 🚀 Archivos que Necesitas Crear al Inicio

Para MVP (Fase 1), estos son los archivos mínimos necesarios:

```bash
# Configuración
✅ .env (copia de .env.example con tus valores)
✅ .gitignore

# Backend básico
✅ backend/app/main.py
✅ backend/app/database.py
✅ backend/app/models.py
✅ backend/app/api/endpoints/search.py
✅ backend/app/services/search_service.py
✅ backend/app/services/embedding_service.py

# Scripts
✅ scripts/etl_oca_modules.py

# Tests
✅ backend/tests/test_search_api.py

# Documentación
✅ README.md
✅ docs/TECHNICAL_GUIDE.md
```

---

## 📦 Archivos Generados (No en Git)

Estos archivos se generan automáticamente y no deben estar en git:

```
__pycache__/
*.pyc
.env
logs/
data/cache/
venv/
node_modules/
dist/
build/
.pytest_cache/
```

---

## 🎨 Convenciones de Nombres

- **Archivos Python**: `snake_case.py`
- **Clases**: `PascalCase`
- **Funciones/Variables**: `snake_case`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Componentes React**: `PascalCase.tsx`
- **Archivos de config**: `kebab-case.yml`

---

<div align="center">

**Estructura diseñada para escalabilidad y mantenibilidad** 🏗️

</div>
