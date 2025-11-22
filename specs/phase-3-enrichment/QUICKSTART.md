# Quick Start Guide - Fase 3: Data Enrichment

**Tiempo estimado:** 8-10 horas (incluye ejecución de pipeline ~2-4 horas)
**Prerequisito:** ✅ Fase 2 completada (Hybrid Search funcional)

---

## 🚀 Inicio Rápido (TL;DR)

```bash
# 1. Migration
psql ai_odoo_finder < migrations/003_add_enrichment_fields.sql

# 2. Implementar servicios
# Ver SPEC-202, SPEC-203, SPEC-204

# 3. Ejecutar pipeline (TEST con 10 módulos primero)
python scripts/enrich_modules.py --limit 10 --dry-run

# 4. Ejecutar pipeline completo
python scripts/enrich_modules.py

# 5. Benchmark
python scripts/run_benchmark.py --search-mode hybrid

# 6. Comparar
python scripts/compare_benchmarks.py \
    tests/results/hybrid_*.json \
    tests/results/enriched_*.json
```

---

## 📋 Paso a Paso

### Paso 1: Schema Migration (30 min)

```bash
# Backup BD
pg_dump ai_odoo_finder > backups/before_phase3_$(date +%Y%m%d).sql

# Aplicar migration
psql ai_odoo_finder < migrations/003_add_enrichment_fields.sql

# Validar
psql ai_odoo_finder -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'odoo_modules' AND column_name IN ('ai_description', 'functional_tags', 'keywords', 'enrichment_metadata');"
```

**Checklist:**
- [ ] Migration aplicada
- [ ] 4 columnas nuevas
- [ ] 3 índices GIN creados

---

### Paso 2: AI Description Service (3 horas)

Crear `app/services/ai_description_service.py` usando código de SPEC-202.

**Key points:**
- Claude Haiku para cost-efficiency
- Prompt template con context del módulo
- Quality validation automática
- Batch processing con rate limiting

**Test:**
```python
service = AIDescriptionService(api_key=settings.anthropic_api_key)

test_module = {
    'technical_name': 'sale_subscription',
    'name': 'Sale Subscription',
    'summary': 'Recurring invoices',
    'depends': ['sale', 'account'],
    'version': '16.0'
}

description = service.generate_description(test_module)
print(description)  # Should be 2-3 paragraphs
```

---

### Paso 3: Tagging Service (2 horas)

1. Crear `config/functional_tags_taxonomy.yaml` con taxonomy
2. Implementar `app/services/tagging_service.py`

**Test:**
```python
service = TaggingService()

module = {
    'technical_name': 'account_invoice_recurring',
    'summary': 'Recurring invoices'
}

tags = service.assign_tags(module)
print(tags)  # ['accounting_finance', 'subscription_management', ...]
```

---

### Paso 4: Keywords Service (2 horas)

Implementar `app/services/keyword_service.py` con:
- TF-IDF extraction
- Domain keywords matching
- Synonym expansion

**Test:**
```python
service = KeywordService()

module = {
    'technical_name': 'sale_b2b_portal',
    'summary': 'B2B portal for suppliers',
    'ai_description': '...'
}

keywords = service.extract_keywords(module)
print(keywords)  # ['b2b', 'portal', 'supplier', 'sale', ...]
```

---

### Paso 5: Enrichment Pipeline (2 horas)

Crear `scripts/enrich_modules.py` que orquesta todo.

**Test con 10 módulos:**
```bash
python scripts/enrich_modules.py --limit 10 --dry-run

# Output esperado:
# [1/7] Loading modules... Found 10
# [2/7] Generating AI descriptions... 10/10
# [3/7] Assigning tags... 10
# [4/7] Extracting keywords... 10
# [5/7] SKIPPED (dry run)
# [6/7] SKIPPED (dry run)
# [7/7] Report saved to: tests/results/enrichment_report_*.json
```

---

### Paso 6: Ejecución Completa (2-4 horas)

```bash
# Ejecutar pipeline completo
# NOTA: Esto puede tardar 2-4 horas dependiendo de:
# - Número de módulos sin README (~40% del total)
# - Rate limits de Claude API
# - Batch size configurado

python scripts/enrich_modules.py

# Monitor progress
tail -f logs/enrichment.log  # Si implementas logging

# Verificar en BD
psql ai_odoo_finder -c "
    SELECT
        COUNT(*) as total,
        COUNT(ai_description) as enriched,
        ROUND(100.0 * COUNT(ai_description) / COUNT(*), 1) as pct
    FROM odoo_modules
    WHERE readme IS NULL OR LENGTH(readme) < 500;
"
```

**Checklist:**
- [ ] Pipeline ejecutado sin errores fatales
- [ ] >80% de módulos enriquecidos
- [ ] Report generado
- [ ] API costs < $10

---

### Paso 7: Benchmark & Validación (1 hora)

```bash
# Ejecutar benchmark
python scripts/run_benchmark.py --search-mode hybrid

# Comparar con Fase 2
python scripts/compare_benchmarks.py \
    tests/results/hybrid_20251122_*.json \
    tests/results/enriched_*.json

# Output esperado:
# Hybrid (Fase 2):   P@3 = 52.0%
# Enriched (Fase 3): P@3 = 63.0%  (+11.0%)
# ✅ PHASE 3 SUCCESS
```

---

## ✅ Definition of Done

```bash
# Tests
pytest tests/test_phase3_acceptance.py -v  # All PASSED

# Benchmark mejora
# P@3 improvement >= 10%

# Commit
git add .
git commit -m "feat: Complete Phase 3 - Data Enrichment"
git tag phase-3-complete
git push origin main --tags
```

---

## 🚨 Troubleshooting

### Error: "Anthropic API rate limit"

**Solución:**
```python
# En ai_description_service.py, aumentar delay
delay_between_batches=2.0  # En vez de 1.0
```

### Error: "Low quality descriptions"

**Solución:**
- Review prompt template
- Ajustar quality validation thresholds
- Test con módulos específicos

### Costo > $10

**Solución:**
- Limitar a módulos más importantes (por github_stars)
- Usar batch size más pequeño
- Pausar y continuar después

---

## 💰 Cost Tracking

```python
# Monitorear costs durante ejecución
SELECT
    COUNT(*) FILTER (WHERE ai_description IS NOT NULL) as generated,
    COUNT(*) FILTER (WHERE ai_description IS NOT NULL) * 0.001 as estimated_cost_usd
FROM odoo_modules;
```

---

**Happy enriching! 🚀**
