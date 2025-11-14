from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from .database import get_db, init_db
from .services.search_service import get_search_service
from .models import OdooModule

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear app
app = FastAPI(
    title="AI-OdooFinder API",
    description="Búsqueda inteligente de módulos de Odoo usando RAG híbrido",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS (permitir requests desde cualquier origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar DB al arrancar
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Iniciando AI-OdooFinder API...")
    init_db()
    logger.info("✅ Base de datos inicializada")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "name": "AI-OdooFinder API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check - verificar que la API y DB funcionan"""
    try:
        # Contar módulos en DB
        total_modules = db.query(OdooModule).count()

        return {
            "status": "healthy",
            "database": "connected",
            "total_modules": total_modules
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/search")
@app.post("/search")
async def search_modules(
    query: str = Query(..., description="Consulta en lenguaje natural"),
    version: str = Query(..., description="Versión de Odoo (16.0, 17.0, 18.0)"),
    dependencies: Optional[List[str]] = Query(None, description="Dependencias requeridas"),
    limit: int = Query(10, ge=1, le=50, description="Número máximo de resultados"),
    min_score: int = Query(0, ge=0, le=100, description="Score mínimo (0-100)"),
    db: Session = Depends(get_db)
):
    """
    Búsqueda híbrida de módulos de Odoo.

    Acepta tanto GET como POST requests.

    **Ejemplo:**
    ```
    GET /search?query=sales+subscriptions&version=17.0&limit=5
    POST /search?query=sales+subscriptions&version=17.0&limit=5
    ```

    **Respuesta:**
    ```json
    {
      "query": "sales subscriptions",
      "version": "17.0",
      "total_results": 5,
      "results": [
        {
          "id": 123,
          "technical_name": "sale_subscription",
          "name": "Sale Subscription",
          "score": 89,
          ...
        }
      ]
    }
    ```
    """
    try:
        logger.info(f"Búsqueda: query='{query[:50]}...', version={version}, limit={limit}")

        # Validar versión
        if version not in ["14.0", "15.0", "16.0", "17.0", "18.0"]:
            raise HTTPException(
                status_code=400,
                detail=f"Versión inválida. Use: 14.0, 15.0, 16.0, 17.0 o 18.0"
            )

        # Buscar
        search_service = get_search_service(db)
        results = search_service.search(
            query=query,
            version=version,
            dependencies=dependencies,
            limit=limit,
            min_score=min_score
        )

        logger.info(f"Retornando {len(results)} resultados")

        return {
            "query": query,
            "version": version,
            "dependencies": dependencies,
            "total_results": len(results),
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/modules/{module_id}")
async def get_module_detail(
    module_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener detalle completo de un módulo por ID.

    **Ejemplo:**
    ```
    GET /modules/123
    ```
    """
    try:
        module = db.query(OdooModule).filter(OdooModule.id == module_id).first()

        if not module:
            raise HTTPException(status_code=404, detail="Módulo no encontrado")

        return {
            "id": module.id,
            "technical_name": module.technical_name,
            "name": module.name,
            "version": module.version,
            "summary": module.summary,
            "description": module.description,
            "depends": module.depends,
            "author": module.author,
            "license": module.license,
            "repo_name": module.repo_name,
            "repo_url": module.repo_url,
            "module_path": module.module_path,
            "github_stars": module.github_stars,
            "github_issues_open": module.github_issues_open,
            "last_commit_date": module.last_commit_date.isoformat() if module.last_commit_date else None,
            "created_at": module.created_at.isoformat(),
            "updated_at": module.updated_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo módulo {module_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Estadísticas generales de la base de datos.

    **Ejemplo:**
    ```
    GET /stats
    ```
    """
    try:
        total = db.query(OdooModule).count()

        # Por versión
        by_version = {}
        for version in ["14.0", "15.0", "16.0", "17.0", "18.0"]:
            count = db.query(OdooModule).filter(OdooModule.version == version).count()
            if count > 0:
                by_version[version] = count

        # Por repositorio (top 10)
        from sqlalchemy import func
        by_repo = db.query(
            OdooModule.repo_name,
            func.count(OdooModule.id).label('count')
        ).group_by(OdooModule.repo_name).order_by(func.count(OdooModule.id).desc()).limit(10).all()

        return {
            "total_modules": total,
            "by_version": by_version,
            "top_repositories": [
                {"name": repo, "modules": count}
                for repo, count in by_repo
            ]
        }

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8989)
