---
name: observatorio-bacata-design
description: Sistema de diseño del Observatorio Bacatá (tokens, tipografía, paletas de datos, componentes y reglas de contenido). Úsalo para construir o revisar cualquier página, gráfico o componente del sitio, o para hacer prototipos con la marca.
user-invocable: true
---

El sistema de diseño vive en `docs/diseno/`. Empieza por `docs/diseno/README.md` y después revisa los demás archivos:

- `docs/diseno/design/DESIGN_SYSTEM.md`: reglas de contenido, fundamentos visuales e iconografía.
- `docs/diseno/design/tokens/*.css` y `docs/diseno/design/components/components.css`: CSS portable. Son la fuente de verdad de colores, tipografía y espaciado.
- `docs/diseno/design/components/**`: componentes React de referencia (`.jsx`, `.d.ts` y `.prompt.md`).
- `docs/diseno/screenshots/`: cómo se debe ver.

En código de producción (el sitio en `site/`), usa los tokens y las clases tal como están y sigue las reglas de contenido: tuteo, sin emoji ni signos de exclamación, fuente y fecha de corte junto a cada cifra, sin rojo ni verde de estado. Si haces prototipos o artefactos visuales, copia los recursos y genera HTML estático.

Si te invocan sin más contexto, pregunta qué se quiere construir y actúa como diseñador experto de la marca.
