# Changelog

**Language**: [English](../en/CHANGELOG.md) | [Español](../es/CHANGELOG.md)

All notable changes to AI-OdooFinder will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.4.0] - 2025-12-22

### PyPI Publication

The MCP server is now published on **[PyPI](https://pypi.org/project/ai-odoofinder-mcp/)**, making installation simpler and faster.

### Added

#### PyPI Package
- **Package name**: `ai-odoofinder-mcp`
- **Version**: 1.0.0
- **Python**: >=3.11
- **License**: MIT

#### Simplified Installation
Installation is now much simpler:

```bash
# Using pip
pip install ai-odoofinder-mcp

# Using uvx
uvx ai-odoofinder-mcp
```

#### Simplified MCP Configuration
Configuration for all MCP clients is now shorter:

```json
{
  "mcpServers": {
    "ai-odoofinder": {
      "command": "uvx",
      "args": ["ai-odoofinder-mcp"],
      "env": {
        "AI_ODOOFINDER_API_URL": "https://strategy-orchestrator-prod.tailf7d690.ts.net"
      }
    }
  }
}
```

### Changed

- **README.md** and **README.es.md**: Updated installation section with PyPI as primary method
- **mcp-server/README.md** and **mcp-server/README.es.md**: Updated quick start and publishing sections
- **docs/en/MCP_CLIENT_CONFIGURATIONS.md** and **docs/es/MCP_CLIENT_CONFIGURATIONS.md**: All client configurations updated
- Added PyPI badge to all README files
- Git installation preserved as alternative for development versions

### Benefits

| Aspect | Before (Git) | After (PyPI) |
|--------|--------------|--------------|
| Args length | 4 lines | 1 line |
| Install speed | Clones repo | Downloads package |
| Versioning | Commit hash | Semantic version |
| Reliability | Depends on GitHub | PyPI CDN |
| Config size | ~150 chars | ~30 chars |

---

## [1.3.0] - 2025-01-19

### MCP Client Configurations Documentation

This version adds comprehensive documentation for MCP client configurations across multiple AI IDEs and platforms.

### Added

#### New MCP Client Support Documentation
- **Claude Code CLI**: Terminal-based Claude with MCP support
  - Installation and configuration guide
  - Interactive and manual setup options
  - Usage examples with commands

- **ChatGPT Developer Mode**: OpenAI's MCP implementation (Beta - September 2025)
  - Requirements and setup steps
  - Remote and local configuration options
  - Full read/write capabilities

- **VSCode Copilot**: GitHub Copilot with MCP support (GA - July 2025)
  - Project-level and global configuration
  - Business/Enterprise policy requirements
  - Integration with GitHub authentication

#### Comprehensive Configuration Guides
- **`docs/en/MCP_CLIENT_CONFIGURATIONS.md`**: Complete 790-line technical guide
  - Detailed setup for 9 different MCP clients
  - Local (STDIO) vs Remote (HTTP) modes comparison
  - Troubleshooting section with common issues
  - Environment variables reference
  - Client compatibility matrix

- **`docs/es/MCP_CLIENT_CONFIGURATIONS.md`**: Spanish version with full parity

#### Enhanced Antigravity Support
- **3 workaround solutions** for uvx compatibility issues:
  1. Use `npx` instead of `uvx` (Recommended)
  2. Use full path to `uvx.exe` (Windows)
  3. Use Python directly
- **Alternative**: `mcp-remote` proxy configuration
- Clear documentation of limitations (SSE protocol incompatibility)

#### Client Compatibility Matrix
Added to both READMEs showing:
- 9 MCP clients with support status
- Local/Remote mode availability
- Stability level (Stable/Beta/Issues)
- Specific notes per client

### Changed

- **README.md** and **README.es.md**:
  - Reorganized IDE/Client Configuration section
  - Added Claude Code CLI configuration
  - Added ChatGPT Developer Mode configuration
  - Added VSCode Copilot configuration
  - Improved Antigravity section with multiple solutions
  - Added compatibility matrix table
  - Added cross-references to detailed guides

### Documentation Structure

```
docs/
├── en/
│   ├── CHANGELOG.md
│   ├── DEPLOYMENT_OPERATIONS.md
│   ├── PROJECT_HISTORY.md
│   └── MCP_CLIENT_CONFIGURATIONS.md  (NEW)
└── es/
    ├── CHANGELOG.md
    ├── DEPLOYMENT_OPERATIONS.md
    ├── PROJECT_HISTORY.md
    └── MCP_CLIENT_CONFIGURATIONS.md  (NEW)
```

### Supported MCP Clients

| Client | Local | Remote | Status | Notes |
|--------|-------|--------|--------|-------|
| Claude Desktop | ✅ | ❌ | Stable | Best experience |
| Claude Code CLI | ✅ | ✅ | Stable | **NEW!** Terminal-based |
| Claude.ai Web | ❌ | ✅ | Stable | Zero install |
| ChatGPT Dev Mode | ✅ | ✅ | Beta | **NEW!** Sept 2025 |
| VSCode Copilot | ✅ | ⚠️ | GA | **NEW!** July 2025 |
| Cursor | ✅ | ❌ | Stable | Popular choice |
| Zed | ✅ | ❌ | Stable | Fast editor |
| Windsurf | ✅ | ❌ | Stable | Full support |
| Antigravity | ⚠️ | ❌ | Issues | Multiple workarounds |

---

## [1.2.0] - 2025-11-30

### Remote MCP Server Support

This version adds support for remote MCP clients (Claude.ai Web, Zed, Cursor).

### Added

#### HTTP Transport for Remote MCP
- **HTTP transport mode** with `--http` flag in `mcp-server/src/ai_odoofinder_mcp/server.py`
- **Dockerfile** for MCP server containerization
- **docker-compose.yml** updated with MCP service on port 8080
- **Tailscale Funnel** integration for HTTPS exposure

#### Multi-language Documentation
- **README.md** rewritten in English (default)
- **README.es.md** created for Spanish documentation
- Language selector badges for easy switching

### Changed

- All code comments translated to English
- All tool descriptions translated to English
- Removed hardcoded server details from documentation

### Deployment

MCP Server now accessible at:
- **Claude.ai Web**: Add as remote MCP server
- **Claude Desktop**: Local STDIO or remote HTTP
- **Zed/Cursor**: Remote HTTP connection

---

## [1.1.0] - 2025-01-XX

### Phase 6: Intelligent MCP (SPEC-602)

This version implements the intelligent search flow for MCP according to SPEC-602.

### Added

#### Local MCP Server for Claude Desktop
- **New `mcp-server/` directory** with standalone MCP server
  - `mcp-server/src/ai_odoofinder_mcp/server.py` - Main server
  - `mcp-server/pyproject.toml` - Package configuration
  - `mcp-server/README.md` - Installation instructions

#### Enriched Tool Description
- **Smart clarification instructions** in the `query` parameter:
  - When to ask for clarifications (generic queries, ambiguous, no version)
  - When NOT to ask for clarifications (specific queries, technical names)
  
- **Query construction instructions**:
  - Critical rule for localizations: use `l10n_XX_` prefix as main term
  - Specific examples for Spain, Mexico, Argentina, France, Italy, etc.
  - ES/EN synonym guide for non-localized searches

#### Structured Response Format
- **Confidence levels**: HIGH (>=80), MEDIUM (50-79), LOW (<50), NONE
- **Differentiated sections**:
  - RECOMMENDED: Modules with score >=80, detailed format
  - ALTERNATIVES: Modules with score <80, summary format
- **Contextual guidance** based on confidence level
- **LLM instructions** on how to present results

#### Database Migration
- **`backend/migrations/005_add_repo_name_to_searchable_text.sql`**
  - Adds `repo_name` to `searchable_text` field (tsvector)
  - Improves localization search by country name
  - Example: searching "Spain" now finds modules from `l10n-spain`

### Changed

- **`backend/app/mcp_tools.py`**: 
  - Updated `QUERY_DESCRIPTION` with intelligent instructions
  - New function `_format_results_intelligent()` with confidence levels
  - New function `_calculate_confidence()` 
  - New function `_format_module_detailed()` for recommended modules
  - New function `_format_module_summary()` for alternatives
  - New function `_get_confidence_guidance()` with contextual guides
  - New function `_get_llm_instructions()` with LLM instructions
  - New function `_format_no_results()` for no-results cases

### Fixed

- **Localization search**: Previously, searching "facturae Spain" didn't find `l10n_es_facturae` because:
  - Module description was in Spanish
  - The `repo_name` field (l10n-spain) wasn't indexed in BM25
  - Now `repo_name` is included in `searchable_text` with weight B

### Metrics

Testing results with Claude Desktop:

| Query | Result | Modules found correctly |
|-------|--------|-------------------------|
| Facturae Spain (Odoo 16) | Success | `l10n_es_facturae_face`, `l10n_es_facturae_igic` |
| CFDI Mexico (Odoo 17) | Success | `l10n_mx_cfdi`, `l10n_mx_cfdi_account` |
| Subscriptions (Odoo 16) | Success | `contract`, `subscription_oca` |
| DMS + OCR (Odoo 17) | Success | `dms`, `dms_storage` |
| AEAT mod303 (Odoo 16) | Success | `l10n_es_aeat_mod303` |
| Delivery carriers (Odoo 17) | Success | `delivery_price_method`, `product_packaging_dimension` |

---

## [1.0.0] - 2025-11-XX

### Phase 5: Search Quality & Testing

#### Added
- Benchmark suite for search quality evaluation
- Benchmark comparison scripts
- Test cases for localizations

#### Metrics
- Precision@3: 41.7%
- Precision@5: 30.0%
- MRR: 0.687

---

## [0.9.0] - 2025-11-XX

### Phase 4: Data Enrichment

#### Added
- `ai_description` field with AI-generated descriptions
- `keywords` field with extracted keywords
- `functional_tags` field with functional categories
- Migration 004: Full-text search with enrichment fields

#### Metrics
- 15,881 modules enriched (100%)

---

## [0.8.0] - 2025-11-XX

### Phase 3: Hybrid Search

#### Added
- Hybrid search (Vector + BM25)
- Reciprocal Rank Fusion (RRF)
- `searchable_text` field (tsvector)
- GIN index for full-text search

---

## [0.7.0] - 2025-11-XX

### Phase 2: Vector Search

#### Added
- Embeddings with Qwen3-Embedding-4B
- HNSW index for vector search
- pgVector integration

---

## [0.6.0] - 2025-11-XX

### Phase 1: ETL & Data Ingestion

#### Added
- ETL pipeline for OCA modules
- GitHub API integration
- 15,881 modules indexed from 176 repositories
- Support for versions 12.0 to 19.0

---

## How to Use This Changelog

- **Added**: New features
- **Changed**: Changes to existing features
- **Deprecated**: Features that will be removed
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerabilities fixed
- **Metrics**: Performance/quality metrics
