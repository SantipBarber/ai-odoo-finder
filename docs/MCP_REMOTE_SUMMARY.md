# 📋 Resumen Ejecutivo - MCP Remoto en Render

**Fecha:** 15 Noviembre 2025
**Decisión:** Cambio de arquitectura de MCP local (STDIO) a **MCP Remoto (HTTP/SSE)**

---

## 🎯 Cambio Principal

### Antes (Diseño Inicial)
- Servidor MCP **local** en cada máquina
- Transporte: STDIO
- Instalación: `uv run mcp install`
- Usuarios necesitan clonar repo

### Ahora (Diseño Actualizado) ✅
- Servidor MCP **remoto** en Render.com
- Transporte: HTTP/SSE
- Instalación: Agregar URL en Claude Web (Settings → Integrations)
- **Cero instalación local**

---

## 🏗️ Nueva Arquitectura

```
Claude Web/Desktop
       ↓ HTTPS (Conector Personalizado)
https://ai-odoo-finder.onrender.com/mcp
       ↓ import local (mismo proceso)
SearchService (backend/app/services)
       ↓ PostgreSQL
Neon Database
```

### Ventajas Clave

1. **Cero fricción para usuarios**
   - No necesitan instalar nada
   - Solo configuran URL una vez en Claude

2. **Un solo deployment**
   - MCP y API en el mismo proceso de Render
   - Reduce costos (1 instancia en lugar de 2)
   - Cero latencia entre MCP y API (imports locales)

3. **Mantenimiento centralizado**
   - Actualizaciones benefician a todos automáticamente
   - No need para que usuarios actualicen localmente

4. **Escalabilidad**
   - Render escala automáticamente
   - Todos los usuarios comparten la misma infra robusta

---

## 🛠️ Cambios de Implementación

### 1. Stack Tecnológico

| Componente | Antes | Ahora |
|------------|-------|-------|
| **SDK** | `mcp[cli]` | `fastmcp` |
| **Transporte** | STDIO | HTTP/SSE |
| **Ubicación** | Local (cada usuario) | Remoto (Render) |
| **Integración** | Standalone script | Integrado con FastAPI |
| **Deployment** | No requerido | Junto con API |

### 2. Estructura de Archivos

**Antes:**
```
ai-odoo-finder/
├── mcp-server/           # ← Servidor separado
│   ├── src/
│   │   └── ai_odoofinder_mcp/
│   │       └── server.py
│   └── pyproject.toml
└── backend/              # ← API
    └── app/
        └── main.py
```

**Ahora:**
```
ai-odoo-finder/
└── backend/
    └── app/
        ├── main.py              # ← API + MCP juntos
        ├── mcp_tools.py         # ← Tools de MCP (NUEVO)
        └── services/
            └── search_service.py
```

### 3. Código Principal

**Antes (MCP local standalone):**
```python
# mcp-server/src/ai_odoofinder_mcp/server.py
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("ai-odoofinder")

@mcp.tool()
async def search_odoo_modules(...):
    # Hace HTTP request a API en Render
    response = await http_client.post(
        "https://ai-odoo-finder.onrender.com/search",
        json={...}
    )
    return format_results(response.json())

if __name__ == "__main__":
    mcp.run(transport='stdio')  # ← STDIO
```

**Ahora (MCP integrado en Render):**
```python
# backend/app/main.py
from fastapi import FastAPI
from fastmcp import FastMCP
from .services.search_service import SearchService

app = FastAPI()
mcp = FastMCP.from_fastapi(app=app)  # ← Integrado

@mcp.tool()
async def search_odoo_modules(query: str, version: str, ...):
    # Llama DIRECTAMENTE al servicio (NO HTTP)
    service = SearchService(db_session)
    results = await service.search(query, version, ...)
    return format_results(results)

# FastMCP automáticamente expone en /mcp con HTTP/SSE
```

---

## 📝 Configuración para Usuarios

### Antes (Local)

**Paso 1:** Clonar repo
```bash
git clone https://github.com/SantipBarber/ai-odoo-finder.git
cd ai-odoo-finder/mcp-server
```

**Paso 2:** Instalar
```bash
uv run mcp install src/ai_odoofinder_mcp/server.py
```

**Paso 3:** Reiniciar Claude Desktop

### Ahora (Remoto) ✅

**Paso 1:** Ir a Claude Web → Settings → Integrations

**Paso 2:** Agregar Conector Personalizado
- **Nombre:** AI-OdooFinder
- **URL:** `https://ai-odoo-finder.onrender.com/mcp`
- **OAuth:** (dejar vacío por ahora)

**Paso 3:** ¡Listo! Ya pueden buscar módulos

---

## 🚀 Plan de Implementación Actualizado

### Fase 1: Implementación Core (2-3 días)

#### Día 1: Integrar FastMCP
- [x] Instalar `fastmcp` en requirements.txt
- [ ] Actualizar `backend/app/main.py`
  - Crear instancia FastMCP con `FastMCP.from_fastapi(app)`
  - Configurar para HTTP/SSE
- [ ] Crear `backend/app/mcp_tools.py`
  - Tool `search_odoo_modules`
  - Formateo de respuestas

#### Día 2: Testing Local
- [ ] Levantar servidor localmente
- [ ] Verificar endpoint `/mcp` responde
- [ ] Probar tool con cliente MCP de prueba
- [ ] Testing con `fastmcp dev`

#### Día 3: Deploy y Testing
- [ ] Deploy a Render
- [ ] Configurar en Claude Web (conector personalizado)
- [ ] Testing funcional end-to-end
- [ ] Refinamiento de mensajes

### Fase 2: Documentación (1 día)

- [ ] Crear guía de usuario ([MCP_USER_GUIDE.md](MCP_USER_GUIDE.md))
- [ ] Actualizar README principal
- [ ] Screenshots de configuración
- [ ] Video tutorial (opcional)

---

## ⚠️ Consideraciones Importantes

### 1. Autenticación

**MVP (Sin OAuth):**
- Servidor abierto públicamente
- Solo rate limiting básico
- Aceptable para MVP/beta

**Futuro (Con OAuth):**
- OAuth 2.0 opcional para usuarios premium
- API keys para control de uso
- Rate limiting por usuario

### 2. CORS

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://claude.ai",      # Claude Web
        "https://claude.com"      # Claude Web (alt)
    ],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/mcp")
@limiter.limit("10/minute")  # 10 requests por minuto por IP
async def mcp_endpoint(...):
    ...
```

---

## 📊 Comparación de Costos

| Aspecto | MCP Local | MCP Remoto |
|---------|-----------|------------|
| **Infraestructura** | $0 (corre en PC usuario) | $0 (mismo Render actual) |
| **Desarrollo** | ~5 días | ~3 días |
| **Mantenimiento** | Alto (usuarios deben actualizar) | Bajo (auto-update) |
| **UX** | Media (requiere instalación) | Excelente (solo URL) |
| **Escalabilidad** | N/A (cada usuario su servidor) | Alta (Render autoscale) |

**Conclusión:** MCP Remoto es superior en todos los aspectos excepto privacidad (aunque no aplica para este caso de uso público).

---

## ✅ Checklist de Migración

### Código
- [ ] Instalar `fastmcp` en requirements.txt
- [ ] Modificar `backend/app/main.py` para integrar FastMCP
- [ ] Crear `backend/app/mcp_tools.py` con tools
- [ ] Configurar CORS para Claude Web
- [ ] Agregar rate limiting básico

### Testing
- [ ] Probar localmente con FastMCP dev mode
- [ ] Deploy a Render staging (si existe)
- [ ] Configurar en Claude Web
- [ ] Testing funcional:
  - [ ] Búsqueda simple
  - [ ] Búsqueda con dependencias
  - [ ] Error handling
  - [ ] Performance

### Documentación
- [ ] Actualizar [MCP_DESIGN.md](MCP_DESIGN.md) ✅ DONE
- [ ] Crear [MCP_USER_GUIDE.md](MCP_USER_GUIDE.md)
- [ ] Actualizar README.md con instrucciones
- [ ] Screenshots de configuración

### Deploy
- [ ] Deploy a producción (Render)
- [ ] Verificar `/mcp` endpoint accesible
- [ ] Compartir URL con beta testers
- [ ] Monitorear logs y errores

---

## 🎉 Beneficios del Cambio

1. **Mejor UX:** Usuarios solo pegan URL, no instalan nada
2. **Más simple:** Una sola codebase, un solo deployment
3. **Más rápido:** Sin HTTP entre MCP y API (imports locales)
4. **Más barato:** Una instancia en lugar de dos
5. **Mejor mantenimiento:** Updates centralizados

---

## 🔗 Referencias

- [FastMCP Documentation](https://gofastmcp.com)
- [MCP HTTP/SSE Transport](https://modelcontextprotocol.io/docs/concepts/transports)
- [Claude Web Custom Connectors](https://claude.ai) (Settings → Integrations)
- [Guía de Implementación FastAPI + SSE](https://www.ragie.ai/blog/building-a-server-sent-events-sse-mcp-server-with-fastapi)

---

**Próximo paso:** Implementar la integración FastMCP en `backend/app/main.py`
