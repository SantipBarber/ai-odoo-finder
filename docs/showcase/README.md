# AI-OdooFinder Showcase

Página de presentación del proyecto: **[santipbarber.github.io/ai-odoo-finder/showcase](https://santipbarber.github.io/ai-odoo-finder/showcase/)**

## Qué contiene

1. **Hero con demo**: preguntas de ejemplo que reproducen resultados reales del servidor público (`https://addon-finder.eticco.es`), capturados el 14 de octubre de 2026. El servidor no admite peticiones desde el navegador (sin CORS), así que la demo no consulta en vivo.
2. **Conectar**: configuración por cliente (Claude, Claude Code, ChatGPT, VS Code, Cursor, Windsurf, Zed y `mcp-remote` para el resto), con botón de copiar.
3. **Cómo busca**: los cuatro pasos de la búsqueda híbrida (consulta, semántica + texto completo, RRF, filtro por versión y confianza).
4. **Cómo se construyó**: las seis etapas del programa AI Expert (DevExpert) aplicadas al proyecto, con detalle desplegable.
5. **Hoy, en producción**: el servicio público en la infraestructura de Eticco.

## Detalles técnicos

- Un solo archivo `index.html`, sin dependencias ni build. Fuentes: Schibsted Grotesk y Martian Mono (Google Fonts).
- Español e inglés: los textos en español están en el HTML y los ingleses en el diccionario `I18N` del script. El idioma inicial sigue al navegador y se recuerda en `localStorage`.
- Tema claro/oscuro: sigue al sistema; el botón lo fija y se recuerda en `localStorage`.
- Respeta `prefers-reduced-motion`, navegación por teclado (pestañas de clientes con flechas) y funciona desde 320 px de ancho.

## Actualizar la demo

Los resultados están en la constante `DEMO` del script. Para refrescarlos, llama a `search_odoo_modules` en el servidor público con la misma `query` y `version` y copia módulo, nombre, puntuación, repositorio, estrellas y fecha de actualización. Actualiza también la fecha del pie de la demo.

## Probar en local

```bash
cd docs/showcase
python3 -m http.server 8000
# http://localhost:8000
```
