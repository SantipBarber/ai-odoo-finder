"""
Hybrid Search Service: Combines vector similarity and BM25 full-text search.

This service implements Reciprocal Rank Fusion (RRF) to combine results from
semantic vector search and keyword-based BM25 full-text search.
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from dataclasses import dataclass, field
import logging

from ..core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """Resultado de búsqueda con múltiples scores."""

    id: int
    technical_name: str
    name: str
    summary: str
    version: str
    depends: List[str] = field(default_factory=list)
    github_stars: int = 0

    # Scores
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None
    rrf_score: Optional[float] = None

    # Rankings
    vector_rank: Optional[int] = None
    bm25_rank: Optional[int] = None
    final_rank: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'technical_name': self.technical_name,
            'name': self.name,
            'summary': self.summary,
            'version': self.version,
            'depends': self.depends,
            'github_stars': self.github_stars,
            'vector_score': self.vector_score,
            'bm25_score': self.bm25_score,
            'rrf_score': self.rrf_score,
            'vector_rank': self.vector_rank,
            'bm25_rank': self.bm25_rank,
            'final_rank': self.final_rank
        }


class HybridSearchService:
    """Servicio de búsqueda híbrida (Vector + BM25)."""

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        query: str,
        query_embedding: List[float],
        version: str,
        dependencies: Optional[List[str]] = None,
        limit: int = 5,
        k: int = 60,
        top_candidates: int = 50
    ) -> List[SearchResult]:
        """Ejecuta búsqueda híbrida con RRF."""

        logger.info(f"Hybrid search: query='{query}', version={version}, limit={limit}")

        # Validate embedding (updated for current embedding model dimension)
        expected_dim = 2560  # Current embedding model dimension
        if len(query_embedding) != expected_dim:
            raise ValueError(f"Expected embedding dimension {expected_dim}, got {len(query_embedding)}")

        # 1. Vector similarity search
        logger.debug(f"Executing vector search (top {top_candidates})")
        vector_results = self._vector_search(
            embedding=query_embedding,
            version=version,
            dependencies=dependencies,
            limit=top_candidates
        )
        logger.debug(f"Vector search returned {len(vector_results)} results")

        # 2. BM25 full-text search
        logger.debug(f"Executing BM25 search (top {top_candidates})")
        fulltext_results = self._fulltext_search(
            query=query,
            version=version,
            dependencies=dependencies,
            limit=top_candidates
        )
        logger.debug(f"BM25 search returned {len(fulltext_results)} results")

        # 3. Reciprocal Rank Fusion
        logger.debug(f"Fusing results with RRF (k={k})")
        fused_results = self._reciprocal_rank_fusion(
            vector_results=vector_results,
            fulltext_results=fulltext_results,
            k=k
        )

        # 4. Return top N
        final_results = fused_results[:limit]
        logger.info(f"Hybrid search complete: returning {len(final_results)} results")

        return final_results

    def _vector_search(
        self,
        embedding: List[float],
        version: str,
        dependencies: Optional[List[str]],
        limit: int
    ) -> List[SearchResult]:
        """Búsqueda vectorial por similitud."""

        # Convert embedding to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'

        # Use raw psycopg3 connection
        raw_conn = self.db.connection().connection

        if dependencies:
            query_sql = """
                SELECT
                    id,
                    technical_name,
                    name,
                    summary,
                    version,
                    depends,
                    github_stars,
                    1 - (embedding <=> %s::vector) as similarity_score
                FROM odoo_modules
                WHERE version = %s
                    AND depends && %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """
            params = (embedding_str, version, dependencies, embedding_str, limit)
        else:
            query_sql = """
                SELECT
                    id,
                    technical_name,
                    name,
                    summary,
                    version,
                    depends,
                    github_stars,
                    1 - (embedding <=> %s::vector) as similarity_score
                FROM odoo_modules
                WHERE version = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """
            params = (embedding_str, version, embedding_str, limit)

        cursor = raw_conn.cursor()
        cursor.execute(query_sql, params)
        rows = cursor.fetchall()

        # Get column names
        columns = [desc[0] for desc in cursor.description]

        # Convert to dictionaries
        result_dicts = [dict(zip(columns, row)) for row in rows]
        cursor.close()

        return [
            SearchResult(
                id=row['id'],
                technical_name=row['technical_name'],
                name=row['name'] or '',
                summary=row['summary'] or '',
                version=row['version'],
                depends=row['depends'] or [],
                github_stars=row['github_stars'] or 0,
                vector_score=float(row['similarity_score']),
                vector_rank=i + 1
            )
            for i, row in enumerate(result_dicts)
        ]

    def _fulltext_search(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]],
        limit: int
    ) -> List[SearchResult]:
        """Búsqueda BM25 full-text."""

        # Use raw psycopg3 connection for consistency
        raw_conn = self.db.connection().connection

        if dependencies:
            query_sql = """
                SELECT
                    id,
                    technical_name,
                    name,
                    summary,
                    version,
                    depends,
                    github_stars,
                    ts_rank_cd(searchable_text, q) as bm25_score
                FROM odoo_modules,
                     plainto_tsquery('english', %s) q
                WHERE version = %s
                    AND depends && %s
                    AND searchable_text @@ q
                ORDER BY bm25_score DESC
                LIMIT %s
            """
            params = (query, version, dependencies, limit)
        else:
            query_sql = """
                SELECT
                    id,
                    technical_name,
                    name,
                    summary,
                    version,
                    depends,
                    github_stars,
                    ts_rank_cd(searchable_text, q) as bm25_score
                FROM odoo_modules,
                     plainto_tsquery('english', %s) q
                WHERE version = %s
                    AND searchable_text @@ q
                ORDER BY bm25_score DESC
                LIMIT %s
            """
            params = (query, version, limit)

        cursor = raw_conn.cursor()
        cursor.execute(query_sql, params)
        rows = cursor.fetchall()

        # Get column names
        columns = [desc[0] for desc in cursor.description]

        # Convert to dictionaries
        result_dicts = [dict(zip(columns, row)) for row in rows]
        cursor.close()

        return [
            SearchResult(
                id=row['id'],
                technical_name=row['technical_name'],
                name=row['name'] or '',
                summary=row['summary'] or '',
                version=row['version'],
                depends=row['depends'] or [],
                github_stars=row['github_stars'] or 0,
                bm25_score=float(row['bm25_score']),
                bm25_rank=i + 1
            )
            for i, row in enumerate(result_dicts)
        ]

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[SearchResult],
        fulltext_results: List[SearchResult],
        k: int = 60
    ) -> List[SearchResult]:
        """
        Fusiona resultados con RRF.

        Formula: RRF_score(d) = Σ 1/(k + rank_i(d))
        """

        # Build index of all modules by ID
        modules: Dict[int, SearchResult] = {}
        rrf_scores: Dict[int, float] = {}

        # Add vector results
        for result in vector_results:
            module_id = result.id
            modules[module_id] = result
            rrf_scores[module_id] = 1.0 / (k + result.vector_rank)

        # Add BM25 results
        for result in fulltext_results:
            module_id = result.id

            if module_id in modules:
                # Module in both lists - merge
                modules[module_id].bm25_score = result.bm25_score
                modules[module_id].bm25_rank = result.bm25_rank
                rrf_scores[module_id] += 1.0 / (k + result.bm25_rank)
            else:
                # Module only in BM25 list
                modules[module_id] = result
                rrf_scores[module_id] = 1.0 / (k + result.bm25_rank)

        # Set RRF scores
        for module_id, score in rrf_scores.items():
            modules[module_id].rrf_score = score

        # Sort by RRF score
        sorted_modules = sorted(
            modules.values(),
            key=lambda m: m.rrf_score or 0,
            reverse=True
        )

        # Set final ranks
        for i, module in enumerate(sorted_modules, 1):
            module.final_rank = i

        return sorted_modules


def get_hybrid_search_service(db: Session) -> HybridSearchService:
    """Factory function para crear instancia de HybridSearchService"""
    return HybridSearchService(db)
