# Historial de Cambios

Todos los cambios notables de AI-OdooFinder se documentarán en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.4.0] - 2025-12-22

### Publicación en PyPI

El servidor MCP ahora está publicado en **[PyPI](https://pypi.org/project/ai-odoofinder-mcp/)**, haciendo la instalación más simple y rápida.

### Añadido

#### Paquete PyPI
- **Nombre del paquete**: `ai-odoofinder-mcp`
- **Versión**: 1.0.0
- **Python**: >=3.11
- **Licencia**: MIT

#### Instalación Simplificada
La instalación ahora es mucho más simple:

```bash
# Usando pip
pip install ai-odoofinder-mcp

# Usando uvx
uvx ai-odoofinder-mcp
```

#### Configuración MCP Simplificada
La configuración para todos los clientes MCP ahora es más corta:

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

### Cambiado

- **README.md** y **README.es.md**: Actualizada sección de instalación con PyPI como método principal
- **mcp-server/README.md** y **mcp-server/README.es.md**: Actualizadas secciones de inicio rápido y publicación
- **docs/en/MCP_CLIENT_CONFIGURATIONS.md** y **docs/es/MCP_CLIENT_CONFIGURATIONS.md**: Todas las configuraciones de clientes actualizadas
- Añadido badge de PyPI a todos los archivos README
- Instalación desde Git conservada como alternativa para versiones de desarrollo

### Beneficios

| Aspecto | Antes (Git) | Después (PyPI) |
|---------|-------------|----------------|
| Longitud args | 4 líneas | 1 línea |
| Velocidad instalación | Clona repo | Descarga paquete |
| Versionado | Hash commit | Versión semántica |
| Fiabilidad | Depende de GitHub | CDN de PyPI |
| Tamaño config | ~150 chars | ~30 chars |

---

## [1.3.0] - 2025-01-19

### Documentación de Configuraciones de Clientes MCP

Esta versión añade documentación completa para configuraciones de clientes MCP en múltiples IDEs y plataformas de IA.

### Añadido

#### Documentación de Soporte para Nuevos Clientes MCP
- **Claude Code CLI**: Claude basado en terminal con soporte MCP
  - Guía de instalación y configuración
  - Opciones de configuración interactiva y manual
  - Ejemplos de uso con comandos

- **ChatGPT Developer Mode**: Implementación MCP de OpenAI (Beta - Septiembre 2025)
  - Requisitos y pasos de configuración
  - Opciones de configuración remota y local
  - Capacidades completas de lectura/escritura

- **VSCode Copilot**: GitHub Copilot con soporte MCP (GA - Julio 2025)
  - Configuración a nivel de proyecto y global
  - Requisitos de política Business/Enterprise
  - Integración con autenticación de GitHub

#### Guías de Configuración Completas
- **`docs/es/MCP_CLIENT_CONFIGURATIONS.md`**: Guía técnica completa de 790 líneas
  - Configuración detallada para 9 clientes MCP diferentes
  - Comparación de modos Local (STDIO) vs Remoto (HTTP)
  - Sección de solución de problemas con issues comunes
  - Referencia de variables de entorno
  - Matriz de compatibilidad de clientes

- **`docs/en/MCP_CLIENT_CONFIGURATIONS.md`**: Versión en inglés con paridad completa

#### Soporte Mejorado para Antigravity
- **3 soluciones alternativas** para problemas de compatibilidad con uvx:
  1. Usar `npx` en lugar de `uvx` (Recomendado)
  2. Usar ruta completa a `uvx.exe` (Windows)
  3. Usar Python directamente
- **Alternativa**: Configuración de proxy `mcp-remote`
- Documentación clara de limitaciones (incompatibilidad de protocolo SSE)

#### Matriz de Compatibilidad de Clientes
Añadida a ambos READMEs mostrando:
- 9 clientes MCP con estado de soporte
- Disponibilidad de modo Local/Remoto
- Nivel de estabilidad (Estable/Beta/Problemas)
- Notas específicas por cliente

### Cambiado

- **README.md** y **README.es.md**:
  - Reorganizada sección de Configuración por IDE/Cliente
  - Añadida configuración de Claude Code CLI
  - Añadida configuración de ChatGPT Developer Mode
  - Añadida configuración de VSCode Copilot
  - Mejorada sección de Antigravity con múltiples soluciones
  - Añadida tabla de matriz de compatibilidad
  - Añadidas referencias cruzadas a guías detalladas

### Estructura de Documentación

```
docs/
├── en/
│   ├── CHANGELOG.md
│   ├── DEPLOYMENT_OPERATIONS.md
│   ├── PROJECT_HISTORY.md
│   └── MCP_CLIENT_CONFIGURATIONS.md  (NUEVO)
└── es/
    ├── CHANGELOG.md
    ├── DEPLOYMENT_OPERATIONS.md
    ├── PROJECT_HISTORY.md
    └── MCP_CLIENT_CONFIGURATIONS.md  (NUEVO)
```

### Clientes MCP Soportados

| Cliente | Local | Remoto | Estado | Notas |
|---------|-------|--------|--------|-------|
| Claude Desktop | ✅ | ❌ | Estable | Mejor experiencia |
| Claude Code CLI | ✅ | ✅ | Estable | **¡NUEVO!** Basado en terminal |
| Claude.ai Web | ❌ | ✅ | Estable | Sin instalación |
| ChatGPT Dev Mode | ✅ | ✅ | Beta | **¡NUEVO!** Sept 2025 |
| VSCode Copilot | ✅ | ⚠️ | GA | **¡NUEVO!** Julio 2025 |
| Cursor | ✅ | ❌ | Estable | Opción popular |
| Zed | ✅ | ❌ | Estable | Editor rápido |
| Windsurf | ✅ | ❌ | Estable | Soporte completo |
| Antigravity | ⚠️ | ❌ | Problemas | Múltiples workarounds |

---

## [1.2.0] - 2025-11-30

### Soporte para Servidor MCP Remoto

Esta versión añade soporte para clientes MCP remotos (Claude.ai Web, Zed, Cursor).

### Añadido

#### Transporte HTTP para MCP Remoto
- **Modo de transporte HTTP** con bandera `--http` en `mcp-server/src/ai_odoofinder_mcp/server.py`
- **Dockerfile** para contenerización del servidor MCP
- **docker-compose.yml** actualizado con servicio MCP en el puerto 8080
- **Integración de Tailscale Funnel** para exposición HTTPS

#### Documentación Multi-idioma
- **README.md** reescrito en inglés (predeterminado)
- **README.es.md** creado para documentación en español
- Insignias de selector de idioma para cambio fácil

### Cambiado

- Todos los comentarios del código traducidos al inglés
- Todas las descripciones de herramientas traducidas al inglés
- Removidos detalles del servidor hardcodeados de la documentación

### Despliegue

El Servidor MCP ahora es accesible en:
- **Claude.ai Web**: Añadir como servidor MCP remoto
- **Claude Desktop**: STDIO local o HTTP remoto
- **Zed/Cursor**: Conexión HTTP remota

---

## [1.1.0] - 2025-01-XX

### Fase 6: MCP Inteligente (SPEC-602)

Esta versión implementa el flujo de búsqueda inteligente para MCP según SPEC-602.

### Añadido

#### Servidor MCP Local para Claude Desktop
- **Nuevo directorio `mcp-server/`** con servidor MCP independiente
  - `mcp-server/src/ai_odoofinder_mcp/server.py` - Servidor principal
  - `mcp-server/pyproject.toml` - Configuración del paquete
  - `mcp-server/README.md` - Instrucciones de instalación

#### Descripción de Herramienta Enriquecida
- **Instrucciones de aclaración inteligentes** en el parámetro `query`:
  - Cuándo pedir aclaraciones (consultas genéricas, ambiguas, sin versión)
  - Cuándo NO pedir aclaraciones (consultas específicas, nombres técnicos)
  
- **Instrucciones de construcción de consultas**:
  - Regla crítica para localizaciones: usar prefijo `l10n_XX_` como término principal
  - Ejemplos específicos para España, México, Argentina, Francia, Italia, etc.
  - Guía de sinónimos ES/EN para búsquedas no localizadas

#### Formato de Respuesta Estructurada
- **Niveles de confianza**: HIGH (>=80), MEDIUM (50-79), LOW (<50), NONE
- **Secciones diferenciadas**:
  - RECOMENDADO: Módulos con puntuación >=80, formato detallado
  - ALTERNATIVAS: Módulos con puntuación <80, formato resumen
- **Guía contextual** basada en el nivel de confianza
- **Instrucciones LLM** sobre cómo presentar resultados

#### Migración de Base de Datos
- **`backend/migrations/005_add_repo_name_to_searchable_text.sql`**
  - Añade `repo_name` al campo `searchable_text` (tsvector)
  - Mejora la búsqueda de localizaciones por nombre de país
  - Ejemplo: buscar "Spain" ahora encuentra módulos desde `l10n-spain`

### Cambiado

- **`backend/app/mcp_tools.py`**: 
  - Actualizada `QUERY_DESCRIPTION` con instrucciones inteligentes
  - Nueva función `_format_results_intelligent()` con niveles de confianza
  - Nueva función `_calculate_confidence()` 
  - Nueva función `_format_module_detailed()` para módulos recomendados
  - Nueva función `_format_module_summary()` para alternativas
  - Nueva función `_get_confidence_guidance()` con guías contextuales
  - Nueva función `_get_llm_instructions()` con instrucciones LLM
  - Nueva función `_format_no_results()` para casos sin resultados

### Corregido

- **Búsqueda de localizaciones**: Anteriormente, buscar "facturae Spain" no encontraba `l10n_es_facturae` porque:
  - La descripción del módulo estaba en español
  - El campo `repo_name` (l10n-spain) no estaba indexado en BM25
  - Ahora `repo_name` está incluido en `searchable_text` con peso B

### Métricas

Resultados de pruebas con Claude Desktop:

| Consulta | Resultado | Módulos encontrados correctamente |
|----------|-----------|-----------------------------------|
| Facturae Spain (Odoo 16) | Éxito | `l10n_es_facturae_face`, `l10n_es_facturae_igic` |
| CFDI Mexico (Odoo 17) | Éxito | `l10n_mx_cfdi`, `l10n_mx_cfdi_account` |
| Subscriptions (Odoo 16) | Éxito | `contract`, `subscription_oca` |
| DMS + OCR (Odoo 17) | Éxito | `dms`, `dms_storage` |
| AEAT mod303 (Odoo 16) | Éxito | `l10n_es_aeat_mod303` |
| Delivery carriers (Odoo 17) | Éxito | `delivery_price_method`, `product_packaging_dimension` |

---

## [1.0.0] - 2025-11-XX

### Fase 5: Calidad de Búsqueda y Pruebas

#### Añadido
- Conjunto de pruebas para evaluación de calidad de búsqueda
- Scripts de comparación de pruebas
- Casos de prueba para localizaciones

#### Métricas
- Precision@3: 41.7%
- Precision@5: 30.0%
- MRR: 0.687

---

## [0.9.0] - 2025-11-XX

### Fase 4: Enriquecimiento de Datos

#### Añadido
- Campo `ai_description` con descripciones generadas por IA
- Campo `keywords` con palabras clave extraídas
- Campo `functional_tags` con categorías funcionales
- Migración 004: Búsqueda full-text con campos enriquecidos

#### Métricas
- 15,881 módulos enriquecidos (100%)

---

## [0.8.0] - 2025-11-XX

### Fase 3: Búsqueda Híbrida

#### Añadido
- Búsqueda híbrida (Vector + BM25)
- Fusión Recíproca de Ranking (RRF)
- Campo `searchable_text` (tsvector)
- Índice GIN para búsqueda full-text

---

## [0.7.0] - 2025-11-XX

### Fase 2: Búsqueda Vectorial

#### Añadido
- Embeddings con Qwen3-Embedding-4B
- Índice HNSW para búsqueda vectorial
- Integración pgVector

---

## [0.6.0] - 2025-11-XX

### Fase 1: ETL y Captura de Datos

#### Añadido
- Pipeline ETL para módulos OCA
- Integración API de GitHub
- 15,881 módulos indexados desde 176 repositorios
- Soporte para versiones 12.0 a 19.0

---

## Cómo Usar Este Historial de Cambios

- **Añadido**: Nuevas funcionalidades
- **Cambiado**: Cambios en funcionalidades existentes
- **Obsoleto**: Funcionalidades que serán removidas
- **Removido**: Funcionalidades removidas
- **Corregido**: Corrección de errores
- **Seguridad**: Vulnerabilidades de seguridad corregidas
- **Métricas**: Métricas de rendimiento/calidad
