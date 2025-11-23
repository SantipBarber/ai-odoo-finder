"""
Hybrid Search Service: Combines vector similarity and BM25 full-text search.
"""
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


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

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
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

        # Validate embedding
        if len(query_embedding) != 1024:
            raise ValueError(f"Expected embedding dimension 1024, got {len(query_embedding)}")

        # 1. Vector similarity search
        logger.debug(f"Executing vector search (top {top_candidates})")
        vector_results = await self._vector_search(
            embedding=query_embedding,
            version=version,
            dependencies=dependencies,
            limit=top_candidates
        )
        logger.debug(f"Vector search returned {len(vector_results)} results")

        # 2. BM25 full-text search
        logger.debug(f"Executing BM25 search (top {top_candidates})")
        fulltext_results = await self._fulltext_search(
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

    async def _vector_search(
        self,
        embedding: List[float],
        version: str,
        dependencies: Optional[List[str]],
        limit: int
    ) -> List[SearchResult]:
        """Búsqueda vectorial por similitud."""

        query_sql = text("""
            SELECT
                id,
                technical_name,
                name,
                summary,
                version,
                depends,
                github_stars,
                1 - (embedding <=> :embedding::vector) as similarity_score
            FROM odoo_modules
            WHERE version = :version
                AND (:deps::text[] IS NULL OR depends && :deps)
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """)

        result = await self.db.execute(query_sql, {
            "embedding": embedding,
            "version": version,
            "deps": dependencies,
            "limit": limit
        })

        rows = result.fetchall()

        return [
            SearchResult(
                id=row.id,
                technical_name=row.technical_name,
                name=row.name or '',
                summary=row.summary or '',
                version=row.version,
                depends=row.depends or [],
                github_stars=row.github_stars or 0,
                vector_score=float(row.similarity_score),
                vector_rank=i + 1
            )
            for i, row in enumerate(rows)
        ]

    async def _fulltext_search(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]],
        limit: int
    ) -> List[SearchResult]:
        """Búsqueda BM25 full-text."""

        query_sql = text("""
            SELECT
                id,
                technical_name,
                name,
                summary,
                version,
                depends,
                github_stars,
                ts_rank_cd(searchable_text, query) as bm25_score
            FROM odoo_modules,
                 plainto_tsquery('english', :query) query
            WHERE version = :version
                AND (:deps::text[] IS NULL OR depends && :deps)
                AND searchable_text @@ query
            ORDER BY bm25_score DESC
            LIMIT :limit
        """)

        result = await self.db.execute(query_sql, {
            "query": query,
            "version": version,
            "deps": dependencies,
            "limit": limit
        })

        rows = result.fetchall()

        return [
            SearchResult(
                id=row.id,
                technical_name=row.technical_name,
                name=row.name or '',
                summary=row.summary or '',
                version=row.version,
                depends=row.depends or [],
                github_stars=row.github_stars or 0,
                bm25_score=float(row.bm25_score),
                bm25_rank=i + 1
            )
            for i, row in enumerate(rows)
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
