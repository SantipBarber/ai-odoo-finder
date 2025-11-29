# SPEC-602: Checklist de Deployment
## Flujo Inteligente de Búsqueda MCP

**Versión:** 1.0  
**Última actualización:** Enero 2025

---

## 📋 Pre-requisitos

### Entorno de Desarrollo

- [ ] Python 3.11+ instalado
- [ ] `uv` instalado (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- [ ] Claude Desktop instalado
- [ ] Acceso a la base de datos PostgreSQL (Neon)
- [ ] Variables de entorno configuradas en `.env`

### Verificar Estado Actual

- [ ] Backend API funcionando en `http://localhost:8989`
- [ ] Base de datos accesible y con datos
- [ ] Migración 004 aplicada (enrichment fields)

---

## 🗄️ Base de Datos

### Migración 005: repo_name en searchable_text

**Archivo:** `backend/migrations/005_add_repo_name_to_searchable_text.sql`

**Pasos:**

1. [ ] Hacer backup de la base de datos
   ```bash
   pg_dump $DATABASE_URL > backup_before_migration_005.sql
   ```

2. [ ] Verificar que la migración 004 está aplicada
   ```bash
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM odoo_modules WHERE ai_description IS NOT NULL;"
   ```

3. [ ] Ejecutar migración 005
   ```bash
   psql $DATABASE_URL -f backend/migrations/005_add_repo_name_to_searchable_text.sql
   ```

4. [ ] Verificar que se ejecutó correctamente
   ```bash
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM odoo_modules WHERE searchable_text @@ plainto_tsquery('english', 'spain');"
   ```
   **Resultado esperado:** ~449 módulos

5. [ ] Verificar trigger actualizado
   ```bash
   psql $DATABASE_URL -c "\df update_odoo_modules_searchable_text"
   ```

### Rollback (si algo falla)

- [ ] Restaurar desde backup
   ```bash
   psql $DATABASE_URL < backup_before_migration_005.sql
   ```

---

## 🖥️ Backend API

### Actualizar mcp_tools.py

**Archivo:** `backend/app/mcp_tools.py`

**Verificar cambios:**

- [ ] `QUERY_DESCRIPTION` contiene instrucciones de localizaciones
- [ ] Función `_format_results_intelligent()` existe
- [ ] Función `_calculate_confidence()` existe
- [ ] Función `_format_module_detailed()` existe
- [ ] Función `_format_module_summary()` existe
- [ ] Función `_get_confidence_guidance()` existe
- [ ] Función `_get_llm_instructions()` existe
- [ ] Función `_format_no_results()` existe

**Testing local:**

- [ ] Arrancar servidor backend
   ```bash
   cd /ruta/a/ai-odoo-finder
   uv run python scripts/run_server.py
   ```

- [ ] Probar endpoint `/search` con curl
   ```bash
   curl "http://localhost:8989/search?query=facturae+Spain&version=16.0&limit=5"
   ```

- [ ] Verificar que devuelve módulos españoles en top 5
   - [ ] `l10n_es_facturae` aparece con BM25 score
   - [ ] `l10n_es_facturae_face` aparece con BM25 score

---

## 📦 Servidor MCP

### Instalación

**Directorio:** `mcp-server/`

1. [ ] Verificar que existe `pyproject.toml`
2. [ ] Verificar que existe `src/ai_odoofinder_mcp/server.py`
3. [ ] Instalar dependencias
   ```bash
   cd mcp-server
   uv sync
   ```

4. [ ] Verificar que se instaló correctamente
   ```bash
   uv run python -c "from ai_odoofinder_mcp.server import mcp; print('✅ OK')"
   ```

### Verificar Código

- [ ] `server.py` tiene ~538 líneas
- [ ] `QUERY_DESCRIPTION` contiene reglas de localizaciones
- [ ] Función `_format_results_intelligent()` implementada
- [ ] Función `get_http_client()` usa URL correcta
- [ ] Endpoint de API es `/search` (no `/api/v1/search`)
- [ ] Manejo de errores implementado (timeout, conexión)

---

## 🖥️ Claude Desktop

### Configuración

**Ubicación archivo config:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

1. [ ] Obtener ruta completa de `uv`
   ```bash
   which uv
   ```
   **Resultado esperado:** `/Users/USUARIO/.local/bin/uv`

2. [ ] Obtener ruta completa del proyecto
   ```bash
   pwd  # desde ai-odoo-finder/mcp-server
   ```

3. [ ] Crear/editar `claude_desktop_config.json`
   ```json
   {
     "mcpServers": {
       "ai-odoofinder": {
         "command": "/Users/USUARIO/.local/bin/uv",
         "args": [
           "--directory",
           "/ruta/completa/a/ai-odoo-finder/mcp-server",
           "run",
           "ai-odoofinder-mcp"
         ],
         "env": {
           "AI_ODOOFINDER_API_URL": "http://localhost:8989"
         }
       }
     }
   }
   ```

4. [ ] **IMPORTANTE:** Usar rutas absolutas (no relativas)
5. [ ] **IMPORTANTE:** No incluir `~` en rutas, usar path completo

### Verificación

1. [ ] Cerrar Claude Desktop completamente (`Cmd+Q` en macOS)
2. [ ] Abrir Claude Desktop de nuevo
3. [ ] Buscar ícono de herramientas 🔧 en la interfaz
4. [ ] Verificar que aparece "ai-odoofinder"
5. [ ] Verificar que tiene la herramienta `search_odoo_modules`

### Logs

- [ ] Verificar logs si hay problemas
   ```bash
   # macOS
   tail -f ~/Library/Logs/Claude/mcp*.log
   
   # Windows
   type %USERPROFILE%\AppData\Local\Claude\logs\mcp*.log
   ```

**Errores comunes:**
- `spawn uv ENOENT` → Ruta de `uv` incorrecta
- `ModuleNotFoundError` → `uv sync` no ejecutado
- `Connection refused` → Backend no está corriendo

---

## 🧪 Testing

### Test 1: Localización España

**Consulta:** "Busco un módulo de facturación electrónica Facturae para España en Odoo 16"

**Resultado esperado:**
- [ ] Claude usa el MCP automáticamente
- [ ] Aparecen módulos `l10n_es_facturae_*` en resultados
- [ ] Respuesta tiene formato con confianza (ALTA/MEDIA/BAJA)
- [ ] Aparece sección "✅ RECOMENDADO"
- [ ] Aparece sección "📋 ALTERNATIVAS"

**Módulos esperados:**
- [ ] `l10n_es_facturae_face` (score ~98)
- [ ] `l10n_es_facturae_igic` (score ~95)

### Test 2: Localización México

**Consulta:** "Necesito facturación electrónica CFDI para México en Odoo 17"

**Resultado esperado:**
- [ ] `l10n_mx_cfdi` aparece en resultados
- [ ] `l10n_mx_cfdi_account` aparece en resultados

### Test 3: Funcionalidad Genérica

**Consulta:** "Módulo para gestionar suscripciones y contratos recurrentes en Odoo 16"

**Resultado esperado:**
- [ ] `contract` aparece como recomendado
- [ ] `subscription_oca` aparece en alternativas

### Test 4: Sin Resultados

**Consulta:** "Módulo para gestionar blockchain en Odoo 12"

**Resultado esperado:**
- [ ] Respuesta con "🔴 Confianza: NINGUNA"
- [ ] Sugerencias de alternativas
- [ ] NO inventa módulos que no existen

### Test 5: Verificar BM25

**Comando directo a API:**
```bash
curl "http://localhost:8989/search?query=facturae+Spain&version=16.0&limit=10"
```

**Verificar en JSON:**
- [ ] Módulos `l10n_es_*` tienen `bm25_score` > 0 (not null)
- [ ] `l10n_es_facturae` está en top 5

---

## 📝 Documentación

### Verificar Archivos

- [ ] `docs/CHANGELOG.md` creado con entrada para SPEC-602
- [ ] `README.md` actualizado con sección MCP
- [ ] `mcp-server/README.md` tiene instrucciones de instalación
- [ ] `specs/phase-6-intelligent-mcp/SPEC-602-intelligent-mcp-flow.md` marcado como completado
- [ ] `specs/phase-6-intelligent-mcp/IMPLEMENTATION_SUMMARY.md` creado
- [ ] `specs/phase-6-intelligent-mcp/QUICK_REFERENCE.md` creado
- [ ] `specs/phase-6-intelligent-mcp/EXECUTIVE_SUMMARY.md` creado

### Actualizar Links

- [ ] README principal enlaza a `mcp-server/README.md`
- [ ] CHANGELOG enlaza a SPEC-602
- [ ] SPEC-602 marca tareas como completadas

---

## 🚀 Deployment a Producción

### Preparación

- [ ] Todos los tests locales pasaron
- [ ] Documentación completa
- [ ] Migración 005 probada en staging

### Backend (Render)

1. [ ] Push código a GitHub
   ```bash
   git add .
   git commit -m "feat: Implement SPEC-602 Intelligent MCP Flow"
   git push origin main
   ```

2. [ ] Verificar que Render hace deploy automáticamente
3. [ ] Esperar a que el deploy termine (~5 min)
4. [ ] Ejecutar migración 005 en producción
   ```bash
   psql $PRODUCTION_DATABASE_URL -f backend/migrations/005_add_repo_name_to_searchable_text.sql
   ```

5. [ ] Verificar que funciona
   ```bash
   curl "https://tu-api.onrender.com/search?query=facturae+Spain&version=16.0&limit=5"
   ```

### MCP Server

**Para producción (API en Render):**

- [ ] Usuarios deben actualizar `claude_desktop_config.json`:
   ```json
   "env": {
     "AI_ODOOFINDER_API_URL": "https://tu-api.onrender.com"
   }
   ```

### Comunicación

- [ ] Anunciar en README que SPEC-602 está completo
- [ ] Compartir en redes sociales (opcional)
- [ ] Notificar a usuarios activos (si hay lista)

---

## 🔍 Monitoreo Post-Deploy

### Día 1

- [ ] Revisar logs de errores en Render
- [ ] Verificar que no hay errores en migraciones
- [ ] Probar endpoint `/search` en producción

### Semana 1

- [ ] Recopilar feedback de usuarios
- [ ] Identificar queries que no encuentran resultados
- [ ] Medir tiempo de respuesta promedio

### Mes 1

- [ ] Ejecutar benchmark formal (50+ queries)
- [ ] Medir métricas: P@3, MRR
- [ ] Analizar patrones de uso

---

## 🐛 Troubleshooting

### Problema: BM25 score es null

**Síntoma:** Todos los resultados tienen `bm25_score: null`

**Causa:** Migración 005 no ejecutada o trigger no actualizado

**Solución:**
```bash
psql $DATABASE_URL -c "\df update_odoo_modules_searchable_text"
# Verificar que incluye repo_name
```

### Problema: Claude Desktop no encuentra el servidor

**Síntoma:** MCP server no aparece en lista de herramientas

**Solución:**
1. Verificar logs: `tail -f ~/Library/Logs/Claude/mcp*.log`
2. Verificar ruta absoluta de `uv`: `which uv`
3. Verificar ruta absoluta del proyecto
4. Reiniciar Claude Desktop completamente (`Cmd+Q`)

### Problema: API timeout

**Síntoma:** Error "Timeout after 60 seconds"

**Causa:** API en Render está en sleep mode o sobrecargada

**Solución:**
1. Primera petición puede tardar ~30s (cold start)
2. Aumentar timeout en `mcp-server/server.py`:
   ```python
   API_TIMEOUT = int(os.getenv("AI_ODOOFINDER_API_TIMEOUT", "90"))
   ```

### Problema: Módulos no aparecen

**Síntoma:** Query específica no encuentra módulos esperados

**Solución:**
1. Verificar que el módulo existe: `curl "http://localhost:8989/search?query=nombre_tecnico&version=X.0"`
2. Verificar que tiene `searchable_text`: `psql -c "SELECT searchable_text FROM odoo_modules WHERE technical_name='...'"`
3. Si falta, regenerar: `UPDATE odoo_modules SET searchable_text = ... WHERE id = ...`

---

## ✅ Sign-off Final

**Antes de dar por completado:**

- [ ] Todos los tests pasaron (6/6)
- [ ] Documentación completa
- [ ] Migración 005 aplicada en producción
- [ ] Backend desplegado en Render
- [ ] MCP funciona en Claude Desktop
- [ ] Sin errores en logs
- [ ] Feedback inicial positivo

**Responsables:**
- Desarrollo: _________________
- QA: _________________
- Product Owner: _________________

**Fecha de deployment:** _________________

**Notas adicionales:**
```

---

**Fin del checklist**