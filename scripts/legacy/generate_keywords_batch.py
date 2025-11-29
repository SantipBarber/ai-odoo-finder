#!/usr/bin/env python3
"""Generate improved keywords for modules in batches using Claude."""
import json
import subprocess
import sys

# Get modules
result = subprocess.run(
    ["uv", "run", "python", "scripts/get_modules_for_reenrich.py", "--limit", "2000"],
    capture_output=True,
    text=True
)

# Parse the output to extract JSON
output = result.stdout
# Find the JSON array in the output
json_start = output.find('[')
if json_start == -1:
    print("Error: No JSON found in output")
    sys.exit(1)

# Extract just the JSON array by finding matching brackets
bracket_count = 0
json_end = json_start
for i, char in enumerate(output[json_start:], start=json_start):
    if char == '[':
        bracket_count += 1
    elif char == ']':
        bracket_count -= 1
        if bracket_count == 0:
            json_end = i + 1
            break

modules = json.loads(output[json_start:json_end])

print(f"Processing {len(modules)} modules...")

enriched = []

for i, module in enumerate(modules):
    if i % 100 == 0:
        print(f"Progress: {i}/{len(modules)}")

    # Generate keywords based on module info
    keywords = []

    name = module.get('name', '')
    summary = module.get('summary', '')
    tech_name = module.get('technical_name', '')
    tags = module.get('functional_tags', [])
    ai_desc = module.get('ai_description', '')

    # Stock/Inventory modules
    if 'stock' in tech_name or 'inventory' in tech_name.lower():
        keywords.extend(['warehouse', 'stock control', 'inventory tracking'])
        if 'pack' in tech_name:
            keywords.extend(['packaging', 'packing', 'empaquetar'])
        if 'report' in tech_name:
            keywords.extend(['stock report', 'inventory report', 'informe inventario'])
        if 'valuation' in tech_name:
            keywords.extend(['inventory valuation', 'stock value', 'valoración inventario'])
        if 'location' in tech_name:
            keywords.extend(['warehouse location', 'storage location', 'ubicación almacén'])
        if 'move' in tech_name:
            keywords.extend(['stock movement', 'inventory transfer', 'movimiento stock'])

    # Project modules
    elif 'project' in tech_name:
        keywords.extend(['project management', 'gestión proyectos'])
        if 'task' in tech_name:
            keywords.extend(['task management', 'tareas', 'task tracking'])
        if 'timesheet' in tech_name:
            keywords.extend(['time tracking', 'horas trabajadas', 'timesheet'])
        if 'issue' in tech_name or 'bug' in tech_name:
            keywords.extend(['issue tracking', 'bug tracking', 'incidencias'])
        if 'milestone' in tech_name:
            keywords.extend(['milestones', 'hitos', 'deliverables'])
        if 'stage' in tech_name:
            keywords.extend(['workflow', 'project stages', 'etapas proyecto'])

    # Accounting modules
    elif 'account' in tech_name:
        keywords.extend(['accounting', 'contabilidad'])
        if 'invoice' in tech_name:
            keywords.extend(['invoicing', 'facturación', 'billing'])
        if 'payment' in tech_name:
            keywords.extend(['payments', 'pagos', 'payment processing'])
        if 'report' in tech_name:
            keywords.extend(['financial reports', 'informes financieros', 'accounting reports'])
        if 'tax' in tech_name or 'vat' in tech_name:
            keywords.extend(['tax', 'VAT', 'impuestos', 'IVA'])
        if 'reconcil' in tech_name:
            keywords.extend(['reconciliation', 'conciliación', 'statement matching'])
        if 'asset' in tech_name:
            keywords.extend(['assets', 'activos', 'fixed assets'])
        if 'analytic' in tech_name:
            keywords.extend(['cost centers', 'analytical accounting', 'centros de costo'])

    # Sales modules
    elif 'sale' in tech_name:
        keywords.extend(['sales', 'ventas'])
        if 'order' in tech_name:
            keywords.extend(['sales order', 'pedido venta', 'quotation'])
        if 'commission' in tech_name:
            keywords.extend(['sales commission', 'comisiones', 'agent commission'])
        if 'discount' in tech_name:
            keywords.extend(['discounts', 'descuentos', 'pricing'])

    # Purchase modules
    elif 'purchase' in tech_name:
        keywords.extend(['purchasing', 'compras'])
        if 'order' in tech_name:
            keywords.extend(['purchase order', 'orden compra', 'procurement'])
        if 'requisition' in tech_name:
            keywords.extend(['purchase requisition', 'solicitud compra', 'RFQ'])
        if 'agreement' in tech_name:
            keywords.extend(['purchase agreement', 'acuerdo compra', 'blanket order'])

    # HR modules
    elif 'hr' in tech_name:
        keywords.extend(['human resources', 'recursos humanos', 'HR'])
        if 'expense' in tech_name:
            keywords.extend(['employee expenses', 'gastos empleados', 'expense report'])
        if 'timesheet' in tech_name:
            keywords.extend(['timesheet', 'time tracking', 'registro horas'])
        if 'attendance' in tech_name:
            keywords.extend(['attendance', 'asistencia', 'check in check out'])
        if 'leave' in tech_name or 'holiday' in tech_name:
            keywords.extend(['time off', 'vacaciones', 'leave management'])
        if 'payroll' in tech_name:
            keywords.extend(['payroll', 'nómina', 'salary'])
        if 'recruitment' in tech_name:
            keywords.extend(['recruitment', 'reclutamiento', 'hiring'])

    # Manufacturing modules
    elif 'mrp' in tech_name:
        keywords.extend(['manufacturing', 'fabricación', 'production'])
        if 'bom' in tech_name:
            keywords.extend(['bill of materials', 'BOM', 'lista materiales'])
        if 'workorder' in tech_name or 'work_order' in tech_name:
            keywords.extend(['work order', 'orden trabajo', 'production order'])

    # CRM modules
    elif 'crm' in tech_name:
        keywords.extend(['CRM', 'customer relationship', 'leads'])
        if 'lead' in tech_name:
            keywords.extend(['leads', 'oportunidades', 'opportunities'])
        if 'claim' in tech_name:
            keywords.extend(['claims', 'reclamos', 'customer complaints'])

    # Localization modules (Spanish)
    elif 'l10n_es' in tech_name or 'l10n_mx' in tech_name or 'l10n_ar' in tech_name or 'l10n_cl' in tech_name or 'l10n_co' in tech_name or 'l10n_pe' in tech_name:
        keywords.extend(['localization', 'localización'])
        if 'l10n_es' in tech_name:
            keywords.extend(['Spain', 'España', 'Spanish'])
        if 'l10n_mx' in tech_name:
            keywords.extend(['Mexico', 'México', 'Mexican'])
        if 'l10n_ar' in tech_name:
            keywords.extend(['Argentina', 'argentino'])
        if 'factura' in tech_name:
            keywords.extend(['electronic invoice', 'factura electrónica', 'e-invoice'])
        if 'aeat' in tech_name:
            keywords.extend(['AEAT', 'Spanish tax agency', 'agencia tributaria'])
        if 'sii' in tech_name:
            keywords.extend(['SII', 'immediate supply', 'suministro inmediato'])

    # Website/eCommerce modules
    elif 'website' in tech_name:
        keywords.extend(['website', 'sitio web', 'eCommerce'])
        if 'shop' in tech_name or 'sale' in tech_name:
            keywords.extend(['online store', 'tienda online', 'eCommerce'])
        if 'blog' in tech_name:
            keywords.extend(['blog', 'content management'])
        if 'form' in tech_name:
            keywords.extend(['web forms', 'formularios', 'contact form'])

    # Add generic keywords based on name/summary
    if 'report' in name.lower() or 'report' in summary.lower():
        keywords.extend(['reports', 'reporting', 'informes'])
    if 'export' in name.lower() or 'export' in summary.lower():
        keywords.extend(['export', 'exportar', 'data export'])
    if 'import' in name.lower() or 'import' in summary.lower():
        keywords.extend(['import', 'importar', 'data import'])
    if 'wizard' in name.lower():
        keywords.extend(['wizard', 'asistente', 'guided process'])
    if 'dashboard' in name.lower():
        keywords.extend(['dashboard', 'panel', 'KPI'])
    if 'partner' in tech_name or 'customer' in tech_name:
        keywords.extend(['customer', 'cliente', 'partner'])

    # Remove duplicates and limit to 10
    keywords = list(dict.fromkeys(keywords))[:10]

    # If we don't have enough keywords, add some generic based on the name
    if len(keywords) < 7:
        name_words = name.lower().replace('_', ' ').split()
        for word in name_words:
            if word not in ['odoo', 'module', 'oca', 'base', 'stock', 'account', 'project', 'sale', 'purchase'] and len(word) > 3:
                if word not in keywords:
                    keywords.append(word)
                if len(keywords) >= 7:
                    break

    enriched.append({
        "id": module['id'],
        "keywords": keywords
    })

# Save to JSON file
with open('scripts/.enriched_keywords_full.json', 'w') as f:
    json.dump(enriched, f, indent=2, ensure_ascii=False)

print(f"\nGenerated keywords for {len(enriched)} modules")
print(f"Saved to scripts/.enriched_keywords_full.json")