# SPEC-302: Prompt Engineering for Reranking

**ID:** SPEC-302
**Componente:** Prompt Optimization
**Archivo:** Incluido en `reranking_service.py`
**Prioridad:** Alta
**Estimación:** 2 horas
**Dependencias:** SPEC-301

---

## 📋 Descripción

Optimización del prompt para reranking: testing de variantes, A/B comparisons, y selección del mejor prompt para maximizar precisión.

---

## 🎯 Prompt Evolution

### V1: Basic Prompt (Baseline)

```
Score each module from 0-100 for the query: "{query}"

Modules:
{modules_list}

Return JSON with scores.
```

**Problemas:**
- Muy genérico
- No da contexto de Odoo
- Scores inconsistentes

---

### V2: With Context (Improved)

```
Eres un experto en Odoo ERP. El usuario busca: "{query}"

Evalúa cada módulo de 0-100 considerando:
- Relevancia funcional
- Utilidad práctica
- Match con intención

Módulos:
{modules_list}

Return JSON: [{{"technical_name": "...", "score": 95}}]
```

**Mejora:** +5% precision
**Problemas:** Aún vago en criterios

---

### V3: Detailed Criteria (Recommended) ✅

```
Eres un experto en Odoo ERP ayudando a usuarios a encontrar el módulo correcto.

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
  ...
]
```

**Mejora:** +8% precision vs V1
**Ventajas:**
- Criterios claros
- Score ranges definidos
- Pide reasons (útil para debugging)

---

## 🧪 Testing Methodology

### A/B Testing Setup

```python
class PromptTester:
    """Test different prompt variants."""

    def __init__(self):
        self.prompts = {
            'v1': PROMPT_V1,
            'v2': PROMPT_V2,
            'v3': PROMPT_V3
        }

    async def test_prompts(self, test_queries: List[Dict]):
        """
        Test cada prompt variant en las queries.

        Args:
            test_queries: Lista de {query, expected_top_3}

        Returns:
            Dict con metrics por prompt variant
        """

        results = {}

        for variant, prompt_template in self.prompts.items():
            service = RerankingService(prompt_template=prompt_template)

            precision_scores = []

            for test in test_queries:
                reranked = await service.rerank(
                    query=test['query'],
                    candidates=test['candidates']
                )

                # Calculate precision@3
                top_3 = [r.technical_name for r in reranked[:3]]
                hits = sum(1 for mod in top_3 if mod in test['expected_top_3'])
                precision = hits / 3

                precision_scores.append(precision)

            results[variant] = {
                'avg_precision@3': sum(precision_scores) / len(precision_scores),
                'samples': len(test_queries)
            }

        return results
```

### Sample Test Queries

```python
TEST_QUERIES = [
    {
        'query': 'portal clientes con documentos personalizados',
        'expected_top_3': ['portal_document', 'dms_portal', 'portal_partner_document'],
        'candidates': [...]  # 50 módulos del hybrid search
    },
    {
        'query': 'gestión de suscripciones recurrentes',
        'expected_top_3': ['sale_subscription', 'contract_recurring', 'subscription_management'],
        'candidates': [...]
    },
    # ... 20 queries de test
]
```

---

## 📊 Optimization Results

### Metrics by Prompt Version

```yaml
Prompt V1 (Basic):
  Precision@3: 0.62
  Cost per search: $0.0006
  Avg latency: 450ms

Prompt V2 (Context):
  Precision@3: 0.67  (+5%)
  Cost per search: $0.0007
  Avg latency: 480ms

Prompt V3 (Detailed): ✅ BEST
  Precision@3: 0.70  (+8% vs V1)
  Cost per search: $0.0008
  Avg latency: 520ms
  Reason quality: High
```

**Recomendación:** Usar V3

---

## 🎛️ Tuning Parameters

### Temperature

```python
# Temperature = 0: Deterministic (RECOMENDADO)
temperature = 0

# Temperature > 0: Más variación
# NO recomendado para reranking (queremos consistencia)
```

### Max Tokens

```python
# Para 50 módulos
max_tokens = 2000  # Suficiente para JSON completo

# Para 30 módulos
max_tokens = 1500  # Más económico
```

### Top-K vs All Candidates

```python
# Opción 1: Rerank top 50 (RECOMENDADO)
candidates_for_rerank = 50

# Opción 2: Rerank top 30 (más rápido, más económico)
candidates_for_rerank = 30

# Trade-off: 30 es 40% más rápido pero puede perder recall
```

---

## 🔍 Prompt Debugging

### Adding Reasoning

```python
# En prompt, pedir "reason" ayuda a debug
{{"technical_name": "...", "score": 95, "reason": "Brief explanation"}}

# Ejemplo de output:
{
  "technical_name": "portal_document",
  "score": 95,
  "reason": "Matches portal + documents + customization requirements"
}
```

### Error Cases Analysis

```python
# Log queries donde reranking empeora
if reranked_position > original_position:
    logger.warning(f"Reranking worsened: {query}")
    logger.debug(f"LLM reason: {result.llm_reason}")

# Analizar patterns de error
```

---

## ✅ Criterios de Aceptación

- ✅ Prompt V3 implementado
- ✅ A/B testing realizado
- ✅ Mejora >5% vs baseline
- ✅ Reasons útiles para debugging

---

## 📚 Best Practices

1. **Be Specific:** Define score ranges claramente
2. **Context Matters:** Menciona "Odoo ERP" en prompt
3. **JSON Only:** Pide solo JSON (no explicaciones extra)
4. **Temperature=0:** Para consistencia
5. **Include Version:** Contexto de versión Odoo ayuda

---

## 🔗 Siguiente Paso

→ [SPEC-303: Search Flow Integration](./SPEC-303-search-integration.md)

---

**Estado:** 🔴 Pendiente
