#!/usr/bin/env python3
"""
Generate enrichment data for modules using Claude API in batches.
Processes 750 modules with descriptions, tags, and keywords.
"""

import json
import sys
import os
import subprocess
import anthropic
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Define available functional tags
FUNCTIONAL_TAGS = [
    "sales", "accounting", "inventory", "manufacturing", "hr", "website",
    "localization", "reporting", "integration", "automation", "crm", "purchase",
    "project", "pos", "b2b", "b2c", "multi_company", "subscription",
    "document_management", "compliance"
]

def get_modules(limit: int = 500) -> list:
    """Get modules needing enrichment."""
    try:
        result = subprocess.run(
            ["uv", "run", "python", "scripts/get_modules_for_enrichment.py", f"--limit", str(limit)],
            capture_output=True,
            text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )

        # Find JSON array in output - look for [ and find matching ]
        output = result.stdout
        json_start = output.find('[')
        if json_start == -1:
            print("❌ Could not find JSON start in output", file=sys.stderr)
            return []

        # Find the matching closing bracket
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
            print("❌ Could not find JSON end in output", file=sys.stderr)
            return []

        json_str = output[json_start:json_end]
        modules = json.loads(json_str)
        return modules
    except Exception as e:
        print(f"❌ Error getting modules: {e}", file=sys.stderr)
        return []

def get_inferred_tags(module: dict) -> list:
    """Infer tags based on module characteristics."""
    tags = []
    technical_name = module.get('technical_name', '').lower()
    repo_name = module.get('repo_name', '').lower()
    depends = [d.lower() for d in module.get('depends', [])]

    tag_mappings = {
        'sale': 'sales', 'invoice': 'accounting', 'account': 'accounting',
        'purchase': 'purchase', 'stock': 'inventory', 'mrp': 'manufacturing',
        'hr': 'hr', 'project': 'project', 'crm': 'crm', 'website': 'website',
        'pos': 'pos', 'l10n': 'localization', 'report': 'reporting',
        'api': 'integration', 'connector': 'integration', 'server': 'integration',
    }

    for key, tag in tag_mappings.items():
        if key in technical_name or key in repo_name or key in depends:
            if tag not in tags:
                tags.append(tag)

    return tags[:5] if tags else ['integration']

def generate_batch_enrichments(modules: list, batch_size: int = 10) -> list:
    """Generate enrichments in batches using Claude API."""
    client = anthropic.Anthropic()
    enrichments = []
    failed = []

    for batch_num in range(0, len(modules), batch_size):
        batch = modules[batch_num:batch_num + batch_size]
        batch_index = batch_num // batch_size + 1
        batch_pct = (batch_num / len(modules)) * 100
        print(f"\n📦 Batch {batch_index}: Processing {len(batch)} modules ({batch_pct:.1f}%)", file=sys.stderr)

        # Create batch prompt with module details
        batch_prompt = """Generate enrichment data for these Odoo modules. For each module, provide:
1. ai_description: 2-3 sentences about functionality, use cases, and integration
2. functional_tags: 2-5 tags from the list
3. keywords: 5-10 relevant search terms

Available tags: sales, accounting, inventory, manufacturing, hr, website, localization, reporting, integration, automation, crm, purchase, project, pos, b2b, b2c, multi_company, subscription, document_management, compliance

Modules:
"""
        for mod in batch:
            batch_prompt += f"\nID {mod['id']} - {mod.get('technical_name')}:\n"
            batch_prompt += f"  Name: {mod.get('name', 'N/A')}\n"
            batch_prompt += f"  Version: {mod.get('version', 'N/A')}\n"
            batch_prompt += f"  Summary: {mod.get('summary', 'N/A')}\n"
            batch_prompt += f"  Dependencies: {', '.join(mod.get('depends', []))}\n"
            if mod.get('readme_preview'):
                preview = mod['readme_preview'][:400].replace('\n', ' ')
                batch_prompt += f"  Preview: {preview}\n"

        batch_prompt += """

Return a JSON array with exactly this structure for each module:
[
  {
    "id": <number>,
    "ai_description": "<description>",
    "functional_tags": ["tag1", "tag2"],
    "keywords": ["keyword1", "keyword2", ...]
  }
]

Return ONLY the JSON array, no explanation or markdown."""

        try:
            message = client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": batch_prompt}
                ]
            )

            response_text = message.content[0].text.strip()

            # Extract JSON from response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                batch_enrichments = json.loads(response_text[json_start:json_end])
                enrichments.extend(batch_enrichments)
                print(f"  ✅ Processed {len(batch_enrichments)}/{len(batch)} modules", file=sys.stderr)
            else:
                raise ValueError("No JSON array found in response")

        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON parse error: {e}", file=sys.stderr)
            # Fallback: create enrichments with inferred tags
            for mod in batch:
                enrichments.append({
                    "id": mod['id'],
                    "ai_description": f"{mod.get('name', 'Module')} extends Odoo's {mod.get('repo_name', 'core')} functionality. It depends on {', '.join(mod.get('depends', ['base']))}.",
                    "functional_tags": get_inferred_tags(mod),
                    "keywords": [mod.get('technical_name', ''), mod.get('repo_name', ''), 'odoo']
                })
                failed.append(mod.get('technical_name'))

        except Exception as e:
            print(f"  ⚠️ API error: {e}", file=sys.stderr)
            # Fallback: create enrichments with inferred tags
            for mod in batch:
                enrichments.append({
                    "id": mod['id'],
                    "ai_description": f"{mod.get('name', 'Module')} extends Odoo's {mod.get('repo_name', 'core')} functionality.",
                    "functional_tags": get_inferred_tags(mod),
                    "keywords": [mod.get('technical_name', ''), mod.get('repo_name', '')]
                })
                failed.append(mod.get('technical_name'))

    return enrichments, failed

def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 500

    print(f"📦 Getting {limit} modules...", file=sys.stderr)
    modules = get_modules(limit)

    if not modules:
        print("❌ No modules found", file=sys.stderr)
        sys.exit(1)

    print(f"📦 Got {len(modules)} modules", file=sys.stderr)
    print(f"🔄 Generating enrichments in batches of 10...", file=sys.stderr)

    enrichments, failed = generate_batch_enrichments(modules, batch_size=10)

    print(f"\n✅ Generated {len(enrichments)} enrichments", file=sys.stderr)
    if failed:
        print(f"⚠️  {len(failed)} modules used fallback enrichment", file=sys.stderr)

    # Output as JSON to stdout
    print(json.dumps(enrichments, indent=2))

if __name__ == "__main__":
    main()
