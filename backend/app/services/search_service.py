import logging
from typing import List, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, String, cast
from sqlalchemy.dialects.postgresql import ARRAY, array

from ..models import OdooModule
from ..core.logging import get_logger
from .embedding_service import get_embedding_service

logger = get_logger(__name__)
embedding_service = get_embedding_service()


class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = embedding_service

    def search(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]] = None,
        limit: int = 10,
        min_score: int = 0,
    ) -> List[Dict]:
        """
        Búsqueda híbrida: Filtros SQL + Similitud Vectorial

        Args:
            query: Consulta en lenguaje natural
            version: Versión de Odoo (ej: "17.0")
            dependencies: Lista de dependencias requeridas (opcional)
            limit: Número máximo de resultados
            min_score: Score mínimo (0-100) para filtrar resultados

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

        logger.info(
            f"Búsqueda: query='{query[:50]}...', version={version}, "
            f"dependencies={dependencies}, limit={limit}"
        )

        try:
            # 1. FASE 1: Filtro determinista (SQL)
            filters = [OdooModule.version == version]

            # Filtrar por dependencias usando operador @> de PostgreSQL
            # Verificar que el módulo tenga TODAS las dependencias requeridas
            if dependencies:
                # Usar @> (contains) - el array del módulo debe contener estas dependencias
                # Crear array de PostgreSQL con cast explícito a VARCHAR[]
                dep_array = cast(array(dependencies), ARRAY(String))
                filters.append(OdooModule.depends.op("@>")(dep_array))

            # 2. FASE 2: Generar embedding de la query
            try:
                query_embedding = self.embedding_service.get_embedding(query)
            except Exception as e:
                logger.error(f"Error generando embedding: {e}")
                return []

            # 3. FASE 3: Búsqueda por similitud de coseno
            # Usar cosine_distance de pgvector (retorna 0-2, donde 0 es idéntico)
            results = (
                self.db.query(
                    OdooModule,
                    # Distancia de coseno (0 = idéntico, 2 = opuesto)
                    OdooModule.embedding.cosine_distance(query_embedding).label("distance"),
                )
                .filter(and_(*filters))
                .order_by("distance")
                .limit(limit * 2)  # Obtener más para filtrar por min_score
                .all()
            )

            if not results:
                logger.info("No se encontraron resultados")
                return []

            logger.info(f"Encontrados {len(results)} candidatos tras búsqueda vectorial")

            # 4. FASE 4: Calcular scores y formatear resultados
            output = []
            for module, distance in results:
                # Convertir distancia a score (0-100)
                # distance: 0 (idéntico) a 2 (opuesto)
                # similarity: 1 - (distance / 2) -> rango 0-1
                similarity = max(0.0, 1.0 - (float(distance) / 2.0))
                score = int(similarity * 100)

                # Filtrar por score mínimo
                if score < min_score:
                    continue

                # Truncar descripción si es muy larga
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

            # Limitar resultados finales
            output = output[:limit]

            logger.info(f"Retornando {len(output)} resultados")
            return output

        except Exception as e:
            logger.error(f"Error en búsqueda: {e}", exc_info=True)
            # Hacer rollback para evitar que la transacción quede abortada
            try:
                self.db.rollback()
            except Exception:
                pass
            return []


def get_search_service(db: Session) -> SearchService:
    """Factory function para crear instancia de SearchService"""
    return SearchService(db)
