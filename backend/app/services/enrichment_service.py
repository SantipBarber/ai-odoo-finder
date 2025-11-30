"""
Enrichment Service - Generate AI descriptions, tags, and keywords for Odoo modules.
Uses OpenRouter API with Grok-4-fast model.
"""

import json
import time
from typing import Dict, List, Optional, Tuple

import requests

from ..config import get_settings

settings = get_settings()

# Functional tags available for categorization
FUNCTIONAL_TAGS = [
    "sales",
    "accounting",
    "inventory",
    "manufacturing",
    "hr",
    "website",
    "localization",
    "reporting",
    "integration",
    "automation",
    "crm",
    "purchase",
    "project",
    "pos",
    "b2b",
    "b2c",
    "multi_company",
    "subscription",
    "document_management",
    "compliance",
    "maintenance",
    "fleet",
    "helpdesk",
    "e-commerce",
    "marketing",
    "quality",
    "plm",
    "mrp",
    "wms",
]


class EnrichmentService:
    """Service to enrich Odoo modules with AI-generated metadata."""

    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "x-ai/grok-4-fast"  # Fast and cost-effective
        self.max_retries = 3
        self.retry_delay = 2

    def enrich_module(
        self,
        technical_name: str,
        name: str,
        summary: str,
        description: str,
        readme: Optional[str],
        depends: List[str],
        repo_name: str,
    ) -> Optional[Dict]:
        """
        Generate AI enrichment for a single module.

        Args:
            technical_name: Module technical name (e.g., 'sale_order_line_discount')
            name: Human-readable name
            summary: Short summary from manifest
            description: Full description from manifest
            readme: README content (truncated)
            depends: List of dependencies
            repo_name: OCA repository name

        Returns:
            Dict with ai_description, functional_tags, keywords, or None on error
        """
        # Build context for the LLM
        context_parts = [
            f"Technical name: {technical_name}",
            f"Name: {name}",
            f"Repository: OCA/{repo_name}",
        ]

        if summary:
            context_parts.append(f"Summary: {summary}")
        if description:
            # Limit description to avoid token overflow
            desc_preview = description[:1500] if len(description) > 1500 else description
            context_parts.append(f"Description: {desc_preview}")
        if readme:
            # Limit README
            readme_preview = readme[:1000] if len(readme) > 1000 else readme
            context_parts.append(f"README excerpt: {readme_preview}")
        if depends:
            context_parts.append(f"Dependencies: {', '.join(depends[:15])}")

        module_context = "\n".join(context_parts)

        prompt = f"""Analyze this Odoo module and generate enrichment data.

MODULE INFORMATION:
{module_context}

Generate a JSON response with:
1. "ai_description": A clear, searchable description in English (2-3 sentences). Explain what the module does, typical use cases, and how it helps users. Use terms that people would search for.
2. "functional_tags": 2-5 tags from this list: {", ".join(FUNCTIONAL_TAGS)}
3. "keywords": 5-10 search keywords in English (lowercase, single words or short phrases)

Respond with ONLY valid JSON, no markdown, no explanation:
{{"ai_description": "...", "functional_tags": ["...", "..."], "keywords": ["...", "..."]}}"""

        # Call the API with retries
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/OCA",
                        "X-Title": "AI-OdooFinder ETL",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert in Odoo ERP modules. Generate concise, accurate metadata for module search optimization. Always respond with valid JSON only.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.3,  # Low temperature for consistent output
                        "max_tokens": 500,
                    },
                    timeout=30,
                )

                response.raise_for_status()
                data = response.json()

                # Extract content
                content = data["choices"][0]["message"]["content"].strip()

                # Parse JSON (handle potential markdown code blocks)
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()

                result = json.loads(content)

                # Validate and sanitize
                return self._validate_enrichment(result)

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"      ⚠️  Enrichment API error: {e}")
                    return None

            except json.JSONDecodeError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    print(f"      ⚠️  Enrichment JSON parse error: {e}")
                    return None

            except Exception as e:
                print(f"      ⚠️  Enrichment unexpected error: {e}")
                return None

        return None

    def _validate_enrichment(self, result: Dict) -> Dict:
        """Validate and sanitize enrichment result."""
        validated = {}

        # ai_description
        ai_desc = result.get("ai_description", "")
        if isinstance(ai_desc, str) and len(ai_desc) > 10:
            validated["ai_description"] = ai_desc[:2000]  # Limit length
        else:
            validated["ai_description"] = None

        # functional_tags
        tags = result.get("functional_tags", [])
        if isinstance(tags, list):
            # Filter to valid tags only
            valid_tags = [
                t.lower() for t in tags if isinstance(t, str) and t.lower() in FUNCTIONAL_TAGS
            ]
            validated["functional_tags"] = valid_tags[:5]  # Max 5 tags
        else:
            validated["functional_tags"] = []

        # keywords
        keywords = result.get("keywords", [])
        if isinstance(keywords, list):
            # Sanitize keywords
            valid_keywords = [
                k.lower().strip()[:50]  # Lowercase, limit length
                for k in keywords
                if isinstance(k, str) and len(k.strip()) > 2
            ]
            validated["keywords"] = valid_keywords[:10]  # Max 10 keywords
        else:
            validated["keywords"] = []

        return validated

    def generate_fallback_enrichment(
        self, technical_name: str, name: str, summary: str, depends: List[str]
    ) -> Dict:
        """
        Generate basic enrichment without AI when API fails.
        Uses heuristics based on module name and dependencies.
        """
        # Infer tags from technical name and dependencies
        tags = set()
        text = (technical_name + " " + (summary or "") + " " + " ".join(depends or [])).lower()

        tag_keywords = {
            "sale": ["sales", "b2b"],
            "account": ["accounting"],
            "invoice": ["accounting", "reporting"],
            "stock": ["inventory"],
            "purchase": ["purchase", "b2b"],
            "hr": ["hr"],
            "website": ["website", "b2c"],
            "pos": ["pos"],
            "project": ["project"],
            "crm": ["crm", "sales"],
            "report": ["reporting"],
            "mrp": ["manufacturing", "mrp"],
            "quality": ["quality"],
            "maintenance": ["maintenance"],
            "fleet": ["fleet"],
            "helpdesk": ["helpdesk"],
            "l10n": ["localization"],
        }

        for keyword, tag_list in tag_keywords.items():
            if keyword in text:
                tags.update(tag_list)

        if not tags:
            tags.add("integration")

        # Generate basic keywords from technical name
        keywords = set()
        for part in technical_name.split("_"):
            if len(part) > 3:
                keywords.add(part)
        for word in name.split():
            if len(word) > 3:
                keywords.add(word.lower())

        return {
            "ai_description": None,  # No AI description in fallback
            "functional_tags": list(tags)[:5],
            "keywords": list(keywords)[:10],
        }


# Singleton
_enrichment_service = None


def get_enrichment_service() -> EnrichmentService:
    """Get singleton instance of EnrichmentService."""
    global _enrichment_service
    if _enrichment_service is None:
        _enrichment_service = EnrichmentService()
    return _enrichment_service
