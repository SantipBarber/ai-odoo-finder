# Enrich Odoo Modules

You are tasked with enriching Odoo module data with AI-generated descriptions, functional tags, and keywords.

**IMPORTANT: Execute all commands automatically without asking for confirmation. This is a safe, read-write operation on a local database.**

## Arguments
- `$ARGUMENTS` - Number of modules to process (default: 20)

## Instructions

Execute these steps automatically and sequentially:

### Step 1: Get modules needing enrichment

Run immediately without confirmation:

```bash
uv run python scripts/get_modules_for_enrichment.py --limit $ARGUMENTS
```

### Step 2: Generate enrichment for ALL modules

For EACH module in the JSON output, generate:

1. **ai_description** (English, 2-3 paragraphs):
   - What functionality does this module provide?
   - Typical use cases
   - Integration with other Odoo modules
   - Use searchable terms (not just technical jargon)

2. **functional_tags** (2-5 tags from this list):
   - `sales`, `accounting`, `inventory`, `manufacturing`, `hr`, `website`, `localization`, `reporting`, `integration`, `automation`, `crm`, `purchase`, `project`, `pos`
   - `b2b`, `b2c`, `multi_company`, `subscription`, `document_management`, `compliance`

3. **keywords** (5-10 relevant search terms in English)

### Step 3: Save ALL enrichments at once

Build a JSON array with ALL modules and save in a SINGLE command:

```bash
uv run python scripts/save_module_enrichment.py --json '[{"id": 123, "ai_description": "...", "functional_tags": ["sales"], "keywords": ["invoice"]}, ...]'
```

**DO NOT save one by one. Build the complete JSON array and execute ONE save command.**

### Step 4: Report progress

Show:
- Total modules processed
- Success/failure count
- Run: `uv run python scripts/get_modules_for_enrichment.py --stats`

## Example Output Format

For a module like `sale_subscription`:

```json
{
  "id": 123,
  "ai_description": "Sale Subscription manages recurring revenue through automated subscription billing in Odoo. It enables businesses to create subscription products with customizable billing periods (monthly, quarterly, yearly), automatic invoice generation, and renewal management. Key features include trial periods, proration for mid-cycle changes, and integration with the sales and accounting modules. Ideal for SaaS companies, membership organizations, and any business with recurring billing needs.",
  "functional_tags": ["sales", "accounting", "subscription", "automation"],
  "keywords": ["subscription", "recurring billing", "saas", "membership", "automatic invoicing", "renewal", "recurring revenue"]
}
```

## Important Notes

- Generate descriptions in **English** for better search compatibility
- Be concise but comprehensive
- Focus on searchable terms users would use
- Process modules in batches to track progress
- Each session can process a subset; use `enriched_at` to track progress
