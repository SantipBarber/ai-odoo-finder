# SPEC-203: Functional Tagging System

**ID:** SPEC-203
**Componente:** Tagging Service
**Archivo:** `app/services/tagging_service.py`
**Prioridad:** Alta
**Estimación:** 2 horas
**Dependencias:** SPEC-201

---

## 📋 Descripción

Sistema de tagging automático que asigna tags funcionales a módulos basándose en reglas y patterns, mejorando la categorización y búsqueda.

---

## 🏷️ Taxonomy de Tags

```yaml
# config/functional_tags_taxonomy.yaml

categories:
  sales_workflow:
    keywords: [sale, quotation, order, customer]
    technical_names: [sale_*, crm_*]

  accounting_finance:
    keywords: [account, invoice, payment, financial]
    technical_names: [account_*, l10n_*]

  inventory_logistics:
    keywords: [stock, warehouse, delivery, inventory]
    technical_names: [stock_*, delivery_*, warehouse_*]

  manufacturing:
    keywords: [mrp, manufacturing, production, bom]
    technical_names: [mrp_*, production_*]

  hr_payroll:
    keywords: [employee, payroll, attendance, hr]
    technical_names: [hr_*, payroll_*]

  portal_website:
    keywords: [portal, website, ecommerce, web]
    technical_names: [portal_*, website_*, web_*]

  reporting:
    keywords: [report, dashboard, analytics, bi]
    technical_names: [report_*, mis_*, dashboard_*]

use_cases:
  b2b_commerce:
    keywords: [b2b, partner, wholesale]

  b2c_ecommerce:
    keywords: [b2c, ecommerce, shop, customer]

  subscription_management:
    keywords: [subscription, recurring, periodic]

  multi_company:
    keywords: [multi, company, consolidation]

  automation:
    keywords: [automatic, cron, scheduled, workflow]

  integration:
    keywords: [api, connector, import, export]
```

---

## 📐 Implementación

```python
"""
Functional Tagging Service.
"""
from typing import List, Dict, Set
import yaml
from pathlib import Path


class TaggingService:
    """Asigna tags funcionales a módulos."""

    def __init__(self, taxonomy_path: str = "config/functional_tags_taxonomy.yaml"):
        """Carga taxonomy de tags."""
        with open(taxonomy_path) as f:
            self.taxonomy = yaml.safe_load(f)

    def assign_tags(self, module: Dict) -> List[str]:
        """
        Asigna tags automáticamente basándose en reglas.

        Args:
            module: Diccionario con metadata del módulo

        Returns:
            Lista de tags asignados

        Rules:
        1. Category tags: Por technical_name pattern y keywords
        2. Use case tags: Por keywords en description
        3. Max 5 tags por módulo (ordenados por relevancia)
        """

        tags = set()

        # 1. Category tags
        tags.update(self._assign_category_tags(module))

        # 2. Use case tags
        tags.update(self._assign_use_case_tags(module))

        # 3. Technical tags
        tags.update(self._assign_technical_tags(module))

        # Sort by relevance and limit to 5
        sorted_tags = self._sort_by_relevance(list(tags), module)

        return sorted_tags[:5]

    def _assign_category_tags(self, module: Dict) -> Set[str]:
        """Asigna category tags por pattern matching."""

        tags = set()
        tech_name = module.get('technical_name', '').lower()
        name = module.get('name', '').lower()
        summary = module.get('summary', '').lower()
        all_text = f"{tech_name} {name} {summary}"

        for category, rules in self.taxonomy['categories'].items():
            # Check technical_name patterns
            for pattern in rules.get('technical_names', []):
                if self._matches_pattern(tech_name, pattern):
                    tags.add(category)
                    break

            # Check keywords
            keywords = rules.get('keywords', [])
            if any(kw in all_text for kw in keywords):
                tags.add(category)

        return tags

    def _assign_use_case_tags(self, module: Dict) -> Set[str]:
        """Asigna use case tags por keywords."""

        tags = set()
        description = module.get('ai_description', '') or module.get('readme', '') or ''
        description = description.lower()

        for use_case, rules in self.taxonomy.get('use_cases', {}).items():
            keywords = rules.get('keywords', [])
            if any(kw in description for kw in keywords):
                tags.add(use_case)

        return tags

    def _assign_technical_tags(self, module: Dict) -> Set[str]:
        """Asigna technical feature tags."""

        tags = set()
        depends = module.get('depends', [])
        description = (module.get('ai_description', '') or module.get('readme', '') or '').lower()

        # API integration
        if any(dep in depends for dep in ['base_rest', 'connector', 'api']) or 'api' in description:
            tags.add('api_integration')

        # Automation
        if 'cron' in depends or any(kw in description for kw in ['automatic', 'automation', 'scheduled']):
            tags.add('automation_workflow')

        return tags

    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Match pattern (supports wildcards with *)."""
        if '*' not in pattern:
            return text == pattern

        # Simple wildcard matching
        if pattern.endswith('*'):
            prefix = pattern[:-1]
            return text.startswith(prefix)
        elif pattern.startswith('*'):
            suffix = pattern[1:]
            return text.endswith(suffix)

        return False

    def _sort_by_relevance(self, tags: List[str], module: Dict) -> List[str]:
        """Ordena tags por relevancia (categories first, then use_cases)."""

        categories = list(self.taxonomy['categories'].keys())
        use_cases = list(self.taxonomy.get('use_cases', {}).keys())

        def tag_priority(tag):
            if tag in categories:
                return (0, categories.index(tag))
            elif tag in use_cases:
                return (1, use_cases.index(tag))
            else:
                return (2, 0)

        return sorted(tags, key=tag_priority)
```

---

## 🧪 Tests

```python
def test_assign_category_tags():
    """Test category tagging."""

    service = TaggingService()

    module = {
        'technical_name': 'sale_order_approval',
        'name': 'Sale Order Approval',
        'summary': 'Approval workflow for sales'
    }

    tags = service.assign_tags(module)

    assert 'sales_workflow' in tags


def test_assign_use_case_tags():
    """Test use case tagging."""

    service = TaggingService()

    module = {
        'technical_name': 'portal_b2b',
        'ai_description': 'This module provides B2B portal for wholesale customers'
    }

    tags = service.assign_tags(module)

    assert 'b2b_commerce' in tags
    assert 'portal_website' in tags


def test_max_5_tags():
    """Test que limita a 5 tags."""

    service = TaggingService()

    # Module that could match many tags
    module = {
        'technical_name': 'sale_stock_account_report',
        'summary': 'Sales stock accounting reports'
    }

    tags = service.assign_tags(module)

    assert len(tags) <= 5
```

---

## ✅ Criterios de Aceptación

- ✅ Taxonomy YAML creada
- ✅ Asigna 2-5 tags por módulo
- ✅ Pattern matching funciona
- ✅ Priority sorting correcto
- ✅ Tests passing

---

## 🔗 Siguiente Paso

→ [SPEC-204: Keywords Extraction](./SPEC-204-keywords-extraction.md)

---

**Estado:** 🔴 Pendiente
