# AI-OdooFinder Claude Skill

Esta skill permite a Claude buscar módulos de Odoo en repositorios de OCA usando búsqueda híbrida (SQL + semántica con embeddings).

## 📦 Instalación

### En Claude Web (claude.ai)

1. Ve a [claude.ai](https://claude.ai)
2. Haz clic en tu perfil (esquina superior derecha)
3. Selecciona "Settings" → "Skills"
4. Haz clic en "Add Custom Skill"
5. Sube el archivo `ai-odoofinder-skill.zip`
6. La skill estará disponible como "ai-odoofinder"

### En Claude Code (VSCode Extension)

La skill se puede usar directamente si está disponible en el sistema.

## 🎯 Diferencias Importantes entre Claude Web y Claude Code

### Claude Web (claude.ai)

**Limitación:** Claude Web NO puede hacer llamadas WebFetch a URLs arbitrarias por razones de seguridad.

**Flujo de trabajo:**

1. Pides buscar módulos de Odoo
2. Claude construye la URL y te la muestra
3. **TÚ haces clic en el enlace** y copias el JSON
4. Pegas el JSON en el chat
5. Claude formatea e interpreta los resultados

**Ejemplo:**

```
Usuario: "Busco módulos de suscripciones para Odoo 16"

Claude responde:
🔗 Haz clic aquí: https://ai-odoo-finder.onrender.com/search?query=...
📋 Copia el JSON y pégalo aquí

Usuario: [pega el JSON]

Claude: [interpreta y formatea los resultados]
```

### Claude Code (VSCode)

**Capacidad completa:** Claude Code SÍ puede usar WebFetch directamente.

**Flujo de trabajo:**

1. Pides buscar módulos de Odoo
2. Claude hace la búsqueda automáticamente
3. Te muestra los resultados formateados

## 🚀 Uso

### Búsqueda Simple

```
Necesito un módulo de inventario para Odoo 17
```

### Con Dependencias

```
Busco algo para Odoo 16 que maneje suscripciones y trabaje con ventas
```

### Especificando Versión

```
Módulo de reportes avanzados para contabilidad en 18.0
```

## ⏱️ Nota sobre Cold Start

La primera búsqueda puede tardar **50-60 segundos** si el servicio en Render estaba dormido (Free Tier). Las búsquedas subsiguientes son instantáneas.

## 📊 Estadísticas

- **Total módulos indexados:** 991
  - Odoo 16.0: 421 módulos
  - Odoo 17.0: 264 módulos
  - Odoo 18.0: 306 módulos

## 🔗 Enlaces

- **API Endpoint:** https://ai-odoo-finder.onrender.com/search
- **GitHub:** https://github.com/SantipBarber/ai-odoo-finder
- **Documentación Completa:** [Ver README principal](../README.md)

## 🐛 Solución de Problemas

### Error "No puedo acceder a la URL"

**En Claude Web:** Esto es normal. Sigue el flujo descrito arriba (Claude te da el enlace, tú copias el JSON).

**En Claude Code:** Verifica que el servicio esté corriendo en Render.

### La búsqueda tarda mucho

Si es la primera búsqueda del día, el servicio puede estar despertando (Free Tier). Espera 60 segundos y reintenta.

### No encuentro resultados

- Verifica que la versión sea correcta (16.0, 17.0, 18.0)
- Intenta con una descripción más general
- Revisa las dependencias especificadas

## 📞 Soporte

- **Issues:** https://github.com/SantipBarber/ai-odoo-finder/issues
- **Email:** [Tu email de contacto]
