import logging
from typing import List, Dict, Optional, Literal

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, String, cast
from sqlalchemy.dialects.postgresql import ARRAY, array

from ..models import OdooModule
from ..core.logging import get_logger
from .embedding_service import get_embedding_service
from .hybrid_search_service import HybridSearchService

logger = get_logger(__name__)
embedding_service = get_embedding_service()

# Lazy load reranking service (heavy model)
_reranking_service = None


def _get_reranking_service():
    """Lazy load reranking service to avoid loading model at import time."""
    global _reranking_service
    if _reranking_service is None:
        from .reranking_service import get_reranking_service
        _reranking_service = get_reranking_service()
    return _reranking_service

# Type alias for search modes
SearchMode = Literal["vector", "bm25", "hybrid"]


class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = embedding_service
        self.hybrid_search_service = HybridSearchService(db)

    def search(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]] = None,
        limit: int = 10,
        min_score: int = 0,
        search_mode: SearchMode = "hybrid",
        use_reranking: bool = False,
    ) -> List[Dict]:
        """
        Búsqueda multi-modal: Vector, BM25, o Híbrida.

        Args:
            query: Consulta en lenguaje natural
            version: Versión de Odoo (ej: "17.0")
            dependencies: Lista de dependencias requeridas (opcional)
            limit: Número máximo de resultados
            min_score: Score mínimo (0-100) para filtrar resultados
            search_mode: Modo de búsqueda:
                - "vector": Solo búsqueda semántica (legacy)
                - "bm25": Solo full-text search
                - "hybrid": Vector + BM25 con RRF (default, recomendado)
            use_reranking: Si True, aplica reranking con Qwen3-Reranker-4B

        Returns:
            Lista de módulos rankeados con score y metadata
        """
        # Validaciones
        if not query or not query.strip():
            logger.warning("Query vacía recibida")
            return []

        if not version:
            logger.warning("Versión no especificada")
            return []

        query = query.strip()
        dependencies = dependencies or []

        rerank_suffix = " +rerank" if use_reranking else ""
        logger.info(
            f"Búsqueda [{search_mode}{rerank_suffix}]: query='{query[:50]}...', version={version}, "
            f"dependencies={dependencies}, limit={limit}"
        )

        try:
            # Route to appropriate search method
            if search_mode == "hybrid":
                results = self._search_hybrid(query, version, dependencies, limit, min_score)
            elif search_mode == "bm25":
                results = self._search_bm25(query, version, dependencies, limit, min_score)
            elif search_mode == "vector":
                results = self._search_vector(query, version, dependencies, limit, min_score)
            else:
                raise ValueError(f"Invalid search_mode: {search_mode}")

            # Apply reranking if enabled
            if use_reranking and results:
                results = self._apply_reranking(query, results, limit)

            return results

        except Exception as e:
            logger.error(f"Error en búsqueda [{search_mode}]: {e}", exc_info=True)
            # Hacer rollback para evitar que la transacción quede abortada
            try:
                self.db.rollback()
            except Exception:
                pass
            return []

    def _apply_reranking(
        self,
        query: str,
        candidates: List[Dict],
        limit: int
    ) -> List[Dict]:
        """
        Apply reranking to search results using Qwen3-Reranker-4B.

        Args:
            query: Original search query
            candidates: List of search results to rerank
            limit: Number of results to return

        Returns:
            Reranked list of results
        """
        try:
            reranking_service = _get_reranking_service()

            # Enrich candidates with ai_description and keywords for better reranking
            enriched_candidates = []
            for candidate in candidates:
                module = self.db.query(OdooModule).filter(
                    OdooModule.id == candidate['id']
                ).first()

                if module:
                    enriched = candidate.copy()
                    enriched['ai_description'] = module.ai_description or ""
                    enriched['keywords'] = module.keywords or []
                    enriched_candidates.append(enriched)
                else:
                    enriched_candidates.append(candidate)

            # Rerank
            reranked = reranking_service.rerank(
                query=query,
                candidates=enriched_candidates,
                top_k=limit
            )

            logger.info(f"Reranking complete: {len(reranked)} results")
            return reranked

        except Exception as e:
            logger.error(f"Reranking failed, returning original order: {e}")
            return candidates[:limit]

    def _search_hybrid(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]],
        limit: int,
        min_score: int,
    ) -> List[Dict]:
        """Búsqueda híbrida usando HybridSearchService."""

        # Generate embedding
        try:
            query_embedding = self.embedding_service.get_embedding(query)
        except Exception as e:
            logger.error(f"Error generando embedding: {e}")
            return []

        # Execute hybrid search
        results = self.hybrid_search_service.search(
            query=query,
            query_embedding=query_embedding,
            version=version,
            dependencies=dependencies,
            limit=limit,
            k=60,
            top_candidates=50
        )

        # Convert SearchResult to dict format
        output = []
        for result in results:
            # Calculate score 0-100 from RRF score
            score = int(min(100, result.rrf_score * 100 * 60))  # Approximate normalization

            if score < min_score:
                continue

            # Fetch full module data for metadata
            module = self.db.query(OdooModule).filter(OdooModule.id == result.id).first()
            if not module:
                continue

            description = module.description or ""
            if len(description) > 200:
                description = description[:200] + "..."

            output.append(
                {
                    "id": module.id,
                    "technical_name": module.technical_name,
                    "name": module.name,
                    "version": module.version,
                    "summary": module.summary or "",
                    "description": description,
                    "depends": module.depends or [],
                    "author": module.author or "",
                    "license": module.license or "AGPL-3",
                    "repo_name": module.repo_name,
                    "repo_url": module.repo_url or f"https://github.com/OCA/{module.repo_name}",
                    "module_path": module.module_path,
                    "github_stars": module.github_stars or 0,
                    "github_issues_open": module.github_issues_open or 0,
                    "last_commit_date": (
                        module.last_commit_date.isoformat()
                        if module.last_commit_date
                        else None
                    ),
                    "score": score,
                    "rrf_score": result.rrf_score,
                    "vector_score": result.vector_score,
                    "bm25_score": result.bm25_score,
                }
            )

        logger.info(f"Hybrid search retornando {len(output)} resultados")
        return output

    def _search_bm25(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]],
        limit: int,
        min_score: int,
    ) -> List[Dict]:
        """Búsqueda BM25 full-text pura."""

        results = self.hybrid_search_service._fulltext_search(
            query=query,
            version=version,
            dependencies=dependencies,
            limit=limit
        )

        # Convert to dict format
        output = []
        for result in results:
            # Normalize BM25 score to 0-100 range (approximate)
            score = int(min(100, result.bm25_score * 10))

            if score < min_score:
                continue

            module = self.db.query(OdooModule).filter(OdooModule.id == result.id).first()
            if not module:
                continue

            description = module.description or ""
            if len(description) > 200:
                description = description[:200] + "..."

            output.append(
                {
                    "id": module.id,
                    "technical_name": module.technical_name,
                    "name": module.name,
                    "version": module.version,
                    "summary": module.summary or "",
                    "description": description,
                    "depends": module.depends or [],
                    "author": module.author or "",
                    "license": module.license or "AGPL-3",
                    "repo_name": module.repo_name,
                    "repo_url": module.repo_url or f"https://github.com/OCA/{module.repo_name}",
                    "module_path": module.module_path,
                    "github_stars": module.github_stars or 0,
                    "github_issues_open": module.github_issues_open or 0,
                    "last_commit_date": (
                        module.last_commit_date.isoformat()
                        if module.last_commit_date
                        else None
                    ),
                    "score": score,
                    "bm25_score": result.bm25_score,
                }
            )

        logger.info(f"BM25 search retornando {len(output)} resultados")
        return output

    def _search_vector(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]],
        limit: int,
        min_score: int,
    ) -> List[Dict]:
        """Búsqueda vectorial pura (legacy mode)."""

        # Generate embedding
        try:
            query_embedding = self.embedding_service.get_embedding(query)
        except Exception as e:
            logger.error(f"Error generando embedding: {e}")
            return []

        # Build filters
        filters = [OdooModule.version == version]

        if dependencies:
            dep_array = cast(array(dependencies), ARRAY(String))
            filters.append(OdooModule.depends.op("@>")(dep_array))

        # Vector search using cosine distance
        results = (
            self.db.query(
                OdooModule,
                OdooModule.embedding.cosine_distance(query_embedding).label("distance"),
            )
            .filter(and_(*filters))
            .order_by("distance")
            .limit(limit * 2)
            .all()
        )

        if not results:
            logger.info("No se encontraron resultados")
            return []

        # Format results
        output = []
        for module, distance in results:
            # Convert distance to score (0-100)
            similarity = max(0.0, 1.0 - (float(distance) / 2.0))
            score = int(similarity * 100)

            if score < min_score:
                continue

            description = module.description or ""
            if len(description) > 200:
                description = description[:200] + "..."

            output.append(
                {
                    "id": module.id,
                    "technical_name": module.technical_name,
                    "name": module.name,
                    "version": module.version,
                    "summary": module.summary or "",
                    "description": description,
                    "depends": module.depends or [],
                    "author": module.author or "",
                    "license": module.license or "AGPL-3",
                    "repo_name": module.repo_name,
                    "repo_url": module.repo_url or f"https://github.com/OCA/{module.repo_name}",
                    "module_path": module.module_path,
                    "github_stars": module.github_stars or 0,
                    "github_issues_open": module.github_issues_open or 0,
                    "last_commit_date": (
                        module.last_commit_date.isoformat()
                        if module.last_commit_date
                        else None
                    ),
                    "score": score,
                    "distance": round(float(distance), 4),
                }
            )

        # Limit final results
        output = output[:limit]

        logger.info(f"Vector search retornando {len(output)} resultados")
        return output


def get_search_service(db: Session) -> SearchService:
    """Factory function para crear instancia de SearchService"""
    return SearchService(db)
