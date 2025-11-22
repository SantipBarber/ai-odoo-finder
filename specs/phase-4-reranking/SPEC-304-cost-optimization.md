# SPEC-304: Cost Optimization

**ID:** SPEC-304
**Componente:** Cost Control & Caching
**Prioridad:** Media
**Estimación:** 1 hora
**Dependencias:** SPEC-301, SPEC-303

---

## 📋 Descripción

Estrategias de optimización de costos para reranking LLM: caching, budget limits, y monitoring.

---

## 💰 Cost Analysis

### Per-Search Cost Breakdown

```
Claude Haiku Pricing:
  Input:  $0.25 per 1M tokens
  Output: $1.25 per 1M tokens

Per Search:
  Query: ~50 tokens
  50 modules context: ~2,500 tokens
  LLM response: ~200 tokens

  Total input:  2,550 tokens × $0.25/1M = $0.00064
  Total output:   200 tokens × $1.25/1M = $0.00025
  Total cost per search: ~$0.0009

Monthly projections:
  1,000 searches/day  = $27/month
  5,000 searches/day  = $135/month
  10,000 searches/day = $270/month
```

---

## 🎯 Optimization Strategies

### 1. Caching (High Impact)

```python
# app/services/reranking_cache.py

from functools import lru_cache
import hashlib
import json

class RerankingCache:
    """Cache reranking results."""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.ttl = 3600  # 1 hour

    def _cache_key(self, query: str, module_ids: List[int], version: str) -> str:
        """Generate cache key."""

        # Sort module_ids for consistency
        sorted_ids = sorted(module_ids)

        key_data = f"{query}|{version}|{','.join(map(str, sorted_ids))}"
        return f"rerank:{hashlib.md5(key_data.encode()).hexdigest()}"

    async def get(self, query: str, module_ids: List[int], version: str) -> Optional[List]:
        """Get cached reranking result."""

        key = self._cache_key(query, module_ids, version)

        if self.redis:
            cached = await self.redis.get(key)
            if cached:
                return json.loads(cached)

        return None

    async def set(
        self,
        query: str,
        module_ids: List[int],
        version: str,
        results: List
    ):
        """Cache reranking result."""

        key = self._cache_key(query, module_ids, version)

        if self.redis:
            await self.redis.setex(
                key,
                self.ttl,
                json.dumps([r.to_dict() for r in results])
            )


# Usage in RerankingService
class RerankingService:

    def __init__(self, api_key: str, cache: RerankingCache = None):
        self.client = Anthropic(api_key=api_key)
        self.cache = cache or RerankingCache()

    async def rerank(self, query, candidates, version, limit):
        # Check cache
        module_ids = [c['id'] for c in candidates]
        cached = await self.cache.get(query, module_ids, version)

        if cached:
            logger.info("Cache hit for reranking")
            return cached[:limit]

        # Not cached: call LLM
        results = await self._rerank_with_llm(query, candidates, version, limit)

        # Save to cache
        await self.cache.set(query, module_ids, version, results)

        return results
```

**Impact:** ~70% cache hit rate → $8/month instead of $27/month

---

### 2. Reduce Candidates (Medium Impact)

```python
# Option 1: Top 50 (baseline)
candidate_limit = 50
cost_per_search = $0.0009

# Option 2: Top 30 (optimized)
candidate_limit = 30
cost_per_search = $0.0006  # 33% savings

# Trade-off analysis needed
```

---

### 3. Smart Reranking (Medium Impact)

```python
def should_rerank(query: str, hybrid_scores: List[float]) -> bool:
    """
    Decide if reranking is worth it.

    Skip reranking if:
    - Query is simple (1-2 words)
    - Hybrid top result has very high score (>0.95)
    - All hybrid scores are very similar (low variance)
    """

    # Simple query
    if len(query.split()) <= 2:
        return False

    # Very confident hybrid result
    if hybrid_scores[0] > 0.95:
        return False

    # Low score variance (all similar)
    if max(hybrid_scores) - min(hybrid_scores) < 0.1:
        return False

    return True
```

**Impact:** Skip ~20% of rerankings → 20% cost savings

---

### 4. Budget Limits (Safety)

```python
# app/services/budget_monitor.py

class BudgetMonitor:
    """Monitor and enforce budget limits."""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.daily_limit_usd = 5.0

    async def can_rerank(self) -> bool:
        """Check if under budget."""

        today = datetime.now().strftime('%Y-%m-%d')
        key = f"rerank:budget:{today}"

        current_cost = float(await self.redis.get(key) or 0)

        return current_cost < self.daily_limit_usd

    async def record_cost(self, cost_usd: float):
        """Record cost for today."""

        today = datetime.now().strftime('%Y-%m-%d')
        key = f"rerank:budget:{today}"

        await self.redis.incrbyfloat(key, cost_usd)
        await self.redis.expire(key, 86400)  # 24 hours
```

---

## 📊 Cost Monitoring

### Metrics to Track

```python
# app/utils/cost_tracker.py

class CostTracker:
    """Track reranking costs."""

    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'cached_requests': 0,
            'llm_requests': 0,
            'total_cost_usd': 0.0,
            'daily_cost': {}
        }

    def record_request(
        self,
        cache_hit: bool,
        cost_usd: float = 0.0
    ):
        """Record a reranking request."""

        self.metrics['total_requests'] += 1

        if cache_hit:
            self.metrics['cached_requests'] += 1
        else:
            self.metrics['llm_requests'] += 1
            self.metrics['total_cost_usd'] += cost_usd

            # Daily tracking
            today = datetime.now().strftime('%Y-%m-%d')
            self.metrics['daily_cost'][today] = \
                self.metrics['daily_cost'].get(today, 0) + cost_usd

    def get_stats(self) -> Dict:
        """Get cost statistics."""

        total = self.metrics['total_requests']
        cache_rate = self.metrics['cached_requests'] / total if total > 0 else 0

        return {
            'total_requests': total,
            'cache_hit_rate': round(cache_rate, 2),
            'llm_requests': self.metrics['llm_requests'],
            'total_cost_usd': round(self.metrics['total_cost_usd'], 4),
            'avg_cost_per_search': round(
                self.metrics['total_cost_usd'] / max(total, 1), 6
            )
        }
```

### Dashboard Metrics

```
Reranking Dashboard (Daily):
  Total searches:        1,234
  Reranking triggered:     925 (75%)
  Cache hits:              648 (70%)
  LLM calls:               277 (30%)
  Cost today:           $0.25
  Projected monthly:    $7.50
```

---

## 🎛️ Configuration

### Cost Control Settings

```python
# config/reranking.yaml

cost_control:
  daily_budget_usd: 5.0
  cache_ttl_seconds: 3600  # 1 hour
  max_candidates: 30  # Reduced from 50
  skip_simple_queries: true
  high_confidence_threshold: 0.95

alerts:
  budget_warning_threshold: 0.8  # Alert at 80%
  budget_critical_threshold: 0.95  # Disable at 95%
```

---

## ✅ Optimization Summary

| Strategy | Impact | Savings | Complexity |
|----------|--------|---------|------------|
| Caching | High | ~70% | Medium |
| Reduce candidates (30) | Medium | ~33% | Low |
| Smart reranking | Medium | ~20% | Medium |
| Budget limits | Safety | N/A | Low |

**Combined savings:** ~85% cost reduction
- Without optimization: $27/month (1000 searches/day)
- With optimization: $4/month

---

## ✅ Criterios de Aceptación

- ✅ Caching implementado
- ✅ Budget monitoring funcional
- ✅ Smart reranking logic
- ✅ Cost tracking dashboard
- ✅ Alert system configurado

---

## 🔗 Siguiente Paso

→ [SPEC-305: Acceptance Criteria](./SPEC-305-acceptance-criteria.md)

---

**Estado:** 🔴 Pendiente
