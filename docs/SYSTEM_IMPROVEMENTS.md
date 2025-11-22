# AI-OdooFinder - Especificaciones Técnicas de Mejoras v1.0

**Fecha:** 22 Noviembre 2025  
**Proyecto:** AI-OdooFinder  
**Objetivo:** Mejorar precisión y relevancia de resultados de búsqueda  
**Prioridad:** Enriquecimiento de datos + Hybrid Search + Reranking

---

## 📋 ÍNDICE

1. [Contexto y Arquitectura Actual](#contexto)
2. [Fase 1: Diagnóstico y Benchmark](#fase-1)
3. [Fase 2: Hybrid Search (BM25 + Vector)](#fase-2)
4. [Fase 3: Enriquecimiento de Datos](#fase-3)
5. [Fase 4: Two-Stage Retrieval con Reranking](#fase-4)
6. [Fase 5: Testing y Métricas](#fase-5)
7. [Roadmap de Implementación](#roadmap)

---

## 1. CONTEXTO Y ARQUITECTURA ACTUAL <a name="contexto"></a>

### 1.1 Stack Técnico Actual
```yaml
Backend:
  - FastAPI (Python 3.14)
  - PostgreSQL 17 con pgVector
  - SQLAlchemy 2.0
  - OpenRouter API (embeddings)

Datos:
  - 2,508 módulos OCA indexados
  - Versiones: 12.0 a 19.0
  - 60% con README indexado
  - Modelo embeddings: Qwen3-Embedding-4B (1024 dims)

MCP:
  - Tool: search_odoo_modules()
  - Parámetros: query, version, dependencies, limit
  - Respuesta: JSON con top N módulos
```

### 1.2 Esquema BD Actual
```sql
-- Archivo: app/models.py
CREATE TABLE odoo_modules (
    id SERIAL PRIMARY KEY,
    technical_name TEXT NOT NULL UNIQUE,
    name TEXT,
    summary TEXT,
    description TEXT,
    readme TEXT,  -- 60% populated
    version TEXT,  -- e.g., "16.0"
    depends TEXT[],  -- Dependencies array
    author TEXT,
    github_stars INT DEFAULT 0,
    last_commit_date TIMESTAMP,
    repository_url TEXT,
    manifest_path TEXT,
    embedding vector(1024),  -- pgVector
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices actuales
CREATE INDEX idx_modules_version ON odoo_modules(version);
CREATE INDEX idx_modules_embedding ON odoo_modules 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### 1.3 Búsqueda Actual (Baseline)
```python
# Archivo: app/services/search_service.py
async def search_modules(
    query: str,
    version: str,
    dependencies: Optional[List[str]] = None,
    limit: int = 5
) -> List[ModuleResult]:
    # 1. Generate query embedding
    query_embedding = await embedding_service.get_embedding(query)
    
    # 2. Vector similarity search
    sql = """
        SELECT *, 
               1 - (embedding <=> :query_vector) as similarity_score
        FROM odoo_modules
        WHERE version = :version
    """
    
    if dependencies:
        sql += " AND depends && :deps"
    
    sql += """
        ORDER BY embedding <=> :query_vector
        LIMIT :limit
    """
    
    return await db.execute(sql, {
        "query_vector": query_embedding,
        "version": version,
        "deps": dependencies,
        "limit": limit
    })
```

### 1.4 Problemas Identificados
1. **Datos pobres:** 40% sin README = contexto limitado
2. **Solo vector search:** Ignora coincidencias exactas
3. **Sin reranking:** El primer match vectorial puede no ser el mejor
4. **Falta metadata estructurada:** Sin tags funcionales, keywords, casos de uso

---

## 2. FASE 1: DIAGNÓSTICO Y BENCHMARK <a name="fase-1"></a>

### 2.1 Objetivo
Crear 20 búsquedas de prueba documentadas que representen casos de uso reales y medir baseline de precisión.

### 2.2 Especificación Técnica

**Archivo nuevo:** `tests/benchmark_queries.json`

```json
{
  "benchmark_queries": [
    {
      "id": 1,
      "query": "separar flujos B2B y B2C en ventas",
      "version": "16.0",
      "expected_modules": ["sale_b2b_b2c", "portal_partner_type", "sale_portal"],
      "category": "sales_workflow",
      "difficulty": "hard"
    },
    {
      "id": 2,
      "query": "facturación electrónica España",
      "version": "16.0",
      "expected_modules": ["l10n_es_facturae", "l10n_es_aeat", "l10n_es_vat_book"],
      "category": "localization_spain",
      "difficulty": "medium"
    },
    {
      "id": 3,
      "query": "gestión de trazabilidad lotes y series",
      "version": "17.0",
      "expected_modules": ["stock_production_lot", "product_expiry", "stock_lot_traceability"],
      "category": "inventory",
      "difficulty": "medium"
    },
    {
      "id": 4,
      "query": "portal clientes con documentos personalizados",
      "version": "16.0",
      "expected_modules": ["portal_document", "portal_partner_document", "dms_portal"],
      "category": "portal",
      "difficulty": "hard"
    },
    {
      "id": 5,
      "query": "descuentos automáticos por volumen",
      "version": "16.0",
      "expected_modules": ["sale_discount_volume", "sale_promotion", "product_pricelist_volume"],
      "category": "sales_pricing",
      "difficulty": "easy"
    }
    // ... 15 more queries covering:
    // - Accounting (invoicing, payments, reconciliation)
    // - Inventory (kits, dropshipping, cross-docking)
    // - Manufacturing (BoM, work orders, subcontracting)
    // - HR (payroll, expenses, recruitment)
    // - Website (ecommerce, blog, forms)
  ]
}
```

**Archivo nuevo:** `scripts/run_benchmark.py`

```python
"""
Ejecuta benchmark de búsquedas y genera reporte de precisión.
"""
import json
import asyncio
from datetime import datetime
from typing import List, Dict
from app.services.search_service import SearchService

async def run_benchmark():
    """Ejecuta todas las queries del benchmark y calcula métricas."""
    
    # Load benchmark queries
    with open('tests/benchmark_queries.json', 'r') as f:
        data = json.load(f)
        queries = data['benchmark_queries']
    
    results = []
    search_service = SearchService()
    
    for query_data in queries:
        # Execute search
        search_results = await search_service.search_modules(
            query=query_data['query'],
            version=query_data['version'],
            limit=10
        )
        
        # Calculate metrics
        returned_modules = [r.technical_name for r in search_results]
        expected_modules = query_data['expected_modules']
        
        # Precision@k
        precision_at_3 = calculate_precision_at_k(returned_modules[:3], expected_modules)
        precision_at_5 = calculate_precision_at_k(returned_modules[:5], expected_modules)
        
        # Recall@10
        recall_at_10 = calculate_recall(returned_modules[:10], expected_modules)
        
        # MRR (Mean Reciprocal Rank)
        mrr = calculate_mrr(returned_modules, expected_modules)
        
        results.append({
            'query_id': query_data['id'],
            'query': query_data['query'],
            'category': query_data['category'],
            'difficulty': query_data['difficulty'],
            'precision@3': precision_at_3,
            'precision@5': precision_at_5,
            'recall@10': recall_at_10,
            'mrr': mrr,
            'returned_modules': returned_modules[:5],
            'expected_modules': expected_modules
        })
    
    # Generate report
    report = generate_report(results)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'benchmark_results_{timestamp}.json'
    
    with open(f'tests/results/{filename}', 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'total_queries': len(queries),
            'aggregate_metrics': report['aggregate'],
            'per_category': report['per_category'],
            'per_difficulty': report['per_difficulty'],
            'detailed_results': results
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"BENCHMARK RESULTS - {timestamp}")
    print(f"{'='*60}")
    print(f"\nAggregate Metrics:")
    print(f"  Precision@3: {report['aggregate']['precision@3']:.2%}")
    print(f"  Precision@5: {report['aggregate']['precision@5']:.2%}")
    print(f"  Recall@10:   {report['aggregate']['recall@10']:.2%}")
    print(f"  Mean MRR:    {report['aggregate']['mrr']:.3f}")
    print(f"\nResults saved to: tests/results/{filename}")

def calculate_precision_at_k(retrieved: List[str], expected: List[str]) -> float:
    """Calcula precision@k."""
    if not retrieved:
        return 0.0
    relevant = sum(1 for mod in retrieved if mod in expected)
    return relevant / len(retrieved)

def calculate_recall(retrieved: List[str], expected: List[str]) -> float:
    """Calcula recall."""
    if not expected:
        return 0.0
    relevant = sum(1 for mod in retrieved if mod in expected)
    return relevant / len(expected)

def calculate_mrr(retrieved: List[str], expected: List[str]) -> float:
    """Calcula Mean Reciprocal Rank."""
    for i, mod in enumerate(retrieved):
        if mod in expected:
            return 1 / (i + 1)
    return 0.0

def generate_report(results: List[Dict]) -> Dict:
    """Genera reporte agregado de métricas."""
    # Aggregate metrics
    aggregate = {
        'precision@3': sum(r['precision@3'] for r in results) / len(results),
        'precision@5': sum(r['precision@5'] for r in results) / len(results),
        'recall@10': sum(r['recall@10'] for r in results) / len(results),
        'mrr': sum(r['mrr'] for r in results) / len(results)
    }
    
    # By category
    categories = {}
    for result in results:
        cat = result['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result)
    
    per_category = {}
    for cat, cat_results in categories.items():
        per_category[cat] = {
            'precision@3': sum(r['precision@3'] for r in cat_results) / len(cat_results),
            'precision@5': sum(r['precision@5'] for r in cat_results) / len(cat_results),
            'count': len(cat_results)
        }
    
    # By difficulty
    difficulties = {}
    for result in results:
        diff = result['difficulty']
        if diff not in difficulties:
            difficulties[diff] = []
        difficulties[diff].append(result)
    
    per_difficulty = {}
    for diff, diff_results in difficulties.items():
        per_difficulty[diff] = {
            'precision@3': sum(r['precision@3'] for r in diff_results) / len(diff_results),
            'precision@5': sum(r['precision@5'] for r in diff_results) / len(diff_results),
            'count': len(diff_results)
        }
    
    return {
        'aggregate': aggregate,
        'per_category': per_category,
        'per_difficulty': per_difficulty
    }

if __name__ == '__main__':
    asyncio.run(run_benchmark())
```

### 2.3 Entregable Fase 1
- ✅ `tests/benchmark_queries.json` con 20 queries
- ✅ `scripts/run_benchmark.py` funcional
- ✅ Baseline metrics documentadas en `tests/results/baseline_YYYYMMDD.json`
- ✅ Identificar 5 patrones de fallo más comunes

**Criterio de éxito:** 
- Precision@3 baseline < 40% → Confirma necesidad de mejoras
- Documentar qué tipo de queries fallan más (exactas vs semánticas)

---

## 3. FASE 2: HYBRID SEARCH (BM25 + VECTOR) <a name="fase-2"></a>

### 3.1 Objetivo
Combinar búsqueda vectorial semántica con búsqueda textual BM25 para capturar tanto coincidencias semánticas como exactas.

### 3.2 Cambios en Base de Datos

**Archivo:** `migrations/002_add_fulltext_search.sql`

```sql
-- Añadir columna tsvector para full-text search
ALTER TABLE odoo_modules 
ADD COLUMN searchable_text tsvector;

-- Crear índice GIN para búsqueda full-text
CREATE INDEX idx_modules_fulltext ON odoo_modules USING GIN(searchable_text);

-- Función para actualizar searchable_text
CREATE OR REPLACE FUNCTION update_searchable_text()
RETURNS TRIGGER AS $$
BEGIN
    NEW.searchable_text := 
        setweight(to_tsvector('english', COALESCE(NEW.technical_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.readme, '')), 'D');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para auto-actualizar en INSERT/UPDATE
CREATE TRIGGER trigger_update_searchable_text
    BEFORE INSERT OR UPDATE OF technical_name, name, summary, description, readme
    ON odoo_modules
    FOR EACH ROW
    EXECUTE FUNCTION update_searchable_text();

-- Poblar columna para registros existentes
UPDATE odoo_modules SET searchable_text = 
    setweight(to_tsvector('english', COALESCE(technical_name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(summary, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(description, '')), 'C') ||
    setweight(to_tsvector('english', COALESCE(readme, '')), 'D');
```

### 3.3 Servicio Hybrid Search

**Archivo:** `app/services/hybrid_search_service.py`

```python
"""
Hybrid Search: Combina vector similarity + BM25 full-text usando RRF.
"""
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import numpy as np

class HybridSearchService:
    """Servicio de búsqueda híbrida (vector + BM25)."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def search(
        self,
        query: str,
        query_embedding: List[float],
        version: str,
        dependencies: Optional[List[str]] = None,
        limit: int = 5,
        k: int = 60  # RRF parameter
    ) -> List[Dict]:
        """
        Ejecuta búsqueda híbrida y fusiona resultados con RRF.
        
        Args:
            query: Query de texto del usuario
            query_embedding: Vector embedding de la query
            version: Versión Odoo (e.g., "16.0")
            dependencies: Filtro de dependencias (opcional)
            limit: Número de resultados finales
            k: Parámetro RRF (default 60, común en literatura)
        
        Returns:
            Lista de módulos rankeados por RRF score
        """
        
        # 1. Vector similarity search (top 50)
        vector_results = await self._vector_search(
            query_embedding, version, dependencies, limit=50
        )
        
        # 2. BM25 full-text search (top 50)
        fulltext_results = await self._fulltext_search(
            query, version, dependencies, limit=50
        )
        
        # 3. Reciprocal Rank Fusion (RRF)
        fused_results = self._reciprocal_rank_fusion(
            vector_results, fulltext_results, k=k
        )
        
        # 4. Return top N
        return fused_results[:limit]
    
    async def _vector_search(
        self,
        embedding: List[float],
        version: str,
        dependencies: Optional[List[str]],
        limit: int
    ) -> List[Dict]:
        """Búsqueda por similitud vectorial."""
        
        query = text("""
            SELECT 
                id,
                technical_name,
                name,
                summary,
                version,
                depends,
                github_stars,
                1 - (embedding <=> :embedding::vector) as similarity_score
            FROM odoo_modules
            WHERE version = :version
                AND (:deps::text[] IS NULL OR depends && :deps)
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """)
        
        result = await self.db.execute(query, {
            "embedding": embedding,
            "version": version,
            "deps": dependencies,
            "limit": limit
        })
        
        rows = result.fetchall()
        return [
            {
                "id": row.id,
                "technical_name": row.technical_name,
                "name": row.name,
                "summary": row.summary,
                "version": row.version,
                "depends": row.depends,
                "github_stars": row.github_stars,
                "vector_score": float(row.similarity_score),
                "rank": i + 1
            }
            for i, row in enumerate(rows)
        ]
    
    async def _fulltext_search(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]],
        limit: int
    ) -> List[Dict]:
        """Búsqueda BM25 full-text."""
        
        sql = text("""
            SELECT 
                id,
                technical_name,
                name,
                summary,
                version,
                depends,
                github_stars,
                ts_rank_cd(searchable_text, query) as bm25_score
            FROM odoo_modules, 
                 plainto_tsquery('english', :query) query
            WHERE version = :version
                AND (:deps::text[] IS NULL OR depends && :deps)
                AND searchable_text @@ query
            ORDER BY bm25_score DESC
            LIMIT :limit
        """)
        
        result = await self.db.execute(sql, {
            "query": query,
            "version": version,
            "deps": dependencies,
            "limit": limit
        })
        
        rows = result.fetchall()
        return [
            {
                "id": row.id,
                "technical_name": row.technical_name,
                "name": row.name,
                "summary": row.summary,
                "version": row.version,
                "depends": row.depends,
                "github_stars": row.github_stars,
                "bm25_score": float(row.bm25_score),
                "rank": i + 1
            }
            for i, row in enumerate(rows)
        ]
    
    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Dict],
        fulltext_results: List[Dict],
        k: int = 60
    ) -> List[Dict]:
        """
        Fusiona resultados usando Reciprocal Rank Fusion (RRF).
        
        Formula: RRF(d) = Σ 1/(k + rank(d))
        
        Referencia: https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf
        """
        
        # Create module_id -> score mapping
        scores = {}
        module_data = {}
        
        # Add vector scores
        for result in vector_results:
            module_id = result['id']
            rank = result['rank']
            scores[module_id] = scores.get(module_id, 0) + 1 / (k + rank)
            module_data[module_id] = result
        
        # Add BM25 scores
        for result in fulltext_results:
            module_id = result['id']
            rank = result['rank']
            scores[module_id] = scores.get(module_id, 0) + 1 / (k + rank)
            
            # Update module_data if not exists
            if module_id not in module_data:
                module_data[module_id] = result
            else:
                # Merge scores
                module_data[module_id]['bm25_score'] = result.get('bm25_score', 0)
        
        # Sort by RRF score
        sorted_modules = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Build final results
        results = []
        for module_id, rrf_score in sorted_modules:
            data = module_data[module_id]
            data['rrf_score'] = rrf_score
            results.append(data)
        
        return results
```

### 3.4 Integración en Search Service

**Archivo:** `app/services/search_service.py` (modificado)

```python
from app.services.hybrid_search_service import HybridSearchService
from app.services.embedding_service import EmbeddingService

class SearchService:
    """Servicio principal de búsqueda."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.hybrid_search = HybridSearchService(db)
    
    async def search_modules(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]] = None,
        limit: int = 5,
        search_mode: str = "hybrid"  # "hybrid", "vector", "fulltext"
    ) -> List[ModuleResult]:
        """
        Busca módulos usando el modo especificado.
        
        Args:
            search_mode: "hybrid" (default), "vector", "fulltext"
        """
        
        # Generate embedding
        query_embedding = await self.embedding_service.get_embedding(query)
        
        if search_mode == "hybrid":
            results = await self.hybrid_search.search(
                query=query,
                query_embedding=query_embedding,
                version=version,
                dependencies=dependencies,
                limit=limit
            )
        elif search_mode == "vector":
            results = await self.hybrid_search._vector_search(
                embedding=query_embedding,
                version=version,
                dependencies=dependencies,
                limit=limit
            )
        elif search_mode == "fulltext":
            results = await self.hybrid_search._fulltext_search(
                query=query,
                version=version,
                dependencies=dependencies,
                limit=limit
            )
        else:
            raise ValueError(f"Invalid search_mode: {search_mode}")
        
        return [ModuleResult(**r) for r in results]
```

### 3.5 Entregable Fase 2
- ✅ Migration SQL aplicada (fulltext search)
- ✅ `HybridSearchService` implementado
- ✅ Integración en `SearchService` con flag `search_mode`
- ✅ Re-ejecutar benchmark con `search_mode="hybrid"`
- ✅ Comparar métricas: baseline vs hybrid

**Criterio de éxito:**
- Precision@3 mejora >15-20% sobre baseline
- Queries con términos exactos mejoran significativamente

---

## 4. FASE 3: ENRIQUECIMIENTO DE DATOS <a name="fase-3"></a>

### 4.1 Objetivo
Añadir metadata estructurada a los módulos para mejorar contexto y búsqueda: tags funcionales, keywords, descripciones IA para módulos sin README.

### 4.2 Cambios en Base de Datos

**Archivo:** `migrations/003_add_enrichment_fields.sql`

```sql
-- Añadir nuevos campos de enriquecimiento
ALTER TABLE odoo_modules
ADD COLUMN functional_tags TEXT[] DEFAULT '{}',
ADD COLUMN keywords TEXT[] DEFAULT '{}',
ADD COLUMN ai_description TEXT,
ADD COLUMN use_cases TEXT[] DEFAULT '{}',
ADD COLUMN category TEXT,
ADD COLUMN subcategory TEXT;

-- Índice para búsqueda por tags
CREATE INDEX idx_modules_functional_tags ON odoo_modules USING GIN(functional_tags);
CREATE INDEX idx_modules_keywords ON odoo_modules USING GIN(keywords);
CREATE INDEX idx_modules_category ON odoo_modules(category);

-- Tabla de mapping dependency → functional area
CREATE TABLE dependency_to_functional_area (
    dependency TEXT PRIMARY KEY,
    functional_area TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT
);

-- Poblar mappings comunes
INSERT INTO dependency_to_functional_area (dependency, functional_area, category, subcategory) VALUES
    ('sale', 'Sales & CRM', 'sales', 'core'),
    ('sale_management', 'Sales & CRM', 'sales', 'management'),
    ('crm', 'Sales & CRM', 'sales', 'crm'),
    ('purchase', 'Purchases', 'purchase', 'core'),
    ('stock', 'Inventory', 'inventory', 'core'),
    ('mrp', 'Manufacturing', 'manufacturing', 'core'),
    ('account', 'Accounting & Finance', 'accounting', 'core'),
    ('website', 'Website & eCommerce', 'website', 'core'),
    ('website_sale', 'Website & eCommerce', 'website', 'ecommerce'),
    ('hr', 'Human Resources', 'hr', 'core'),
    ('project', 'Project Management', 'project', 'core'),
    ('helpdesk', 'Helpdesk & Support', 'services', 'helpdesk'),
    ('portal', 'Customer Portal', 'portal', 'core'),
    ('mail', 'Messaging & Communication', 'communication', 'mail'),
    ('l10n_', 'Localization', 'localization', NULL);  -- Prefix match

-- Tabla de sinónimos y keywords Odoo-específicos
CREATE TABLE odoo_terminology (
    term TEXT PRIMARY KEY,
    synonyms TEXT[] NOT NULL,
    related_dependencies TEXT[],
    category TEXT
);

INSERT INTO odoo_terminology (term, synonyms, related_dependencies, category) VALUES
    ('B2B', ARRAY['business to business', 'empresa a empresa', 'portal empresas'], ARRAY['portal', 'sale'], 'sales'),
    ('B2C', ARRAY['business to consumer', 'empresa a consumidor', 'retail', 'minorista'], ARRAY['website_sale'], 'sales'),
    ('factura electrónica', ARRAY['e-invoice', 'electronic invoice', 'facturae', 'AEAT'], ARRAY['account', 'l10n_es'], 'localization'),
    ('trazabilidad', ARRAY['traceability', 'lotes', 'series', 'tracking'], ARRAY['stock', 'product_expiry'], 'inventory'),
    ('descuentos', ARRAY['discounts', 'promociones', 'offers', 'rebajas'], ARRAY['sale', 'product_pricelist'], 'sales');
```

### 4.3 Script de Enriquecimiento Automático

**Archivo:** `scripts/enrich_module_data.py`

```python
"""
Enriquece módulos con tags funcionales, keywords y descripciones IA.
"""
import asyncio
import json
from typing import List, Dict, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.embedding_service import EmbeddingService
import anthropic

class ModuleEnrichmentService:
    """Servicio de enriquecimiento de datos de módulos."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.anthropic = anthropic.Anthropic()  # Usar Claude para generar descripciones
    
    async def enrich_all_modules(self):
        """Pipeline completo de enriquecimiento."""
        
        print("🚀 Iniciando enriquecimiento de módulos...")
        
        # 1. Extract functional tags from dependencies
        print("\n[1/5] Extrayendo tags funcionales de dependencies...")
        await self.extract_functional_tags()
        
        # 2. Extract keywords from manifest
        print("\n[2/5] Extrayendo keywords de manifests...")
        await self.extract_keywords_from_manifest()
        
        # 3. Generate AI descriptions for modules without README
        print("\n[3/5] Generando descripciones IA para módulos sin README...")
        await self.generate_ai_descriptions()
        
        # 4. Extract use cases from README
        print("\n[4/5] Extrayendo casos de uso de READMEs...")
        await self.extract_use_cases()
        
        # 5. Regenerate embeddings with enriched data
        print("\n[5/5] Regenerando embeddings con datos enriquecidos...")
        await self.regenerate_embeddings()
        
        print("\n✅ Enriquecimiento completado!")
    
    async def extract_functional_tags(self):
        """Extrae tags funcionales basados en dependencies."""
        
        query = text("""
            UPDATE odoo_modules m
            SET functional_tags = ARRAY(
                SELECT DISTINCT d.functional_area
                FROM unnest(m.depends) dep
                JOIN dependency_to_functional_area d ON (
                    d.dependency = dep OR dep LIKE d.dependency || '%'
                )
            ),
            category = (
                SELECT d.category
                FROM unnest(m.depends) dep
                JOIN dependency_to_functional_area d ON d.dependency = dep
                LIMIT 1
            )
        """)
        
        await self.db.execute(query)
        await self.db.commit()
        
        # Log statistics
        result = await self.db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN array_length(functional_tags, 1) > 0 THEN 1 END) as with_tags
            FROM odoo_modules
        """))
        row = result.fetchone()
        print(f"  ✓ {row.with_tags}/{row.total} módulos tienen functional_tags")
    
    async def extract_keywords_from_manifest(self):
        """Extrae keywords de technical_name, name, summary."""
        
        query = text("""
            UPDATE odoo_modules
            SET keywords = ARRAY(
                SELECT DISTINCT unnest(
                    string_to_array(
                        regexp_replace(
                            lower(
                                COALESCE(technical_name, '') || ' ' || 
                                COALESCE(name, '') || ' ' || 
                                COALESCE(summary, '')
                            ),
                            '[^a-z0-9_]', ' ', 'g'
                        ),
                        ' '
                    )
                )
                WHERE length(unnest) > 3  -- Ignore short words
            )
        """)
        
        await self.db.execute(query)
        await self.db.commit()
        
        print(f"  ✓ Keywords extraídos de manifests")
    
    async def generate_ai_descriptions(self, batch_size: int = 10):
        """
        Genera descripciones con IA para módulos sin README.
        Usa Claude Haiku para eficiencia.
        """
        
        # Get modules without README
        query = text("""
            SELECT id, technical_name, name, summary, depends, author, category
            FROM odoo_modules
            WHERE (readme IS NULL OR readme = '')
                AND ai_description IS NULL
            LIMIT :batch_size
        """)
        
        while True:
            result = await self.db.execute(query, {"batch_size": batch_size})
            modules = result.fetchall()
            
            if not modules:
                break
            
            print(f"  Procesando batch de {len(modules)} módulos...")
            
            for module in modules:
                try:
                    description = await self._generate_description_with_claude(module)
                    
                    # Update module
                    update_query = text("""
                        UPDATE odoo_modules
                        SET ai_description = :description
                        WHERE id = :module_id
                    """)
                    
                    await self.db.execute(update_query, {
                        "description": description,
                        "module_id": module.id
                    })
                    
                    await self.db.commit()
                    
                except Exception as e:
                    print(f"  ⚠️  Error procesando {module.technical_name}: {e}")
                    continue
        
        # Log statistics
        result = await self.db.execute(text("""
            SELECT COUNT(*) as total
            FROM odoo_modules
            WHERE ai_description IS NOT NULL
        """))
        count = result.scalar()
        print(f"  ✓ {count} módulos con ai_description generada")
    
    async def _generate_description_with_claude(self, module) -> str:
        """Genera descripción usando Claude Haiku."""
        
        prompt = f"""Given this Odoo module information, generate a concise, technical description (2-3 sentences) of what the module does and its main features:

Technical Name: {module.technical_name}
Name: {module.name}
Summary: {module.summary}
Dependencies: {', '.join(module.depends or [])}
Author: {module.author}
Category: {module.category}

Focus on:
1. Primary functionality
2. Key features
3. Use cases
4. Integration points

Description:"""

        response = self.anthropic.messages.create(
            model="claude-haiku-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    async def extract_use_cases(self):
        """
        Extrae casos de uso del README usando patterns comunes.
        """
        
        query = text("""
            UPDATE odoo_modules
            SET use_cases = ARRAY(
                SELECT DISTINCT trim(both from match[1])
                FROM (
                    SELECT regexp_matches(
                        readme,
                        '(?:Use case|Usage|Example|Scenario):\s*([^
]+)',
                        'gi'
                    ) as match
                ) subq
                WHERE match[1] IS NOT NULL
            )
            WHERE readme IS NOT NULL
                AND readme != ''
        """)
        
        await self.db.execute(query)
        await self.db.commit()
        
        print(f"  ✓ Casos de uso extraídos de READMEs")
    
    async def regenerate_embeddings(self, batch_size: int = 50):
        """
        Regenera embeddings usando datos enriquecidos.
        Combina: technical_name + name + summary + ai_description + functional_tags
        """
        
        # Get all modules
        query = text("""
            SELECT id, technical_name, name, summary, 
                   readme, ai_description, functional_tags, keywords
            FROM odoo_modules
            ORDER BY id
        """)
        
        result = await self.db.execute(query)
        modules = result.fetchall()
        
        total = len(modules)
        print(f"  Total módulos a procesar: {total}")
        
        for i in range(0, total, batch_size):
            batch = modules[i:i+batch_size]
            print(f"  Procesando batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}...")
            
            # Prepare enriched texts
            enriched_texts = []
            for module in batch:
                # Build enriched text
                parts = [
                    f"Module: {module.technical_name}",
                    f"Name: {module.name}" if module.name else "",
                    f"Summary: {module.summary}" if module.summary else "",
                ]
                
                # Add AI description or README
                if module.ai_description:
                    parts.append(f"Description: {module.ai_description}")
                elif module.readme:
                    # Use first 500 chars of README
                    parts.append(f"README: {module.readme[:500]}")
                
                # Add functional context
                if module.functional_tags:
                    parts.append(f"Functional Areas: {', '.join(module.functional_tags)}")
                
                if module.keywords:
                    # Top 10 keywords
                    top_keywords = module.keywords[:10]
                    parts.append(f"Keywords: {', '.join(top_keywords)}")
                
                enriched_text = "\n".join(p for p in parts if p)
                enriched_texts.append(enriched_text)
            
            # Generate embeddings
            embeddings = await self.embedding_service.get_embeddings_batch(enriched_texts)
            
            # Update database
            for module, embedding in zip(batch, embeddings):
                update_query = text("""
                    UPDATE odoo_modules
                    SET embedding = :embedding::vector,
                        updated_at = NOW()
                    WHERE id = :module_id
                """)
                
                await self.db.execute(update_query, {
                    "embedding": embedding,
                    "module_id": module.id
                })
            
            await self.db.commit()
        
        print(f"  ✓ Embeddings regenerados para {total} módulos")

async def main():
    """Entry point del script."""
    async with get_db() as db:
        service = ModuleEnrichmentService(db)
        await service.enrich_all_modules()

if __name__ == '__main__':
    asyncio.run(main())
```

### 4.4 Entregable Fase 3
- ✅ Migration SQL aplicada (nuevos campos)
- ✅ Tabla `dependency_to_functional_area` poblada
- ✅ Tabla `odoo_terminology` con sinónimos
- ✅ Script `enrich_module_data.py` ejecutado
- ✅ Re-ejecutar benchmark después de enriquecimiento
- ✅ Comparar métricas: hybrid vs hybrid+enriched

**Criterio de éxito:**
- 90%+ módulos tienen `functional_tags`
- 100% módulos tienen `ai_description` o `readme`
- Precision@3 mejora >10% adicional

---

## 5. FASE 4: TWO-STAGE RETRIEVAL CON RERANKING <a name="fase-4"></a>

### 5.1 Objetivo
Implementar reranking inteligente: recuperar 50 candidatos con hybrid search, luego usar LLM para reordenar top 5 más relevantes.

### 5.2 Servicio de Reranking

**Archivo:** `app/services/reranking_service.py`

```python
"""
Reranking service: Usa LLM para reordenar resultados de búsqueda.
"""
from typing import List, Dict
import anthropic
import json

class RerankingService:
    """Servicio de reranking con LLM."""
    
    def __init__(self):
        self.anthropic = anthropic.Anthropic()
    
    async def rerank(
        self,
        query: str,
        candidates: List[Dict],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Reordena candidatos usando Claude para determinar relevancia.
        
        Args:
            query: Query original del usuario
            candidates: Lista de candidatos (hasta 50)
            top_k: Número de resultados finales (default 5)
        
        Returns:
            Top K candidatos reordenados por relevancia
        """
        
        if not candidates:
            return []
        
        # Prepare candidates for LLM
        candidates_text = self._format_candidates_for_llm(candidates)
        
        # Create prompt
        prompt = f"""You are an Odoo module search expert. Given a user query and a list of candidate modules, rank them by relevance.

User Query: "{query}"

Candidate Modules:
{candidates_text}

Instructions:
1. Analyze each module's relevance to the query
2. Consider: exact matches, semantic relevance, functional fit, popularity
3. Return ONLY a JSON array of module IDs in order of relevance (most relevant first)
4. Return exactly {top_k} module IDs

Output format (JSON only, no explanation):
[module_id_1, module_id_2, module_id_3, ...]"""

        # Call Claude
        response = self.anthropic.messages.create(
            model="claude-haiku-4-20250514",  # Fast and cost-effective
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        try:
            ranked_ids = json.loads(response.content[0].text.strip())
            
            # Build result maintaining order
            id_to_candidate = {c['id']: c for c in candidates}
            reranked = []
            
            for module_id in ranked_ids[:top_k]:
                if module_id in id_to_candidate:
                    candidate = id_to_candidate[module_id]
                    candidate['rerank_position'] = len(reranked) + 1
                    reranked.append(candidate)
            
            # Fill remaining slots if needed
            for candidate in candidates:
                if len(reranked) >= top_k:
                    break
                if candidate['id'] not in [r['id'] for r in reranked]:
                    candidate['rerank_position'] = len(reranked) + 1
                    reranked.append(candidate)
            
            return reranked[:top_k]
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parsing reranking response: {e}")
            # Fallback: return original order
            return candidates[:top_k]
    
    def _format_candidates_for_llm(self, candidates: List[Dict]) -> str:
        """Formatea candidatos para el prompt del LLM."""
        
        formatted = []
        for i, c in enumerate(candidates, 1):
            # Build functional context
            context_parts = []
            if 'functional_tags' in c and c['functional_tags']:
                context_parts.append(f"Areas: {', '.join(c['functional_tags'])}")
            if 'category' in c and c['category']:
                context_parts.append(f"Category: {c['category']}")
            if 'depends' in c and c['depends']:
                # Show first 3 dependencies
                deps = c['depends'][:3]
                context_parts.append(f"Depends: {', '.join(deps)}")
            
            context = " | ".join(context_parts)
            
            formatted.append(f"""
{i}. ID: {c['id']}
   Name: {c['technical_name']}
   Title: {c.get('name', 'N/A')}
   Summary: {c.get('summary', 'N/A')[:150]}...
   {context}
   Stars: {c.get('github_stars', 0)} | RRF Score: {c.get('rrf_score', 0):.3f}
""")
        
        return "\n".join(formatted)
```

### 5.3 Integración en Search Service

**Archivo:** `app/services/search_service.py` (modificado)

```python
from app.services.reranking_service import RerankingService

class SearchService:
    """Servicio principal de búsqueda."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.hybrid_search = HybridSearchService(db)
        self.reranking_service = RerankingService()
    
    async def search_modules(
        self,
        query: str,
        version: str,
        dependencies: Optional[List[str]] = None,
        limit: int = 5,
        use_reranking: bool = True  # NEW: Enable reranking
    ) -> List[ModuleResult]:
        """
        Busca módulos con two-stage retrieval (hybrid + reranking).
        """
        
        # Generate embedding
        query_embedding = await self.embedding_service.get_embedding(query)
        
        # Stage 1: Hybrid search for top 50 candidates
        candidates = await self.hybrid_search.search(
            query=query,
            query_embedding=query_embedding,
            version=version,
            dependencies=dependencies,
            limit=50 if use_reranking else limit
        )
        
        # Stage 2: LLM reranking (optional)
        if use_reranking and len(candidates) > limit:
            results = await self.reranking_service.rerank(
                query=query,
                candidates=candidates,
                top_k=limit
            )
        else:
            results = candidates[:limit]
        
        return [ModuleResult(**r) for r in results]
```

### 5.4 Entregable Fase 4
- ✅ `RerankingService` implementado
- ✅ Integración en `SearchService` con flag `use_reranking`
- ✅ Re-ejecutar benchmark con reranking activado
- ✅ Comparar métricas: enriched vs enriched+reranking
- ✅ Analizar costo/latencia del reranking

**Criterio de éxito:**
- Precision@3 mejora >5-10% adicional
- Latencia <2s para búsquedas con reranking
- Costo Claude Haiku < $0.01 por búsqueda

---

## 6. FASE 5: TESTING Y MÉTRICAS <a name="fase-5"></a>

### 6.1 Test Suite Completo

**Archivo:** `tests/test_search_improvements.py`

```python
"""
Suite de tests para validar mejoras de búsqueda.
"""
import pytest
from app.services.search_service import SearchService
from tests.benchmark_queries import load_benchmark_queries

class TestSearchImprovements:
    """Tests de regresión y mejora de búsqueda."""
    
    @pytest.fixture
    def search_service(self, db_session):
        return SearchService(db_session)
    
    @pytest.fixture
    def benchmark_queries(self):
        return load_benchmark_queries()
    
    @pytest.mark.asyncio
    async def test_hybrid_search_improves_over_baseline(
        self, search_service, benchmark_queries
    ):
        """Verifica que hybrid search mejora sobre baseline."""
        
        baseline_precision = 0.35  # From phase 1
        
        total_queries = len(benchmark_queries)
        correct_at_3 = 0
        
        for query_data in benchmark_queries:
            results = await search_service.search_modules(
                query=query_data['query'],
                version=query_data['version'],
                limit=10,
                use_reranking=False  # Only hybrid
            )
            
            # Check if any expected module is in top 3
            returned = [r.technical_name for r in results[:3]]
            expected = query_data['expected_modules']
            
            if any(exp in returned for exp in expected):
                correct_at_3 += 1
        
        hybrid_precision = correct_at_3 / total_queries
        
        # Assert improvement
        assert hybrid_precision > baseline_precision + 0.15, \
            f"Hybrid search precision ({hybrid_precision:.2%}) should improve " \
            f"at least 15% over baseline ({baseline_precision:.2%})"
    
    @pytest.mark.asyncio
    async def test_reranking_improves_over_hybrid(
        self, search_service, benchmark_queries
    ):
        """Verifica que reranking mejora sobre hybrid alone."""
        
        total_queries = len(benchmark_queries)
        
        # Test without reranking
        hybrid_correct = 0
        for query_data in benchmark_queries:
            results = await search_service.search_modules(
                query=query_data['query'],
                version=query_data['version'],
                limit=10,
                use_reranking=False
            )
            returned = [r.technical_name for r in results[:3]]
            if any(exp in returned for exp in query_data['expected_modules']):
                hybrid_correct += 1
        
        # Test with reranking
        reranked_correct = 0
        for query_data in benchmark_queries:
            results = await search_service.search_modules(
                query=query_data['query'],
                version=query_data['version'],
                limit=10,
                use_reranking=True
            )
            returned = [r.technical_name for r in results[:3]]
            if any(exp in returned for exp in query_data['expected_modules']):
                reranked_correct += 1
        
        hybrid_precision = hybrid_correct / total_queries
        reranked_precision = reranked_correct / total_queries
        
        # Assert improvement
        assert reranked_precision >= hybrid_precision, \
            f"Reranking ({reranked_precision:.2%}) should not regress " \
            f"from hybrid ({hybrid_precision:.2%})"
    
    @pytest.mark.asyncio
    async def test_functional_tags_populated(self, db_session):
        """Verifica que los módulos tienen functional tags."""
        
        result = await db_session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN array_length(functional_tags, 1) > 0 
                      THEN 1 END) as with_tags
            FROM odoo_modules
        """))
        
        row = result.fetchone()
        coverage = row.with_tags / row.total
        
        assert coverage > 0.85, \
            f"Functional tags coverage ({coverage:.1%}) should be >85%"
    
    @pytest.mark.asyncio
    async def test_all_modules_have_description(self, db_session):
        """Verifica que todos los módulos tienen descripción."""
        
        result = await db_session.execute(text("""
            SELECT COUNT(*) as total
            FROM odoo_modules
            WHERE (readme IS NULL OR readme = '')
              AND (ai_description IS NULL OR ai_description = '')
        """))
        
        missing = result.scalar()
        
        assert missing == 0, \
            f"{missing} modules are missing both README and AI description"
```

### 6.2 Métricas y Dashboards

**Archivo:** `scripts/generate_comparison_report.py`

```python
"""
Genera reporte comparativo de todas las fases de mejora.
"""
import json
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

def generate_comparison_report():
    """Genera reporte visual comparando todas las fases."""
    
    # Load all benchmark results
    results_dir = Path('tests/results')
    
    baseline = json.load(open(results_dir / 'baseline_YYYYMMDD.json'))
    hybrid = json.load(open(results_dir / 'hybrid_YYYYMMDD.json'))
    enriched = json.load(open(results_dir / 'enriched_YYYYMMDD.json'))
    reranked = json.load(open(results_dir / 'reranked_YYYYMMDD.json'))
    
    # Extract metrics
    phases = ['Baseline', 'Hybrid', 'Enriched', 'Reranked']
    precision_3 = [
        baseline['aggregate_metrics']['precision@3'],
        hybrid['aggregate_metrics']['precision@3'],
        enriched['aggregate_metrics']['precision@3'],
        reranked['aggregate_metrics']['precision@3']
    ]
    precision_5 = [
        baseline['aggregate_metrics']['precision@5'],
        hybrid['aggregate_metrics']['precision@5'],
        enriched['aggregate_metrics']['precision@5'],
        reranked['aggregate_metrics']['precision@5']
    ]
    mrr = [
        baseline['aggregate_metrics']['mrr'],
        hybrid['aggregate_metrics']['mrr'],
        enriched['aggregate_metrics']['mrr'],
        reranked['aggregate_metrics']['mrr']
    ]
    
    # Create comparison chart
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Precision@3
    axes[0].bar(phases, precision_3, color=['red', 'orange', 'yellow', 'green'])
    axes[0].set_ylabel('Precision@3')
    axes[0].set_title('Precision@3 Improvement')
    axes[0].set_ylim([0, 1])
    for i, v in enumerate(precision_3):
        axes[0].text(i, v + 0.02, f'{v:.1%}', ha='center')
    
    # Precision@5
    axes[1].bar(phases, precision_5, color=['red', 'orange', 'yellow', 'green'])
    axes[1].set_ylabel('Precision@5')
    axes[1].set_title('Precision@5 Improvement')
    axes[1].set_ylim([0, 1])
    for i, v in enumerate(precision_5):
        axes[1].text(i, v + 0.02, f'{v:.1%}', ha='center')
    
    # MRR
    axes[2].bar(phases, mrr, color=['red', 'orange', 'yellow', 'green'])
    axes[2].set_ylabel('Mean Reciprocal Rank')
    axes[2].set_title('MRR Improvement')
    axes[2].set_ylim([0, 1])
    for i, v in enumerate(mrr):
        axes[2].text(i, v + 0.02, f'{v:.3f}', ha='center')
    
    plt.tight_layout()
    plt.savefig('tests/results/comparison_chart.png', dpi=300)
    print("✅ Comparison chart saved to tests/results/comparison_chart.png")
    
    # Generate markdown report
    report = f"""# AI-OdooFinder Search Improvements - Final Report

## Executive Summary

| Phase | Precision@3 | Precision@5 | MRR | Improvement |
|-------|-------------|-------------|-----|-------------|
| Baseline | {precision_3[0]:.1%} | {precision_5[0]:.1%} | {mrr[0]:.3f} | - |
| Hybrid Search | {precision_3[1]:.1%} | {precision_5[1]:.1%} | {mrr[1]:.3f} | +{(precision_3[1]-precision_3[0]):.1%} |
| Data Enrichment | {precision_3[2]:.1%} | {precision_5[2]:.1%} | {mrr[2]:.3f} | +{(precision_3[2]-precision_3[0]):.1%} |
| LLM Reranking | {precision_3[3]:.1%} | {precision_5[3]:.1%} | {mrr[3]:.3f} | +{(precision_3[3]-precision_3[0]):.1%} |

**Total Improvement:** {(precision_3[3]-precision_3[0]):.1%} in Precision@3

## Key Findings

1. **Hybrid Search**: Combining vector similarity with BM25 full-text improved precision by {(precision_3[1]-precision_3[0]):.1%}
2. **Data Enrichment**: Adding functional tags, AI descriptions, and keywords boosted precision by {(precision_3[2]-precision_3[1]):.1%}
3. **LLM Reranking**: Final reranking with Claude Haiku added {(precision_3[3]-precision_3[2]):.1%} improvement

## Next Steps

- Monitor production metrics
- A/B test with real users
- Fine-tune reranking prompts
- Consider additional enrichment sources

![Comparison Chart](comparison_chart.png)
"""
    
    with open('tests/results/FINAL_REPORT.md', 'w') as f:
        f.write(report)
    
    print("✅ Final report saved to tests/results/FINAL_REPORT.md")

if __name__ == '__main__':
    generate_comparison_report()
```

### 6.3 Entregable Fase 5
- ✅ Suite de tests implementada
- ✅ Benchmark ejecutado en todas las fases
- ✅ Reporte comparativo generado
- ✅ Gráficas de mejora visualizadas

---

## 7. ROADMAP DE IMPLEMENTACIÓN <a name="roadmap"></a>

### Semana 1: Fundación (Días 1-7)

**Día 1: Setup y Diagnóstico**
```bash
# Tasks
- ✅ Crear tests/benchmark_queries.json (20 queries)
- ✅ Implementar scripts/run_benchmark.py
- ✅ Ejecutar baseline benchmark
- ✅ Documentar patrones de fallo

# Entregables
- tests/results/baseline_YYYYMMDD.json
- Documento con 5 patrones de fallo identificados
```

**Días 2-3: Hybrid Search**
```bash
# Tasks
- ✅ Crear migration 002_add_fulltext_search.sql
- ✅ Aplicar migración a BD
- ✅ Implementar app/services/hybrid_search_service.py
- ✅ Integrar en search_service.py
- ✅ Ejecutar benchmark con hybrid search

# Entregables
- BD con fulltext search configurado
- Hybrid search funcional
- tests/results/hybrid_YYYYMMDD.json
```

**Días 4-6: Data Enrichment**
```bash
# Tasks
- ✅ Crear migration 003_add_enrichment_fields.sql
- ✅ Poblar tablas de mappings
- ✅ Implementar scripts/enrich_module_data.py
- ✅ Ejecutar enriquecimiento (tags, AI descriptions, keywords)
- ✅ Regenerar embeddings
- ✅ Ejecutar benchmark post-enrichment

# Entregables
- 2,508 módulos enriquecidos
- Embeddings actualizados
- tests/results/enriched_YYYYMMDD.json
```

**Día 7: Review y Análisis**
```bash
# Tasks
- ✅ Comparar métricas baseline vs hybrid vs enriched
- ✅ Identificar queries que aún fallan
- ✅ Documentar aprendizajes

# Decisión
- Si mejora >40%: Continuar a Fase 4 (Reranking)
- Si mejora 20-40%: Revisar embedding model
- Si mejora <20%: Re-evaluar approach
```

### Semana 2: Optimización (Días 8-14)

**Días 8-10: LLM Reranking**
```bash
# Tasks
- ✅ Implementar app/services/reranking_service.py
- ✅ Integrar en search_service.py
- ✅ Ejecutar benchmark con reranking
- ✅ Analizar costo/latencia

# Entregables
- Reranking service funcional
- tests/results/reranked_YYYYMMDD.json
- Análisis costo/beneficio
```

**Días 11-12: Testing Completo**
```bash
# Tasks
- ✅ Implementar tests/test_search_improvements.py
- ✅ Ejecutar test suite completo
- ✅ Validar cobertura de functional tags
- ✅ Validar descripciones completas

# Entregables
- Test suite passing
- Coverage reports
```

**Días 13-14: Reportes y Documentación**
```bash
# Tasks
- ✅ Generar reporte comparativo final
- ✅ Crear visualizaciones
- ✅ Documentar aprendizajes
- ✅ Actualizar README del proyecto

# Entregables
- tests/results/FINAL_REPORT.md
- tests/results/comparison_chart.png
- Documentación actualizada
```

### Próximos Pasos (Post Semana 2)

**Fase Opcional: Odoo App Store Integration**
```
SOLO si después de semana 2:
- Precision@3 < 70%
- Identificas gaps claros de cobertura
- Justifica el esfuerzo (1-2 semanas)

Tasks:
- Scraper de apps.odoo.com
- Nueva tabla odoo_store_modules
- Merge de resultados OCA + Store
```

**Monitoring en Producción**
```
- Implementar logging de búsquedas reales
- Tracker user satisfaction (thumbs up/down)
- A/B testing: reranking on/off
- Alertas si precision cae <threshold
```

---

## 📊 MÉTRICAS DE ÉXITO

### Objetivos Mínimos
- ✅ Precision@3: >60% (desde ~35% baseline)
- ✅ Precision@5: >70%
- ✅ MRR: >0.6
- ✅ Latencia: <2s con reranking

### Objetivos Stretch
- 🎯 Precision@3: >70%
- 🎯 Precision@5: >80%
- 🎯 MRR: >0.7
- 🎯 User satisfaction: >80% positive feedback

---

## 🔧 CONFIGURACIÓN Y SETUP

### Variables de Entorno Requeridas

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
OPENROUTER_API_KEY=sk-or-xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# Feature flags
ENABLE_HYBRID_SEARCH=true
ENABLE_RERANKING=true
ENABLE_ENRICHMENT=true

# Tuning parameters
RRF_K=60  # Reciprocal Rank Fusion parameter
RERANKING_MODEL=claude-haiku-4-20250514
EMBEDDING_MODEL=qwen3-embedding-4b
```

### Comandos Útiles

```bash
# Run benchmark
python scripts/run_benchmark.py

# Enrich data
python scripts/enrich_module_data.py

# Generate comparison report
python scripts/generate_comparison_report.py

# Run tests
pytest tests/test_search_improvements.py -v

# Apply migrations
alembic upgrade head
```

---

## 🚨 RIESGOS Y MITIGACIONES

### Riesgo 1: Regeneración de embeddings costosa
**Impacto:** Alto  
**Probabilidad:** Media  
**Mitigación:**
- Batch processing (50 módulos a la vez)
- Cache embeddings antiguos
- Monitorear costos OpenRouter

### Riesgo 2: Reranking con Claude aumenta latencia
**Impacto:** Medio  
**Probabilidad:** Alta  
**Mitigación:**
- Usar Claude Haiku (más rápido)
- Cache de resultados frecuentes
- Timeout de 5s con fallback

### Riesgo 3: Functional tags incorrectos
**Impacto:** Medio  
**Probabilidad:** Baja  
**Mitigación:**
- Review manual de mappings críticos
- Tests de cobertura
- User feedback loop

### Riesgo 4: AI descriptions de baja calidad
**Impacto:** Medio  
**Probabilidad:** Media  
**Mitigación:**
- Prompt engineering cuidadoso
- Sample review (20 módulos)
- Fallback a summary original

---

## 📚 REFERENCIAS TÉCNICAS

### Papers y Recursos
1. **Reciprocal Rank Fusion (RRF)**
   - Paper: Cormack et al., SIGIR 2009
   - URL: https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf

2. **Hybrid Search Best Practices**
   - Pinecone Guide: https://www.pinecone.io/learn/hybrid-search/
   - Weaviate Blog: https://weaviate.io/blog/hybrid-search-explained

3. **LLM Reranking**
   - Cohere Rerank: https://txt.cohere.com/rerank/
   - BGE Reranker: https://github.com/FlagOpen/FlagEmbedding

### Herramientas
- PostgreSQL 17 + pgVector
- FastAPI + SQLAlchemy 2.0
- OpenRouter (embeddings)
- Anthropic Claude (reranking + descriptions)

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Pre-requisitos
- [ ] PostgreSQL 17 con pgVector instalado
- [ ] Python 3.14 environment activo
- [ ] OpenRouter API key configurada
- [ ] Anthropic API key configurada
- [ ] Backup de BD actual

### Fase 1: Diagnóstico
- [ ] benchmark_queries.json creado (20 queries)
- [ ] run_benchmark.py implementado
- [ ] Baseline ejecutado y documentado
- [ ] Patrones de fallo identificados

### Fase 2: Hybrid Search
- [ ] Migration 002 aplicada
- [ ] Fulltext search funcionando
- [ ] HybridSearchService implementado
- [ ] Integración en SearchService
- [ ] Benchmark hybrid ejecutado

### Fase 3: Enrichment
- [ ] Migration 003 aplicada
- [ ] Mappings poblados (dependencies, terminology)
- [ ] enrich_module_data.py ejecutado
- [ ] Functional tags >85% cobertura
- [ ] AI descriptions 100% cobertura
- [ ] Embeddings regenerados
- [ ] Benchmark enriched ejecutado

### Fase 4: Reranking
- [ ] RerankingService implementado
- [ ] Integración en SearchService
- [ ] Benchmark reranked ejecutado
- [ ] Análisis costo/latencia completado

### Fase 5: Testing
- [ ] test_search_improvements.py implementado
- [ ] Test suite passing
- [ ] Reporte comparativo generado
- [ ] Gráficas de mejora creadas
- [ ] Documentación actualizada

### Deploy
- [ ] MCP tool actualizado con nuevos features
- [ ] Feature flags configurados
- [ ] Monitoring configurado
- [ ] Alertas configuradas
- [ ] User feedback loop implementado

---

## 🎯 CONCLUSIÓN

Este plan prioriza **mejoras incrementales y medibles** con foco en:

1. **Datos de calidad** (Fase 3: Enrichment) como fundación
2. **Hybrid search** (Fase 2) para capturar exactas + semánticas
3. **Reranking inteligente** (Fase 4) para precisión final

Cada fase es **independiente y testeable**, permitiendo validar ROI antes de continuar.

**Estimated Total Time:** 10-14 días  
**Expected Improvement:** Precision@3 de ~35% → >60% (>70% objetivo)  
**Risk Level:** Medio (con mitigaciones claras)

---

**Documento creado:** 22 Noviembre 2025  
**Versión:** 1.0  
**Autor:** Claude (Sonnet 4.5)  
**Para:** AI-OdooFinder Development Team

¡Adelante con la implementación! 🚀
