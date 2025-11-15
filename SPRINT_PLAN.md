# 🚀 Plan de Sprints - AI-OdooFinder

**Versión:** 2.0
**Fecha de inicio:** Noviembre 2025
**Duración total:** 7-8 semanas

---

## 📍 Estado Actual

**Completado:**
- ✅ MVP funcional con API REST
- ✅ 991 módulos indexados (v16, v17, v18)
- ✅ Claude Skill básica (modo copy-paste)
- ✅ Deployment en Render + Neon

**Pendiente:**
- ⚠️ GitHub Actions ETL (corregido, pending test)
- ❌ MCP para Claude
- ❌ Versiones 12-15 y 19
- ❌ Odoo App Store integration
- ❌ Módulos custom/propios

---

## 🗓️ SPRINT 1: Limpieza y Corrección (Semana 1)

**Objetivo:** Limpiar deuda técnica y documentación

### Tareas

#### 1.1 Corregir GitHub Actions ETL ✅ HECHO
- [x] Añadir instalación de dependencias
- [x] Configurar variables de entorno
- [ ] Configurar secrets en GitHub (DATABASE_URL, GH_TOKEN, OPENROUTER_API_KEY)
- [ ] Probar ejecución manual
- [ ] Decidir frecuencia del ETL automático

**Archivos modificados:**
- `.github/workflows/etl.yml`

**Tiempo:** 2h

---

#### 1.2 Auditoría de Documentación
- [ ] Revisar `docs/CREATED_FILES.md` - eliminar si temporal
- [ ] Revisar `docs/GALLERY.md` - consolidar o eliminar
- [ ] Revisar `docs/BRANDING.md` - consolidar o eliminar
- [ ] Revisar `docs/NEXT_STEPS.md` - consolidar con ROADMAP
- [ ] Eliminar `claude-skill/prompts.md` si vacío
- [ ] Eliminar `claude-skill/examples.md` si vacío
- [ ] Eliminar `CONTRIBUTING.md` raíz (duplicado)

**Criterio de eliminación:**
- Contenido < 50 líneas útiles
- Información duplicada en otro doc
- Contenido obsoleto

**Tiempo:** 3-4h

---

#### 1.3 Actualizar Documentación Clave
- [ ] `README.md`: stats, roadmap, Claude Skill info
- [ ] `docs/TECHNICAL_GUIDE.md`: arquitectura actual, búsqueda híbrida
- [ ] `docs/API.md`: GET/POST `/search`, parámetros, ejemplos
- [ ] `docs/INDEX.md`: nueva estructura de docs
- [ ] `claude-skill/README.md`: verificar completitud

**Tiempo:** 4-5h

---

**Total Sprint 1:** ~11h (1-2 días)

---

## 🔌 SPRINT 2: MCP (Semanas 2-3)

**Objetivo:** Implementar servidor MCP para Claude nativo

### Tarea 2.1: Investigación y Setup (5-7 días)

#### Recursos
- https://modelcontextprotocol.io
- https://github.com/modelcontextprotocol
- Ejemplos de servidores MCP

#### Pasos
1. [ ] Estudiar protocolo MCP
2. [ ] Decidir lenguaje (Python vs Node.js)
3. [ ] Crear proyecto en `/mcp-server/`
4. [ ] Implementar tool `search_odoo_modules`
5. [ ] Testing local con Claude Desktop
6. [ ] Documentación de instalación

#### Estructura propuesta
```
mcp-server/
├── README.md
├── package.json (si Node.js)
├── requirements.txt (si Python)
├── src/
│   ├── server.py (o server.ts)
│   └── tools/
│       └── search_odoo_modules.py
└── tests/
```

---

### Tarea 2.2: Testing e Integración (2-3 días)
- [ ] Probar con Claude Desktop
- [ ] Probar con Claude Web (si posible)
- [ ] Crear ejemplos de uso
- [ ] Actualizar `claude-skill/Skill.md`
- [ ] Video/guía de instalación
- [ ] PR y merge

**Total Sprint 2:** 7-10 días

---

## 📦 SPRINT 3: Multi-Versión (Semana 4)

**Objetivo:** Ampliar a v12-v19

### Tarea 3.1: Implementación (3-4 días)

#### Cambios en código
1. [ ] `scripts/etl_oca_modules.py`: añadir v12-v19 a `ODOO_VERSIONS`
2. [ ] `backend/app/schemas.py`: actualizar validación de versiones
3. [ ] Ejecutar ETL para nuevas versiones
4. [ ] Verificar indexación

#### Verificaciones
- [ ] Confirmar que OCA tiene ramas 12.0, 13.0, 14.0, 15.0, 19.0
- [ ] Estimar número de módulos por versión
- [ ] Calcular costo de embeddings

#### Documentación
- [ ] Actualizar `docs/API.md`
- [ ] Actualizar `claude-skill/Skill.md`
- [ ] Actualizar estadísticas en `README.md`

**Estimación de nuevos módulos:** ~1000-1250
**Total:** ~2000-2250 módulos

**Total Sprint 3:** 3-4 días

---

## 🏪 SPRINT 4: Odoo App Store (Semanas 5-6)

**Objetivo:** Integrar módulos del Odoo App Store

### Tarea 4.1: Scraping (7-10 días)

#### Investigación
- [ ] Analizar estructura HTML de apps.odoo.com
- [ ] Identificar categorías y filtros
- [ ] Investigar API no oficial (reverse engineering)
- [ ] Decidir: scraping vs manual vs híbrido

#### Implementación
1. [ ] Crear `scripts/scrape_odoo_store.py`
2. [ ] Implementar scraper (BeautifulSoup/Scrapy)
3. [ ] Crear modelo `OdooStoreModule` en `backend/app/models.py`
4. [ ] Migración de BD (Alembic)
5. [ ] Modificar `search_service.py` para multi-source
6. [ ] Añadir parámetro `source` en API

#### Datos a extraer
- Nombre, descripción, versión
- Autor, precio, rating
- Dependencias
- URL del store

---

### Tarea 4.2: Testing (2-3 días)
- [ ] Probar scraping en categorías populares
- [ ] Verificar calidad de datos
- [ ] Testing búsqueda multi-source
- [ ] Documentar limitaciones
- [ ] Actualizar API docs
- [ ] Actualizar Skill.md

**Total Sprint 4:** 9-13 días

---

## 🏢 SPRINT 5: Módulos Custom (Semana 7)

**Objetivo:** Permitir indexar módulos propios

### Tarea 5.1: Core Implementation (5-6 días)

#### Diseño
**Flujo:**
1. Usuario escribe README del módulo custom
2. Ejecuta: `python scripts/index_custom_module.py --path /path --company "Mi Empresa"`
3. Script indexa en tabla `custom_modules`

#### Implementación
- [ ] Crear `scripts/index_custom_module.py`
- [ ] Crear modelo `CustomModule`
- [ ] Migración BD
- [ ] Modificar `search_service.py`
- [ ] Implementar autenticación básica
- [ ] Filtrado por tenant/empresa

#### Seguridad
- [ ] No mostrar módulos privados en búsquedas públicas
- [ ] API key por empresa
- [ ] Rate limiting

---

### Tarea 5.2: CLI y API (2-3 días)
- [ ] CLI para CRUD de custom modules
- [ ] Endpoints API REST
- [ ] Documentar en `docs/CUSTOM_MODULES.md`
- [ ] Ejemplo end-to-end

**Total Sprint 5:** 7-9 días

---

## 📊 Resumen Total

```
SPRINT 1: Limpieza              [1-2 días]    ████
SPRINT 2: MCP                   [7-10 días]   ████████████████
SPRINT 3: Multi-versión         [3-4 días]    ██████
SPRINT 4: Odoo Store            [9-13 días]   ██████████████████
SPRINT 5: Módulos Custom        [7-9 días]    ██████████████

Total: 27-38 días (~7-8 semanas)
```

---

## ✅ Quick Start - Empezar Hoy

### Paso 1: Configurar GitHub Secrets
Ve a tu repositorio en GitHub → Settings → Secrets and variables → Actions

Añade estos secrets:
- `DATABASE_URL` - Tu connection string de Neon
- `GH_TOKEN` - Tu GitHub Personal Access Token
- `OPENROUTER_API_KEY` - Tu API key de OpenRouter

### Paso 2: Probar GitHub Actions
```bash
# Ir a GitHub Actions → ETL Scheduler → Run workflow
```

### Paso 3: Auditar Documentación
```bash
cd docs
ls -lh *.md  # Ver tamaños
```

Revisar cada archivo marcado con ⚠️ en ROADMAP.md

### Paso 4: Crear branch para Sprint 1
```bash
git checkout -b sprint-1-cleanup
```

---

## 📞 Preguntas Frecuentes

### ¿Debo completar los sprints en orden?
**Recomendado:** Sí, especialmente Sprint 1 (limpieza)

**Flexible:** Sprints 2-5 se pueden hacer en diferente orden, pero MCP (Sprint 2) tiene mayor impacto en UX

### ¿Puedo saltar algún sprint?
- **Sprint 1:** NO - es crítico para calidad del proyecto
- **Sprint 2 (MCP):** Alta prioridad - mejora significativa UX
- **Sprint 3 (Multi-versión):** Media - amplía cobertura
- **Sprint 4 (Store):** Media - añade módulos comerciales
- **Sprint 5 (Custom):** Baja si no necesitas módulos propios

### ¿Qué sprint tiene mejor ROI?
1. **Sprint 2 (MCP)** - Mejor UX, búsqueda nativa
2. **Sprint 3 (Multi-versión)** - 2x módulos disponibles
3. **Sprint 4 (Store)** - Módulos comerciales
4. **Sprint 5 (Custom)** - Específico para empresas

---

## 🎯 Objetivos Finales

Al completar todos los sprints:

**Datos:**
- 2000-2500 módulos indexados
- 8 versiones (v12-v19)
- 3 fuentes (OCA, Store, Custom)

**Features:**
- MCP nativo en Claude
- Búsqueda multi-source
- Módulos privados

**Calidad:**
- Docs limpios y actualizados
- CI/CD funcionando
- Tests completos

---

**¿Listo para empezar?**

1. Lee el [ROADMAP completo](docs/ROADMAP.md)
2. Configura GitHub Secrets
3. Crea branch `sprint-1-cleanup`
4. ¡A trabajar! 🚀
