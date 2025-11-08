# 🤝 Guía de Contribución - AI-OdooFinder

¡Gracias por tu interés en contribuir a AI-OdooFinder! Este documento te guiará a través del proceso de contribución.

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo Puedo Contribuir?](#cómo-puedo-contribuir)
- [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Guías de Estilo](#guías-de-estilo)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Mejoras](#sugerir-mejoras)

---

## 📜 Código de Conducta

Este proyecto se adhiere a un código de conducta. Al participar, se espera que mantengas este código. Por favor reporta comportamientos inaceptables a [tu-email@ejemplo.com].

### Nuestros Estándares

**Comportamientos que contribuyen a crear un ambiente positivo:**
- ✅ Usar lenguaje acogedor e inclusivo
- ✅ Respetar diferentes puntos de vista y experiencias
- ✅ Aceptar críticas constructivas con gracia
- ✅ Enfocarse en lo que es mejor para la comunidad
- ✅ Mostrar empatía hacia otros miembros

**Comportamientos inaceptables:**
- ❌ Uso de lenguaje o imágenes sexualizadas
- ❌ Trolling, comentarios insultantes/despectivos
- ❌ Acoso público o privado
- ❌ Publicar información privada de otros sin permiso
- ❌ Otras conductas que puedan considerarse inapropiadas

---

## 🚀 ¿Cómo Puedo Contribuir?

### Tipos de Contribuciones

1. **🐛 Reportar Bugs**: Encuentra y reporta errores
2. **💡 Sugerir Features**: Propón nuevas funcionalidades
3. **📝 Mejorar Documentación**: Corrige typos, clarifica instrucciones
4. **💻 Código**: Implementa features, arregla bugs
5. **🧪 Tests**: Añade o mejora tests
6. **🎨 Diseño**: Mejora UI/UX
7. **🌍 Traducción**: Ayuda a internacionalizar el proyecto

---

## 🛠️ Configuración del Entorno de Desarrollo

### Prerrequisitos

- Python 3.10 o superior
- PostgreSQL 15+ con extensión pgVector
- Git
- Node.js 18+ (opcional, para frontend)

### Paso a Paso

1. **Fork el repositorio**
   ```bash
   # En GitHub, haz click en "Fork"
   ```

2. **Clona tu fork**
   ```bash
   git clone https://github.com/TU-USUARIO/ai-odoofinder.git
   cd ai-odoofinder
   ```

3. **Configura el upstream**
   ```bash
   git remote add upstream https://github.com/USUARIO-ORIGINAL/ai-odoofinder.git
   ```

4. **Crea un entorno virtual**
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

5. **Instala dependencias**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Dependencias de desarrollo
   ```

6. **Configura variables de entorno**
   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales
   ```

7. **Configura la base de datos**
   ```bash
   createdb ai_odoofinder
   psql ai_odoofinder -c "CREATE EXTENSION vector;"
   ```

8. **Ejecuta las migraciones**
   ```bash
   alembic upgrade head
   ```

9. **Ejecuta los tests**
   ```bash
   pytest
   ```

10. **Inicia el servidor de desarrollo**
    ```bash
    uvicorn app.main:app --reload
    ```

---

## 🔄 Proceso de Pull Request

### Antes de Empezar

1. **Busca issues existentes**: Verifica que tu cambio no esté ya en progreso
2. **Abre un issue primero**: Para cambios grandes, discute primero con el equipo
3. **Un PR por feature**: Mantén los cambios enfocados y atómicos

### Workflow

1. **Crea una rama**
   ```bash
   git checkout -b feature/nombre-descriptivo
   # o
   git checkout -b fix/nombre-del-bug
   ```

2. **Haz tus cambios**
   - Escribe código limpio y legible
   - Sigue las guías de estilo
   - Añade tests si es necesario
   - Actualiza documentación

3. **Commit tus cambios**
   ```bash
   git add .
   git commit -m "feat: descripción clara del cambio"
   ```
   
   **Formato de commits (Conventional Commits):**
   - `feat:` Nueva funcionalidad
   - `fix:` Corrección de bug
   - `docs:` Solo documentación
   - `style:` Formato (sin cambios de código)
   - `refactor:` Refactorización
   - `test:` Añadir tests
   - `chore:` Mantenimiento

4. **Sincroniza con upstream**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

5. **Ejecuta tests y linting**
   ```bash
   pytest
   black .
   flake8 .
   mypy .
   ```

6. **Push a tu fork**
   ```bash
   git push origin feature/nombre-descriptivo
   ```

7. **Abre un Pull Request**
   - Ve a GitHub y crea el PR
   - Usa el template de PR
   - Describe claramente qué cambia y por qué
   - Referencia issues relacionados (#123)

### Checklist del PR

Antes de enviar, verifica:

- [ ] Los tests pasan (`pytest`)
- [ ] El código sigue el estilo del proyecto (`black`, `flake8`)
- [ ] Documentación actualizada (si aplica)
- [ ] Tests nuevos para funcionalidades nuevas
- [ ] No hay conflictos con `main`
- [ ] El commit message sigue Conventional Commits
- [ ] El PR tiene una descripción clara

---

## 📝 Guías de Estilo

### Python

Seguimos **PEP 8** con algunas adaptaciones:

```python
# ✅ BIEN
def search_modules(query: str, version: str) -> List[Module]:
    """
    Busca módulos de Odoo.
    
    Args:
        query: Texto de búsqueda
        version: Versión de Odoo
        
    Returns:
        Lista de módulos encontrados
    """
    results = db.query(Module).filter(
        Module.version == version
    ).all()
    return results

# ❌ MAL
def searchModules(query,version):
    results=db.query(Module).filter(Module.version==version).all()
    return results
```

**Herramientas:**
- **Black**: Formateo automático
- **Flake8**: Linting
- **MyPy**: Type checking
- **isort**: Ordenar imports

```bash
# Formatear código
black .

# Linting
flake8 .

# Type checking
mypy app/
```

### Documentación

- Usa docstrings estilo Google
- Comenta código complejo
- Actualiza README.md si cambias funcionalidad principal
- Mantén ejemplos actualizados

### Tests

```python
# tests/test_search.py
import pytest
from app.services.search_service import SearchService

def test_search_by_version():
    """Debe retornar solo módulos de la versión especificada"""
    service = SearchService(db)
    results = service.search(query="test", version="17.0")
    
    assert len(results) > 0
    assert all(m.version == "17.0" for m in results)

def test_search_with_invalid_version():
    """Debe retornar lista vacía con versión inválida"""
    service = SearchService(db)
    results = service.search(query="test", version="99.0")
    
    assert len(results) == 0
```

---

## 🐛 Reportar Bugs

### Antes de Reportar

1. **Verifica que no esté ya reportado**: Busca en los issues
2. **Usa la última versión**: Actualiza y verifica si persiste
3. **Recopila información**: Logs, pasos para reproducir

### Template de Bug Report

```markdown
## Descripción del Bug
[Descripción clara y concisa del problema]

## Pasos para Reproducir
1. Ve a '...'
2. Haz click en '...'
3. Scroll hasta '...'
4. Observa el error

## Comportamiento Esperado
[Qué debería pasar]

## Comportamiento Actual
[Qué está pasando]

## Screenshots
[Si aplica, añade screenshots]

## Entorno
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.10.5]
- Versión: [e.g. 0.1.0]

## Logs
```
[Pega los logs relevantes aquí]
```

## Contexto Adicional
[Cualquier otra información relevante]
```

---

## 💡 Sugerir Mejoras

### Template de Feature Request

```markdown
## Resumen
[Descripción breve de la funcionalidad]

## Motivación
**¿Qué problema soluciona?**
[Describe el problema actual]

**¿Por qué es importante?**
[Beneficios para los usuarios]

## Propuesta de Solución
[Describe cómo debería funcionar]

## Alternativas Consideradas
[Otras formas de resolver el problema]

## Impacto
- **Usuarios afectados**: [cuántos]
- **Complejidad**: [baja/media/alta]
- **Breaking changes**: [sí/no]

## Mockups/Ejemplos
[Si aplica, añade diseños o código de ejemplo]
```

---

## 🏆 Reconocimientos

Los contribuidores serán:
- Listados en README.md
- Mencionados en release notes
- Incluidos en el archivo CONTRIBUTORS.md

---

## 📞 ¿Necesitas Ayuda?

- **Discord**: [Link a servidor](https://discord.gg/tu-server)
- **GitHub Discussions**: [Link](https://github.com/tu-usuario/ai-odoofinder/discussions)
- **Email**: tu-email@ejemplo.com

---

## 📚 Recursos Adicionales

- [Documentación Técnica](docs/TECHNICAL_GUIDE.md)
- [API Reference](docs/API.md)
- [Arquitectura del Sistema](docs/ARCHITECTURE.md)

---

<div align="center">

**¡Gracias por contribuir a AI-OdooFinder! 🎉**

Tu trabajo hace que este proyecto sea mejor para todos.

</div>
