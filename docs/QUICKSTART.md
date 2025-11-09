# ⚡ Quick Start - AI-OdooFinder

<div align="center">

![AI-OdooFinder Banner](logo-banner.svg)

</div>

Esta guía te llevará de 0 a tu primera búsqueda en **menos de 10 minutos**. ⏱️

---

## 🎯 Lo que Construirás

Al final de esta guía tendrás:
- ✅ Backend API corriendo en `http://localhost:8000`
- ✅ Base de datos con ~50 módulos de OCA indexados
- ✅ Capacidad de buscar módulos por versión y funcionalidad
- ✅ Claude Skill configurada (opcional)

---

## 🔧 Requisitos Previos

### Cuentas Necesarias
1. **[Neon](https://console.neon.tech/signup)** - PostgreSQL serverless (Free tier)
2. **[OpenRouter](https://openrouter.ai/keys)** - Embeddings con Qwen3 (~$10 crédito inicial)
3. **[GitHub](https://github.com/settings/tokens)** - Token personal (scope: `public_repo`)
4. **[Render](https://render.com)** - Hosting API (Free tier para empezar)

### Software Local
```bash
# Python 3.10+
python --version

# Git
git --version

# Opcional: Docker (para desarrollo local)
docker --version
```

### Variables de Entorno
Crear archivo `.env` en raíz:
```bash
# Neon Database
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/ai_odoofinder?sslmode=require

# OpenRouter API
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxx

# GitHub API
GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Opcional: Desarrollo local
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## 🚀 Instalación en 5 Pasos

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/ai-odoofinder.git
cd ai-odoofinder
```

### Paso 2: Configurar Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 3: Configurar Base de Datos

```bash
# Crear base de datos
createdb ai_odoofinder

# Instalar extensión pgVector
psql ai_odoofinder -c "CREATE EXTENSION vector;"

# Verificar
psql ai_odoofinder -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Paso 4: Configurar Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar con tus credenciales
nano .env  # o usa tu editor favorito
```

**Mínimo necesario para MVP:**
```env
# .env
OPENAI_API_KEY=sk-tu-api-key-aqui
GITHUB_TOKEN=ghp_tu-token-aqui
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_odoofinder
```

> 💡 **Cómo obtener las API keys:**
> - **OpenAI**: https://platform.openai.com/api-keys
> - **GitHub Token**: https://github.com/settings/tokens (scope: `public_repo`)

### Paso 5: Cargar Datos Iniciales

```bash
# Ejecutar ETL (toma ~5-10 minutos para 50 módulos)
python scripts/etl_oca_modules.py

# Verificar que se cargaron datos
psql ai_odoofinder -c "SELECT COUNT(*) FROM odoo_modules;"
```

---

## ✅ Verificación

### 1. Iniciar el Servidor

```bash
uvicorn app.main:app --reload
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 2. Probar el Health Check

Abre tu navegador en: http://localhost:8000/health

Deberías ver:
```json
{
  "status": "healthy"
}
```

### 3. Probar la API de Búsqueda

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "gestión de inventario",
    "version": "17.0",
    "limit": 3
  }'
```

**Respuesta esperada:**
```json
[
  {
    "name": "Stock Module Name",
    "technical_name": "stock_module",
    "version": "17.0",
    "description": "...",
    "similarity_score": 0.85,
    "quality_score": 78.5
  }
]
```

### 4. Explorar la Documentación Interactiva

Visita: http://localhost:8000/docs

Aquí puedes:
- Ver todos los endpoints disponibles
- Probar la API directamente desde el navegador
- Ver esquemas de request/response

---

## 🎨 Bonus: Configurar Claude Skill (Opcional)

### 1. Crear un Proyecto en Claude

1. Ve a [claude.ai](https://claude.ai)
2. Crea un nuevo proyecto: "AI-OdooFinder"

### 2. Añadir la Skill

1. En el proyecto, ve a "Project Knowledge"
2. Crea un nuevo archivo "SKILL.md"
3. Copia el contenido de `claude-skill/SKILL.md`

### 3. Probar

Pregunta a Claude:
```
"Necesito un módulo para Odoo 17 que gestione proyectos con timesheet"
```

Claude debería automáticamente llamar a tu API local (asegúrate de que esté corriendo).

---

## 🐛 Solución de Problemas Comunes

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Solución:**
```bash
# Asegúrate de que el venv esté activado
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "psycopg2.OperationalError: could not connect to server"

**Solución:**
```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql

# Si no está corriendo
sudo systemctl start postgresql
```

### Error: "pgvector extension not found"

**Solución:**
```bash
# Instalar pgvector
# Ubuntu/Debian
sudo apt install postgresql-15-pgvector

# Mac (Homebrew)
brew install pgvector

# Luego en psql
psql ai_odoofinder -c "CREATE EXTENSION vector;"
```

### La búsqueda no retorna resultados

**Solución:**
```bash
# Verificar que hay datos
psql ai_odoofinder -c "SELECT COUNT(*) FROM odoo_modules;"

# Si retorna 0, ejecutar ETL
python scripts/etl_oca_modules.py
```

### Error de rate limit de GitHub

**Solución:**
```bash
# Verifica que tu token esté correctamente configurado en .env
echo $GITHUB_TOKEN

# Espera unos minutos (GitHub tiene rate limits)
# O crea un nuevo token con permisos correctos
```

---

## 📚 Siguientes Pasos

Ahora que tienes AI-OdooFinder corriendo:

1. **📖 Lee la documentación técnica**: [docs/TECHNICAL_GUIDE.md](docs/TECHNICAL_GUIDE.md)
2. **🧪 Ejecuta los tests**: `pytest backend/tests/`
3. **🎨 Personaliza la búsqueda**: Modifica `backend/app/services/search_service.py`
4. **📊 Añade más repositorios**: Edita `TARGET_REPOS` en `.env`
5. **🚀 Contribuye**: Lee [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🎓 Tutoriales Recomendados

### Tutorial 1: Tu Primera Búsqueda Personalizada
Modifica el scoring para priorizar módulos con más estrellas.

### Tutorial 2: Añadir Filtros Personalizados
Aprende a filtrar por autor o licencia.

### Tutorial 3: Integrar con tu IDE
Usa la API desde VS Code o PyCharm.

### Tutorial 4: Deploy en Producción
Guía paso a paso para subir a Render o Railway.

---

## 💬 ¿Necesitas Ayuda?

- 📖 **Docs completas**: [docs/](docs/)
- 💬 **Discord**: [Únete](https://discord.gg/tu-server)
- 🐛 **Issues**: [GitHub Issues](https://github.com/tu-usuario/ai-odoofinder/issues)
- 📧 **Email**: tu-email@ejemplo.com

---

## ⏱️ Tiempo Total

- ⚡ Setup básico: **5-10 minutos**
- 🔄 ETL inicial: **5-10 minutos**
- ✅ Primera búsqueda: **2 minutos**

**Total: ~15-20 minutos** de 0 a funcionando 🎉

---

<div align="center">

![AI-OdooFinder Banner](logo-banner.svg)

**¡Felicitaciones! Ya tienes AI-OdooFinder funcionando! 🎉**

Ahora empieza a buscar módulos como un pro 🚀

</div>
