import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db, init_db
from .models import OdooModule
from .services.search_service import get_search_service

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI-OdooFinder API...")
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down server...")


app = FastAPI(
    title="AI-OdooFinder API",
    description="Búsqueda inteligente de módulos de Odoo usando RAG híbrido",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI-OdooFinder API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "mcp": {
            "endpoint": "/mcp/",
            "protocol": "HTTP/SSE",
            "tools": ["search_odoo_modules"],
            "description": "Model Context Protocol server for Claude and other AI assistants",
            "claude_config": {
                "url": "https://ai-odoo-finder.onrender.com/mcp/",
                "note": "IMPORTANT: Use this URL with trailing slash in Claude Web → Settings → Integrations → MCP",
            },
        },
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check - verify that API and DB are working."""
    try:
        total_modules = db.query(OdooModule).count()

        return {"status": "healthy", "database": "connected", "total_modules": total_modules}
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
    min_score: int = Query(0, ge=0, le=100, description="Minimum score (0-100)"),
    db: Session = Depends(get_db),
):
    """
    Hybrid search for Odoo modules.

    Accepts both GET and POST requests.

    **Example:**
    ```
    GET /search?query=sales+subscriptions&version=17.0&limit=5
    POST /search?query=sales+subscriptions&version=17.0&limit=5
    ```

    **Response:**
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
        logger.info(f"Search: query='{query[:50]}...', version={version}, limit={limit}")

        if version not in ["12.0", "13.0", "14.0", "15.0", "16.0", "17.0", "18.0", "19.0"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid version. Use: 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0 or 19.0",
            )

        search_service = get_search_service(db)
        results = search_service.search(
            query=query,
            version=version,
            dependencies=dependencies,
            limit=limit,
            min_score=min_score,
        )

        logger.info(f"Returning {len(results)} results")

        return {
            "query": query,
            "version": version,
            "dependencies": dependencies,
            "total_results": len(results),
            "results": results,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/modules/{module_id}")
async def get_module_detail(module_id: int, db: Session = Depends(get_db)):
    """
    Get complete module details by ID.

    **Example:**
    ```
    GET /modules/123
    ```
    """
    try:
        module = db.query(OdooModule).filter(OdooModule.id == module_id).first()

        if not module:
            raise HTTPException(status_code=404, detail="Module not found")

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
            "last_commit_date": module.last_commit_date.isoformat()
            if module.last_commit_date
            else None,
            "created_at": module.created_at.isoformat(),
            "updated_at": module.updated_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting module {module_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    General database statistics.

    **Example:**
    ```
    GET /stats
    ```
    """
    try:
        total = db.query(OdooModule).count()

        by_version = {}
        for version in ["12.0", "13.0", "14.0", "15.0", "16.0", "17.0", "18.0", "19.0"]:
            count = db.query(OdooModule).filter(OdooModule.version == version).count()
            if count > 0:
                by_version[version] = count

        from sqlalchemy import func

        by_repo = (
            db.query(OdooModule.repo_name, func.count(OdooModule.id).label("count"))
            .group_by(OdooModule.repo_name)
            .order_by(func.count(OdooModule.id).desc())
            .limit(10)
            .all()
        )

        return {
            "total_modules": total,
            "by_version": by_version,
            "top_repositories": [{"name": repo, "modules": count} for repo, count in by_repo],
        }

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8989)
