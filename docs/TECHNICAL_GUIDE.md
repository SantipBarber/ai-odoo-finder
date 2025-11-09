# 🔍 AI-OdooFinder - Guía Técnica Completa

> **Sistema de búsqueda inteligente de módulos Odoo impulsado por IA**

Documentación técnica detallada para desarrolladores que desean comprender, implementar o contribuir al proyecto AI-OdooFinder.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Odoo](https://img.shields.io/badge/Odoo-16.0%20|%2017.0%20|%2018.0-714B67)](https://www.odoo.com)

---

## 📋 Tabla de Contenidos

- [El Problema](#-el-problema)
- [La Solución](#-la-solución)
- [Arquitectura](#-arquitectura)
- [Roadmap de Implementación](#-roadmap-de-implementación)
  - [Fase 0: Setup y Validación](#fase-0-setup-y-validación-1-2-semanas)
  - [Fase 1: MVP Funcional](#fase-1-mvp-funcional-2-3-semanas)
  - [Fase 2: Producción](#fase-2-producción-1-2-meses)
- [Stack Tecnológico](#-stack-tecnológico)
- [Instalación Rápida](#-instalación-rápida)
- [Uso](#-uso)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## 🎯 El Problema

Los desarrolladores de Odoo enfrentan varios desafíos al buscar módulos existentes:

1. **Versionado Estricto**: Un módulo de Odoo 16.0 no funciona en 17.0
2. **Fragmentación de Fuentes**: OCA, GitHub público, Odoo Apps Store
3. **Dependencias Complejas**: No es obvio qué módulos necesitas instalar primero
4. **Calidad Variable**: No todos los módulos están bien mantenidos
5. **Búsqueda Ineficiente**: Las búsquedas actuales son puramente textuales

**Resultado**: Los desarrolladores pierden tiempo desarrollando funcionalidades que ya existen.

---

## 💡 La Solución

Un **Asistente de IA Híbrido** que combina:

- 🔍 **Búsqueda Semántica** (RAG): Entiende "gestión de pagos recurrentes" = "subscripciones"
- 🎯 **Filtrado Determinista**: Garantiza compatibilidad con versión y dependencias
- 📊 **Sistema de Scoring**: Recomienda módulos bien mantenidos
- 🤖 **Interfaz Conversacional**: Claude Skill para lenguaje natural

### Ejemplo de Uso

```
Desarrollador: "Necesito un módulo para v17 que gestione pagos de 
               suscripciones y que se integre con 'sale'"

AI Assistant:  He encontrado 3 módulos compatibles con Odoo 17.0:

               1. ⭐ sale_subscription (OCA/sale-workflow)
                  - Stars: 245 | Last update: 2 días
                  - Dependencias: sale, account, payment
                  
               2. contract (OCA/contract)
                  - Stars: 189 | Last update: 1 semana
                  - Dependencias: sale, account
                  
               3. subscription_payment (OCA/...)
                  ...
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO (Desarrollador)                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              CLAUDE SKILL (Frontend Conversacional)          │
│  - Procesamiento de Lenguaje Natural                        │
│  - Orquestación de consultas                                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND (Python)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Recibe: query + version + depends                │   │
│  │  2. Filtrado SQL: WHERE version='17.0' AND ...       │   │
│  │  3. Búsqueda Vectorial: similarity(query, embeddings)│   │
│  │  4. Scoring: calidad + mantenimiento                 │   │
│  │  5. Retorna: Top 5 módulos ordenados                 │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│  PostgreSQL + pgVector    │  │    GitHub API            │
│  ┌─────────────────────┐ │  │  - Repos OCA             │
│  │ Tabla: modules      │ │  │  - Metadata en tiempo    │
│  │ - id                │ │  │    real (stars, issues)  │
│  │ - name              │ │  └──────────────────────────┘
│  │ - version           │ │
│  │ - depends (array)   │ │
│  │ - repo_url          │ │
│  │ - description       │ │
│  │ - embedding (vector)│ │
│  └─────────────────────┘ │
└───────────────────────────┘
```

### Flujo de Datos

**1. Ingesta (ETL - ejecuta cada 24h):**
```python
GitHub API → Parse __manifest__.py → PostgreSQL (metadata)
                ↓
           README.md → Generate embeddings → pgVector
```

**2. Consulta (Runtime):**
```python
User Query → Claude Skill → Backend API
    ↓
    ├─→ SQL Filter (version, depends)
    ├─→ Vector Search (semantic similarity)
    ├─→ Score & Rank
    └─→ Return Results → Claude formats response
```

---

## 🚀 Roadmap de Implementación

### **Fase 0: Setup y Validación (1-2 semanas)**

**Objetivo**: Verificar viabilidad técnica y configurar entorno.

#### Tareas

- [ ] **Configuración de Entorno**
  ```bash
  # Crear repositorio
  git init ai-odoofinder
  cd ai-odoofinder
  
  # Estructura inicial
  mkdir -p backend/{app,tests,scripts}
  mkdir -p claude-skill
  mkdir -p docs
  
  # Python virtual environment
  python3.10 -m venv venv
  source venv/bin/activate
  ```

- [ ] **Explorar GitHub API de OCA**
  ```python
  # scripts/explore_oca.py
  import requests
  
  # Obtener repos de OCA
  response = requests.get(
      "https://api.github.com/orgs/OCA/repos",
      headers={"Authorization": "token YOUR_GITHUB_TOKEN"}
  )
  
  # Listar ramas de un repo
  repo = "server-tools"
  response = requests.get(
      f"https://api.github.com/repos/OCA/{repo}/branches"
  )
  
  # Encontrar manifiestos en una rama
  response = requests.get(
      f"https://api.github.com/repos/OCA/{repo}/git/trees/16.0?recursive=1"
  )
  manifests = [f for f in response.json()["tree"] 
               if f["path"].endswith("__manifest__.py")]
  ```

- [ ] **Probar Parsing de Manifiestos**
  ```python
  # scripts/parse_manifest.py
  import ast
  
  # Descargar y parsear un __manifest__.py
  manifest_url = "https://raw.githubusercontent.com/OCA/server-tools/16.0/module_name/__manifest__.py"
  content = requests.get(manifest_url).text
  
  # Parse del diccionario Python
  manifest_dict = ast.literal_eval(content)
  print(manifest_dict['name'])
  print(manifest_dict['depends'])
  ```

- [ ] **Experimentar con Embeddings**
  ```python
  # scripts/test_embeddings.py
  from openai import OpenAI
  
  client = OpenAI()
  
  text = "Módulo para gestionar pagos de suscripciones mensuales"
  response = client.embeddings.create(
      model="text-embedding-3-small",
      input=text
  )
  
  embedding = response.data[0].embedding  # Vector de 1536 dimensiones
  ```

#### Deliverables

- ✅ Script que lista 10 repos de OCA
- ✅ Script que parsea 5 manifiestos correctamente
- ✅ Prueba de concepto de embeddings
- ✅ Estimación de costos (API calls, embeddings)

#### Decisiones Clave

- **¿Usar OpenAI o Anthropic para embeddings?**
  - OpenAI: `text-embedding-3-small` ($0.02/1M tokens) ✅ Recomendado para MVP
  - Anthropic: No tiene API de embeddings nativa

- **¿Qué base de datos?**
  - SQLite: Solo para prototipo local
  - PostgreSQL + pgVector: ✅ Recomendado (escalable y gratis en Render)

---

### **Fase 1: MVP Funcional (2-3 semanas)**

**Objetivo**: Sistema end-to-end funcionando con 100-200 módulos de OCA.

#### 1.1 Backend API (Semana 1)

**Estructura del Proyecto:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # DB connection
│   ├── services/
│   │   ├── github_service.py
│   │   ├── search_service.py
│   │   └── embedding_service.py
│   └── api/
│       └── endpoints/
│           └── search.py
├── tests/
├── requirements.txt
└── .env.example
```

**requirements.txt:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pgvector==0.2.3
pydantic==2.5.0
pydantic-settings==2.1.0
openai==1.3.7
httpx==0.25.1
python-dotenv==1.0.0
```

**models.py:**
```python
from sqlalchemy import Column, Integer, String, ARRAY, DateTime, Text
from pgvector.sqlalchemy import Vector
from .database import Base

class OdooModule(Base):
    __tablename__ = "odoo_modules"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    technical_name = Column(String, nullable=False, unique=True)
    version = Column(String, nullable=False, index=True)
    depends = Column(ARRAY(String), nullable=False)
    author = Column(String)
    license = Column(String)
    repo_url = Column(String, nullable=False)
    repo_name = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    description = Column(Text)
    summary = Column(Text)
    
    # Metadata para scoring
    github_stars = Column(Integer, default=0)
    github_issues_open = Column(Integer, default=0)
    last_commit_date = Column(DateTime)
    
    # Vector embedding (1536 dimensiones para text-embedding-3-small)
    embedding = Column(Vector(1536))
    
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

**main.py:**
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import search

app = FastAPI(
    title="AI-OdooFinder API",
    description="API para búsqueda inteligente de módulos de Odoo impulsada por IA",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "AI-OdooFinder API - AI-powered Odoo module discovery",
        "docs": "/docs",
        "version": "0.1.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**endpoints/search.py:**
```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...database import get_db
from ...schemas import ModuleSearchRequest, ModuleSearchResponse
from ...services.search_service import SearchService

router = APIRouter(tags=["search"])

@router.post("/search", response_model=List[ModuleSearchResponse])
async def search_modules(
    request: ModuleSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Buscar módulos de Odoo por funcionalidad, versión y dependencias.
    
    Ejemplo:
    {
        "query": "gestión de pagos de suscripciones",
        "version": "17.0",
        "depends": ["sale"],
        "limit": 5
    }
    """
    search_service = SearchService(db)
    results = await search_service.search(
        query=request.query,
        version=request.version,
        depends=request.depends,
        limit=request.limit
    )
    return results
```

**services/search_service.py:**
```python
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models import OdooModule
from .embedding_service import EmbeddingService
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
    
    async def search(
        self,
        query: str,
        version: str,
        depends: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[dict]:
        """
        Búsqueda híbrida: SQL filtering + Vector similarity
        """
        
        # Paso 1: Filtrado determinista por versión
        base_query = self.db.query(OdooModule).filter(
            OdooModule.version == version
        )
        
        # Paso 2: Filtrado por dependencias (si se especifican)
        if depends:
            # Buscar módulos que contengan TODAS las dependencias especificadas
            for dep in depends:
                base_query = base_query.filter(
                    OdooModule.depends.contains([dep])
                )
        
        candidate_ids = [m.id for m in base_query.all()]
        
        if not candidate_ids:
            logger.warning(f"No candidates found for version={version}, depends={depends}")
            return []
        
        # Paso 3: Búsqueda semántica en los candidatos
        query_embedding = await self.embedding_service.get_embedding(query)
        
        # Búsqueda vectorial usando pgvector
        results = self.db.query(
            OdooModule,
            OdooModule.embedding.cosine_distance(query_embedding).label("distance")
        ).filter(
            OdooModule.id.in_(candidate_ids)
        ).order_by(
            "distance"
        ).limit(limit).all()
        
        # Paso 4: Formatear resultados con scoring
        formatted_results = []
        for module, distance in results:
            score = self._calculate_quality_score(module)
            formatted_results.append({
                "id": module.id,
                "name": module.name,
                "technical_name": module.technical_name,
                "version": module.version,
                "description": module.description,
                "repo_url": module.repo_url,
                "depends": module.depends,
                "similarity_score": round(1 - distance, 3),
                "quality_score": score,
                "github_stars": module.github_stars,
                "last_commit_date": module.last_commit_date.isoformat() if module.last_commit_date else None
            })
        
        return formatted_results
    
    def _calculate_quality_score(self, module: OdooModule) -> float:
        """
        Calcular score de calidad (0-100) basado en:
        - GitHub stars
        - Actividad reciente
        - Ratio de issues
        """
        from datetime import datetime, timedelta
        
        score = 0.0
        
        # Stars (máximo 40 puntos)
        score += min(module.github_stars / 10, 40)
        
        # Actividad reciente (máximo 40 puntos)
        if module.last_commit_date:
            days_since_commit = (datetime.now() - module.last_commit_date).days
            if days_since_commit < 30:
                score += 40
            elif days_since_commit < 90:
                score += 30
            elif days_since_commit < 180:
                score += 20
            elif days_since_commit < 365:
                score += 10
        
        # Issues ratio (máximo 20 puntos)
        if module.github_issues_open < 5:
            score += 20
        elif module.github_issues_open < 15:
            score += 10
        
        return round(min(score, 100), 1)
```

#### 1.2 Pipeline de Ingesta (Semana 1-2)

**scripts/etl_oca_modules.py:**
```python
import requests
import ast
from datetime import datetime
from sqlalchemy.orm import Session
from openai import OpenAI
from app.database import SessionLocal, engine
from app.models import Base, OdooModule
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
GITHUB_TOKEN = "tu_token_aqui"
OCA_ORG = "OCA"
TARGET_REPOS = ["server-tools", "web", "sale-workflow"]  # MVP: solo 3 repos
ODOO_VERSIONS = ["16.0", "17.0", "18.0"]

openai_client = OpenAI()

def get_oca_repositories():
    """Obtener lista de repositorios de OCA"""
    url = f"https://api.github.com/orgs/{OCA_ORG}/repos"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    all_repos = []
    page = 1
    
    while True:
        response = requests.get(url, headers=headers, params={"page": page, "per_page": 100})
        response.raise_for_status()
        repos = response.json()
        
        if not repos:
            break
            
        all_repos.extend([r["name"] for r in repos])
        page += 1
    
    return all_repos

def get_repo_branches(repo_name: str):
    """Obtener ramas de un repositorio"""
    url = f"https://api.github.com/repos/{OCA_ORG}/{repo_name}/branches"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    branches = [b["name"] for b in response.json()]
    return [b for b in branches if b in ODOO_VERSIONS]

def find_manifests_in_branch(repo_name: str, branch: str):
    """Encontrar todos los __manifest__.py en una rama"""
    url = f"https://api.github.com/repos/{OCA_ORG}/{repo_name}/git/trees/{branch}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers, params={"recursive": "1"})
    response.raise_for_status()
    
    tree = response.json().get("tree", [])
    manifests = [
        item["path"] for item in tree 
        if item["path"].endswith("__manifest__.py")
    ]
    return manifests

def fetch_file_content(repo_name: str, branch: str, file_path: str):
    """Obtener contenido de un archivo"""
    url = f"https://raw.githubusercontent.com/{OCA_ORG}/{repo_name}/{branch}/{file_path}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_manifest(content: str):
    """Parsear el contenido de __manifest__.py"""
    try:
        # Usar ast.literal_eval para evaluar el diccionario de manera segura
        manifest_dict = ast.literal_eval(content)
        return manifest_dict
    except Exception as e:
        logger.error(f"Error parsing manifest: {e}")
        return None

def get_embedding(text: str):
    """Generar embedding usando OpenAI"""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def get_repo_metadata(repo_name: str):
    """Obtener metadata del repositorio (stars, issues, etc.)"""
    url = f"https://api.github.com/repos/{OCA_ORG}/{repo_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    return {
        "stars": data["stargazers_count"],
        "open_issues": data["open_issues_count"],
        "last_push": datetime.fromisoformat(data["pushed_at"].replace("Z", "+00:00"))
    }

def process_module(db: Session, repo_name: str, branch: str, manifest_path: str, repo_metadata: dict):
    """Procesar un módulo individual"""
    
    # Obtener el nombre técnico del módulo (nombre de la carpeta)
    module_folder = manifest_path.rsplit("/", 1)[0]
    technical_name = module_folder.split("/")[-1]
    
    logger.info(f"Processing: {repo_name}/{branch}/{technical_name}")
    
    # Descargar __manifest__.py
    manifest_content = fetch_file_content(repo_name, branch, manifest_path)
    manifest = parse_manifest(manifest_content)
    
    if not manifest:
        logger.warning(f"Skipping {technical_name}: invalid manifest")
        return
    
    # Intentar descargar README.md
    readme_content = ""
    readme_path = f"{module_folder}/README.md"
    try:
        readme_content = fetch_file_content(repo_name, branch, readme_path)
    except:
        logger.warning(f"No README found for {technical_name}")
    
    # Preparar texto para embedding
    embedding_text = f"{manifest.get('name', '')} {manifest.get('summary', '')} {manifest.get('description', '')} {readme_content[:1000]}"
    
    # Generar embedding
    embedding = get_embedding(embedding_text)
    
    # Verificar si el módulo ya existe
    existing = db.query(OdooModule).filter(
        OdooModule.technical_name == technical_name,
        OdooModule.version == branch
    ).first()
    
    if existing:
        logger.info(f"Module {technical_name} v{branch} already exists, updating...")
        # Actualizar
        existing.name = manifest.get("name", technical_name)
        existing.depends = manifest.get("depends", [])
        existing.description = manifest.get("description", "")
        existing.summary = manifest.get("summary", "")
        existing.embedding = embedding
        existing.github_stars = repo_metadata["stars"]
        existing.github_issues_open = repo_metadata["open_issues"]
        existing.last_commit_date = repo_metadata["last_push"]
        existing.updated_at = datetime.now()
    else:
        # Crear nuevo
        module = OdooModule(
            name=manifest.get("name", technical_name),
            technical_name=technical_name,
            version=branch,
            depends=manifest.get("depends", []),
            author=manifest.get("author", ""),
            license=manifest.get("license", ""),
            repo_url=f"https://github.com/{OCA_ORG}/{repo_name}",
            repo_name=repo_name,
            branch=branch,
            description=manifest.get("description", ""),
            summary=manifest.get("summary", ""),
            embedding=embedding,
            github_stars=repo_metadata["stars"],
            github_issues_open=repo_metadata["open_issues"],
            last_commit_date=repo_metadata["last_push"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(module)
    
    db.commit()
    logger.info(f"✓ Processed: {technical_name}")

def main():
    """Pipeline principal de ingesta"""
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        for repo_name in TARGET_REPOS:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing repository: {repo_name}")
            logger.info(f"{'='*60}")
            
            # Obtener metadata del repo
            repo_metadata = get_repo_metadata(repo_name)
            
            # Obtener ramas compatibles
            branches = get_repo_branches(repo_name)
            logger.info(f"Found branches: {branches}")
            
            for branch in branches:
                logger.info(f"\nProcessing branch: {branch}")
                
                # Encontrar manifiestos
                manifests = find_manifests_in_branch(repo_name, branch)
                logger.info(f"Found {len(manifests)} modules")
                
                # Procesar cada módulo
                for manifest_path in manifests:
                    try:
                        process_module(db, repo_name, branch, manifest_path, repo_metadata)
                    except Exception as e:
                        logger.error(f"Error processing {manifest_path}: {e}")
                        continue
        
        logger.info("\n✓ ETL completed successfully!")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
```

**Ejecutar el ETL:**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export OPENAI_API_KEY="tu_api_key"
export GITHUB_TOKEN="tu_github_token"
export DATABASE_URL="postgresql://user:pass@localhost/odoo_finder"

# Ejecutar ETL
python scripts/etl_oca_modules.py
```

#### 1.3 Claude Skill (Semana 2-3)

**claude-skill/SKILL.md:**
```markdown
# AI-OdooFinder Skill

## Propósito
Esta skill permite a Claude ayudar a desarrolladores de Odoo a encontrar módulos existentes que cumplan con sus necesidades, filtrando por versión y dependencias usando AI-OdooFinder.

## Herramientas Disponibles

### search_odoo_modules

Busca módulos de Odoo en repositorios de OCA (Odoo Community Association).

**Parámetros:**
- `query` (string, requerido): Descripción de la funcionalidad deseada en lenguaje natural
  - Ejemplos: "gestión de pagos recurrentes", "reportes de inventario", "integración con WhatsApp"
- `version` (string, requerido): Versión de Odoo
  - Valores válidos: "16.0", "17.0", "18.0"
- `depends` (array de strings, opcional): Lista de módulos de los que debe depender
  - Ejemplos: ["sale"], ["account", "sale"], ["stock"]
- `limit` (integer, opcional): Número máximo de resultados (default: 5, max: 10)

**Endpoint:**
```
POST https://tu-api.com/api/v1/search
Content-Type: application/json

{
  "query": "gestión de suscripciones",
  "version": "17.0",
  "depends": ["sale"],
  "limit": 5
}
```

**Respuesta:**
```json
[
  {
    "name": "Sale Subscription",
    "technical_name": "sale_subscription",
    "version": "17.0",
    "description": "Gestión completa de suscripciones...",
    "repo_url": "https://github.com/OCA/sale-workflow",
    "depends": ["sale", "account"],
    "similarity_score": 0.892,
    "quality_score": 85.5,
    "github_stars": 245,
    "last_commit_date": "2024-01-15"
  }
]
```

## Instrucciones de Uso

### 1. Interpretación de Consultas

Cuando un usuario pregunta sobre módulos de Odoo, identifica:

**Versión:**
- Explícita: "para v17", "en Odoo 16", "versión 18"
- Si no se especifica, pregunta: "¿Para qué versión de Odoo necesitas el módulo?"

**Funcionalidad:**
- Extrae la descripción en lenguaje natural
- Ejemplos:
  - "módulo de pagos" → query: "gestión de pagos"
  - "algo para manejar proyectos" → query: "gestión de proyectos"
  - "reportes de ventas avanzados" → query: "reportes ventas avanzados"

**Dependencias:**
- Explícitas: "que funcione con sale", "integrado con accounting"
- Mapea a nombres técnicos: sale, account, stock, purchase, etc.

### 2. Llamada a la Herramienta

```python
# Ejemplo 1: Consulta simple
Usuario: "Necesito un módulo de inventario para Odoo 17"

Claude llama:
search_odoo_modules(
    query="gestión de inventario",
    version="17.0"
)

# Ejemplo 2: Con dependencias
Usuario: "Busco algo para v16 que maneje pagos recurrentes y se integre con ventas"

Claude llama:
search_odoo_modules(
    query="pagos recurrentes suscripciones",
    version="16.0",
    depends=["sale"]
)
```

### 3. Presentación de Resultados

Formatea la respuesta de manera amigable:

```
He encontrado [N] módulos compatibles con Odoo [version]:

1. ⭐ [Nombre del Módulo] ([quality_score]/100)
   📦 Nombre técnico: [technical_name]
   🔗 Repositorio: [repo_url]
   📊 Popularidad: [github_stars] estrellas
   🔄 Última actualización: [last_commit_date]
   📝 Descripción: [descripción resumida en 1-2 líneas]
   🔗 Dependencias: [lista de depends]
   
2. [Siguiente módulo...]
```

**Recomendaciones adicionales:**
- Si quality_score > 70: Añadir "✅ Muy recomendado"
- Si quality_score < 40: Añadir "⚠️ Módulo poco mantenido, usar con precaución"
- Si similarity_score < 0.5: Mencionar "Relevancia media, verifica si cumple tus necesidades"

### 4. Manejo de Casos Especiales

**Sin resultados:**
```
No encontré módulos que cumplan exactamente con tus criterios:
- Versión: [version]
- Funcionalidad: [query]
- Dependencias: [depends]

Sugerencias:
1. Intenta con una descripción más general
2. Verifica si las dependencias son correctas
3. Considera otra versión de Odoo
```

**Versión no especificada:**
```
Para ayudarte mejor, necesito saber: ¿Para qué versión de Odoo necesitas 
el módulo? (16.0, 17.0 o 18.0)
```

**Dependencias incorrectas:**
Si el usuario menciona módulos que no existen, sugiere alternativas comunes:
- "ventas" → "sale"
- "contabilidad" → "account"
- "almacén" → "stock"
- "compras" → "purchase"

## Ejemplos de Conversaciones

### Ejemplo 1: Búsqueda Básica
```
Usuario: Hola, necesito un módulo para gestionar proyectos en Odoo 17

Asistente: ¡Hola! Te ayudo a buscar módulos de gestión de proyectos para Odoo 17.0.

[Llama a search_odoo_modules]

He encontrado 5 módulos compatibles:

1. ⭐ Project (Core) (95/100) ✅ Muy recomendado
   📦 project
   🔗 https://github.com/odoo/odoo
   ...

[Presenta resultados formateados]

¿Te gustaría más información sobre alguno de estos módulos?
```

### Ejemplo 2: Con Dependencias
```
Usuario: Busco algo para Odoo 16 que maneje pagos recurrentes y trabaje con el 
        módulo de ventas

Asistente: Perfecto, busco módulos de pagos recurrentes para Odoo 16.0 que 
          dependan de 'sale'.

[Llama a search_odoo_modules con depends=["sale"]]

He encontrado 3 módulos que cumplen tus requisitos:

1. ⭐ Sale Subscription (87/100) ✅ Muy recomendado
   ...

[Presenta resultados]
```

### Ejemplo 3: Sin Resultados
```
Usuario: Necesito integración con TikTok para Odoo 18

Asistente: [Llama a search_odoo_modules]

No encontré módulos específicos de integración con TikTok para Odoo 18.0.

Esto podría deberse a que:
- Es una integración muy específica que aún no existe en OCA
- Podría estar disponible en la Odoo App Store oficial

Sugerencias:
1. Buscar "social media integration" de manera más general
2. Considerar desarrollar un conector personalizado
3. Revisar la Odoo App Store: https://apps.odoo.com

¿Te gustaría que busque módulos de integración con redes sociales en general?
```

## Consideraciones Importantes

1. **Siempre valida la versión**: Es el criterio más importante en Odoo
2. **No inventes módulos**: Solo presenta resultados reales de la API
3. **Sé honesto sobre limitaciones**: Si no hay resultados, dilo claramente
4. **Contextualiza las dependencias**: Explica por qué un módulo requiere ciertas dependencias
5. **Prioriza calidad**: Destaca módulos con quality_score alto

## Testing

Para probar la skill manualmente:

```bash
# Consulta de prueba
curl -X POST https://tu-api.com/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "reportes de ventas",
    "version": "17.0",
    "limit": 3
  }'
```

## Troubleshooting

**Error: "API no responde"**
- Verifica que la API esté corriendo
- Comprueba la URL del endpoint

**Error: "No modules found"**
- Verifica que el ETL haya corrido
- Comprueba que hay módulos en la base de datos para esa versión

**Resultados irrelevantes:**
- Revisa la descripción del query (puede ser demasiado genérica)
- Ajusta el límite de resultados
```

#### 1.4 Testing y Validación

**tests/test_search_api.py:**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_search_modules_basic():
    response = client.post(
        "/api/v1/search",
        json={
            "query": "gestión de inventario",
            "version": "17.0",
            "limit": 3
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 3

def test_search_with_depends():
    response = client.post(
        "/api/v1/search",
        json={
            "query": "pagos recurrentes",
            "version": "16.0",
            "depends": ["sale"],
            "limit": 5
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verificar que todos los resultados tienen 'sale' en depends
    for module in data:
        assert "sale" in module["depends"]

def test_search_invalid_version():
    response = client.post(
        "/api/v1/search",
        json={
            "query": "cualquier cosa",
            "version": "99.0"  # Versión inválida
        }
    )
    # Debería retornar lista vacía
    assert response.status_code == 200
    assert len(response.json()) == 0
```

**Ejecutar tests:**
```bash
pytest tests/ -v
```

#### Deliverables Fase 1

- ✅ API REST funcional con endpoint `/search`
- ✅ Base de datos con 100-200 módulos de OCA
- ✅ Claude Skill configurada y funcionando
- ✅ Tests automatizados (cobertura > 70%)
- ✅ Documentación API (Swagger en `/docs`)
- ✅ Demo funcional end-to-end

---

### **Fase 2: Producción (1-2 meses)**

**Objetivo**: Sistema robusto, escalable y con funcionalidades avanzadas.

#### 2.1 Mejoras en ETL

**Características:**

1. **ETL Incremental**
   ```python
   # Solo procesar módulos nuevos o actualizados
   if last_commit_sha != stored_sha:
       process_module()
   ```

2. **GitHub Webhooks**
   ```python
   @app.post("/webhooks/github")
   async def github_webhook(payload: dict):
       # Actualizar módulo específico cuando hay push
       repo = payload["repository"]["name"]
       trigger_etl_for_repo(repo)
   ```

3. **Procesamiento Paralelo**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=10) as executor:
       executor.map(process_module, modules)
   ```

4. **Expansión de Fuentes**
   - OCA (✅ MVP)
   - GitHub público con tema "odoo" (filtrado por calidad)
   - Odoo Apps Store (web scraping ético + rate limiting)

#### 2.2 Sistema de Scoring Avanzado

```python
class AdvancedScorer:
    def calculate_score(self, module: OdooModule) -> dict:
        return {
            "quality_score": self._quality_score(module),
            "popularity_score": self._popularity_score(module),
            "maintenance_score": self._maintenance_score(module),
            "trust_score": self._trust_score(module),
            "overall_score": self._weighted_average(...)
        }
    
    def _quality_score(self, module):
        # Basado en: tests, documentación, estructura del código
        pass
    
    def _maintenance_score(self, module):
        # Commits recientes, issues cerrados vs abiertos
        pass
    
    def _trust_score(self, module):
        # Autor conocido, repo oficial OCA, downloads
        pass
```

#### 2.3 Análisis de Dependencias

```python
class DependencyAnalyzer:
    def check_compatibility(self, module: OdooModule) -> dict:
        """
        Verificar que todas las dependencias:
        1. Existen en la versión correcta
        2. No tienen conflictos circulares
        3. Están disponibles
        """
        missing = []
        conflicts = []
        
        for dep in module.depends:
            dep_module = self.find_module(dep, module.version)
            if not dep_module:
                missing.append(dep)
            # Verificar dependencias recursivas
            
        return {
            "compatible": len(missing) == 0 and len(conflicts) == 0,
            "missing_dependencies": missing,
            "conflicts": conflicts,
            "installation_order": self._resolve_order(module)
        }
```

#### 2.4 Caché y Optimizaciones

```python
from functools import lru_cache
import redis

redis_client = redis.Redis()

@lru_cache(maxsize=1000)
def get_embedding_cached(text: str):
    # Cache de embeddings
    cached = redis_client.get(f"emb:{hash(text)}")
    if cached:
        return pickle.loads(cached)
    
    embedding = generate_embedding(text)
    redis_client.setex(f"emb:{hash(text)}", 3600, pickle.dumps(embedding))
    return embedding
```

#### 2.5 Monitoreo y Métricas

```python
from prometheus_client import Counter, Histogram
import logging

# Métricas
search_requests = Counter('search_requests_total', 'Total search requests')
search_duration = Histogram('search_duration_seconds', 'Search duration')
results_found = Counter('results_found_total', 'Total results found')

@app.post("/api/v1/search")
async def search_modules(request: SearchRequest):
    search_requests.inc()
    
    with search_duration.time():
        results = await search_service.search(...)
    
    results_found.inc(len(results))
    return results
```

#### 2.6 Interfaz Web (Opcional)

```typescript
// Frontend Next.js + React
// components/SearchBar.tsx

export default function SearchBar() {
  const [query, setQuery] = useState('')
  const [version, setVersion] = useState('17.0')
  const [results, setResults] = useState([])
  
  const handleSearch = async () => {
    const response = await fetch('/api/v1/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, version })
    })
    
    const data = await response.json()
    setResults(data)
  }
  
  return (
    <div className="search-container">
      <input 
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Buscar módulos de Odoo..."
      />
      <select value={version} onChange={(e) => setVersion(e.target.value)}>
        <option value="16.0">Odoo 16.0</option>
        <option value="17.0">Odoo 17.0</option>
        <option value="18.0">Odoo 18.0</option>
      </select>
      <button onClick={handleSearch}>Buscar</button>
      
      <ModuleResults results={results} />
    </div>
  )
}
```

#### Deliverables Fase 2

- ✅ ETL incremental con webhooks
- ✅ 1000+ módulos indexados (OCA completo)
- ✅ Sistema de scoring multi-dimensional
- ✅ Análisis de dependencias automático
- ✅ Caché con Redis
- ✅ Monitoreo con Prometheus/Grafana
- ✅ Documentación completa
- ✅ CI/CD con GitHub Actions
- ✅ Deploy en producción (Render/Railway)

---

## 🛠️ Stack Tecnológico

### Backend & Datos
- **Base de Datos:** [Neon](https://neon.com) - PostgreSQL Serverless con pgVector
  - Scale-to-zero para costos óptimos
  - Provisioning en ~300ms
  - Branching como Git
- **Framework**: FastAPI 0.104+ en [Render.com](https://render.com)
- **ORM**: SQLAlchemy 2.0 + Alembic
- **Embeddings**: Qwen3-Embedding-8B via [OpenRouter.ai](https://openrouter.ai)
- **Cache**: Redis 7+ (opcional)
- **Testing**: pytest, httpx

### Configuración de Neon Postgres

**1. Crear Proyecto:**
```bash
# Web: https://console.neon.tech
# 1. New Project → "ai-odoofinder"
# 2. Region: Seleccionar más cercana
# 3. Postgres version: 16 (recomendado)
```

**2. Habilitar pgVector:**
```sql
-- En Neon SQL Editor o via psql
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar versión
SELECT extversion FROM pg_extension WHERE extname = 'vector';
-- Debería ser >= 0.8.0
```

**3. Crear Tablas:**
```sql
-- Script completo en: backend/app/models.py
-- Se ejecuta con: alembic upgrade head
```

**4. Connection String:**
```python
# backend/app/config.py
DATABASE_URL = os.getenv("DATABASE_URL")
# Formato: postgresql://user:pass@ep-xxx.aws.neon.tech/dbname?sslmode=require
```

**Características de Neon relevantes:**
- **Autoscaling:** Ajusta compute según carga (0.25 - 4 CU en Free)
- **Scale-to-zero:** Se apaga tras 5 min inactividad (Free tier)
- **Branching:** Crear copias para testing sin duplicar storage
- **Connection pooling:** Incluido nativamente

### Frontend (Fase 2)
- **Framework**: Next.js 14
- **UI**: Tailwind CSS, shadcn/ui
- **State**: React Query

### DevOps
- **Deploy**: Render.com / Railway
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logs**: Loguru

### APIs Externas
- **GitHub API**: v3 REST
- **OpenAI API**: Embeddings

---

## 📦 Instalación Rápida

### Requisitos Previos

- Python 3.10+
- PostgreSQL 15+ con pgVector
- Node.js 18+ (solo para frontend)
- Git

### Setup Rápido

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/ai-odoofinder.git
cd ai-odoofinder

# 2. Crear entorno virtual
python3.10 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r backend/requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 5. Crear base de datos con Neon
# Ir a https://neon.com y crear cuenta
# Crear proyecto "ai-odoofinder"
# Copiar connection string a .env

# 6. Habilitar pgVector en Neon
# En Neon SQL Editor:
# CREATE EXTENSION IF NOT EXISTS vector;

# 7. Ejecutar migraciones
alembic upgrade head

# 7. Cargar datos iniciales (ETL)
python scripts/etl_oca_modules.py

# 8. Iniciar servidor
uvicorn app.main:app --reload
```

### Docker (Alternativa)

```bash
# Con Docker Compose
docker-compose up -d

# La API estará disponible en http://localhost:8000
```

---

## 🎯 Uso

### API REST

**Búsqueda Básica:**
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "gestión de inventario",
    "version": "17.0",
    "limit": 5
  }'
```

**Búsqueda con Dependencias:**
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "pagos recurrentes",
    "version": "16.0",
    "depends": ["sale", "account"],
    "limit": 3
  }'
```

**Respuesta Ejemplo:**
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

### Claude Skill

```
Usuario: "Necesito un módulo para Odoo 17 que gestione proyectos 
         con facturación por horas"

Claude: "Te ayudo a buscar módulos de gestión de proyectos 
        con facturación por horas para Odoo 17.0"

[Claude llama a la API automáticamente]

Claude: "He encontrado 3 módulos que cumplen tus requisitos:

        1. ⭐ Project Timesheet (92/100) ✅ Muy recomendado
           ..."
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guías de Contribución

- **Código**: Seguir PEP 8 para Python
- **Tests**: Cobertura mínima 70%
- **Documentación**: Actualizar README si añades features

---

## Deployment

### Arquitectura de Producción
```
Usuario (claude.ai)
    ↓
Claude Skill
    ↓ HTTPS
Render.com (FastAPI)
    ↓ PostgreSQL protocol
Neon (Postgres + pgVector)
```

### Desplegar en Render

**1. Preparar repositorio:**
```bash
# Asegurar que existe:
- requirements.txt
- backend/app/main.py
- .env.example (sin valores reales)
```

**2. Crear Web Service en Render:**
- Conectar GitHub repo
- Build: `pip install -r requirements.txt`
- Start: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

**3. Variables de entorno en Render:**
```
DATABASE_URL=postgresql://...@ep-xxx.neon.tech/...
OPENROUTER_API_KEY=sk-or-v1-...
GITHUB_TOKEN=ghp_...
```

**4. Verificar deployment:**
```bash
curl https://ai-odoofinder.onrender.com/health
# Respuesta: {"status": "healthy", "database": "connected"}
```

### Costos Estimados

**Free Tier (MVP):**
- Neon: $0 (0.5GB storage, 191h compute/mes)
- Render: $0 (750h/mes, sleep tras inactividad)
- OpenRouter: ~$0.50/mes (embeddings)
- **Total: ~$0.50/mes**

**Producción (500+ usuarios):**
- Neon Launch: $19/mes (3GB storage, autoscaling)
- Render: $7-25/mes (según uso)
- OpenRouter: $10-20/mes (embeddings + búsquedas)
- **Total: ~$36-64/mes**

---

## 📊 Métricas y Monitoreo

### Dashboard (Grafana)

- Total de búsquedas/día
- Tiempo promedio de respuesta
- Módulos más buscados
- Versiones más consultadas
- Tasa de éxito (resultados encontrados)

### Logs

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Buscar errores
grep ERROR logs/app.log
```

---

## 🐛 Troubleshooting

### Problema: "No se encuentran módulos"

**Solución:**
```bash
# Verificar que el ETL haya corrido
psql odoo_finder -c "SELECT COUNT(*) FROM odoo_modules;"

# Si está vacío, ejecutar ETL
python scripts/etl_oca_modules.py
```

### Problema: "Error de conexión a PostgreSQL"

**Solución:**
```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql

# Verificar credenciales en .env
cat .env | grep DATABASE_URL
```

### Problema: "API lenta"

**Solución:**
```bash
# Verificar índices
psql odoo_finder -c "\d+ odoo_modules"

# Crear índices si faltan
CREATE INDEX idx_version ON odoo_modules(version);
CREATE INDEX idx_embedding ON odoo_modules USING ivfflat (embedding vector_cosine_ops);
```

---

## 📈 Roadmap Futuro

### Corto Plazo (1-3 meses)
- [ ] Soporte para más repositorios (GitHub público)
- [ ] Análisis de compatibilidad entre módulos
- [ ] Recomendaciones automáticas de módulos relacionados
- [ ] CLI para búsquedas desde terminal

### Medio Plazo (3-6 meses)
- [ ] Integración con Odoo Apps Store
- [ ] Sistema de reviews y ratings comunitarios
- [ ] Notificaciones de actualizaciones de módulos
- [ ] API pública para terceros

### Largo Plazo (6-12 meses)
- [ ] Análisis automático de calidad de código
- [ ] Sugerencias de mejora para desarrolladores
- [ ] Marketplace integrado
- [ ] Soporte para módulos privados/empresariales

---

## 💰 Modelo de Negocio (Futuro)

### Plan Gratuito
- 10 búsquedas/mes
- Acceso a módulos de OCA
- Documentación básica

### Plan Pro ($9/mes)
- Búsquedas ilimitadas
- Análisis de dependencias
- Soporte prioritario
- Acceso anticipado a features

### Plan Enterprise (Custom)
- API privada
- Módulos privados indexados
- SLA garantizado
- Soporte dedicado

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 👥 Autores

- **Tu Nombre** - *Trabajo Inicial* - [tu-github](https://github.com/tu-usuario)

---

## 🙏 Agradecimientos

- [Odoo Community Association (OCA)](https://odoo-community.org/) por sus increíbles módulos open source
- [Anthropic](https://www.anthropic.com/) por Claude y el sistema de Skills
- Comunidad de desarrolladores de Odoo

---

## 📞 Contacto

- **Email**: tu-email@ejemplo.com
- **GitHub Issues**: [Reportar un bug](https://github.com/tu-usuario/odoo-module-finder/issues)
- **Discussions**: [Hacer una pregunta](https://github.com/tu-usuario/odoo-module-finder/discussions)

---

## 📚 Enlaces Útiles

- [Documentación de Odoo](https://www.odoo.com/documentation)
- [OCA GitHub](https://github.com/OCA)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [pgVector Docs](https://github.com/pgvector/pgvector)
- [Claude Skills](https://docs.anthropic.com/claude/docs/skills)

---

<div align="center">
  <strong>¿Te gustó el proyecto? ¡Dale una ⭐ en GitHub!</strong>
</div>
