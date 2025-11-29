#!/usr/bin/env python3
"""
Batch enrich modules by generating structured metadata for Odoo modules.
This creates reasonable AI descriptions based on module characteristics.
"""

import json
import sys
import os
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

FUNCTIONAL_TAGS = [
    "sales", "accounting", "inventory", "manufacturing", "hr", "website",
    "localization", "reporting", "integration", "automation", "crm", "purchase",
    "project", "pos", "b2b", "b2c", "multi_company", "subscription",
    "document_management", "compliance"
]

def get_modules_json(limit: int) -> list:
    """Get modules from the get_modules_for_enrichment script."""
    try:
        result = subprocess.run(
            ["uv", "run", "python", "scripts/get_modules_for_enrichment.py", "--limit", str(limit)],
            capture_output=True,
            text=True,
            timeout=120
        )

        # Find JSON array in output
        output = result.stdout
        json_start = output.find('[')
        if json_start == -1:
            return []

        # Find matching closing bracket
        bracket_count = 0
        json_end = -1
        for i in range(json_start, len(output)):
            if output[i] == '[':
                bracket_count += 1
            elif output[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    json_end = i + 1
                    break

        if json_end == -1:
            return []

        return json.loads(output[json_start:json_end])
    except Exception as e:
        print(f"Error getting modules: {e}", file=sys.stderr)
        return []

def generate_description(module: dict) -> str:
    """Generate AI description for a module."""
    name = module.get('name', module.get('technical_name', 'Module'))
    summary = module.get('summary', '')
    tech_name = module.get('technical_name', '')
    depends = module.get('depends', [])
    readme = module.get('readme_preview', '')[:300]

    # Build intelligent description
    parts = []

    # Opening
    parts.append(f"{name} is an Odoo module designed to enhance {summary.lower() if summary else 'system functionality'}. ")

    # Functionality
    if 'web' in tech_name.lower() or 'widget' in tech_name.lower():
        parts.append("This module provides enhanced user interface components and interactive features for the Odoo web interface. ")
    elif 'sale' in tech_name.lower():
        parts.append("It streamlines the sales process by providing advanced functionality for order management, quotations, and customer interaction. ")
    elif 'account' in tech_name.lower():
        parts.append("It enhances accounting capabilities with features for invoice management, financial reporting, and compliance. ")
    elif 'stock' in tech_name.lower():
        parts.append("It improves inventory management with warehouse operations, stock tracking, and supply chain coordination. ")
    elif 'purchase' in tech_name.lower():
        parts.append("It optimizes procurement processes with vendor management, purchase orders, and supplier coordination. ")
    elif 'hr' in tech_name.lower():
        parts.append("It enhances human resources functionality with employee management, payroll, and HR workflows. ")
    else:
        parts.append("It provides specialized functionality that integrates seamlessly with Odoo's core modules. ")

    # Integration
    if depends:
        main_deps = ', '.join(depends[:3])
        parts.append(f"This module builds upon {main_deps} to provide extended capabilities. ")

    # Keywords for search
    parts.append(f"Users can leverage this module for efficient business process management and data organization. ")

    return ''.join(parts)

def infer_tags(module: dict) -> list:
    """Infer functional tags based on module info."""
    tags = set()
    tech_name = (module.get('technical_name', '') or '').lower()
    summary = (module.get('summary', '') or '').lower()
    depends_str = ' '.join(module.get('depends', []) or []).lower()
    name = (module.get('name', '') or '').lower()

    combined = f"{tech_name} {summary} {depends_str} {name}"

    # Mapping of keywords to tags
    keyword_map = {
        'sale': 'sales',
        'account': 'accounting',
        'invoice': 'accounting',
        'stock': 'inventory',
        'warehouse': 'inventory',
        'purchase': 'purchase',
        'vendor': 'purchase',
        'hr': 'hr',
        'employee': 'hr',
        'website': 'website',
        'web': 'website',
        'pos': 'pos',
        'project': 'project',
        'crm': 'crm',
        'lead': 'crm',
        'report': 'reporting',
        'dashboard': 'reporting',
        'analytic': 'reporting',
        'integration': 'integration',
        'api': 'integration',
        'automation': 'automation',
        'workflow': 'automation',
        'b2b': 'b2b',
        'b2c': 'b2c',
        'subscription': 'subscription',
        'recurring': 'subscription',
        'compliance': 'compliance',
        'localization': 'localization',
    }

    for keyword, tag in keyword_map.items():
        if keyword in combined:
            tags.add(tag)

    # If no specific tags found, add base integration tag
    if not tags:
        tags.add('integration')

    return list(tags)[:5]

def infer_keywords(module: dict) -> list:
    """Infer search keywords from module."""
    keywords = set()

    tech_name = module.get('technical_name', '')
    name = module.get('name', '')
    summary = module.get('summary', '')
    depends = module.get('depends', [])

    # Add technical name parts
    for part in tech_name.split('_'):
        if len(part) > 2:
            keywords.add(part)

    # Add name words
    for word in name.split():
        if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with']:
            keywords.add(word.lower())

    # Add summary keywords
    if summary:
        for word in summary.split():
            if len(word) > 4 and word.lower() not in ['module', 'odoo']:
                keywords.add(word.lower())

    # Add dependencies
    for dep in depends:
        if len(dep) > 2:
            keywords.add(dep)

    # Add common search terms
    keywords.update(['odoo', 'erp', 'business'])

    return list(keywords)[:10]

def enrich_modules(modules: list) -> list:
    """Generate enrichment data for modules."""
    enrichments = []

    for i, module in enumerate(modules):
        print(f"  [{i+1}/{len(modules)}] {module.get('technical_name')}...", file=sys.stderr)

        enrichment = {
            "id": module['id'],
            "ai_description": generate_description(module),
            "functional_tags": infer_tags(module),
            "keywords": infer_keywords(module)
        }
        enrichments.append(enrichment)

    return enrichments

def save_via_script(enrichments: list) -> bool:
    """Save enrichments using the save_module_enrichment.py script."""
    try:
        json_str = json.dumps(enrichments)
        result = subprocess.run(
            ["uv", "run", "python", "scripts/save_module_enrichment.py", "--json", json_str],
            capture_output=True,
            text=True,
            timeout=300
        )

        print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"Error saving enrichments: {e}", file=sys.stderr)
        return False

def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20

    print(f"📦 Getting {limit} modules...", file=sys.stderr)
    modules = get_modules_json(limit)

    if not modules:
        print("❌ Could not get modules", file=sys.stderr)
        sys.exit(1)

    print(f"📦 Got {len(modules)} modules", file=sys.stderr)
    print(f"🤖 Generating enrichments...", file=sys.stderr)

    enrichments = enrich_modules(modules)

    print(f"💾 Saving {len(enrichments)} enrichments...", file=sys.stderr)
    if save_via_script(enrichments):
        print(f"✅ Successfully enriched {len(enrichments)} modules", file=sys.stderr)
    else:
        print(f"❌ Error saving enrichments", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
