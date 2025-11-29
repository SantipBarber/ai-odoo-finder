#!/usr/bin/env python3
"""
Generate improved keywords for modules with poor/technical keywords.
This script reads modules from get_modules_for_reenrich.py and generates
functional, searchable keywords.
"""

import json
import subprocess
import sys
from typing import List, Dict, Any


def get_modules_to_reenrich(limit: int = 5000) -> List[Dict[str, Any]]:
    """Get modules that need keyword re-enrichment."""
    result = subprocess.run(
        ['uv', 'run', 'python', 'scripts/get_modules_for_reenrich.py', '--limit', str(limit)],
        capture_output=True,
        text=True,
        cwd='/Users/spbarber/Desarrollo/ai-odoo-finder'
    )

    # Extract JSON from output (skip the header line)
    output_lines = result.stdout.strip().split('\n')
    json_start = next(i for i, line in enumerate(output_lines) if line.strip().startswith('['))
    json_str = '\n'.join(output_lines[json_start:])

    return json.loads(json_str)


def generate_keywords_for_module(module: Dict[str, Any]) -> List[str]:
    """
    Generate 7-10 functional, searchable keywords for a module.

    Rules:
    - NO technical names (module name, dependencies)
    - NO generic terms (erp, odoo, business, system, module)
    - USE business terms users would search for
    - USE action words
    - USE industry terminology
    - USE Spanish AND English for localization modules
    - USE abbreviations users know
    """
    technical_name = module['technical_name']
    name = module['name']
    summary = module.get('summary', '')
    ai_description = module.get('ai_description', '')
    functional_tags = module.get('functional_tags', [])

    keywords = []

    # Project modules
    if 'project' in technical_name or 'project' in functional_tags:
        if 'list' in technical_name or 'list' in name.lower():
            keywords = ["project overview", "task list", "project dashboard", "task tracking", "project monitoring", "lista proyectos", "vista proyectos"]
        elif 'template' in technical_name or 'template' in name.lower():
            keywords = ["project blueprint", "reusable project", "project starter", "task template", "project copy", "plantilla proyecto", "modelo proyecto", "duplicate project"]
        elif 'timeline' in technical_name or 'timeline' in name.lower():
            keywords = ["gantt chart", "project schedule", "task timeline", "milestone planning", "project calendar", "cronograma", "diagrama gantt", "planning"]
        elif 'parent' in technical_name or 'hierarchy' in name.lower():
            keywords = ["nested projects", "sub-projects", "project hierarchy", "parent child projects", "multi-level projects", "proyectos anidados", "sub-proyectos"]
        elif 'version' in technical_name or 'version' in name.lower():
            keywords = ["release management", "project milestones", "version tracking", "sprint planning", "project phases", "versión proyecto", "releases"]
        elif 'timesheet' in technical_name:
            keywords = ["time tracking", "hours worked", "billable hours", "time entry", "labor cost", "registro horas", "parte trabajo"]
        elif 'task' in technical_name:
            keywords = ["task management", "to-do list", "assignments", "work items", "task tracking", "tareas", "gestión tareas"]

    # POS modules
    elif 'pos_' in technical_name or 'pos' in functional_tags:
        if 'mail' in technical_name or 'receipt' in technical_name:
            keywords = ["email receipt", "digital receipt", "receipt by email", "ticket electrónico", "recibo email", "e-receipt"]
        elif 'margin' in technical_name:
            keywords = ["profit margin", "sales margin", "markup", "gross profit", "margen venta", "beneficio", "rentabilidad"]
        elif 'category' in technical_name:
            keywords = ["product categories", "POS navigation", "product organization", "categorías producto", "clasificación"]
        elif 'logo' in technical_name or 'ticket' in technical_name:
            keywords = ["receipt logo", "ticket branding", "custom receipt", "receipt customization", "logo ticket", "personalizar recibo"]
        elif 'timeout' in technical_name:
            keywords = ["session timeout", "auto logout", "security timeout", "idle timeout", "tiempo espera", "cierre sesión"]
        elif 'customer' in technical_name:
            keywords = ["customer info", "client data", "customer display", "customer screen", "pantalla cliente", "información cliente"]
        elif 'payment' in technical_name:
            keywords = ["payment methods", "payment terminal", "card payment", "cash management", "métodos pago", "terminal pago"]
        elif 'discount' in technical_name:
            keywords = ["price reduction", "sales discount", "promotion", "special offer", "descuento", "promoción", "oferta"]
        elif 'order' in technical_name:
            keywords = ["sales order", "ticket", "transaction", "checkout", "venta", "pedido", "transacción"]

    # Account/Finance modules
    elif 'account' in technical_name or 'accounting' in functional_tags or 'finance' in functional_tags:
        if 'invoice' in technical_name:
            keywords = ["billing", "invoicing", "invoice generation", "customer invoice", "facturación", "factura", "cobro"]
        elif 'payment' in technical_name:
            keywords = ["accounts payable", "accounts receivable", "payment processing", "payment matching", "pagos", "cobros", "tesorería"]
        elif 'reconcil' in technical_name:
            keywords = ["bank reconciliation", "statement matching", "transaction matching", "conciliación bancaria", "cuadre cuentas"]
        elif 'report' in technical_name:
            keywords = ["financial reports", "balance sheet", "profit loss", "P&L", "income statement", "reportes financieros", "estados financieros"]
        elif 'asset' in technical_name:
            keywords = ["fixed assets", "depreciation", "asset management", "amortization", "activos fijos", "depreciación"]
        elif 'budget' in technical_name:
            keywords = ["budget planning", "budget control", "budget forecast", "presupuesto", "planificación financiera"]
        elif 'analytic' in technical_name:
            keywords = ["cost center", "cost accounting", "analytical accounting", "project costing", "contabilidad analítica", "centro costos"]

    # Sale modules
    elif 'sale' in technical_name or 'sales' in functional_tags:
        if 'order' in technical_name:
            keywords = ["sales order", "quotation", "sales quote", "order management", "pedido venta", "presupuesto", "cotización"]
        elif 'commission' in technical_name:
            keywords = ["sales commission", "salesperson bonus", "commission calculation", "comisión ventas", "incentivos"]
        elif 'subscription' in technical_name:
            keywords = ["recurring revenue", "subscription billing", "MRR", "recurring sales", "suscripción", "venta recurrente"]
        elif 'discount' in technical_name:
            keywords = ["price discount", "sales promotion", "discount rules", "descuento", "promoción", "oferta"]

    # Purchase modules
    elif 'purchase' in technical_name or 'purchasing' in functional_tags:
        if 'order' in technical_name:
            keywords = ["purchase order", "PO", "procurement", "vendor order", "orden compra", "pedido proveedor"]
        elif 'requisition' in technical_name:
            keywords = ["purchase request", "RFQ", "tender", "bid", "solicitud compra", "petición oferta"]
        elif 'agreement' in technical_name:
            keywords = ["blanket order", "purchase agreement", "framework agreement", "acuerdo compra", "contrato marco"]

    # Stock/Inventory modules
    elif 'stock' in technical_name or 'inventory' in functional_tags or 'warehouse' in functional_tags:
        if 'inventory' in technical_name:
            keywords = ["stock count", "physical inventory", "inventory adjustment", "inventario físico", "recuento stock"]
        elif 'picking' in technical_name or 'transfer' in technical_name:
            keywords = ["stock transfer", "warehouse transfer", "internal move", "stock movement", "transferencia stock", "movimiento almacén"]
        elif 'lot' in technical_name or 'serial' in technical_name:
            keywords = ["lot tracking", "serial numbers", "traceability", "batch tracking", "trazabilidad", "lotes", "números serie"]
        elif 'barcode' in technical_name:
            keywords = ["barcode scanner", "barcode reading", "warehouse scanning", "código barras", "escáner", "lector"]

    # HR modules
    elif 'hr_' in technical_name or 'hr' in functional_tags or 'human_resources' in functional_tags:
        if 'expense' in technical_name:
            keywords = ["employee expenses", "expense report", "travel expenses", "reimbursement", "gastos empleado", "nota gastos", "viáticos"]
        elif 'leave' in technical_name or 'holiday' in technical_name:
            keywords = ["time off", "vacation request", "absence management", "leave request", "vacaciones", "ausencias", "permisos"]
        elif 'payroll' in technical_name:
            keywords = ["salary calculation", "payroll processing", "wage payment", "nómina", "salarios", "sueldos"]
        elif 'recruitment' in technical_name:
            keywords = ["hiring", "job posting", "candidate tracking", "applicant", "reclutamiento", "selección", "candidatos"]
        elif 'attendance' in technical_name:
            keywords = ["time clock", "attendance tracking", "check in out", "work hours", "asistencia", "fichaje", "presencia"]
        elif 'appraisal' in technical_name:
            keywords = ["performance review", "employee evaluation", "appraisal", "evaluación desempeño", "valoración"]

    # Manufacturing modules
    elif 'mrp' in technical_name or 'manufacturing' in functional_tags:
        if 'bom' in technical_name:
            keywords = ["bill of materials", "BOM", "recipe", "product structure", "lista materiales", "componentes"]
        elif 'production' in technical_name or 'work' in technical_name:
            keywords = ["manufacturing order", "production planning", "work order", "orden producción", "fabricación"]
        elif 'quality' in technical_name:
            keywords = ["quality control", "QC", "inspection", "quality check", "control calidad", "inspección"]

    # Website/eCommerce modules
    elif 'website' in technical_name or 'ecommerce' in functional_tags:
        if 'sale' in technical_name or 'shop' in technical_name:
            keywords = ["online store", "web shop", "ecommerce", "online sales", "tienda online", "venta web"]
        elif 'blog' in technical_name:
            keywords = ["content management", "blog posts", "articles", "news", "publicaciones", "artículos"]
        elif 'seo' in technical_name:
            keywords = ["search optimization", "SEO", "metadata", "search ranking", "optimización web", "posicionamiento"]

    # Localization modules
    elif 'l10n_' in technical_name:
        country_code = technical_name.split('_')[1] if len(technical_name.split('_')) > 1 else ''

        if 'es' in country_code.lower():
            if 'aeat' in technical_name or 'sii' in technical_name:
                keywords = ["Spanish tax", "AEAT", "SII", "tax reporting Spain", "modelo impuestos", "hacienda", "agencia tributaria"]
            elif 'facturae' in technical_name:
                keywords = ["electronic invoice Spain", "factura electrónica", "XML invoice", "e-invoice", "facturación electrónica"]
            else:
                keywords = ["Spanish accounting", "Spain localization", "Spanish tax", "contabilidad española", "localización España"]
        elif 'mx' in country_code.lower():
            keywords = ["Mexican accounting", "Mexico localization", "CFDI", "SAT", "contabilidad mexicana", "factura electrónica México"]
        elif 'ar' in country_code.lower():
            keywords = ["Argentine accounting", "Argentina localization", "AFIP", "contabilidad argentina"]
        elif 'co' in country_code.lower():
            keywords = ["Colombian accounting", "Colombia localization", "DIAN", "contabilidad colombiana"]
        elif 'pe' in country_code.lower():
            keywords = ["Peruvian accounting", "Peru localization", "SUNAT", "contabilidad peruana"]
        elif 'cl' in country_code.lower():
            keywords = ["Chilean accounting", "Chile localization", "SII Chile", "contabilidad chilena"]
        elif 'br' in country_code.lower():
            keywords = ["Brazilian accounting", "Brazil localization", "NF-e", "SPED", "contabilidade brasileira"]
        else:
            keywords = [f"{country_code.upper()} accounting", f"{country_code.upper()} localization", "tax compliance", "local regulations"]

    # If we haven't matched any pattern, generate generic functional keywords
    if not keywords:
        # Try to extract meaningful terms from name and description
        if 'report' in name.lower() or 'report' in technical_name:
            keywords = ["reporting", "analytics", "business intelligence", "data analysis", "informes", "reportes", "análisis"]
        elif 'import' in name.lower() or 'import' in technical_name:
            keywords = ["data import", "import data", "bulk import", "CSV import", "importar datos", "carga masiva"]
        elif 'export' in name.lower() or 'export' in technical_name:
            keywords = ["data export", "export data", "download data", "exportar datos", "descargar"]
        elif 'wizard' in technical_name:
            keywords = ["guided process", "wizard", "step by step", "assistant", "asistente", "proceso guiado"]
        elif 'dashboard' in technical_name or 'dashboard' in name.lower():
            keywords = ["KPI dashboard", "metrics", "analytics", "performance", "cuadro mando", "indicadores"]
        else:
            # Extract key terms from name and create search-friendly keywords
            name_words = name.lower().split()
            # Remove common words
            filtered_words = [w for w in name_words if w not in ['the', 'a', 'an', 'for', 'of', 'and', 'in']]
            keywords = filtered_words[:7] if len(filtered_words) >= 7 else filtered_words

    # Ensure we have 7-10 keywords
    if len(keywords) < 7:
        # Add some generic but functional terms based on functional tags
        for tag in functional_tags:
            if tag == 'accounting':
                keywords.extend(["financial management", "accounting"])
            elif tag == 'sales':
                keywords.extend(["sales management", "CRM"])
            elif tag == 'purchasing':
                keywords.extend(["procurement", "vendor management"])
            elif tag == 'inventory':
                keywords.extend(["stock management", "warehouse"])
            elif tag == 'hr':
                keywords.extend(["human resources", "employee management"])
            elif tag == 'project':
                keywords.extend(["project management", "task tracking"])

        # If still not enough, pad with variations
        if len(keywords) < 7:
            # Add variations of existing keywords
            temp = keywords.copy()
            for kw in temp[:3]:
                if ' ' in kw:
                    keywords.append(kw.replace(' ', '_'))

    # Remove duplicates and limit to 10
    keywords = list(dict.fromkeys(keywords))[:10]

    # Ensure minimum 7 keywords
    while len(keywords) < 7:
        keywords.append(f"{name.lower().replace(' ', '_')}_feature")

    return keywords


def main():
    print("🔄 Generating improved keywords for 5000 modules...")

    # Get modules
    modules = get_modules_to_reenrich(5000)
    print(f"📦 Processing {len(modules)} modules...")

    # Generate keywords for each module
    enrichments = []
    for i, module in enumerate(modules):
        keywords = generate_keywords_for_module(module)
        enrichments.append({
            "id": module['id'],
            "keywords": keywords
        })

        if (i + 1) % 500 == 0:
            print(f"  ✓ Processed {i + 1}/{len(modules)} modules...")

    # Output JSON
    print(json.dumps(enrichments, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()