# SPEC-202: AI Description Generator

**ID:** SPEC-202
**Componente:** AI Content Generation
**Archivo:** `app/services/ai_description_service.py`
**Prioridad:** Alta
**Estimación:** 3 horas
**Dependencias:** SPEC-201

---

## 📋 Descripción

Servicio que genera descripciones ricas y útiles para módulos con poca documentación usando Claude Haiku, optimizado para cost-efficiency y calidad.

---

## 🎯 Objetivos

1. **Generar descripciones** de 2-3 párrafos para módulos sin README
2. **Cost-efficient:** Usar Claude Haiku (~$0.001/descripción)
3. **Batch processing:** Con rate limit handling
4. **Quality control:** Validación automática de calidad

---

## 📐 Implementación

### Clase Principal

```python
"""
AI Description Service using Claude Haiku.
"""
from typing import Dict, List, Optional
from anthropic import Anthropic
import time
import logging

logger = logging.getLogger(__name__)


class AIDescriptionService:
    """Genera descripciones de módulos con Claude Haiku."""

    PROMPT_TEMPLATE = """Eres un experto en Odoo ERP. Genera una descripción técnica y útil para este módulo Odoo:

**Información del módulo:**
- Technical Name: {technical_name}
- Name: {name}
- Summary: {summary}
- Dependencies: {depends}
- Version: {version}
- Category: {category}

**Instrucciones:**
1. Escribe 2-3 párrafos (150-300 palabras)
2. Incluye:
   - Qué funcionalidad proporciona
   - Casos de uso típicos
   - Integraciones clave con otros módulos Odoo
3. Usa terminología que usuarios buscarían (no solo jerga técnica)
4. Menciona conceptos clave y keywords relevantes
5. NO uses markdown, bullet points, ni títulos - solo texto corrido

**Ejemplo de buena descripción:**
"Este módulo proporciona gestión avanzada de suscripciones recurrentes para empresas B2B y B2C. Permite crear productos con facturación automática mensual, trimestral o anual, integrándose completamente con el módulo de contabilidad para generar facturas automáticamente. Es ideal para empresas SaaS, servicios de consultoría con retainers, o cualquier negocio con ingresos recurrentes. El módulo se integra con el portal de clientes permitiendo que los usuarios gestionen sus suscripciones directamente."

Ahora genera la descripción para el módulo proporcionado:"""

    def __init__(self, api_key: str):
        """
        Inicializa el servicio.

        Args:
            api_key: Anthropic API key
        """
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-haiku-20240307"
        self.max_tokens = 500
        self.temperature = 0.7

    def generate_description(
        self,
        module: Dict,
        retry_count: int = 3
    ) -> Optional[str]:
        """
        Genera descripción para un módulo.

        Args:
            module: Dict con metadata del módulo
            retry_count: Intentos en caso de error

        Returns:
            Descripción generada o None si falla

        Example:
            >>> service = AIDescriptionService(api_key="...")
            >>> module = {
            ...     "technical_name": "sale_subscription",
            ...     "name": "Sale Subscription",
            ...     "summary": "Recurring invoices",
            ...     "depends": ["sale", "account"],
            ...     "version": "16.0",
            ...     "category": "Sales"
            ... }
            >>> description = service.generate_description(module)
        """

        prompt = self._build_prompt(module)

        for attempt in range(retry_count):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )

                description = response.content[0].text.strip()

                # Quality validation
                if self._validate_quality(description, module):
                    logger.info(f"Generated description for {module['technical_name']}")
                    return description
                else:
                    logger.warning(f"Low quality description for {module['technical_name']}, retrying...")
                    continue

            except Exception as e:
                logger.error(f"Error generating description (attempt {attempt + 1}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return None

        return None

    def generate_batch(
        self,
        modules: List[Dict],
        batch_size: int = 10,
        delay_between_batches: float = 1.0
    ) -> List[Dict]:
        """
        Genera descripciones para múltiples módulos con rate limiting.

        Args:
            modules: Lista de módulos
            batch_size: Módulos por batch
            delay_between_batches: Delay en segundos entre batches

        Returns:
            Lista de módulos con ai_description añadido
        """

        results = []
        total = len(modules)

        for i in range(0, total, batch_size):
            batch = modules[i:i + batch_size]

            logger.info(f"Processing batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}")

            for module in batch:
                description = self.generate_description(module)

                if description:
                    module['ai_description'] = description
                    module['enrichment_metadata'] = {
                        'enriched_at': time.time(),
                        'model_used': self.model,
                        'generation_successful': True
                    }
                else:
                    module['ai_description'] = None
                    module['enrichment_metadata'] = {
                        'enriched_at': time.time(),
                        'model_used': self.model,
                        'generation_successful': False,
                        'error': 'Quality validation failed or API error'
                    }

                results.append(module)

            # Rate limiting
            if i + batch_size < total:
                time.sleep(delay_between_batches)

        return results

    def _build_prompt(self, module: Dict) -> str:
        """Construye prompt con metadata del módulo."""

        return self.PROMPT_TEMPLATE.format(
            technical_name=module.get('technical_name', 'N/A'),
            name=module.get('name', 'N/A'),
            summary=module.get('summary', 'N/A'),
            depends=', '.join(module.get('depends', [])) or 'None',
            version=module.get('version', 'N/A'),
            category=module.get('category', 'Uncategorized')
        )

    def _validate_quality(self, description: str, module: Dict) -> bool:
        """
        Valida calidad de la descripción generada.

        Quality checks:
        - Length: 150-600 words
        - Contains module name or technical_name
        - No markdown formatting (##, **, etc.)
        - Meaningful content (not just repeating summary)
        """

        # Length check
        word_count = len(description.split())
        if word_count < 50 or word_count > 600:
            logger.warning(f"Description length {word_count} out of range [50-600]")
            return False

        # Contains relevant terms
        tech_name = module.get('technical_name', '').lower()
        name = module.get('name', '').lower()

        description_lower = description.lower()

        # Should mention module or its domain
        if not any(term in description_lower for term in [tech_name, name, 'odoo', 'module']):
            logger.warning("Description doesn't mention module or relevant terms")
            return False

        # Should not have markdown
        if any(md in description for md in ['##', '**', '- ', '* ', '1.', '2.']):
            logger.warning("Description contains markdown formatting")
            return False

        # Should be different from summary
        summary = module.get('summary', '').lower()
        if summary and summary in description_lower:
            # OK if it expands on summary, not OK if it's ONLY the summary
            if len(description) < len(summary) * 2:
                logger.warning("Description is too similar to summary")
                return False

        return True
```

---

## 🧪 Tests

```python
# tests/test_ai_description_service.py

import pytest
from unittest.mock import Mock, patch
from app.services.ai_description_service import AIDescriptionService


class TestAIDescriptionService:
    """Tests para AI Description Service."""

    @pytest.fixture
    def mock_anthropic(self):
        """Mock Anthropic client."""
        with patch('app.services.ai_description_service.Anthropic') as mock:
            # Mock response
            mock_response = Mock()
            mock_response.content = [Mock(text="Este módulo proporciona gestión de suscripciones recurrentes...")]

            mock.return_value.messages.create.return_value = mock_response

            yield mock

    def test_generate_description_success(self, mock_anthropic):
        """Test generación exitosa."""

        service = AIDescriptionService(api_key="test-key")

        module = {
            'technical_name': 'sale_subscription',
            'name': 'Sale Subscription',
            'summary': 'Recurring invoices',
            'depends': ['sale', 'account'],
            'version': '16.0',
            'category': 'Sales'
        }

        description = service.generate_description(module)

        assert description is not None
        assert len(description) > 50
        assert 'suscripciones' in description.lower() or 'subscription' in description.lower()

    def test_quality_validation_length(self):
        """Test validación de longitud."""

        service = AIDescriptionService(api_key="test-key")

        module = {'technical_name': 'test', 'name': 'Test'}

        # Too short
        assert not service._validate_quality("Too short", module)

        # Too long
        long_text = " ".join(["word"] * 1000)
        assert not service._validate_quality(long_text, module)

        # Good length
        good_text = " ".join(["This is a good description"] * 20)
        assert service._validate_quality(good_text, module)

    def test_quality_validation_markdown(self):
        """Test que rechaza markdown."""

        service = AIDescriptionService(api_key="test-key")

        module = {'technical_name': 'test', 'name': 'Test Module'}

        # Contains markdown
        markdown_text = "## Header\n\nThis is a **bold** description with - bullets"
        assert not service._validate_quality(markdown_text, module)

    def test_batch_processing(self, mock_anthropic):
        """Test procesamiento por lotes."""

        service = AIDescriptionService(api_key="test-key")

        modules = [
            {'technical_name': f'module_{i}', 'name': f'Module {i}',
             'summary': 'Test', 'depends': [], 'version': '16.0'}
            for i in range(5)
        ]

        results = service.generate_batch(modules, batch_size=2, delay_between_batches=0.1)

        assert len(results) == 5
        assert all('ai_description' in m for m in results)
```

---

## ✅ Criterios de Aceptación

- ✅ Servicio genera descripciones válidas
- ✅ Quality validation funciona
- ✅ Batch processing con rate limiting
- ✅ Error handling con retry
- ✅ Tests passing

---

## 💰 Cost Estimation

```
Claude Haiku pricing: ~$0.25 per million input tokens
                      ~$1.25 per million output tokens

Prompt: ~300 tokens
Output: ~300 tokens
Cost per description: ~$0.0008

For 1,000 modules: ~$0.80
For 2,500 modules: ~$2.00

Budget: $5-10 total
```

---

## 🔗 Siguiente Paso

→ [SPEC-203: Functional Tagging System](./SPEC-203-functional-tagging.md)

---

**Estado:** 🔴 Pendiente
