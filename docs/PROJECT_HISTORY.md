# AI-OdooFinder - Historia del Proyecto

Este documento describe la evolucion del proyecto desde su concepcion inicial hasta la arquitectura actual.

## Contexto

AI-OdooFinder nacio como proyecto para el curso de **Orquestador de Inteligencia Artificial**. El objetivo era crear un asistente que ayudara a desarrolladores de Odoo a encontrar modulos existentes en los repositorios de OCA (Odoo Community Association), evitando desarrollo duplicado.

---

## Fase 1: Claude Skill (Idea Inicial)

### Concepto Original

La primera idea fue crear una **Claude Skill** - una extension para Claude.ai que permitiera buscar modulos de Odoo directamente desde la interfaz web.

### Arquitectura Inicial

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Claude.ai     │────►│   Render        │────►│   Neon          │
│   (Skill)       │     │   (API)         │     │   (PostgreSQL)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Componentes:**
- **Claude Skill**: Interfaz conversacional en claude.ai
- **Render**: Hosting gratuito para la API FastAPI
- **Neon**: PostgreSQL serverless gratuito

### Limitaciones Encontradas

1. **Claude Skills** estaban en beta cerrada y limitadas
2. **Render free tier** tenia cold starts de 30+ segundos
3. **Neon free tier** limitado a 0.5GB de storage
4. La arquitectura dependia de servicios externos con limitaciones

---

## Fase 2: Evolucion a MCP (Model Context Protocol)

### Descubrimiento de MCP

Durante el desarrollo, Anthropic lanzo el **Model Context Protocol (MCP)**, un estandar abierto para conectar modelos de IA con herramientas externas.

### Decision de Pivotar

Decidimos migrar de Claude Skill a MCP por:

1. **Estandar abierto**: No depende de beta cerrada
2. **Control local**: El MCP Server corre en la maquina del usuario
3. **Flexibilidad**: Funciona con Claude Desktop y cualquier cliente MCP
4. **Mejor experiencia**: Respuestas mas rapidas sin cold starts

### Nueva Arquitectura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Claude Desktop  │────►│   MCP Server    │────►│   API Backend   │
│ (Cliente)       │     │   (Local)       │     │   (Remoto)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Fase 3: Migracion a Servidor Propio

### Problemas con Servicios Gratuitos

- **Neon**: Limite de storage alcanzado con ~16k modulos
- **Render**: Cold starts inaceptables para produccion
- **Costes**: Escalar requeria pagar ~$25/mes

### Decision: Self-Hosting

Migramos todo a un **VPS existente en Hetzner** (ya teniamos uno para otros proyectos):

- **Coste adicional**: $0/mes
- **Control total**: Sin limites artificiales
- **Rendimiento**: Respuestas < 500ms

### Arquitectura Final

```
┌─────────────────────┐      ┌──────────────────────────────────┐
│   Claude Desktop    │      │        Hetzner VPS (Docker)      │
│   + MCP Server      │─────►│  ┌────────────┐  ┌────────────┐  │
│   (local)           │ HTTPS│  │  FastAPI   │  │ PostgreSQL │  │
└─────────────────────┘      │  │  :8989     │◄─│ + pgvector │  │
                             │  └────────────┘  └────────────┘  │
                             │                                  │
                             │  Tailscale Funnel (HTTPS)        │
                             └──────────────────────────────────┘
```

**Componentes actuales:**
- **MCP Server**: Python + FastMCP, corre localmente
- **FastAPI Backend**: Docker container en Hetzner
- **PostgreSQL 17 + pgvector**: Docker container con 16,494 modulos
- **Tailscale Funnel**: Expone la API via HTTPS sin abrir puertos

---

## Fase 4: Sistema de Busqueda Hibrida

### Evolucion del Algoritmo de Busqueda

#### Version 1: Solo Embeddings
- Busqueda puramente semantica
- Problema: No encontraba coincidencias exactas de nombres tecnicos

#### Version 2: Hibrida (Vector + BM25)
- Combinamos embeddings con full-text search PostgreSQL
- Usamos **Reciprocal Rank Fusion (RRF)** para combinar rankings
- Mejora significativa en precision

#### Version 3: Con Enrichment
- Anadimos descripcion IA, tags funcionales y keywords
- El embedding ahora incluye contenido enriquecido
- Mejor comprension semantica de cada modulo

### Algoritmo Final: RRF

```
RRF_score = 1/(k + rank_vector) + 1/(k + rank_bm25)
```

Donde `k=60` (constante estandar de RRF).

---

## Fase 5: ETL con Enrichment Automatico

### Proceso de Indexacion

El script `etl_oca_modules.py` realiza:

1. **Descubrimiento**: Obtiene todos los repos de OCA via GitHub API
2. **Extraccion**: Lee `__manifest__.py` y README de cada modulo
3. **Enrichment**: Genera con Grok-4-fast:
   - `ai_description`: Descripcion en ingles
   - `functional_tags`: Tags como "sales", "accounting", etc.
   - `keywords`: Palabras clave para busqueda
4. **Embedding**: Genera vector de 2560 dimensiones con Qwen3-Embedding
5. **Carga**: Inserta en PostgreSQL con pgvector

### Estadisticas Finales

| Metrica | Valor |
|---------|-------|
| Modulos totales | 16,494 |
| Con enrichment | 100% |
| Versiones Odoo | 10.0 - 19.0 |
| Repositorios OCA | 244 |
| Tiempo de indexacion | ~2 horas |

---

## Decisiones Tecnicas Clave

### 1. PostgreSQL + pgvector vs Bases Vectoriales Dedicadas

**Decision**: PostgreSQL con pgvector

**Razones**:
- Una sola base de datos para vectores y metadata
- Sin complejidad adicional de Pinecone/Weaviate
- Full-text search nativo con tsvector
- Suficiente para ~20k documentos

### 2. Modelo de Embeddings

**Decision**: Qwen3-Embedding-4B via OpenRouter

**Razones**:
- 2560 dimensiones (buena representacion)
- Coste bajo ($0.02/1M tokens)
- No requiere GPU local

### 3. Modelo de Enrichment

**Decision**: Grok-4-fast via OpenRouter

**Razones**:
- Muy economico ($0.20/M input, $0.50/M output)
- Rapido y preciso
- Coste total de enrichment: ~$3 para 16k modulos

### 4. Exposicion de API

**Decision**: Tailscale Funnel

**Razones**:
- HTTPS automatico
- Sin abrir puertos en firewall
- URL estable
- Gratis

---

## Lecciones Aprendidas

### Lo que Funciono

1. **Pivotar a MCP** fue la decision correcta - mas flexible y estandar
2. **Self-hosting** elimino todas las limitaciones de free tiers
3. **Busqueda hibrida** mejoro drasticamente la precision
4. **Enrichment automatico** hace los embeddings mucho mas utiles

### Lo que Podria Mejorar

1. **Tests automatizados**: Faltan tests de integracion
2. **Monitorizacion**: No hay alertas de errores
3. **Cache**: Podria anadir Redis para queries frecuentes
4. **Rate limiting**: La API esta abierta sin limites

---

## Futuro del Proyecto

### Posibles Mejoras

- [ ] Publicar MCP Server en PyPI para instalacion con `uvx`
- [ ] Anadir soporte para repositorios privados
- [ ] Interfaz web para busqueda
- [ ] Webhooks para actualizacion automatica cuando OCA publica modulos

### Mantenimiento

El ETL puede ejecutarse periodicamente para mantener el indice actualizado:

```bash
# En el servidor
cd /opt/ai-odoo-finder
~/.local/bin/uv run python scripts/etl_oca_modules.py
```

El script tiene checkpoints, asi que puede interrumpirse y retomarse.

---

## Timeline del Proyecto

| Fecha | Hito |
|-------|------|
| Nov 2024 | Inicio del proyecto como Claude Skill |
| Nov 15 | Pivot a MCP Server |
| Nov 22 | Primera version funcional con busqueda basica |
| Nov 26 | Implementacion de busqueda hibrida |
| Nov 29 | Migracion de Neon a servidor propio |
| Nov 30 | Enrichment automatico con Grok-4-fast |
| Nov 30 | Configuracion Tailscale Funnel |
| Nov 30 | Indexacion completa: 16,494 modulos |

---

*Documento creado: 2024-11-30*
