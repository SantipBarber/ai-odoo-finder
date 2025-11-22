# SPEC-404: Deployment Guide

**ID:** SPEC-404
**Componente:** Production Deployment
**Prioridad:** Alta
**Estimación:** 4-6 horas
**Dependencias:** SPEC-401, SPEC-402, SPEC-403

---

## 📋 Descripción

Guía completa para deployment a producción, incluyendo checklist, configuración, monitoring, rollback procedures, y incident response.

---

## 🎯 Objetivos

1. **Pre-deployment Checklist** - Validar readiness
2. **Deployment Procedure** - Paso a paso para deploy
3. **Monitoring Setup** - Configurar alertas y dashboards
4. **Rollback Plan** - Procedimientos de emergencia
5. **Incident Response** - Playbook para incidentes

---

## ✅ Pre-Deployment Checklist

```markdown
## AI-OdooFinder: Production Deployment Checklist

### Code Quality
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Performance tests meet SLAs
- [ ] Code review completed and approved
- [ ] No critical security vulnerabilities
- [ ] Documentation up to date

### Database
- [ ] Migration scripts tested
- [ ] Backup strategy in place
- [ ] Rollback scripts prepared
- [ ] Indexes created and optimized
- [ ] pgVector extension installed
- [ ] Full-text search configured

### Configuration
- [ ] Environment variables set
- [ ] API keys configured (Anthropic, OpenAI)
- [ ] Database connection strings verified
- [ ] Redis configured (for caching)
- [ ] Logging level set appropriately
- [ ] Feature flags configured

### Infrastructure
- [ ] Production server provisioned
- [ ] SSL certificates installed
- [ ] Load balancer configured
- [ ] Auto-scaling policies set
- [ ] Backup storage configured
- [ ] Monitoring tools installed

### Data
- [ ] Module database populated
- [ ] AI descriptions generated (enrichment)
- [ ] Vector embeddings created
- [ ] Full-text indexes built
- [ ] Data validation completed

### Testing
- [ ] Staging environment tested
- [ ] Load testing completed
- [ ] User acceptance testing done
- [ ] Benchmark results validated
- [ ] Cost projections reviewed

### Documentation
- [ ] Deployment guide reviewed
- [ ] Runbook created
- [ ] API documentation published
- [ ] User guide available
- [ ] Incident response plan ready

### Security
- [ ] API authentication enabled
- [ ] Rate limiting configured
- [ ] CORS policies set
- [ ] SQL injection protections verified
- [ ] Secrets management configured
- [ ] Security audit completed

### Monitoring
- [ ] Application monitoring configured
- [ ] Database monitoring set up
- [ ] Cost tracking enabled
- [ ] Alert thresholds configured
- [ ] Dashboard created
- [ ] On-call rotation established

### Communication
- [ ] Stakeholders notified
- [ ] Maintenance window scheduled
- [ ] Rollback contacts identified
- [ ] Post-deployment review scheduled
```

---

## 🚀 Deployment Procedure

### Option 1: Docker Deployment (Recommended)

#### 1. Build Docker Image

```dockerfile
# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Docker Compose Configuration

```yaml
# docker-compose.prod.yml

version: '3.8'

services:
  db:
    image: ankane/pgvector:latest
    environment:
      POSTGRES_DB: odoo_finder
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/odoo_finder
      REDIS_URL: redis://redis:6379
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ENABLE_RERANKING_DEFAULT: "true"
      LOG_LEVEL: "info"
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

#### 3. Deploy Commands

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 Deploying AI-OdooFinder to Production"

# 1. Pull latest code
echo "📦 Pulling latest code..."
git pull origin main

# 2. Build Docker images
echo "🏗️ Building Docker images..."
docker-compose -f docker-compose.prod.yml build

# 3. Run database migrations
echo "📊 Running database migrations..."
docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# 4. Start services
echo "▶️ Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# 5. Health check
echo "🏥 Running health checks..."
sleep 10

if curl -f http://localhost:8000/health; then
    echo "✅ Deployment successful!"
else
    echo "❌ Health check failed. Rolling back..."
    docker-compose -f docker-compose.prod.yml down
    exit 1
fi

# 6. Run smoke tests
echo "🧪 Running smoke tests..."
python scripts/smoke_tests.py

echo "✅ Deployment complete!"
```

---

### Option 2: Kubernetes Deployment

#### Kubernetes Manifests

```yaml
# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-odoo-finder
  labels:
    app: ai-odoo-finder
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-odoo-finder
  template:
    metadata:
      labels:
        app: ai-odoo-finder
    spec:
      containers:
      - name: api
        image: your-registry/ai-odoo-finder:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: ai-odoo-finder-service
spec:
  selector:
    app: ai-odoo-finder
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-odoo-finder-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-odoo-finder
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 📊 Monitoring Setup

### 1. Application Metrics

```python
# app/monitoring/metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps

# Metrics
search_requests_total = Counter(
    'search_requests_total',
    'Total search requests',
    ['search_mode', 'version', 'status']
)

search_latency_seconds = Histogram(
    'search_latency_seconds',
    'Search request latency',
    ['search_mode', 'reranking_enabled']
)

reranking_cost_dollars = Counter(
    'reranking_cost_dollars_total',
    'Total reranking cost in USD'
)

cache_hit_rate = Gauge(
    'cache_hit_rate',
    'Cache hit rate'
)

active_searches = Gauge(
    'active_searches',
    'Number of active search requests'
)

def monitor_search(func):
    """Decorator to monitor search requests."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        search_mode = kwargs.get('search_mode', 'unknown')
        enable_reranking = kwargs.get('enable_reranking', False)

        active_searches.inc()
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)

            # Record success
            search_requests_total.labels(
                search_mode=search_mode,
                version=kwargs.get('version', 'unknown'),
                status='success'
            ).inc()

            return result

        except Exception as e:
            # Record failure
            search_requests_total.labels(
                search_mode=search_mode,
                version=kwargs.get('version', 'unknown'),
                status='error'
            ).inc()
            raise

        finally:
            # Record latency
            duration = time.time() - start_time
            search_latency_seconds.labels(
                search_mode=search_mode,
                reranking_enabled=str(enable_reranking)
            ).observe(duration)

            active_searches.dec()

    return wrapper
```

### 2. Prometheus Configuration

```yaml
# prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ai-odoo-finder'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### 3. Grafana Dashboard

```json
{
  "dashboard": {
    "title": "AI-OdooFinder Monitoring",
    "panels": [
      {
        "title": "Requests per Second",
        "targets": [
          {
            "expr": "rate(search_requests_total[5m])"
          }
        ]
      },
      {
        "title": "P95 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, search_latency_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "targets": [
          {
            "expr": "cache_hit_rate"
          }
        ]
      },
      {
        "title": "Daily Reranking Cost",
        "targets": [
          {
            "expr": "increase(reranking_cost_dollars_total[24h])"
          }
        ]
      }
    ]
  }
}
```

### 4. Alert Rules

```yaml
# alerts.yml

groups:
  - name: ai_odoo_finder_alerts
    interval: 30s
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, search_latency_seconds_bucket) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High search latency detected"
          description: "P95 latency is {{ $value }}s"

      - alert: HighErrorRate
        expr: rate(search_requests_total{status="error"}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}"

      - alert: DailyCostExceeded
        expr: increase(reranking_cost_dollars_total[24h]) > 10
        labels:
          severity: warning
        annotations:
          summary: "Daily cost budget exceeded"
          description: "Cost is ${{ $value }}"

      - alert: LowCacheHitRate
        expr: cache_hit_rate < 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low cache hit rate"
          description: "Cache hit rate is {{ $value }}"
```

---

## 🔄 Rollback Procedure

### Automatic Rollback Script

```bash
#!/bin/bash
# scripts/rollback.sh

set -e

echo "⚠️ Initiating rollback..."

# 1. Stop current deployment
echo "🛑 Stopping current deployment..."
docker-compose -f docker-compose.prod.yml down

# 2. Checkout previous version
echo "⏮️ Reverting to previous version..."
git checkout HEAD~1

# 3. Rebuild
echo "🏗️ Rebuilding previous version..."
docker-compose -f docker-compose.prod.yml build

# 4. Rollback database
echo "📊 Rolling back database..."
docker-compose -f docker-compose.prod.yml run --rm api alembic downgrade -1

# 5. Start services
echo "▶️ Starting previous version..."
docker-compose -f docker-compose.prod.yml up -d

# 6. Verify
echo "🏥 Verifying rollback..."
sleep 10

if curl -f http://localhost:8000/health; then
    echo "✅ Rollback successful!"
else
    echo "❌ Rollback failed. Manual intervention required."
    exit 1
fi
```

---

## 🚨 Incident Response Playbook

### Severity Levels

```yaml
P1 - Critical:
  Description: Service completely down
  Response Time: Immediate
  Escalation: Page on-call immediately
  Examples:
    - Complete service outage
    - Data loss
    - Security breach

P2 - High:
  Description: Major feature broken
  Response Time: < 1 hour
  Escalation: Notify team lead
  Examples:
    - Search returning no results
    - High error rate (>10%)
    - Severe performance degradation

P3 - Medium:
  Description: Minor feature broken
  Response Time: < 4 hours
  Escalation: Create ticket
  Examples:
    - Reranking disabled
    - Cache not working
    - Latency above target

P4 - Low:
  Description: Cosmetic issue
  Response Time: Next business day
  Examples:
    - Logging issues
    - Minor UI glitches
```

### Common Incidents & Solutions

#### 1. High Latency

```yaml
Symptom: P95 latency > 2000ms

Diagnosis:
  1. Check active_searches metric
  2. Check database connection pool
  3. Check LLM API latency
  4. Check cache hit rate

Solutions:
  - Scale up replicas if under load
  - Temporarily disable reranking
  - Increase connection pool size
  - Clear and rebuild cache
```

#### 2. High Error Rate

```yaml
Symptom: Error rate > 5%

Diagnosis:
  1. Check application logs
  2. Check database connectivity
  3. Check API key validity
  4. Check rate limits

Solutions:
  - Rollback if recent deployment
  - Restart services
  - Verify API keys
  - Contact LLM provider
```

#### 3. Cost Budget Exceeded

```yaml
Symptom: Daily cost > $10

Diagnosis:
  1. Check reranking request count
  2. Check cache hit rate
  3. Check for abuse/bot traffic

Solutions:
  - Enable stricter rate limiting
  - Temporarily disable reranking
  - Improve cache hit rate
  - Block abusive IPs
```

---

## 📝 Post-Deployment Checklist

```markdown
## Post-Deployment Review

### Immediate (T+1 hour)
- [ ] All services healthy
- [ ] No errors in logs
- [ ] Metrics reporting correctly
- [ ] Alerts configured
- [ ] Performance within SLAs

### Short-term (T+24 hours)
- [ ] No degradation in metrics
- [ ] Cost tracking accurate
- [ ] User feedback collected
- [ ] No rollbacks triggered

### Long-term (T+7 days)
- [ ] Benchmark comparison validated
- [ ] Performance trends reviewed
- [ ] Cost projections accurate
- [ ] Team retrospective completed
- [ ] Documentation updated
```

---

## ✅ Criterios de Aceptación

- ✅ Deployment checklist completado
- ✅ Docker configuration lista
- ✅ Monitoring configurado
- ✅ Alerts funcionando
- ✅ Rollback procedure testeado
- ✅ Incident playbook documentado
- ✅ Production deployment exitoso

---

## 🔗 Siguiente Paso

→ [SPEC-405: Final Acceptance & Sign-off](./SPEC-405-final-acceptance.md)

---

**Estado:** 🔴 Pendiente de implementación
