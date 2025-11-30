# AI-OdooFinder - Project History

**Language**: [English](../en/PROJECT_HISTORY.md) | [Español](../es/PROJECT_HISTORY.md)

This document describes the evolution of the project from its initial conception to the current architecture.

## Context

AI-OdooFinder was born as a project for the **AI Orchestrator** course. The goal was to create an assistant that helps Odoo developers find existing modules in OCA (Odoo Community Association) repositories, avoiding duplicate development.

---

## Phase 1: Claude Skill (Initial Idea)

### Original Concept

The first idea was to create a **Claude Skill** - an extension for Claude.ai that would allow searching for Odoo modules directly from the web interface.

### Initial Architecture

```
+-------------------+     +-------------------+     +-------------------+
|    Claude.ai      |---->|     Render        |---->|      Neon         |
|    (Skill)        |     |     (API)         |     |   (PostgreSQL)    |
+-------------------+     +-------------------+     +-------------------+
```

**Components:**
- **Claude Skill**: Conversational interface in claude.ai
- **Render**: Free hosting for FastAPI API
- **Neon**: Serverless PostgreSQL (free tier)

### Limitations Found

1. **Claude Skills** were in closed beta and limited
2. **Render free tier** had cold starts of 30+ seconds
3. **Neon free tier** limited to 0.5GB storage
4. Architecture depended on external services with limitations

---

## Phase 2: Evolution to MCP (Model Context Protocol)

### MCP Discovery

During development, Anthropic released the **Model Context Protocol (MCP)**, an open standard for connecting AI models with external tools.

### Decision to Pivot

We decided to migrate from Claude Skill to MCP because:

1. **Open standard**: Doesn't depend on closed beta
2. **Local control**: MCP Server runs on user's machine
3. **Flexibility**: Works with Claude Desktop and any MCP client
4. **Better experience**: Faster responses without cold starts

### New Architecture

```
+-------------------+     +-------------------+     +-------------------+
| Claude Desktop    |---->|   MCP Server      |---->|   API Backend     |
| (Client)          |     |   (Local)         |     |   (Remote)        |
+-------------------+     +-------------------+     +-------------------+
```

---

## Phase 3: Migration to Own Server

### Problems with Free Services

- **Neon**: Storage limit reached with ~16k modules
- **Render**: Unacceptable cold starts for production
- **Costs**: Scaling required paying ~$25/month

### Decision: Self-Hosting

We migrated everything to an **existing Hetzner VPS** (we already had one for other projects):

- **Additional cost**: $0/month
- **Full control**: No artificial limits
- **Performance**: Responses < 500ms

### Final Architecture

```
+---------------------+      +----------------------------------+
|   Claude Desktop    |      |        Hetzner VPS (Docker)      |
|   + MCP Server      |----->|  +------------+  +------------+  |
|   (local)           | HTTPS|  |  FastAPI   |  | PostgreSQL |  |
+---------------------+      |  |  :8989     |<-| + pgvector |  |
                             |  +------------+  +------------+  |
                             |                                  |
                             |  Tailscale Funnel (HTTPS)        |
                             +----------------------------------+
```

**Current components:**
- **MCP Server**: Python + FastMCP, runs locally or in Docker
- **FastAPI Backend**: Docker container on Hetzner
- **PostgreSQL 17 + pgvector**: Docker container with 16,494 modules
- **Tailscale Funnel**: Exposes API via HTTPS without opening ports

---

## Phase 4: Hybrid Search System

### Search Algorithm Evolution

#### Version 1: Embeddings Only
- Purely semantic search
- Problem: Didn't find exact matches for technical names

#### Version 2: Hybrid (Vector + BM25)
- Combined embeddings with PostgreSQL full-text search
- Used **Reciprocal Rank Fusion (RRF)** to combine rankings
- Significant improvement in precision

#### Version 3: With Enrichment
- Added AI description, functional tags, and keywords
- Embedding now includes enriched content
- Better semantic understanding of each module

### Final Algorithm: RRF

```
RRF_score = 1/(k + rank_vector) + 1/(k + rank_bm25)
```

Where `k=60` (RRF standard constant).

---

## Phase 5: ETL with Automatic Enrichment

### Indexing Process

The `etl_oca_modules.py` script performs:

1. **Discovery**: Gets all OCA repos via GitHub API
2. **Extraction**: Reads `__manifest__.py` and README from each module
3. **Enrichment**: Generates with Grok-4-fast:
   - `ai_description`: Description in English
   - `functional_tags`: Tags like "sales", "accounting", etc.
   - `keywords`: Keywords for search
4. **Embedding**: Generates 2560-dimension vector with Qwen3-Embedding
5. **Loading**: Inserts into PostgreSQL with pgvector

### Final Statistics

| Metric | Value |
|--------|-------|
| Total modules | 16,494 |
| With enrichment | 100% |
| Odoo versions | 10.0 - 19.0 |
| OCA repositories | 244 |
| Indexing time | ~2 hours |

---

## Key Technical Decisions

### 1. PostgreSQL + pgvector vs Dedicated Vector Databases

**Decision**: PostgreSQL with pgvector

**Reasons**:
- Single database for vectors and metadata
- No additional complexity from Pinecone/Weaviate
- Native full-text search with tsvector
- Sufficient for ~20k documents

### 2. Embedding Model

**Decision**: Qwen3-Embedding-4B via OpenRouter

**Reasons**:
- 2560 dimensions (good representation)
- Low cost ($0.02/1M tokens)
- No local GPU required

### 3. Enrichment Model

**Decision**: Grok-4-fast via OpenRouter

**Reasons**:
- Very economical ($0.20/M input, $0.50/M output)
- Fast and accurate
- Total enrichment cost: ~$3 for 16k modules

### 4. API Exposure

**Decision**: Tailscale Funnel

**Reasons**:
- Automatic HTTPS
- No need to open firewall ports
- Stable URL
- Free

---

## Lessons Learned

### What Worked

1. **Pivoting to MCP** was the right decision - more flexible and standard
2. **Self-hosting** eliminated all free tier limitations
3. **Hybrid search** drastically improved precision
4. **Automatic enrichment** makes embeddings much more useful

### What Could Improve

1. **Automated tests**: Missing integration tests
2. **Monitoring**: No error alerts
3. **Cache**: Could add Redis for frequent queries
4. **Rate limiting**: API is open without limits

---

## Project Future

### Possible Improvements

- [ ] Publish MCP Server on PyPI for installation with `uvx`
- [ ] Add support for private repositories
- [ ] Web interface for search
- [ ] Webhooks for automatic updates when OCA publishes modules

### Maintenance

The ETL can be run periodically to keep the index updated:

```bash
# On the server
cd /opt/ai-odoo-finder
~/.local/bin/uv run python scripts/etl_oca_modules.py
```

The script has checkpoints, so it can be interrupted and resumed.

---

## Project Timeline

| Date | Milestone |
|------|-----------|
| Nov 2024 | Project started as Claude Skill |
| Nov 15 | Pivot to MCP Server |
| Nov 22 | First functional version with basic search |
| Nov 26 | Hybrid search implementation |
| Nov 29 | Migration from Neon to own server |
| Nov 30 | Automatic enrichment with Grok-4-fast |
| Nov 30 | Tailscale Funnel configuration |
| Nov 30 | Complete indexing: 16,494 modules |

---

*Document created: 2024-11-30*
