# 🎨 AI-OdooFinder - Branding & ASCII Art

Colección de logos y arte ASCII para usar en el proyecto.

---

## Logo Principal para GitHub

### Banner SVG (Recomendado para README)

El banner principal está en `docs/logo-banner.svg` - se ve perfecto en GitHub y es responsive.

**Uso en README.md:**
```markdown
![AI-OdooFinder Banner](docs/logo-banner.svg)
```

### Logo de Texto (Simple y Limpio)

Para GitHub, usa este formato limpio:

```markdown
<div align="center">

# 🤖 AI-OdooFinder 🔍

### AI-Powered Module Discovery for Odoo Developers

</div>
```

### Logo ASCII (Solo para Terminal/CLI)

⚠️ **Nota:** Este logo NO se ve bien en GitHub (usa fuente proporcional), pero es perfecto para terminal:

```
   ___    ____       ____       __            _______ __          __         
  / _ |  /  _/____  / __ \___  / /__  ____   / ____(_) /__  ____/ /__ _____
 / __ | _/ / /___/ / /_/ / _ \/ _ \ / __ \ / /_  / / / _ \/ __  / _ \\/ ___/
/ /_/ |/___/      / ____/ // / // // /_/ // __/ / / /  __/ /_/ /  __/ /    
\___/|_/         /_/    \___/\___/ \____//_/   /_/_/\___/\__,_/\___/_/     
                                                                             
         🔍 AI-Powered Module Discovery for Odoo Developers
```

---

## Logo Compacto

```
    _    ___        ___      _           ___ _         _
   /_\  |_ _|___   / _ \  __| |___  ___ | __(_)_ _  __| |___ _ _
  / _ \  | ||___| | (_) |/ _` / _ \/ _ \| _|| | ' \/ _` / -_) '_|
 /_/ \_\___|      \___/ \__,_\___/\___/|_| |_|_||_\__,_\___|_|
```

---

## 🎨 Colección de Diseños SVG (GitHub-Friendly)

### 1. Banner Principal (GitHub README)

**Archivo:** `docs/logo-banner.svg` ✅ Ya creado

Gradiente azul-morado con texto centrado. Perfecto para el encabezado del README.

**Uso en README.md:**
```markdown
![AI-OdooFinder Banner](docs/logo-banner.svg)
```

### 2. Logo Circular (Avatar/Icon)

Perfecto para usar como avatar de GitHub o favicon.

```svg
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="circleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#714B67;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <circle cx="100" cy="100" r="95" fill="url(#circleGrad)"/>
  <circle cx="100" cy="100" r="85" fill="none" stroke="#FFFFFF" stroke-width="3"/>
  <text x="100" y="95" font-size="60" text-anchor="middle">🤖</text>
  <text x="100" y="145" font-size="40" text-anchor="middle">🔍</text>
</svg>
```

### 3. Badge Horizontal (Status)

```svg
<svg width="200" height="40" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="badgeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#714B67;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <rect width="200" height="40" rx="20" fill="url(#badgeGrad)"/>
  <text x="25" y="28" font-size="20">🤖</text>
  <text x="50" y="27" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#FFFFFF">
    AI-Powered
  </text>
</svg>
```

### 4. Feature Card

```svg
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:0.9" />
      <stop offset="100%" style="stop-color:#714B67;stop-opacity:0.9" />
    </linearGradient>
  </defs>
  
  <rect width="300" height="200" rx="15" fill="url(#cardGrad)"/>
  <rect x="2" y="2" width="296" height="196" rx="13" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.3"/>
  <text x="150" y="80" font-size="50" text-anchor="middle">🔍</text>
  <text x="150" y="125" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#FFFFFF" text-anchor="middle">
    Smart Search
  </text>
  <text x="150" y="155" font-family="Arial, sans-serif" font-size="14" fill="#E5E7EB" text-anchor="middle">
    Find modules instantly
  </text>
</svg>
```

### 5. Loading Spinner (Animado)

```svg
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="loadGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#714B67;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <circle cx="50" cy="50" r="40" fill="none" stroke="url(#loadGrad)" stroke-width="6" stroke-dasharray="60 200" stroke-linecap="round">
    <animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="1.5s" repeatCount="indefinite"/>
  </circle>
  <text x="50" y="60" font-size="30" text-anchor="middle">🔍</text>
</svg>
```

### 6. Hero Background

```svg
<svg width="1200" height="400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="heroGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#7C3AED;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#714B67;stop-opacity:1" />
    </linearGradient>
    <pattern id="dots" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
      <circle cx="20" cy="20" r="2" fill="#FFFFFF" opacity="0.1"/>
    </pattern>
  </defs>
  
  <rect width="1200" height="400" fill="url(#heroGrad)"/>
  <rect width="1200" height="400" fill="url(#dots)"/>
  <circle cx="200" cy="100" r="120" fill="#FFFFFF" opacity="0.03"/>
  <circle cx="1000" cy="300" r="150" fill="#FFFFFF" opacity="0.03"/>
  <circle cx="600" cy="200" r="80" fill="#FFFFFF" opacity="0.05"/>
  
  <text x="600" y="180" font-family="Arial, sans-serif" font-size="64" font-weight="bold" fill="#FFFFFF" text-anchor="middle">
    AI-OdooFinder
  </text>
  <text x="600" y="240" font-family="Arial, sans-serif" font-size="28" fill="#E5E7EB" text-anchor="middle">
    🔍 AI-Powered Module Discovery
  </text>
</svg>
```

---

## 🎨 Cómo Usar Estos SVG

### Crear los Archivos:
```bash
# En tu proyecto
mkdir -p docs/images

# Copia cada SVG a un archivo
# Por ejemplo: docs/images/logo-circle.svg
```

### En README.md:
```markdown
<!-- Banner principal -->
![AI-OdooFinder](docs/logo-banner.svg)

<!-- Badge inline -->
![AI Powered](docs/images/badge-status.svg)

<!-- Feature cards -->
<div align="center">
  <img src="docs/images/feature-card.svg" width="300">
</div>
```

### Editar SVG:
1. **En VSCode:** Instala "SVG Preview" extension
2. **En Figma:** Import SVG → Edita visualmente
3. **Online:** Usa [svgeditor.io](https://svgeditor.io)

---

## 📐 Especificaciones de Diseño

### Colores del Proyecto
```
Primary Blue:    #3B82F6  ████
Purple:          #714B67  ████
Deep Purple:     #7C3AED  ████
White:           #FFFFFF  ████
Light Gray:      #E5E7EB  ████
Medium Gray:     #D1D5DB  ████
Dark Gray:       #111827  ████
```

### Dimensiones Estándar
```
GitHub Banner:     1280 x 320 px
Circle Logo:       200 x 200 px (o 512x512 para HD)
Badge:             200 x 40 px
Feature Card:      300 x 200 px
Loading Spinner:   100 x 100 px
Hero Section:      1200 x 400 px
Favicon:           32 x 32 px
```

### Gradientes CSS
```css
/* Horizontal */
background: linear-gradient(90deg, #3B82F6 0%, #714B67 100%);

/* Diagonal */
background: linear-gradient(135deg, #3B82F6 0%, #714B67 100%);

/* Triple color */
background: linear-gradient(135deg, #3B82F6 0%, #7C3AED 50%, #714B67 100%);
```

---

## Logo Minimalista

```
╔═══════════════════════════════════════════╗
║                                           ║
║     🤖  A I - O d o o F i n d e r  🔍   ║
║                                           ║
║   Find Odoo Modules with AI • Fast       ║
║                                           ║
╚═══════════════════════════════════════════╝
```

---

## Icono Terminal

```
  ____  _____
 / __ \|  ___|
/ / _` | |_
| | (_| |  _|
\ \__,_|_|
 \____/
```

---

## Banner de Bienvenida

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   █████╗ ██╗      ██████╗ ██████╗  ██████╗  ██████╗        ║
║  ██╔══██╗██║     ██╔═══██╗██╔══██╗██╔═══██╗██╔═══██╗       ║
║  ███████║██║     ██║   ██║██║  ██║██║   ██║██║   ██║       ║
║  ██╔══██║██║     ██║   ██║██║  ██║██║   ██║██║   ██║       ║
║  ██║  ██║██║     ╚██████╔╝██████╔╝╚██████╔╝╚██████╔╝       ║
║  ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═════╝  ╚═════╝  ╚═════╝        ║
║                                                              ║
║        ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗         ║
║        ██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗        ║
║        █████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝        ║
║        ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗        ║
║        ██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║        ║
║        ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝        ║
║                                                              ║
║              🤖 AI-Powered Odoo Module Search 🔍            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Iconos de Estado

### ✅ Success
```
  ✓  Search Complete
     Found 5 compatible modules
```

### ⚠️ Warning
```
  ⚠  No exact matches found
     Showing 3 similar results
```

### ❌ Error
```
  ✗  Connection Failed
     Please check your internet connection
```

### 🔄 Loading
```
  ⟳  Searching repositories...
     Please wait
```

---

## Separadores

### Separador Principal
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Separador Secundario
```
────────────────────────────────────────────────────────────
```

### Separador con Título
```
═══════════════════ Search Results ═══════════════════
```

---

## Cajas de Información

### Módulo Encontrado
```
┌─────────────────────────────────────────────────────────┐
│ 📦 sale_subscription                                    │
│ ⭐ Quality Score: 87/100                                │
│ 🔗 github.com/OCA/sale-workflow                        │
│ 📊 245 stars • Updated 2 days ago                      │
│ 🔗 Depends: sale, account                              │
└─────────────────────────────────────────────────────────┘
```

### Información del Sistema
```
╭─────────────────────────────────────────────────────────╮
│                  System Information                      │
├─────────────────────────────────────────────────────────┤
│  📦 Modules Indexed:  500+                              │
│  🏢 Repositories:     OCA (100% coverage)               │
│  ⚡ Response Time:    < 500ms                           │
│  🔍 Active Searches:  152 today                         │
╰─────────────────────────────────────────────────────────╯
```

---

## Pantalla de Inicio (Terminal)

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║      █████╗ ██╗      ██████╗ ██████╗  ██████╗  ██████╗         ║
║     ██╔══██╗██║     ██╔═══██╗██╔══██╗██╔═══██╗██╔═══██╗        ║
║     ███████║██║     ██║   ██║██║  ██║██║   ██║██║   ██║        ║
║     ██╔══██║██║     ██║   ██║██║  ██║██║   ██║██║   ██║        ║
║     ██║  ██║██║     ╚██████╔╝██████╔╝╚██████╔╝╚██████╔╝        ║
║     ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═════╝  ╚═════╝  ╚═════╝         ║
║                                                                  ║
║           ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗          ║
║           ██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗         ║
║           █████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝         ║
║           ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗         ║
║           ██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║         ║
║           ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝         ║
║                                                                  ║
║                  🤖 AI-Powered Module Search 🔍                 ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Version: 0.1.0                                                 ║
║  Status: 🟢 Online                                              ║
║  Database: ✓ Connected                                          ║
║  Modules: 500+ indexed                                          ║
║                                                                  ║
║  Commands:                                                      ║
║    search <query> <version>  - Search for modules              ║
║    health                    - Check system status             ║
║    stats                     - View statistics                 ║
║    help                      - Show this help                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

> _
```

---

## Resultado de Búsqueda (Terminal)

```
🔍 Search Results for "inventory management" • Odoo 17.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ⭐ Stock Warehouse Management (92/100) ✅ Highly Recommended
   ┌─────────────────────────────────────────────────────────┐
   │ 📦 stock_warehouse                                      │
   │ 🔗 github.com/OCA/stock-logistics-warehouse            │
   │ 📊 342 stars • Updated 1 day ago                       │
   │ 🔗 Depends: stock, purchase                            │
   │ 📝 Advanced warehouse management with multi-location   │
   │    support and inventory optimization                   │
   └─────────────────────────────────────────────────────────┘

2. Stock Inventory Adjustment (85/100)
   ┌─────────────────────────────────────────────────────────┐
   │ 📦 stock_inventory_adjustment                          │
   │ 🔗 github.com/OCA/stock-logistics-warehouse            │
   │ 📊 198 stars • Updated 5 days ago                      │
   │ 🔗 Depends: stock                                       │
   │ 📝 Simplified inventory adjustments and reconciliation  │
   └─────────────────────────────────────────────────────────┘

3. Stock Analytics (78/100)
   ┌─────────────────────────────────────────────────────────┐
   │ 📦 stock_analytics                                      │
   │ 🔗 github.com/OCA/stock-logistics-reporting            │
   │ 📊 156 stars • Updated 2 weeks ago                     │
   │ 🔗 Depends: stock, report                              │
   │ 📝 Comprehensive inventory analytics and reports       │
   └─────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Found 3 modules in 0.42s

> _
```

---

## Footer

```
─────────────────────────────────────────────────────────────
         Developed with ❤️ for the Odoo Community
              https://github.com/tu-usuario/ai-odoofinder
─────────────────────────────────────────────────────────────
```

---

## Paleta de Colores (para UI)

```
Primary Colors:
  - Main Blue:      #3B82F6  ████
  - Dark Blue:      #1E40AF  ████
  - Light Blue:     #DBEAFE  ████

Secondary Colors:
  - Odoo Purple:    #714B67  ████
  - Success Green:  #10B981  ████
  - Warning Yellow: #F59E0B  ████
  - Error Red:      #EF4444  ████

Neutral Colors:
  - Background:     #F9FAFB  ████
  - Text:           #111827  ████
  - Border:         #E5E7EB  ████
```

---

## Emojis del Proyecto

- 🔍 Búsqueda
- 🤖 IA / Inteligencia
- 📦 Módulos / Paquetes
- ⭐ Calidad / Rating
- 🔗 Enlaces / Dependencias
- 📊 Estadísticas / Analytics
- ⚡ Velocidad / Rendimiento
- 🏢 Repositorios / Organizaciones
- ✅ Éxito / Completado
- ⚠️ Advertencia
- ❌ Error
- 🔄 Cargando / Procesando
- 🚀 Lanzamiento / Inicio
- 💡 Ideas / Sugerencias
- 🎯 Objetivo / Target
- 🛠️ Herramientas / Configuración
- 📚 Documentación
- 🐛 Bugs / Errores

---

## Uso en Código

### Python (print al iniciar)
```python
LOGO = """
   ___    ____       ____       __            _______ __          __         
  / _ |  /  _/____  / __ \___  / /__  ____   / ____(_) /__  ____/ /__ _____
 / __ | _/ / /___/ / /_/ / _ \/ _ \ / __ \ / /_  / / / _ \/ __  / _ \\/ ___/
/ /_/ |/___/      / ____/ // / // // /_/ // __/ / / /  __/ /_/ /  __/ /    
\___/|_/         /_/    \___/\___/ \____//_/   /_/_/\___/\__,_/\___/_/     
                                                                             
         🔍 AI-Powered Module Discovery for Odoo Developers
"""

print(LOGO)
```

### Shell Script
```bash
echo "╔══════════════════════════════════════════════════╗"
echo "║    🤖 AI-OdooFinder - Starting...               ║"
echo "╚══════════════════════════════════════════════════╝"
```

---

<div align="center">

**Use estos elementos para dar identidad visual consistente al proyecto** 🎨

</div>
