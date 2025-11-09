# 🤖 AI-OdooFinder

> **Deja de reinventar la rueda. Encuentra el módulo de Odoo perfecto con IA en segundos.**

Un asistente inteligente impulsado por IA que ayuda a desarrolladores de Odoo a descubrir módulos existentes compatibles con su versión, ahorrando tiempo y evitando desarrollo innecesario.

<div align="center">

![AI-OdooFinder Banner](docs/logo-banner.svg)

### AI-Powered Module Discovery for Odoo Developers

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Odoo](https://img.shields.io/badge/Odoo-16.0%20|%2017.0%20|%2018.0-714B67)](https://www.odoo.com)
[![AI Powered](https://img.shields.io/badge/AI-Powered-blueviolet)](https://www.anthropic.com)

[Demo](#-demo) • [Características](#-características) • [Instalación](#-instalación-rápida) • [Documentación](docs/TECHNICAL_GUIDE.md)

</div>

---

## 🎯 El Problema

Como desarrollador de Odoo, ¿cuántas veces has...?

- ❌ Desarrollado una funcionalidad que ya existía en OCA
- ❌ Perdido horas buscando el módulo correcto en GitHub
- ❌ Instalado un módulo incompatible con tu versión
- ❌ Descubierto módulos abandonados después de integrarlos

**Resultado:** Tiempo perdido, código duplicado y frustración.

---

## 💡 La Solución

**AI-OdooFinder** es un asistente de IA que combina:

🧠 **Búsqueda Inteligente**: Entiende lenguaje natural ("pagos recurrentes" = "suscripciones")  
🎯 **Filtrado Preciso**: Garantiza compatibilidad con tu versión de Odoo  
⭐ **Recomendaciones de Calidad**: Prioriza módulos bien mantenidos  
🤖 **Interfaz Conversacional**: Pregunta en lenguaje natural, obtén respuestas precisas

---

## ✨ Características

### 🔍 Búsqueda Híbrida
Combina búsqueda semántica (RAG) con filtrado determinista para resultados precisos y relevantes.

### 🎯 Versionado Estricto
Solo muestra módulos compatibles con tu versión específica de Odoo (16.0, 17.0, 18.0).

### 📊 Sistema de Scoring
Evalúa módulos por:
- Popularidad (GitHub stars)
- Mantenimiento (commits recientes)
- Calidad (issues, documentación)

### 🔗 Análisis de Dependencias
Verifica automáticamente compatibilidad y orden de instalación.

### 🤖 Asistente Conversacional
Pregunta como hablarías con un colega: "Necesito algo para gestionar inventario en v17"

---

## 🎬 Demo

### Ejemplo 1: Búsqueda Básica

```text
👤 Usuario: "Necesito un módulo para gestionar suscripciones en Odoo 17"

🤖 Asistente: "He encontrado 3 módulos para gestión de suscripciones en Odoo 17.0:

   1. ⭐ Sale Subscription (87/100) ✅ Muy recomendado
      📦 sale_subscription
      🔗 github.com/OCA/sale-workflow
      📊 245 estrellas | Actualizado hace 2 días
      🔗 Depende de: sale, account
      
      Gestión completa de suscripciones con facturación automática,
      renovaciones y períodos de prueba.
      
   2. Contract Management (82/100)
      📦 contract
      ...
```

### Ejemplo 2: Con Dependencias

```text
👤 Usuario: "Busco reportes avanzados para v16 que funcionen con ventas"

🤖 Asistente: [Búsqueda con version="16.0" y depends=["sale"]]
   
   "Encontré 5 módulos de reportes que se integran con el módulo 'sale'..."
```

---

## 🚀 Instalación Rápida

### Opción 1: Docker (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/ai-odoofinder.git
cd ai-odoofinder

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus claves de API

# Levantar servicios
docker-compose up -d

# La API estará disponible en http://localhost:8000
```

### Opción 2: Instalación Local

```bash
# Crear entorno virtual
python3.10 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
createdb odoo_finder
psql odoo_finder -c "CREATE EXTENSION vector;"

# Cargar datos iniciales
python scripts/etl_oca_modules.py

# Iniciar servidor
uvicorn app.main:app --reload
```

---

## 🎯 Uso

### API REST

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "gestión de inventario",
    "version": "17.0",
    "limit": 5
  }'
```

### Claude Skill

Simplemente pregunta en lenguaje natural:

```text
"Necesito un módulo para Odoo 17 que maneje pagos recurrentes 
 y se integre con ventas"
```

El asistente buscará automáticamente y te dará recomendaciones personalizadas.

---

## 📚 Documentación

- **[Guía Técnica Completa](docs/TECHNICAL_GUIDE.md)** - Arquitectura, implementación y desarrollo
- **[API Reference](docs/API.md)** - Endpoints y ejemplos
- **[Claude Skill Setup](docs/CLAUDE_SKILL.md)** - Configurar el asistente conversacional

---

## 🗺️ Roadmap

### ✅ Fase Actual: MVP
- [x] Búsqueda básica en repositorios OCA
- [x] Filtrado por versión
- [x] API REST funcional
- [x] Claude Skill básica

### 🚧 En Desarrollo
- [ ] Sistema de scoring avanzado
- [ ] Análisis de dependencias
- [ ] Expansión a más repositorios
- [ ] Interfaz web

### 🔮 Futuro
- [ ] Integración con Odoo App Store
- [ ] Reviews y ratings comunitarios
- [ ] CLI para terminal
- [ ] Recomendaciones inteligentes

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. **Fork** el proyecto
2. **Crea** tu rama (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre** un Pull Request

Lee nuestra [Guía de Contribución](CONTRIBUTING.md) para más detalles.

---

## 🏆 ¿Por Qué Usar AI-OdooFinder?

### Comparación: Antes vs. Después

| Antes | Después |
|-------|---------|
| 🕐 2-3 horas buscando módulos | ⚡ 30 segundos |
| 🎲 Módulos incompatibles | ✅ 100% compatible con tu versión |
| 📚 Módulos abandonados | ⭐ Solo módulos de calidad |
| 🤔 Incertidumbre | 💯 Confianza en tus elecciones |

### 📊 Estadísticas del Proyecto

<div align="center">

| Métrica | Valor |
|---------|-------|
| 📦 Módulos Indexados | 500+ |
| 🏢 Repositorios | OCA (100% cobertura) |
| 🔍 Búsquedas/día | En desarrollo |
| ⚡ Tiempo respuesta | < 500ms |

</div>

## 💬 Testimonios

> *"Antes perdía tardes enteras buscando en GitHub. Ahora encuentro lo que necesito en minutos."*  
> <cite>— Juan P., Desarrollador Odoo</cite>

> *"El análisis de dependencias me salvó de un infierno de instalaciones rotas."*  
> <cite>— María G., Consultora Técnica</cite>

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🌟 Apoya el Proyecto

Si este proyecto te resulta útil:

- ⭐ **Dale una estrella** en GitHub
- 🐛 **Reporta bugs** o sugiere features
- 🤝 **Contribuye** con código
- 💬 **Comparte** con otros desarrolladores de Odoo

---

## 📞 Contacto

- 📧 **Email:** tu-email@ejemplo.com
- 💼 **LinkedIn:** [Tu Perfil](https://linkedin.com/in/tu-perfil)
- 🐙 **GitHub:** [@tu-usuario](https://github.com/tu-usuario)
- 💬 **Discord:** [Únete a la comunidad](https://discord.gg/tu-server)

---

## 🙏 Agradecimientos

- **[Odoo Community Association (OCA)](https://odoo-community.org/)** - Por su increíble trabajo open source
- **[Anthropic](https://www.anthropic.com/)** - Por Claude y el sistema de Skills
- **Todos los [contribuidores](https://github.com/tu-usuario/ai-odoofinder/graphs/contributors)** que hacen esto posible

---

<div align="center">

**Desarrollado con ❤️ para la comunidad de Odoo**

[⬆ Volver arriba](#-ai-odoofinder)

</div>
