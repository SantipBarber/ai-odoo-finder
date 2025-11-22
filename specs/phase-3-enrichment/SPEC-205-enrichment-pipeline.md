# SPEC-205: Enrichment Pipeline

**ID:** SPEC-205
**Componente:** Orchestration Script
**Archivo:** `scripts/enrich_modules.py`
**Prioridad:** Alta
**Estimación:** 2 horas
**Dependencias:** SPEC-202, SPEC-203, SPEC-204

---

## 📋 Descripción

Script orquestador que ejecuta el pipeline completo de enrichment: genera AI descriptions, asigna tags, extrae keywords, actualiza BD y regenera embeddings.

---

## 📐 Pipeline Flow

```
1. Load modules needing enrichment (no ai_description AND poor README)
2. Generate AI descriptions (Claude Haiku)
3. Assign functional tags (rule-based)
4. Extract keywords (TF-IDF + domain)
5. Update database (batch)
6. Regenerate embeddings (with enriched data)
7. Update searchable_text (trigger auto)
8. Generate report
```

---

## 💻 Implementación

```python
#!/usr/bin/env python3
"""
Enrichment Pipeline: Enrich modules with AI descriptions, tags, keywords.
"""
import asyncio
import json
from datetime import datetime
from sqlalchemy import text
from app.database import get_async_session
from app.services.ai_description_service import AIDescriptionService
from app.services.tagging_service import TaggingService
from app.services.keyword_service import KeywordService
from app.services.embedding_service import EmbeddingService
from app.config import settings


class EnrichmentPipeline:
    """Pipeline de enrichment de módulos."""

    def __init__(self, db_session):
        self.db = db_session
        self.ai_service = AIDescriptionService(api_key=settings.anthropic_api_key)
        self.tag_service = TaggingService()
        self.keyword_service = KeywordService()
        self.embedding_service = EmbeddingService()

    async def run(
        self,
        limit: Optional[int] = None,
        dry_run: bool = False
    ):
        """
        Ejecuta pipeline completo.

        Args:
            limit: Limitar a N módulos (para testing)
            dry_run: Si True, no actualiza BD
        """

        print("="*80)
        print("AI-OdooFinder Enrichment Pipeline")
        print("="*80)

        # 1. Load modules needing enrichment
        print("\n[1/7] Loading modules needing enrichment...")
        modules = await self._load_modules_to_enrich(limit)
        print(f"      Found {len(modules)} modules to enrich")

        if not modules:
            print("\n✅ No modules need enrichment!")
            return

        # 2. Generate AI descriptions
        print("\n[2/7] Generating AI descriptions...")
        modules_with_descriptions = self.ai_service.generate_batch(
            modules,
            batch_size=10,
            delay_between_batches=1.0
        )
        success_count = sum(1 for m in modules_with_descriptions if m.get('ai_description'))
        print(f"      Generated {success_count}/{len(modules)} descriptions")

        # 3. Assign tags
        print("\n[3/7] Assigning functional tags...")
        for module in modules_with_descriptions:
            module['functional_tags'] = self.tag_service.assign_tags(module)
        print(f"      Tagged {len(modules_with_descriptions)} modules")

        # 4. Extract keywords
        print("\n[4/7] Extracting keywords...")
        for module in modules_with_descriptions:
            module['keywords'] = self.keyword_service.extract_keywords(module)
        print(f"      Extracted keywords for {len(modules_with_descriptions)} modules")

        # 5. Update database
        if not dry_run:
            print("\n[5/7] Updating database...")
            await self._update_database(modules_with_descriptions)
            print(f"      Updated {len(modules_with_descriptions)} records")
        else:
            print("\n[5/7] SKIPPED (dry run)")

        # 6. Regenerate embeddings
        if not dry_run:
            print("\n[6/7] Regenerating embeddings...")
            await self._regenerate_embeddings(modules_with_descriptions)
            print(f"      Regenerated {len(modules_with_descriptions)} embeddings")
        else:
            print("\n[6/7] SKIPPED (dry run)")

        # 7. Generate report
        print("\n[7/7] Generating report...")
        report_path = self._generate_report(modules_with_descriptions)
        print(f"      Report saved to: {report_path}")

        print("\n" + "="*80)
        print("✅ ENRICHMENT COMPLETE")
        print("="*80)

    async def _load_modules_to_enrich(self, limit: Optional[int]) -> List[Dict]:
        """Carga módulos que necesitan enrichment."""

        query = text("""
            SELECT
                id,
                technical_name,
                name,
                summary,
                description,
                readme,
                depends,
                version,
                category
            FROM odoo_modules
            WHERE ai_description IS NULL
              AND (readme IS NULL OR LENGTH(readme) < 500)
            ORDER BY github_stars DESC NULLS LAST
            LIMIT :limit
        """)

        result = await self.db.execute(query, {"limit": limit or 999999})
        rows = result.fetchall()

        return [
            {
                'id': row.id,
                'technical_name': row.technical_name,
                'name': row.name or '',
                'summary': row.summary or '',
                'description': row.description or '',
                'readme': row.readme or '',
                'depends': row.depends or [],
                'version': row.version,
                'category': row.category or 'Uncategorized'
            }
            for row in rows
        ]

    async def _update_database(self, modules: List[Dict]):
        """Actualiza BD con datos enriquecidos."""

        update_query = text("""
            UPDATE odoo_modules
            SET
                ai_description = :ai_description,
                functional_tags = :functional_tags,
                keywords = :keywords,
                enrichment_metadata = :enrichment_metadata
            WHERE id = :id
        """)

        for module in modules:
            await self.db.execute(update_query, {
                'id': module['id'],
                'ai_description': module.get('ai_description'),
                'functional_tags': module.get('functional_tags', []),
                'keywords': module.get('keywords', []),
                'enrichment_metadata': json.dumps(module.get('enrichment_metadata', {}))
            })

        await self.db.commit()

    async def _regenerate_embeddings(self, modules: List[Dict]):
        """Regenera embeddings incluyendo datos enriquecidos."""

        for module in modules:
            # Combine text for embedding
            combined_text = ' '.join(filter(None, [
                module.get('technical_name', ''),
                module.get('name', ''),
                module.get('summary', ''),
                module.get('ai_description', ''),
                ' '.join(module.get('functional_tags', [])),
                ' '.join(module.get('keywords', []))
            ]))

            # Generate new embedding
            embedding = await self.embedding_service.get_embedding(combined_text)

            # Update in DB
            await self.db.execute(
                text("UPDATE odoo_modules SET embedding = :embedding WHERE id = :id"),
                {'id': module['id'], 'embedding': embedding}
            )

        await self.db.commit()

    def _generate_report(self, modules: List[Dict]) -> str:
        """Genera reporte del enrichment."""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"tests/results/enrichment_report_{timestamp}.json"

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_processed': len(modules),
            'successful_descriptions': sum(1 for m in modules if m.get('ai_description')),
            'failed_descriptions': sum(1 for m in modules if not m.get('ai_description')),
            'modules_with_tags': sum(1 for m in modules if m.get('functional_tags')),
            'modules_with_keywords': sum(1 for m in modules if m.get('keywords')),
            'sample_modules': modules[:5]  # First 5 as sample
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        return report_path


async def main():
    """Entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Enrich modules with AI descriptions, tags, keywords')
    parser.add_argument('--limit', type=int, help='Limit number of modules to enrich')
    parser.add_argument('--dry-run', action='store_true', help='Run without updating database')
    args = parser.parse_args()

    async with get_async_session() as db:
        pipeline = EnrichmentPipeline(db)
        await pipeline.run(limit=args.limit, dry_run=args.dry_run)


if __name__ == '__main__':
    asyncio.run(main())
```

---

## 🧪 Tests

```python
@pytest.mark.asyncio
async def test_load_modules_to_enrich(db_session):
    """Test que carga módulos correctamente."""

    pipeline = EnrichmentPipeline(db_session)

    modules = await pipeline._load_modules_to_enrich(limit=10)

    assert len(modules) <= 10
    assert all('technical_name' in m for m in modules)


@pytest.mark.asyncio
async def test_dry_run_doesnt_modify_db(db_session):
    """Test que dry-run no modifica BD."""

    pipeline = EnrichmentPipeline(db_session)

    # Count before
    result = await db_session.execute(
        text("SELECT COUNT(*) FROM odoo_modules WHERE ai_description IS NOT NULL")
    )
    count_before = result.scalar()

    # Run dry-run
    await pipeline.run(limit=5, dry_run=True)

    # Count after
    result = await db_session.execute(
        text("SELECT COUNT(*) FROM odoo_modules WHERE ai_description IS NOT NULL")
    )
    count_after = result.scalar()

    assert count_before == count_after
```

---

## 📊 Usage

```bash
# Test con 10 módulos (dry run)
python scripts/enrich_modules.py --limit 10 --dry-run

# Enriquecer 100 módulos
python scripts/enrich_modules.py --limit 100

# Enriquecer TODOS los módulos sin descripción
python scripts/enrich_modules.py
```

---

## ✅ Criterios de Aceptación

- ✅ Pipeline ejecuta los 7 pasos
- ✅ Dry-run funciona
- ✅ Genera reporte
- ✅ Error handling robusto
- ✅ Progress visible

---

## 🔗 Siguiente Paso

→ [SPEC-206: Acceptance Criteria](./SPEC-206-acceptance-criteria.md)

---

**Estado:** 🔴 Pendiente
