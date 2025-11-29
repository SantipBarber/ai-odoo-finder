#!/usr/bin/env python3
"""Generate improved keywords for modules using intelligent analysis."""
import json
import subprocess
import sys
import re

def extract_json(output):
    """Extract JSON array from output with extra text."""
    json_start = output.find('[')
    if json_start == -1:
        return None

    bracket_count = 0
    for i, char in enumerate(output[json_start:], start=json_start):
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0:
                return json.loads(output[json_start:i + 1])
    return None

def generate_keywords(module):
    """Generate thoughtful keywords based on module context."""
    keywords = []
    name = module.get('name', '').lower()
    summary = module.get('summary', '').lower()
    tech_name = module.get('technical_name', '').lower()
    ai_desc = module.get('ai_description', '').lower()
    tags = module.get('functional_tags', [])

    combined_text = f"{name} {summary} {tech_name} {ai_desc}"

    # Stock/Inventory - be specific about what it does
    if 'stock_inventory_include_exhausted' in tech_name:
        return ["stock count", "inventory adjustment", "zero stock", "show exhausted products", "stock taking", "recuento inventario", "productos agotados", "physical inventory"]
    elif 'stock_picking_package_grouped' in tech_name:
        return ["batch packaging", "group shipments", "packing automation", "packaging criteria", "put in pack", "agrupar paquetes", "empaquetar lotes", "warehouse packing"]
    elif 'stock_picking_batch' in tech_name:
        return ["batch picking", "wave picking", "pick multiple orders", "recolección lotes", "picking masivo", "warehouse efficiency"]
    elif 'stock_inventory' in tech_name and 'cost' in combined_text:
        return ["inventory valuation", "stock cost", "costing method", "valoración inventario", "costo inventario", "FIFO", "average cost"]
    elif 'stock_location' in tech_name:
        return ["warehouse locations", "storage bins", "ubicaciones almacén", "stock location", "bin management", "warehouse organization"]
    elif 'stock_move_line' in tech_name:
        return ["stock movements", "inventory transfers", "movimientos stock", "stock tracking", "lot tracking", "serial numbers"]
    elif 'stock_quant' in tech_name:
        return ["stock quantities", "on hand inventory", "stock levels", "cantidad inventario", "available stock", "warehouse stock"]
    elif 'stock_warehouse_orderpoint' in tech_name or 'reordering' in combined_text:
        return ["reordering rules", "min max stock", "automatic procurement", "reglas reorden", "stock mínimo", "replenishment"]
    elif 'stock_request' in tech_name:
        return ["stock request", "material request", "solicitud material", "warehouse request", "internal request"]
    elif 'stock_secondary_unit' in tech_name:
        return ["dual UOM", "secondary unit", "unidad secundaria", "multiple units", "unit conversion", "UoM conversion"]

    # Project modules - focus on what users would search for
    elif 'project_category' in tech_name or 'project_type' in tech_name:
        return ["project categorization", "project classification", "organize projects", "project types", "categorías proyecto", "clasificar proyectos", "project taxonomy"]
    elif 'project_custom_info' in tech_name:
        return ["custom fields", "project metadata", "additional information", "project attributes", "custom data", "campos personalizados", "información adicional"]
    elif 'project_deadline' in tech_name:
        return ["project schedule", "project timeline", "due date", "project calendar", "start date", "fecha límite", "cronograma", "project planning"]
    elif 'project_description' in tech_name:
        return ["project overview", "project details", "project documentation", "project notes", "descripción proyecto", "project brief", "project scope"]
    elif 'project_hr' in tech_name:
        return ["employee assignment", "team member", "staff allocation", "resource assignment", "asignar empleados", "equipo proyecto", "human resources"]
    elif 'project_key' in tech_name:
        return ["project code", "project identifier", "project reference", "task numbering", "código proyecto", "identificador", "project tracking"]
    elif 'project_mail_chatter' in tech_name:
        return ["project communication", "project comments", "project messaging", "project discussion", "project notes", "comentarios proyecto", "project collaboration"]
    elif 'project_milestone' in tech_name:
        return ["project milestones", "deliverables", "project phases", "project checkpoints", "hitos proyecto", "entregables", "project goals"]
    elif 'project_parent_task_filter' in tech_name:
        return ["parent task", "task hierarchy", "subtasks", "task tree", "filter tasks", "tareas padre", "jerarquía tareas"]
    elif 'project_purchase_link' in tech_name:
        return ["project procurement", "purchase order", "project materials", "project expenses", "compras proyecto", "procurement tracking", "project costs"]
    elif 'project_recalculate' in tech_name:
        return ["recalculate hours", "update timesheet", "recompute time", "refresh costs", "actualizar horas", "recalcular tiempo"]
    elif 'project_role' in tech_name:
        return ["team roles", "project roles", "responsibility assignment", "role management", "roles equipo", "asignar responsabilidades", "RACI"]
    elif 'project_status' in tech_name:
        return ["project health", "project state", "project progress", "project tracking", "estado proyecto", "seguimiento proyecto", "project monitoring"]
    elif 'project_stock' in tech_name:
        return ["project inventory", "material tracking", "project warehouse", "stock project", "materiales proyecto", "inventario proyecto"]
    elif 'project_tag' in tech_name:
        return ["project labels", "project tags", "categorize projects", "project filters", "etiquetas proyecto", "clasificación"]
    elif 'project_task_add_very_high' in tech_name:
        return ["task priority", "urgent tasks", "high priority", "critical tasks", "prioridad tarea", "tareas urgentes", "task importance"]
    elif 'project_task_code' in tech_name:
        return ["task numbering", "task sequence", "task reference", "task code", "numeración tareas", "código tarea", "task tracking"]
    elif 'project_task_default_stage' in tech_name:
        return ["default stage", "initial status", "task workflow", "starting stage", "etapa inicial", "estado predeterminado"]
    elif 'project_task_digitized_signature' in tech_name:
        return ["electronic signature", "sign task", "task approval", "digital signature", "firma electrónica", "firma digital", "task signoff"]
    elif 'project_task_material' in tech_name and 'stock' not in tech_name:
        return ["task materials", "consumed products", "material tracking", "task costs", "materiales tarea", "productos consumidos", "material consumption"]
    elif 'project_task_material_stock' in tech_name:
        return ["material stock movement", "inventory deduction", "stock consumption", "analytic moves", "movimiento stock", "consumo materiales"]

    # Account/Finance modules - think about user problems
    elif 'account_financial_report' in tech_name or ('financial' in combined_text and 'report' in combined_text):
        return ["financial statements", "balance sheet", "profit loss", "P&L", "estados financieros", "balance general", "income statement"]
    elif 'account_invoice' in tech_name:
        if 'import' in combined_text:
            return ["import invoices", "invoice upload", "bulk invoicing", "importar facturas", "carga facturas", "invoice automation"]
        elif 'export' in combined_text:
            return ["export invoices", "invoice download", "exportar facturas", "invoice extraction", "invoice backup"]
        else:
            return ["invoicing", "billing", "facturación", "customer invoice", "supplier invoice", "invoice management"]
    elif 'account_payment' in tech_name:
        if 'term' in combined_text:
            return ["payment terms", "due date", "términos pago", "payment conditions", "credit terms", "payment schedule"]
        elif 'group' in combined_text or 'batch' in combined_text:
            return ["batch payment", "payment batch", "group payments", "pagos masivos", "multiple payments", "payment processing"]
        else:
            return ["payments", "payment processing", "pagos", "receive payment", "make payment", "payment registration"]
    elif 'account_reconcile' in tech_name or 'reconciliation' in combined_text:
        if 'auto' in combined_text or 'automatic' in combined_text:
            return ["automatic reconciliation", "auto matching", "conciliación automática", "smart reconciliation", "payment matching"]
        else:
            return ["bank reconciliation", "statement matching", "conciliación bancaria", "reconcile payments", "match transactions"]
    elif 'account_asset' in tech_name:
        return ["fixed assets", "asset management", "depreciation", "activos fijos", "depreciación", "asset tracking", "asset register"]
    elif 'account_analytic' in tech_name:
        return ["cost centers", "analytical accounting", "project accounting", "centros costo", "contabilidad analítica", "cost tracking"]
    elif 'account_tax' in tech_name or 'tax' in name:
        if 'balance' in combined_text:
            return ["tax report", "tax balance", "VAT report", "impuestos", "IVA", "tax declaration", "tax return"]
        elif 'python' in combined_text:
            return ["tax calculation", "custom tax", "tax formula", "cálculo impuestos", "tax computation", "programmable tax"]
        else:
            return ["tax", "VAT", "sales tax", "impuestos", "IVA", "tax configuration", "tax codes"]

    # Sales modules
    elif 'sale_order' in tech_name:
        if 'line' in combined_text and ('input' in combined_text or 'quick' in combined_text):
            return ["quick order entry", "fast order", "order import", "entrada rápida", "pedido rápido", "bulk order entry"]
        elif 'archive' in combined_text:
            return ["archive orders", "cancel orders", "archivar pedidos", "clean up orders", "order management"]
        elif 'revision' in combined_text or 'version' in combined_text:
            return ["order revision", "quotation version", "revisión pedido", "order versioning", "quotation history"]
        else:
            return ["sales order", "quotation", "pedido venta", "sales quote", "customer order", "order management"]
    elif 'sale_commission' in tech_name:
        return ["sales commission", "agent commission", "comisiones venta", "commission calculation", "sales incentive", "commission payment"]
    elif 'sale_discount' in tech_name:
        return ["discounts", "price reduction", "descuentos", "promotional pricing", "discount rules", "price discount"]

    # Purchase modules
    elif 'purchase_order' in tech_name:
        if 'approval' in combined_text:
            return ["purchase approval", "PO approval", "aprobación compras", "approval workflow", "purchase authorization"]
        elif 'type' in combined_text:
            return ["purchase types", "PO types", "tipos compra", "purchase classification", "order types"]
        else:
            return ["purchase order", "procurement", "orden compra", "supplier order", "PO", "purchasing"]
    elif 'purchase_requisition' in tech_name:
        return ["purchase requisition", "solicitud compra", "RFQ", "purchase request", "blanket order", "call for tenders"]
    elif 'purchase_agreement' in tech_name or 'blanket' in combined_text:
        return ["purchase agreement", "blanket order", "acuerdo compra", "framework agreement", "contract purchasing"]

    # HR modules
    elif 'hr_expense' in tech_name:
        if 'invoice' in combined_text:
            return ["expense to invoice", "reinvoice expense", "gastos refacturables", "billable expenses", "client expenses"]
        elif 'sheet' in combined_text:
            return ["expense report", "expense claim", "nota gastos", "employee expenses", "expense reimbursement"]
        else:
            return ["employee expenses", "expense management", "gastos empleados", "travel expenses", "expense claim"]
    elif 'hr_timesheet' in tech_name:
        if 'task' in combined_text:
            return ["task timesheet", "time tracking", "registro horas", "project time", "task time", "timesheet entry"]
        elif 'sheet' in combined_text:
            return ["timesheet", "work hours", "hoja horas", "time tracking", "employee hours", "time registration"]
        else:
            return ["timesheet", "time tracking", "registro horas", "work hours", "labor hours", "time entry"]
    elif 'hr_attendance' in tech_name:
        return ["attendance", "check in", "check out", "asistencia", "employee attendance", "clock in", "time clock"]
    elif 'hr_leave' in tech_name or 'hr_holiday' in tech_name:
        if 'type' in combined_text:
            return ["leave types", "time off types", "tipos vacaciones", "absence types", "leave categories"]
        else:
            return ["time off", "vacation", "vacaciones", "leave request", "absence", "holiday request"]
    elif 'hr_payroll' in tech_name:
        return ["payroll", "salary", "nómina", "payroll processing", "wage calculation", "payslip"]
    elif 'hr_recruitment' in tech_name:
        return ["recruitment", "hiring", "reclutamiento", "job application", "candidate", "applicant tracking"]

    # Manufacturing modules
    elif 'mrp_bom' in tech_name:
        if 'cost' in combined_text:
            return ["BOM cost", "product costing", "costo producto", "bill of materials cost", "manufacturing cost"]
        elif 'structure' in combined_text:
            return ["BOM structure", "product structure", "estructura BOM", "component tree", "bill of materials"]
        else:
            return ["bill of materials", "BOM", "lista materiales", "product recipe", "manufacturing BOM", "component list"]
    elif 'mrp_production' in tech_name or 'mrp_workorder' in tech_name:
        return ["manufacturing order", "production order", "orden producción", "work order", "fabrication", "make to order"]
    elif 'mrp_repair' in tech_name:
        return ["repair order", "RMA", "repair management", "orden reparación", "product repair", "after sales service"]

    # CRM modules
    elif 'crm_lead' in tech_name:
        if 'probability' in combined_text:
            return ["lead probability", "win rate", "probabilidad cierre", "opportunity scoring", "sales forecast"]
        elif 'score' in combined_text:
            return ["lead scoring", "lead qualification", "calificación leads", "lead ranking", "sales opportunity"]
        else:
            return ["leads", "opportunities", "oportunidades", "sales pipeline", "CRM", "prospect"]
    elif 'crm_claim' in tech_name:
        return ["claims", "complaints", "reclamos", "customer claim", "customer service", "after sales"]
    elif 'crm_phonecall' in tech_name:
        return ["phone calls", "call log", "llamadas", "call tracking", "customer calls", "phone activity"]

    # Website/eCommerce
    elif 'website_sale' in tech_name:
        if 'checkout' in combined_text:
            return ["online checkout", "eCommerce checkout", "checkout process", "compra online", "payment page"]
        elif 'cart' in combined_text:
            return ["shopping cart", "carrito compras", "cart management", "online cart", "basket"]
        elif 'wishlist' in combined_text:
            return ["wishlist", "favorites", "lista deseos", "save for later", "product wishlist"]
        else:
            return ["eCommerce", "online store", "tienda online", "web shop", "sell online", "online sales"]
    elif 'website_blog' in tech_name:
        return ["blog", "content", "articles", "blogging", "content management", "news"]
    elif 'website_form' in tech_name:
        return ["web forms", "contact form", "formularios", "form builder", "online form", "lead capture"]
    elif 'website_livechat' in tech_name:
        return ["live chat", "chat widget", "customer chat", "chat en vivo", "online support", "webchat"]

    # Localization modules - IMPORTANT: Include country names in Spanish and English
    elif 'l10n_es' in tech_name:
        keywords = ["Spain", "España", "Spanish localization", "localización española"]
        if 'aeat' in combined_text:
            keywords.extend(["AEAT", "Spanish tax agency", "agencia tributaria", "tax declaration"])
        if 'sii' in combined_text or 'suministro' in combined_text:
            keywords.extend(["SII", "immediate supply", "suministro inmediato", "real time invoice"])
        if 'facturae' in tech_name:
            keywords.extend(["factura electrónica", "electronic invoice", "XML invoice", "e-invoice Spain"])
        if 'modelo' in combined_text or 'tax' in name:
            keywords.extend(["tax model", "modelo fiscal", "Spanish tax", "tax form"])
        return keywords[:10]

    elif 'l10n_mx' in tech_name:
        keywords = ["Mexico", "México", "Mexican localization", "localización mexicana"]
        if 'factura' in combined_text or 'cfdi' in combined_text:
            keywords.extend(["CFDI", "Mexican invoice", "factura electrónica México", "SAT invoice"])
        if 'nomina' in combined_text or 'payroll' in combined_text:
            keywords.extend(["Mexican payroll", "nómina México", "CFDI nómina", "payroll Mexico"])
        return keywords[:10]

    elif 'l10n_ar' in tech_name:
        keywords = ["Argentina", "argentino", "Argentine localization", "localización argentina"]
        if 'afip' in combined_text:
            keywords.extend(["AFIP", "Argentine tax", "factura electrónica Argentina"])
        if 'vat' in combined_text or 'iva' in combined_text:
            keywords.extend(["Argentine VAT", "IVA Argentina", "tax Argentina"])
        return keywords[:10]

    elif 'l10n_cl' in tech_name:
        keywords = ["Chile", "Chilean localization", "localización chilena"]
        if 'sii' in combined_text:
            keywords.extend(["SII Chile", "Chilean tax", "factura electrónica Chile"])
        return keywords[:10]

    elif 'l10n_co' in tech_name:
        keywords = ["Colombia", "Colombian localization", "localización colombiana"]
        if 'dian' in combined_text:
            keywords.extend(["DIAN", "Colombian tax", "factura electrónica Colombia"])
        return keywords[:10]

    elif 'l10n_pe' in tech_name:
        keywords = ["Peru", "Perú", "Peruvian localization", "localización peruana"]
        if 'sunat' in combined_text:
            keywords.extend(["SUNAT", "Peruvian tax", "factura electrónica Perú"])
        return keywords[:10]

    elif 'l10n_' in tech_name:
        # Generic localization
        country_code = tech_name.split('l10n_')[1][:2].upper()
        keywords = ["localization", "localización", f"{country_code} localization"]

    # Generic patterns for common functionality
    else:
        # Report modules
        if 'report' in name or '_report' in tech_name:
            keywords.append("reports")
            keywords.append("informes")
            if 'pdf' in combined_text or 'print' in combined_text:
                keywords.extend(["print report", "PDF report", "imprimir"])
            if 'xlsx' in combined_text or 'excel' in combined_text:
                keywords.extend(["Excel report", "export Excel", "exportar Excel"])
            if 'qweb' in combined_text:
                keywords.extend(["custom report", "report template", "report designer"])

        # Import/Export
        if 'import' in name or 'import' in summary:
            keywords.extend(["import data", "importar", "data import", "upload"])
        if 'export' in name or 'export' in summary:
            keywords.extend(["export data", "exportar", "data export", "download"])

        # Wizard modules
        if 'wizard' in name or 'wizard' in tech_name:
            keywords.extend(["wizard", "asistente", "guided process", "step by step"])

        # Dashboard modules
        if 'dashboard' in name or 'dashboard' in tech_name:
            keywords.extend(["dashboard", "panel", "KPI", "metrics", "analytics"])

        # Partner/Customer
        if 'partner' in tech_name or 'customer' in combined_text:
            keywords.extend(["customer", "cliente", "partner", "contact"])

        # Add functional keywords from name if not too technical
        name_words = module.get('name', '').lower().replace('-', ' ').replace('_', ' ').split()
        for word in name_words:
            if word not in ['odoo', 'module', 'oca', 'base', 'and', 'the', 'for', 'with'] and len(word) > 3:
                if word not in [k.lower() for k in keywords]:
                    keywords.append(word)

    # Ensure we have at least 7 keywords
    if len(keywords) < 7:
        # Add keywords from summary
        if summary:
            summary_words = summary.split()
            for word in summary_words:
                word = word.strip('.,;:').lower()
                if len(word) > 4 and word not in [k.lower() for k in keywords]:
                    if word not in ['odoo', 'module', 'system', 'allows', 'provides']:
                        keywords.append(word)
                        if len(keywords) >= 7:
                            break

    return keywords[:10]

# Get modules
result = subprocess.run(
    ["uv", "run", "python", "scripts/get_modules_for_reenrich.py", "--limit", "2000"],
    capture_output=True,
    text=True
)

modules = extract_json(result.stdout)
if not modules:
    print("Error: Could not extract JSON from output")
    sys.exit(1)

print(f"Processing {len(modules)} modules...")

enriched = []
for i, module in enumerate(modules):
    if i % 100 == 0:
        print(f"Progress: {i}/{len(modules)}")

    keywords = generate_keywords(module)

    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower not in seen:
            seen.add(kw_lower)
            unique_keywords.append(kw)

    enriched.append({
        "id": module['id'],
        "keywords": unique_keywords[:10]
    })

# Save to JSON file
with open('scripts/.enriched_keywords_full.json', 'w') as f:
    json.dump(enriched, f, indent=2, ensure_ascii=False)

print(f"\nGenerated keywords for {len(enriched)} modules")
print(f"Saved to scripts/.enriched_keywords_full.json")

# Show sample
print("\n=== Sample Keywords ===")
for item in enriched[:5]:
    mod = next(m for m in modules if m['id'] == item['id'])
    print(f"\n{mod['name']}: {', '.join(item['keywords'])}")