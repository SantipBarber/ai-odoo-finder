# SPEC-301: Reranking Service

**ID:** SPEC-301
**Componente:** LLM Reranking Service
**Archivo:** `app/services/reranking_service.py`
**Prioridad:** Alta
**Estimación:** 3 horas
**Dependencias:** Fase 3 completada

---

## 📋 Descripción

Servicio que usa Claude Haiku para reordenar inteligentemente los top candidatos del hybrid search, mejorando precisión en queries complejas.

---

## 📐 Implementación Completa

```python
"""
LLM Reranking Service using Claude Haiku.
"""
from typing import List, Dict, Optional
from anthropic import Anthropic
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RerankResult:
    """Resultado de reranking."""
    technical_name: str
    original_rank: int
    reranked_score: float
    llm_reason: str
    # Original search result data
    name: str
    summary: str
    ai_description: Optional[str]
    functional_tags: List[str]
    keywords: List[str]


class RerankingService:
    """Reordena resultados de búsqueda con Claude Haiku."""

    PROMPT_TEMPLATE = """Eres un experto en Odoo ERP ayudando a usuarios a encontrar el módulo correcto.

**Búsqueda del usuario:**
"{query}"

**Contexto:**
El usuario busca un módulo de Odoo {version} que resuelva su necesidad.

**Módulos candidatos:**
{modules_context}

**Tarea:**
Evalúa qué tan relevante es CADA módulo para esta búsqueda específica.
Considera:
1. ¿El módulo resuelve el caso de uso exacto que el usuario describe?
2. ¿Es la funcionalidad principal del módulo o solo una feature secundaria?
3. ¿Qué tan bien coincide con la INTENCIÓN (no solo keywords)?

Asigna un score de 0-100 a cada módulo:
- 90-100: Perfecto match, resuelve exactamente la necesidad
- 70-89: Muy relevante, funcionalidad principal
- 50-69: Relevante, pero no ideal
- 30-49: Marginalmente relacionado
- 0-29: No relevante

**Responde SOLO con JSON válido:**
[
  {{"technical_name": "module_1", "score": 95, "reason": "Razón breve"}},
  {{"technical_name": "module_2", "score": 78, "reason": "Razón breve"}},
  ...
]

No incluyas explicaciones fuera del JSON. Solo el array JSON."""

    def __init__(self, api_key: str):
        """Inicializa servicio."""
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-haiku-20240307"
        self.max_tokens = 2000
        self.temperature = 0  # Deterministic for consistency

        # Cost tracking
        self.total_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    async def rerank(
        self,
        query: str,
        candidates: List[Dict],
        version: str = "16.0",
        limit: int = 10
    ) -> List[RerankResult]:
        """
        Reordena candidatos usando LLM.

        Args:
            query: Query original del usuario
            candidates: Lista de resultados del hybrid search
            version: Versión Odoo
            limit: Top N a retornar

        Returns:
            Lista reordenada de RerankResult
        """

        if not candidates:
            return []

        # Build context for LLM
        modules_context = self._build_modules_context(candidates)

        # Build prompt
        prompt = self.PROMPT_TEMPLATE.format(
            query=query,
            version=version,
            modules_context=modules_context
        )

        logger.info(f"Reranking {len(candidates)} candidates for query: {query}")

        try:
            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Track costs
            self.total_requests += 1
            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens

            # Parse response
            llm_scores = self._parse_llm_response(response.content[0].text)

            # Merge scores with candidates
            reranked = self._merge_and_sort(candidates, llm_scores)

            return reranked[:limit]

        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            # Fallback: return original order
            return self._fallback_results(candidates, limit)

    def _build_modules_context(self, candidates: List[Dict]) -> str:
        """Construye contexto de módulos para el LLM."""

        context_parts = []

        for i, module in enumerate(candidates, 1):
            # Truncate long descriptions
            description = module.get('ai_description') or module.get('summary') or ''
            description = description[:300]  # Max 300 chars

            tags = ', '.join(module.get('functional_tags', [])[:3])
            keywords = ', '.join(module.get('keywords', [])[:5])

            context = f"""
{i}. **{module['technical_name']}**
   - Name: {module.get('name', 'N/A')}
   - Summary: {module.get('summary', 'N/A')}
   - Description: {description}
   - Tags: {tags}
   - Keywords: {keywords}
"""
            context_parts.append(context.strip())

        return '\n\n'.join(context_parts)

    def _parse_llm_response(self, response_text: str) -> List[Dict]:
        """Parse JSON response from LLM."""

        try:
            # Extract JSON from response (might have extra text)
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON array found in response")

            json_str = response_text[start_idx:end_idx]
            scores = json.loads(json_str)

            return scores

        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.debug(f"Response text: {response_text}")
            return []

    def _merge_and_sort(
        self,
        candidates: List[Dict],
        llm_scores: List[Dict]
    ) -> List[RerankResult]:
        """Merge LLM scores with candidates and sort."""

        # Create lookup
        scores_lookup = {
            item['technical_name']: {
                'score': item['score'],
                'reason': item.get('reason', '')
            }
            for item in llm_scores
        }

        results = []

        for i, candidate in enumerate(candidates):
            tech_name = candidate['technical_name']

            llm_data = scores_lookup.get(tech_name, {'score': 0, 'reason': 'Not scored'})

            results.append(RerankResult(
                technical_name=tech_name,
                original_rank=i + 1,
                reranked_score=llm_data['score'],
                llm_reason=llm_data['reason'],
                name=candidate.get('name', ''),
                summary=candidate.get('summary', ''),
                ai_description=candidate.get('ai_description'),
                functional_tags=candidate.get('functional_tags', []),
                keywords=candidate.get('keywords', [])
            ))

        # Sort by reranked_score (descending)
        results.sort(key=lambda x: x.reranked_score, reverse=True)

        return results

    def _fallback_results(
        self,
        candidates: List[Dict],
        limit: int
    ) -> List[RerankResult]:
        """Fallback: return original order if reranking fails."""

        logger.warning("Using fallback: returning original order")

        return [
            RerankResult(
                technical_name=c['technical_name'],
                original_rank=i + 1,
                reranked_score=0,
                llm_reason='Reranking failed, original order',
                name=c.get('name', ''),
                summary=c.get('summary', ''),
                ai_description=c.get('ai_description'),
                functional_tags=c.get('functional_tags', []),
                keywords=c.get('keywords', [])
            )
            for i, c in enumerate(candidates[:limit])
        ]

    def get_cost_stats(self) -> Dict:
        """Get cost statistics."""

        # Claude Haiku pricing (as of Nov 2024)
        input_cost_per_1m = 0.25
        output_cost_per_1m = 1.25

        total_cost = (
            (self.total_input_tokens / 1_000_000) * input_cost_per_1m +
            (self.total_output_tokens / 1_000_000) * output_cost_per_1m
        )

        return {
            'total_requests': self.total_requests,
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_cost_usd': round(total_cost, 4),
            'avg_cost_per_request': round(total_cost / max(self.total_requests, 1), 4)
        }
```

---

## 🧪 Tests

```python
# tests/test_reranking_service.py

import pytest
from unittest.mock import Mock, patch
from app.services.reranking_service import RerankingService


class TestRerankingService:
    """Tests para reranking service."""

    @pytest.fixture
    def mock_anthropic(self):
        """Mock Claude API."""
        with patch('app.services.reranking_service.Anthropic') as mock:
            mock_response = Mock()
            mock_response.content = [Mock(text='''[
                {"technical_name": "module_1", "score": 95, "reason": "Perfect match"},
                {"technical_name": "module_2", "score": 60, "reason": "Related"}
            ]''')]
            mock_response.usage = Mock(input_tokens=1000, output_tokens=100)

            mock.return_value.messages.create.return_value = mock_response
            yield mock

    @pytest.mark.asyncio
    async def test_rerank_basic(self, mock_anthropic):
        """Test reranking básico."""

        service = RerankingService(api_key="test-key")

        candidates = [
            {'technical_name': 'module_1', 'name': 'Module 1', 'summary': 'Test'},
            {'technical_name': 'module_2', 'name': 'Module 2', 'summary': 'Test'}
        ]

        results = await service.rerank("test query", candidates)

        assert len(results) > 0
        # Should be sorted by score
        assert results[0].reranked_score >= results[1].reranked_score

    @pytest.mark.asyncio
    async def test_rerank_improves_order(self, mock_anthropic):
        """Test que reranking mejora orden."""

        # Mock response donde module_2 tiene mejor score
        mock_anthropic.return_value.messages.create.return_value.content = [
            Mock(text='''[
                {"technical_name": "module_2", "score": 95},
                {"technical_name": "module_1", "score": 60}
            ]''')
        ]

        service = RerankingService(api_key="test-key")

        # Original order: module_1 first
        candidates = [
            {'technical_name': 'module_1', 'name': 'Module 1'},
            {'technical_name': 'module_2', 'name': 'Module 2'}
        ]

        results = await service.rerank("query", candidates)

        # After reranking: module_2 should be first
        assert results[0].technical_name == 'module_2'

    def test_cost_tracking(self, mock_anthropic):
        """Test que trackea costos."""

        service = RerankingService(api_key="test-key")

        service.rerank("query", [{'technical_name': 'test'}])

        stats = service.get_cost_stats()

        assert stats['total_requests'] > 0
        assert stats['total_cost_usd'] > 0
```

---

## ✅ Criterios de Aceptación

- ✅ Servicio implementado y funcional
- ✅ Parse JSON response correctamente
- ✅ Maneja errores con fallback
- ✅ Cost tracking funcional
- ✅ Tests passing

---

## 🔗 Siguiente Paso

→ [SPEC-302: Prompt Engineering](./SPEC-302-prompt-engineering.md)

---

**Estado:** 🔴 Pendiente
