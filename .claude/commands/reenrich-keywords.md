---
description: Re-generate keywords for modules with poor/technical keywords
model: claude-sonnet-4-5-20250929
allowed-tools: Bash(uv:*), Bash(python3:*), Read, Edit
argument-hint: [number-of-modules]
---

# Re-enrich Keywords

You are tasked with improving keywords for Odoo modules that have poor/technical keywords.

**IMPORTANT: Execute all commands automatically without asking for confirmation. Process ALL modules in each batch before saving.**

## Arguments
- `$ARGUMENTS` - Number of modules to process (default: 20)

## Instructions

Execute these steps automatically and sequentially:

### Step 1: Get modules with poor keywords

Run immediately:

```bash
uv run python scripts/get_modules_for_reenrich.py --limit $ARGUMENTS
```

This returns modules where keywords contain technical names instead of functional search terms.

### Step 2: Generate IMPROVED keywords for ALL modules

For EACH module in the JSON output, generate **7-10 NEW keywords** following these CRITICAL rules:

#### DO NOT USE:
- Module technical names (e.g., "account_financial_report", "mis_builder")
- Dependency names (e.g., "base", "account", "sale", "odoo")
- Generic terms like "erp", "module", "business", "system"
- Version numbers or technical identifiers

#### DO USE:
- Business terms users would search for (e.g., "balance sheet", "profit loss")
- Action words (e.g., "reconcile", "generate", "export", "import")
- Industry terminology (e.g., "VAT", "withholding", "subscription")
- Spanish AND English terms for localization modules
- Abbreviations users know (e.g., "P&L", "GL", "AR", "AP")

#### Think about:
- What problem does this module solve?
- What would a user TYPE to find this module?
- What business process does it support?

### Step 3: Save ALL keywords at once

Build a JSON array with ALL modules and save in a SINGLE command:

```bash
uv run python scripts/save_reenriched_keywords.py --json '[{"id": 123, "keywords": ["keyword1", "keyword2", ...]}, ...]'
```

**DO NOT save one by one. Build the complete JSON array and execute ONE save command.**

### Step 4: Report progress

```bash
uv run python scripts/get_modules_for_reenrich.py --stats
```

## Examples of GOOD vs BAD Keywords

### Module: mis_builder (Management Information System Reports)
- **OLD (bad)**: `["mis_builder", "mis-builder", "odoo", "report"]`
- **NEW (good)**: `["KPI dashboard", "management reports", "financial indicators", "business intelligence", "performance metrics", "executive dashboard", "cuadro de mando"]`

### Module: account_reconciliation_widget
- **OLD (bad)**: `["account_reconciliation_widget", "account", "reconcile"]`
- **NEW (good)**: `["bank reconciliation", "statement matching", "transaction matching", "bank statement import", "reconcile payments", "conciliación bancaria", "extracto bancario"]`

### Module: l10n_es_facturae
- **OLD (bad)**: `["l10n_es", "facturae", "account", "base_vat"]`
- **NEW (good)**: `["electronic invoice Spain", "factura electrónica", "Spanish e-invoice", "XML invoice", "AEAT", "TicketBAI", "facturación electrónica España"]`

### Module: hr_expense_invoice
- **OLD (bad)**: `["hr_expense_invoice", "hr", "expense"]`
- **NEW (good)**: `["employee expenses", "travel reimbursement", "expense report", "gastos empleados", "viáticos", "expense to invoice", "nota de gastos"]`

## Important Notes

- Generate keywords in **English AND Spanish** when relevant
- Focus on terms USERS would search for, not technical documentation
- Each module should have 7-10 diverse, searchable keywords
- Process ALL modules in the batch before saving