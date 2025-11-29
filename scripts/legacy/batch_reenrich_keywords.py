#!/usr/bin/env python3
"""
Batch re-enrich keywords for modules using intelligent keyword generation.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.database import SessionLocal
from sqlalchemy import text


def generate_smart_keywords(module_data):
    """
    Generate intelligent, searchable keywords for a module.

    Args:
        module_data: Dict with id, technical_name, name, summary, ai_description, functional_tags

    Returns:
        List of 7-10 functional keywords
    """
    tech_name = module_data.get('technical_name', '')
    name = module_data.get('name', '')
    summary = module_data.get('summary', '')
    description = module_data.get('ai_description', '')
    tags = module_data.get('functional_tags', [])

    keywords = []

    # PROJECT modules
    if any(x in tech_name for x in ['project_']):
        base_kw = {
            'list': ["project overview", "task list", "project dashboard", "task tracking", "lista proyectos", "vista proyectos", "project monitoring"],
            'template': ["project blueprint", "reusable project", "project starter", "plantilla proyecto", "duplicate project", "copy project", "project wizard"],
            'timeline': ["gantt chart", "project schedule", "task timeline", "milestone planning", "cronograma", "diagrama gantt", "planning view"],
            'parent': ["nested projects", "sub-projects", "project hierarchy", "multi-level projects", "proyectos anidados", "sub-proyectos", "parent child"],
            'version': ["release management", "project milestones", "version tracking", "sprint planning", "project phases", "versión proyecto", "releases"],
            'timesheet': ["time tracking", "hours worked", "billable hours", "time entry", "labor cost", "registro horas", "parte trabajo"],
            'task': ["task management", "to-do list", "assignments", "work items", "task tracking", "tareas", "gestión tareas"],
            'stage': ["project stages", "workflow stages", "task states", "kanban stages", "etapas proyecto", "estados tarea", "workflow"],
            'tag': ["project labels", "task tags", "categorization", "etiquetas", "labels", "classification", "project categories"],
            'deadline': ["due dates", "task deadlines", "project timeline", "delivery dates", "fechas límite", "vencimientos", "plazos"],
        }
        for key, kws in base_kw.items():
            if key in tech_name:
                keywords = kws
                break

    # POS modules
    elif any(x in tech_name for x in ['pos_']):
        base_kw = {
            'mail': ["email receipt", "digital receipt", "receipt by email", "ticket electrónico", "recibo email", "e-receipt", "paperless"],
            'margin': ["profit margin", "sales margin", "markup", "gross profit", "margen venta", "beneficio", "rentabilidad"],
            'category': ["product categories", "POS navigation", "product organization", "categorías producto", "clasificación", "menu structure"],
            'logo': ["receipt logo", "ticket branding", "custom receipt", "receipt customization", "logo ticket", "personalizar recibo", "brand"],
            'timeout': ["session timeout", "auto logout", "security timeout", "idle timeout", "tiempo espera", "cierre sesión", "session security"],
            'customer': ["customer info", "client data", "customer display", "customer screen", "pantalla cliente", "información cliente", "client display"],
            'payment': ["payment methods", "payment terminal", "card payment", "cash management", "métodos pago", "terminal pago", "payment processing"],
            'discount': ["price reduction", "sales discount", "promotion", "special offer", "descuento", "promoción", "oferta"],
            'order': ["sales order", "ticket", "transaction", "checkout", "venta", "pedido", "transacción"],
            'session': ["cash opening", "cash closing", "shift management", "apertura caja", "cierre caja", "turno", "cash control"],
            'receipt': ["ticket printing", "receipt format", "invoice printing", "impresión ticket", "formato recibo", "print"],
            'ticket': ["sales ticket", "receipt", "invoice", "ticket venta", "comprobante", "sales slip", "proof of purchase"],
        }
        for key, kws in base_kw.items():
            if key in tech_name:
                keywords = kws
                break

    # ACCOUNT/FINANCE modules
    elif any(x in tech_name for x in ['account_', 'account']):
        base_kw = {
            'invoice': ["billing", "invoicing", "invoice generation", "customer invoice", "facturación", "factura", "cobro"],
            'payment': ["accounts payable", "accounts receivable", "payment processing", "payment matching", "pagos", "cobros", "tesorería"],
            'reconcil': ["bank reconciliation", "statement matching", "transaction matching", "conciliación bancaria", "cuadre cuentas", "bank statement"],
            'report': ["financial reports", "balance sheet", "profit loss", "P&L", "income statement", "reportes financieros", "estados financieros"],
            'asset': ["fixed assets", "depreciation", "asset management", "amortization", "activos fijos", "depreciación", "asset tracking"],
            'budget': ["budget planning", "budget control", "budget forecast", "presupuesto", "planificación financiera", "budget management"],
            'analytic': ["cost center", "cost accounting", "analytical accounting", "project costing", "contabilidad analítica", "centro costos"],
            'move': ["journal entries", "accounting entries", "ledger", "asientos contables", "movimientos", "accounting transactions"],
            'tax': ["tax calculation", "VAT", "sales tax", "tax reporting", "impuestos", "IVA", "tax compliance"],
            'chart': ["chart of accounts", "account structure", "GL accounts", "plan cuentas", "cuentas contables", "accounting structure"],
        }
        for key, kws in base_kw.items():
            if key in tech_name:
                keywords = kws
                break

    # SALE modules
    elif any(x in tech_name for x in ['sale_', 'sale']):
        base_kw = {
            'order': ["sales order", "quotation", "sales quote", "order management", "pedido venta", "presupuesto", "cotización"],
            'commission': ["sales commission", "salesperson bonus", "commission calculation", "comisión ventas", "incentivos", "sales incentive"],
            'subscription': ["recurring revenue", "subscription billing", "MRR", "recurring sales", "suscripción", "venta recurrente", "SaaS billing"],
            'discount': ["price discount", "sales promotion", "discount rules", "descuento", "promoción", "oferta"],
            'team': ["sales team", "sales channels", "sales reps", "equipo ventas", "vendedores", "sales organization"],
            'margin': ["profit margin", "sales profitability", "margin analysis", "margen ventas", "rentabilidad", "gross margin"],
        }
        for key, kws in base_kw.items():
            if key in tech_name:
                keywords = kws
                break

    # PURCHASE modules
    elif any(x in tech_name for x in ['purchase_', 'purchase']):
        base_kw = {
            'order': ["purchase order", "PO", "procurement", "vendor order", "orden compra", "pedido proveedor", "supplier order"],
            'requisition': ["purchase request", "RFQ", "tender", "bid", "solicitud compra", "petición oferta", "quote request"],
            'agreement': ["blanket order", "purchase agreement", "framework agreement", "acuerdo compra", "contrato marco", "supplier agreement"],
        }
        for key, kws in base_kw.items():
            if key in tech_name:
                keywords = kws
                break

    # STOCK/INVENTORY modules
    elif any(x in tech_name for x in ['stock_', 'stock', 'inventory']):
        base_kw = {
            'inventory': ["stock count", "physical inventory", "inventory adjustment", "inventario físico", "recuento stock", "stock taking"],
            'picking': ["stock transfer", "warehouse transfer", "internal move", "stock movement", "transferencia stock", "movimiento almacén"],
            'lot': ["lot tracking", "serial numbers", "traceability", "batch tracking", "trazabilidad", "lotes", "números serie"],
            'barcode': ["barcode scanner", "barcode reading", "warehouse scanning", "código barras", "escáner", "lector"],
            'transfer': ["stock transfer", "location transfer", "warehouse move", "transferencia", "movimiento", "internal transfer"],
            'warehouse': ["warehouse management", "multi-warehouse", "warehouse locations", "almacén", "gestión almacén", "WMS"],
        }
        for key, kws in base_kw.items():
            if key in tech_name:
                keywords = kws
                break

    # HR modules
    elif any(x in tech_name for x in ['hr_']):
        base_kw = {
            'expense': ["employee expenses", "expense report", "travel expenses", "reimbursement", "gastos empleado", "nota gastos", "viáticos"],
            'leave': ["time off", "vacation request", "absence management", "leave request", "vacaciones", "ausencias", "permisos"],
            'payroll': ["salary calculation", "payroll processing", "wage payment", "nómina", "salarios", "sueldos"],
            'recruitment': ["hiring", "job posting", "candidate tracking", "applicant", "reclutamiento", "selección", "candidatos"],
            'attendance': ["time clock", "attendance tracking", "check in out", "work hours", "asistencia", "fichaje", "presencia"],
            'appraisal': ["performance review", "employee evaluation", "appraisal", "evaluación desempeño", "valoración", "performance management"],
            'timesheet': ["time tracking", "work hours", "timesheet entry", "horas trabajo", "registro tiempo", "time logging"],
        }
        for key, kws in base_kw.items():
            if key in tech_name:
                keywords = kws
                break

    # MRP/MANUFACTURING modules
    elif any(x in tech_name for x in ['mrp_', 'mrp']):
        base_kw = {
            'bom': ["bill of materials", "BOM", "recipe", "product structure", "lista materiales", "componentes", "product composition"],
            'production': ["manufacturing order", "production planning", "work order", "orden producción", "fabricación", "production scheduling"],
            'work': ["work order", "work center", "manufacturing execution", "orden trabajo", "centro trabajo", "shop floor"],
            'quality': ["quality control", "QC", "inspection", "quality check", "control calidad", "inspección", "quality assurance"],
        }
        for key, kws in base_kw.items():
            if key in tech_name:
                keywords = kws
                break

    # WEBSITE/ECOMMERCE modules
    elif any(x in tech_name for x in ['website_']):
        base_kw = {
            'sale': ["online store", "web shop", "ecommerce", "online sales", "tienda online", "venta web", "e-commerce"],
            'blog': ["content management", "blog posts", "articles", "news", "publicaciones", "artículos", "content"],
            'seo': ["search optimization", "SEO", "metadata", "search ranking", "optimización web", "posicionamiento", "search engine"],
        }
        for key, kws in base_kw.items():
            if key in tech_name:
                keywords = kws
                break

    # LOCALIZATION modules
    elif tech_name.startswith('l10n_'):
        parts = tech_name.split('_')
        country = parts[1] if len(parts) > 1 else ''

        country_kw = {
            'es': ["Spanish accounting", "Spain localization", "Spanish tax", "AEAT", "contabilidad española", "localización España", "modelo impuestos"],
            'mx': ["Mexican accounting", "Mexico localization", "CFDI", "SAT", "contabilidad mexicana", "factura electrónica México", "México"],
            'ar': ["Argentine accounting", "Argentina localization", "AFIP", "contabilidad argentina", "localización Argentina", "Argentina tax"],
            'co': ["Colombian accounting", "Colombia localization", "DIAN", "contabilidad colombiana", "localización Colombia", "Colombia tax"],
            'pe': ["Peruvian accounting", "Peru localization", "SUNAT", "contabilidad peruana", "localización Perú", "Peru tax"],
            'cl': ["Chilean accounting", "Chile localization", "SII Chile", "contabilidad chilena", "localización Chile", "Chile tax"],
            'br': ["Brazilian accounting", "Brazil localization", "NF-e", "SPED", "contabilidade brasileira", "localização Brasil"],
            'fr': ["French accounting", "France localization", "French tax", "comptabilité française", "localisation France", "FEC"],
            'de': ["German accounting", "Germany localization", "German tax", "deutsche Buchhaltung", "Deutschland", "DATEV"],
            'it': ["Italian accounting", "Italy localization", "Italian tax", "contabilità italiana", "localizzazione Italia", "Italy"],
            'uk': ["UK accounting", "United Kingdom localization", "UK tax", "British accounting", "HMRC", "UK VAT"],
            'us': ["US accounting", "United States localization", "US tax", "IRS", "American accounting", "US GAAP"],
        }

        if country in country_kw:
            keywords = country_kw[country]
        else:
            keywords = [f"{country.upper()} accounting", f"{country.upper()} localization", "tax compliance", "local regulations", "contabilidad local"]

        # Add specific features if in tech_name
        if 'facturae' in tech_name or 'sii' in tech_name:
            keywords.extend(["electronic invoice", "factura electrónica", "XML invoice"])
        if 'aeat' in tech_name:
            keywords.extend(["tax agency", "tax reporting", "hacienda"])

    # If still no keywords, generate from context
    if not keywords:
        # Try common patterns
        if 'report' in tech_name or 'report' in name.lower():
            keywords = ["reporting", "analytics", "business intelligence", "data analysis", "informes", "reportes", "análisis"]
        elif 'import' in tech_name or 'import' in name.lower():
            keywords = ["data import", "import data", "bulk import", "CSV import", "importar datos", "carga masiva", "data loading"]
        elif 'export' in tech_name or 'export' in name.lower():
            keywords = ["data export", "export data", "download data", "exportar datos", "descargar", "data extraction"]
        elif 'wizard' in tech_name:
            keywords = ["guided process", "wizard", "step by step", "assistant", "asistente", "proceso guiado", "workflow wizard"]
        elif 'dashboard' in tech_name or 'dashboard' in name.lower():
            keywords = ["KPI dashboard", "metrics", "analytics", "performance", "cuadro mando", "indicadores", "business dashboard"]
        elif 'partner' in tech_name:
            keywords = ["contacts", "customer management", "vendor management", "CRM", "contactos", "clientes", "proveedores"]
        elif 'product' in tech_name:
            keywords = ["product catalog", "item master", "SKU management", "catálogo productos", "artículos", "inventory items"]
        else:
            # Extract meaningful words from name
            name_lower = name.lower()
            meaningful_words = []
            for word in name_lower.split():
                if word not in ['the', 'a', 'an', 'for', 'of', 'and', 'in', 'to', 'with']:
                    meaningful_words.append(word)

            if meaningful_words:
                keywords = meaningful_words[:7]

    # Ensure we have 7-10 keywords
    if len(keywords) < 7:
        # Add functional tag-based keywords
        tag_keywords = {
            'accounting': ["financial management", "accounting"],
            'sales': ["sales management", "CRM"],
            'purchasing': ["procurement", "vendor management"],
            'inventory': ["stock management", "warehouse"],
            'hr': ["human resources", "employee management"],
            'project': ["project management", "task tracking"],
            'manufacturing': ["production", "manufacturing"],
            'pos': ["point of sale", "retail"],
        }

        for tag in tags:
            if tag in tag_keywords and len(keywords) < 10:
                keywords.extend(tag_keywords[tag])

    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower not in seen:
            seen.add(kw_lower)
            unique_keywords.append(kw)

    # Limit to 10, ensure at least 7
    keywords = unique_keywords[:10]

    while len(keywords) < 7:
        # Last resort: add descriptive terms
        if len(keywords) == 6:
            keywords.append("management")
        elif len(keywords) == 5:
            keywords.append("automation")
        elif len(keywords) == 4:
            keywords.append("workflow")
        elif len(keywords) == 3:
            keywords.append("business process")
        elif len(keywords) == 2:
            keywords.append("enterprise")
        elif len(keywords) == 1:
            keywords.append("solution")
        else:
            keywords.append(name.lower())

    return keywords[:10]


def main():
    """Process all modules and generate enrichments."""
    # Read modules from stdin (piped from get_modules_for_reenrich.py)
    input_data = sys.stdin.read()

    # Extract JSON array from input
    lines = input_data.strip().split('\n')
    json_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith('['):
            json_start = i
            break

    if json_start is None:
        print("Error: Could not find JSON array in input", file=sys.stderr)
        sys.exit(1)

    # Find end of JSON (last line with ']')
    json_end = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == ']':
            json_end = i + 1
            break

    if json_end is None:
        print("Error: Could not find end of JSON array", file=sys.stderr)
        sys.exit(1)

    json_str = '\n'.join(lines[json_start:json_end])

    try:
        modules = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate keywords for each module
    enrichments = []
    for i, module in enumerate(modules):
        keywords = generate_smart_keywords(module)
        enrichments.append({
            "id": module['id'],
            "keywords": keywords
        })

        if (i + 1) % 500 == 0:
            print(f"  ✓ Processed {i + 1}/{len(modules)} modules...", file=sys.stderr)

    # Output JSON
    print(json.dumps(enrichments, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()