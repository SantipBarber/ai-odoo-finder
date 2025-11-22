# SPEC-204: Keywords Extraction

**ID:** SPEC-204
**Componente:** Keywords Service
**Archivo:** `app/services/keyword_service.py`
**Prioridad:** Media
**Estimación:** 2 horas
**Dependencias:** SPEC-201

---

## 📋 Descripción

Extrae keywords relevantes de módulos usando TF-IDF y rules-based extraction para mejorar búsqueda por términos específicos.

---

## 📐 Implementación

```python
"""
Keyword Extraction Service.
"""
from typing import List, Dict, Set
from sklearn.feature_extraction.text import TfidfVectorizer
import re


class KeywordService:
    """Extrae keywords de módulos."""

    # Domain-specific keywords (Odoo terminology)
    DOMAIN_KEYWORDS = {
        'b2b', 'b2c', 'erp', 'crm', 'mrp', 'pos', 'ecommerce',
        'invoice', 'quotation', 'purchase', 'sales', 'stock',
        'warehouse', 'manufacturing', 'payroll', 'accounting',
        'portal', 'website', 'api', 'integration', 'automation',
        'workflow', 'approval', 'notification', 'report',
        'dashboard', 'analytics', 'export', 'import'
    }

    # Synonyms mapping (query term → module term)
    SYNONYMS = {
        'factura': 'invoice',
        'facturación': 'invoicing',
        'cotización': 'quotation',
        'presupuesto': 'quotation',
        'almacén': 'warehouse',
        'inventario': 'stock',
        'compras': 'purchase',
        'ventas': 'sales',
        'clientes': 'customers',
        'proveedores': 'suppliers'
    }

    def __init__(self):
        self.tfidf = TfidfVectorizer(
            max_features=20,
            stop_words='english',
            ngram_range=(1, 2),  # uni and bigrams
            min_df=1
        )

    def extract_keywords(
        self,
        module: Dict,
        max_keywords: int = 12
    ) -> List[str]:
        """
        Extrae keywords del módulo.

        Strategy:
        1. TF-IDF keywords del description
        2. Technical name tokens
        3. Domain keywords matching
        4. Synonym expansion

        Args:
            module: Metadata del módulo
            max_keywords: Máximo número de keywords

        Returns:
            Lista de keywords (lowercase, deduplicados)
        """

        keywords = set()

        # 1. From technical_name
        keywords.update(self._extract_from_technical_name(module))

        # 2. TF-IDF from text
        keywords.update(self._extract_tfidf_keywords(module))

        # 3. Domain keywords
        keywords.update(self._extract_domain_keywords(module))

        # 4. Add synonyms
        keywords = self._expand_with_synonyms(keywords)

        # Clean and limit
        keywords = self._clean_keywords(keywords)

        return list(keywords)[:max_keywords]

    def _extract_from_technical_name(self, module: Dict) -> Set[str]:
        """Extrae tokens del technical_name."""

        tech_name = module.get('technical_name', '')

        # Split by _ and remove common prefixes
        tokens = re.split(r'[_\-]', tech_name)
        tokens = [t for t in tokens if len(t) > 2]  # Remove short tokens

        # Remove common prefixes
        prefixes_to_remove = ['odoo', 'oca', 'l10n', 'base', 'web']
        tokens = [t for t in tokens if t not in prefixes_to_remove]

        return set(t.lower() for t in tokens)

    def _extract_tfidf_keywords(self, module: Dict) -> Set[str]:
        """Extrae keywords usando TF-IDF."""

        # Combine text fields
        text_fields = [
            module.get('name', ''),
            module.get('summary', ''),
            module.get('ai_description', ''),
            module.get('description', '')
        ]

        text = ' '.join(filter(None, text_fields))

        if not text:
            return set()

        try:
            # TF-IDF on single document (comparing against empty corpus)
            tfidf_matrix = self.tfidf.fit_transform([text])
            feature_names = self.tfidf.get_feature_names_out()

            # Get top features
            scores = tfidf_matrix.toarray()[0]
            top_indices = scores.argsort()[-10:][::-1]

            keywords = [feature_names[i] for i in top_indices if scores[i] > 0]

            return set(kw.lower() for kw in keywords)

        except:
            return set()

    def _extract_domain_keywords(self, module: Dict) -> Set[str]:
        """Match domain-specific keywords."""

        keywords = set()

        # Combine all text
        all_text = ' '.join([
            module.get('technical_name', ''),
            module.get('name', ''),
            module.get('summary', ''),
            module.get('ai_description', '')
        ]).lower()

        # Check domain keywords
        for keyword in self.DOMAIN_KEYWORDS:
            if keyword in all_text:
                keywords.add(keyword)

        return keywords

    def _expand_with_synonyms(self, keywords: Set[str]) -> Set[str]:
        """Expande keywords con sinónimos."""

        expanded = keywords.copy()

        # Add English equivalents of Spanish terms if found
        for synonym_source, synonym_target in self.SYNONYMS.items():
            if synonym_source in keywords:
                expanded.add(synonym_target)

        return expanded

    def _clean_keywords(self, keywords: Set[str]) -> List[str]:
        """Limpia y filtra keywords."""

        cleaned = []

        for kw in keywords:
            # Remove very short or very long
            if len(kw) < 3 or len(kw) > 30:
                continue

            # Remove numbers-only
            if kw.isdigit():
                continue

            # Remove special chars
            if not re.match(r'^[a-z0-9_\-]+$', kw):
                continue

            cleaned.append(kw)

        # Sort by length (shorter = more general = higher priority)
        return sorted(cleaned, key=len)
```

---

## 🧪 Tests

```python
def test_extract_from_technical_name():
    """Test extracción del technical_name."""

    service = KeywordService()

    module = {'technical_name': 'sale_subscription_recurring'}

    keywords = service._extract_from_technical_name(module)

    assert 'sale' in keywords
    assert 'subscription' in keywords
    assert 'recurring' in keywords


def test_domain_keywords():
    """Test matching de domain keywords."""

    service = KeywordService()

    module = {
        'summary': 'B2B portal for suppliers',
        'ai_description': 'API integration with ecommerce'
    }

    keywords = service._extract_domain_keywords(module)

    assert 'b2b' in keywords
    assert 'api' in keywords
    assert 'ecommerce' in keywords


def test_max_keywords_limit():
    """Test límite de keywords."""

    service = KeywordService()

    module = {
        'technical_name': 'test_module',
        'summary': 'Long description with many words...'
    }

    keywords = service.extract_keywords(module, max_keywords=5)

    assert len(keywords) <= 5
```

---

## ✅ Criterios de Aceptación

- ✅ Extrae 8-12 keywords por módulo
- ✅ TF-IDF funciona
- ✅ Domain keywords matching
- ✅ Synonym expansion
- ✅ Keywords limpios (sin special chars)

---

## 🔗 Siguiente Paso

→ [SPEC-205: Enrichment Pipeline](./SPEC-205-enrichment-pipeline.md)

---

**Estado:** 🔴 Pendiente
