# 🧠 Guía de Enrichment - AI-OdooFinder

**Fecha:** 25-26 Noviembre 2025
**Fase:** 3 - Data Enrichment ✅ COMPLETADO
**Costo:** $0 (usando Claude Max subscription)

---

## 📋 Descripción

El sistema de enrichment permite mejorar los datos de los módulos Odoo con:
- **AI Description**: Descripción generada por IA en inglés
- **Functional Tags**: Categorías funcionales (sales, accounting, inventory...)
- **Keywords**: Palabras clave para mejorar búsquedas

---

## 🗄️ Campos en Base de Datos

```sql
ai_description     TEXT        -- Descripción AI en inglés
functional_tags    TEXT[]      -- Tags funcionales
keywords           TEXT[]      -- Keywords de búsqueda
enriched_at        TIMESTAMP   -- Cuándo se enriqueció
enrichment_version VARCHAR(20) -- Versión del proceso (v1.0)
```

---

## 🚀 Cómo Usar

### Opción 1: Slash Command `/enrich`

En un nuevo hilo de Claude Code, ejecuta:

```
/enrich 50
```

Esto le indica a Claude que:
1. Obtenga 50 módulos sin enriquecer
2. Genere ai_description, tags y keywords para cada uno
3. Guarde los resultados en la BD

### Opción 2: Flujo Manual

**Paso 1: Obtener módulos sin enriquecer**
```bash
uv run python scripts/get_modules_for_enrichment.py --limit 20
```

**Paso 2: Ver estadísticas de progreso**
```bash
uv run python scripts/get_modules_for_enrichment.py --stats
```

**Paso 3: Guardar enrichment (individual)**
```bash
uv run python scripts/save_module_enrichment.py \
  --id 123 \
  --description "AI generated description..." \
  --tags "sales,accounting,automation" \
  --keywords "invoice,billing,recurring"
```

**Paso 4: Guardar enrichment (batch JSON)**
```bash
uv run python scripts/save_module_enrichment.py --json '[
  {
    "id": 123,
    "ai_description": "Description...",
    "functional_tags": ["sales", "accounting"],
    "keywords": ["invoice", "billing"]
  },
  {
    "id": 456,
    "ai_description": "Another description...",
    "functional_tags": ["inventory"],
    "keywords": ["stock", "warehouse"]
  }
]'
```

---

## 🏷️ Taxonomía de Tags Funcionales

### Categorías Principales
- `sales` - Ventas y CRM
- `accounting` - Contabilidad y finanzas
- `inventory` - Inventario y almacén
- `manufacturing` - Fabricación y producción
- `hr` - Recursos humanos
- `website` - Web y eCommerce
- `localization` - Localización por país
- `reporting` - Informes y análisis
- `integration` - Integraciones externas
- `automation` - Automatización de procesos
- `crm` - Gestión de clientes
- `purchase` - Compras
- `project` - Proyectos
- `pos` - Punto de venta

### Casos de Uso
- `b2b` - Business to Business
- `b2c` - Business to Consumer
- `multi_company` - Multi-empresa
- `subscription` - Suscripciones
- `document_management` - Gestión documental
- `compliance` - Cumplimiento normativo

---

## 📝 Formato de AI Description

Las descripciones deben:
1. Estar en **inglés**
2. Tener 2-3 párrafos
3. Incluir:
   - Qué funcionalidad proporciona el módulo
   - Casos de uso típicos
   - Integraciones con otros módulos
4. Usar términos que los usuarios buscarían

### Ejemplo

```
Sale Subscription manages recurring revenue through automated subscription
billing in Odoo. It enables businesses to create subscription products with
customizable billing periods (monthly, quarterly, yearly), automatic invoice
generation, and renewal management.

Key features include trial periods, proration for mid-cycle changes, and
integration with the sales and accounting modules. The module supports
multiple pricing strategies and can handle both B2B and B2C subscription
models.

Ideal for SaaS companies, membership organizations, magazines, and any
business with recurring billing needs. Integrates seamlessly with payment
acquirers for automated payment collection.
```

---

## 🔄 Propagación Automática

**Importante:** El sistema detecta automáticamente todas las versiones de un módulo y propaga el enrichment a todas ellas.

Ejemplo: Si enriqueces `web_m2x_options_manager` (v18.0), el sistema también actualiza:
- `web_m2x_options_manager` v17.0
- `web_m2x_options_manager` v16.0
- etc.

Esto reduce drásticamente el trabajo necesario:
- **Total módulos en BD:** 15,880
- **Módulos únicos (technical_name):** 5,425
- **Promedio versiones por módulo:** 2.9
- **Reducción:** ~66% menos trabajo

---

## 📊 Progreso Final (Completado 25 Nov 2025)

```
Total módulos:           15,881
Con ai_description:      15,881 (100%)
Con functional_tags:     15,881 (100%)
Con keywords:            15,881 (100%)
Progress:                100% ✅ COMPLETADO
```

### Resumen de Ejecución

| Métrica | Valor |
|---------|-------|
| Módulos enriquecidos | 15,881 |
| Tiempo total | ~1 tarde |
| Batch size óptimo | ~2,500 módulos |
| Modelo usado | Claude Haiku |
| Contexto usado por batch | ~50% |

**Nota:** El enrichment se completó en una tarde usando batches de ~2,500 módulos con Claude Haiku

---

## 🔧 Archivos del Sistema

```
scripts/
├── get_modules_for_enrichment.py  # Obtiene módulos sin enriquecer
└── save_module_enrichment.py      # Guarda enrichment en BD

.claude/commands/
└── enrich.md                      # Slash command /enrich

backend/
├── app/models.py                  # Modelo con campos de enrichment
└── migrations/
    └── 003_add_enrichment_fields.sql  # Migration de BD
```

---

## ⚠️ Notas Importantes

1. **No usar API externa** - Usa tu suscripción Claude Max
2. **Guardar progreso** - `enriched_at` marca módulos ya procesados
3. **Idioma** - Descripciones siempre en inglés para mejor búsqueda
4. **Tags limitados** - Usar solo tags de la taxonomía definida
5. **Keywords relevantes** - 5-10 keywords por módulo

---

## 🆘 Troubleshooting

### Error: "Module ID not found"
- Verificar que el ID existe: `uv run python scripts/get_modules_for_enrichment.py --limit 1`

### Error: "Column does not exist"
- Aplicar migration: Ejecutar SQL en `backend/migrations/003_add_enrichment_fields.sql`

### Ver módulos ya enriquecidos
```bash
uv run python -c "
from backend.app.database import SessionLocal
from backend.app.models import OdooModule

db = SessionLocal()
enriched = db.query(OdooModule).filter(OdooModule.enriched_at.isnot(None)).limit(5).all()
for m in enriched:
    print(f'{m.technical_name} - {m.enriched_at}')
db.close()
"
```

---

## 📞 Comandos Rápidos

```bash
# Ver progreso
uv run python scripts/get_modules_for_enrichment.py --stats

# Obtener 50 módulos para enriquecer
uv run python scripts/get_modules_for_enrichment.py --limit 50

# Obtener módulos de versión específica
uv run python scripts/get_modules_for_enrichment.py --limit 20 --version 16.0

# Guardar batch desde archivo JSON
uv run python scripts/save_module_enrichment.py --json enrichment_batch.json
```

---

## 🔍 Full-Text Search Actualizado

La migración `004_update_fulltext_with_enrichment.sql` actualiza el índice de búsqueda full-text para incluir los campos de enrichment:

| Peso | Campos | Prioridad |
|------|--------|-----------|
| A (1.0) | `technical_name`, `name` | Máxima |
| B (0.4) | `summary`, `ai_description`, `keywords` | Alta |
| C (0.2) | `description`, `functional_tags` | Media |
| D (0.1) | `readme` | Baja |

Esto mejora significativamente la calidad de la búsqueda híbrida sin necesidad de regenerar embeddings.

---

**Última actualización:** 26 Nov 2025