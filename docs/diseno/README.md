# Handoff: Observatorio Bacatá — sistema de diseño + portada

## Overview
Observatorio Bacatá es un sitio cívico y gratuito que muestra datos abiertos de Bogotá por localidad a vecinos, periodistas y estudiantes, sobre todo desde el celular. *Bacatá* es el nombre muisca de Bogotá. Tono: confiable, sereno y cercano; nada gubernamental ni alarmista.

Este paquete contiene:
1. **El sistema de diseño**: tokens CSS, 4 componentes (tarjeta de indicador, leyenda de mapa, selector de localidad, aviso de datos retrasados) y las reglas de contenido.
2. **La portada** (RF-01 buscar localidad, RF-02 ver indicadores de ciudad), en móvil 360 px y escritorio 1280 px.
3. **La ficha de localidad móvil** (UI kit de referencia).

## About the Design Files
Los archivos de `design/` son **referencias de diseño hechas en HTML**: prototipos que muestran el aspecto y el comportamiento esperados, **no código de producción para copiar tal cual**. La tarea es **recrear estos diseños en el entorno del código destino** (React, Vue, Astro, etc.) con sus patrones y librerías. Si aún no hay proyecto, elige el framework más adecuado: sugerimos uno orientado a contenido estático con hidratación ligera (p. ej. Astro o Next.js con SSG), porque el público entra desde celulares con datos móviles.

Los tokens (`design/tokens/*.css`) y las clases de componentes (`design/components/components.css`) **sí pueden portarse casi tal cual**: son CSS plano con custom properties.

Para ver los prototipos: sirve la carpeta `design/` con un servidor local (`npx serve design`) y abre `Portada.dc.html` o `ui_kits/movil/index.html`. `Portada.dc.html` necesita `support.js` a su lado (runtime del prototipo; no forma parte del producto).

## Fidelity
**Alta fidelidad (hifi).** Colores, tipografía, espaciado, textos e interacciones son finales. Recréalos al píxel. Las **cifras son de ejemplo** (PM2.5 = 18 µg/m³, valores por localidad) y deben venir de datos reales.

## Screens / Views

### 1. Portada — móvil 360 px (`screenshots/01-portada-movil-360.png`)
- **Propósito:** en 30 segundos, un vecino sin formación técnica encuentra su localidad o ve cómo está la ciudad.
- **Layout:** una columna. Margen lateral 18.4px (`--page-gutter`). Espacio entre bloques de `main` 27.6px (`--space-6`); `main` padding 18.4px arriba, 36.8px abajo.
- **Cabecera** (`.nav`): padding 14px 18.4px, línea inferior hairline. Marca: "OBSERVATORIO" (Lora 10px, tracking .2em, versalitas, #7d5411) sobre "Bacatá" (Cormorant Garamond 400, 24px, line-height 1). Enlace "Metodología" a la derecha, 14px, área táctil 44px.
- **Titular:** "Los datos de tu barrio, claros y gratis" — Cormorant 400, 30px, line-height 1.08, `text-wrap: pretty`.
- **Buscador:** label "Busca tu localidad" (14px, #5b5853). Control `.loc-control`: alto 48px, borde 1px #8a8680, radio 4px, icono lupa (Lucide `search`, 18px, #7d5411) a 14px del borde izquierdo; input 16px (evita el zoom de iOS), padding-left 44px, placeholder "Ej.: Kennedy, Suba…". Hover: borde #b68235. Focus: outline 2px #b68235, offset 2px.
- **Sugerencias** (aparecen al escribir): lista con borde hairline, radio 4px, `--shadow-md`. Filas de 48px, padding 0 14px: nombre (16px) a la izquierda y "Localidad 08" (12px, #5b5853, cifras tabulares) a la derecha. Hover: fondo #fff3e4. Máximo 5 resultados. Sin coincidencias: "No encontramos esa localidad. Prueba con otro nombre." (14px, #5b5853).
- **Sección "Toda Bogotá":** encabezado h2 Cormorant 600 22px + "4 temas" (12px) a la derecha, con línea hairline debajo (padding-bottom 6px). Tarjetas separadas 13.8px.
  - **Aire (con dato)** — `.ind`: kicker "AIRE" con icono Lucide `wind` 14px; título "Partículas finas en el aire"; valor "18" (Cormorant 400, 48px, tabular) + "µg/m³ de PM2.5" (14px, #5b5853); frase "Promedio de la ciudad. Cuanto más bajo, más limpio el aire." (14px, #201f1d); pie "Fuente: **RMCAB** · Corte: 24 sep 2026" (12px).
  - **Movilidad / Seguridad / Costo de vida (próximamente)** — fila compacta: `.ind[data-state="soon"]` (borde punteado), flex-direction row, padding 13.8px 18.4px. Icono Lucide (`route`, `shield`, `wallet`) en #5b5853 · kicker gris + subtítulo 14px ("Tiempos de viaje", "Convivencia y seguridad", "Precios del hogar") · pastilla `.ind-soon` "Próximamente" (12px, borde 1px #8a8680, radio 2px).
- **Acceso al mapa:** enlace-bloque con borde 1px #b68235, radio 4px, padding 18.4px. Icono Lucide `map` + "Ver el mapa" (Cormorant 600 20px) + flecha `arrow-right`; "Compara las 20 localidades de un vistazo." (14px, #5b5853); tira de 8px con los 5 colores de la escala secuencial (seq-2…seq-6). Hover: fondo #fff3e4.
- **Pie:** línea hairline arriba, 12px #5b5853: "Datos abiertos de Bogotá · Sitio gratuito".

### 2. Portada — escritorio 1280 px (`screenshots/02-portada-escritorio-1280.png`)
- **Cabecera:** padding 18px 64px; marca en línea ("OBSERVATORIO" 11px + "Bacatá" 28px); enlaces Mapa · Localidades · Metodología (15px).
- **Hero:** grid 2 columnas `1.1fr / 1fr`, gap 64px, alineadas abajo. Izquierda: titular Cormorant 400 56px / 1.02 + entradilla 17px #5b5853, máximo 30em: "Cifras públicas de Bogotá, contadas localidad por localidad. Cada dato dice de dónde viene y hasta qué fecha llega." Derecha: buscador de 56px de alto, input 18px; sugerencias en popover absoluto (top 100% + 6px, z-index 2); debajo: "O elige en el mapa entre las 20 localidades." (13px, enlace en #7d5411).
- **Toda Bogotá:** h2 28px + "Más temas en camino". Grid de 4 columnas iguales, gap 18.4px, altura igualada (stretch). Las tarjetas "próximamente" usan el layout vertical de `.ind` con título gris, pastilla y una línea de descripción: "Cuánto tardamos en llegar al trabajo o al estudio." / "Reportes de convivencia en cada localidad." / "Lo que cuesta vivir en tu zona."
- **Mapa:** banda-enlace en grid `auto | 1fr | 320px | auto`, gap 32px, padding 28px 32px, borde 1px oro. Icono de mapa 32px · "Ver el mapa de las 20 localidades" (Cormorant 600 26px) + "Compara tu localidad con las demás de un vistazo." · barra de escala de 12px con "Menos / Más" · flecha de 24px.
- `main` padding 56px 64px 64px, gap 56px. Por encima de 1280, centrar con `max-width`; entre 360 y 1024, pasar a la versión de una columna y las tarjetas a un grid de 2 columnas.

### 3. Ficha de localidad — móvil (`screenshots/03-ficha-localidad-movil.png`, `design/ui_kits/movil/index.html`)
Selector de localidad → titular "{Localidad}, en cifras" → indicador de árboles por cada 1.000 habitantes → leyenda + lista de las 20 localidades ordenada de mayor a menor, cada una con una muestra de color por clase y la localidad elegida marcada con un contorno oro de 2px → aviso de retraso → indicador marcado como retrasado. Al cambiar la localidad se actualiza todo.

## Componentes (`screenshots/10–13`)
Cada uno tiene una implementación React de referencia en `design/components/**/<Nombre>.jsx`, con su contrato de props en `<Nombre>.d.ts` y su guía de uso en `<Nombre>.prompt.md`. El CSS está en `components.css`.
- **IndicatorCard** (`.ind`): kicker, localidad, título, valor + unidad, tendencia, comparación, fuente y fecha de corte, marca de retraso opcional. Variante `data-state="soon"`. **Regla:** la tendencia se escribe en color cerro #3e5566 con icono + palabra ("Sube 3 frente a 2025"), **nunca** en verde o rojo.
- **MapLegend** (`.legend`): título, unidad, barra de clases, cortes en cifras tabulares, extremos opcionales, claves "Sin dato" (rayado) y "localidad elegida" (contorno oro). Secuencial para magnitudes; divergente solo si hay una referencia real (promedio, meta, cero).
- **LocalitySelector** (`.loc`): `<select>` nativo de 48px con las 20 localidades numeradas ("08 · Kennedy"), icono map-pin a la izquierda y chevron a la derecha, texto en Cormorant 600 22px.
- **DataDelayNotice** (`.notice`): `role="status"`, grid icono + texto, borde 1px y fondo tintado. Tono `delay`: oro (#b68235 / #fff3e4, texto #7d5411). Tono `info`: cerro (#56707f / #e8eef1).

## Interactions & Behavior
- **Buscador:** filtra las 20 localidades al escribir, sin distinguir tildes ni mayúsculas (normalizar con NFD y quitar diacríticos). Coincidencia por subcadena, máximo 5 resultados. Al elegir, ir a `/localidad/{slug}`. Recomendado: patrón ARIA combobox (flechas, Enter, Escape) y `aria-activedescendant`.
- **Tarjetas "próximamente":** no son interactivas y no llevan enlace.
- **Acceso al mapa:** enlace a `/mapa`, con toda la tarjeta clicable.
- **Hover/press:** tinte oro-100 (#fff3e4) en tarjetas-enlace y filas; botones outline con tinte oro del 12% en hover y del 22% en press. Focus visible: outline 2px #b68235, offset 2px, en todo lo interactivo.
- **Movimiento:** mínimo, con fundidos de 150ms como máximo. Sin rebotes. Respetar `prefers-reduced-motion`.
- **Carga:** placeholder con el mismo tamaño que la tarjeta; nunca mostrar "0" mientras carga.
- **Datos retrasados:** si la fecha de corte supera la periodicidad esperada de la fuente, mostrar la marca en la tarjeta y un `DataDelayNotice` con las dos fechas (la del último corte y la del corte que se esperaba).

## State Management
- `query: string`: texto del buscador; las sugerencias se derivan de él.
- `selectedLocality: string`: se persiste (localStorage o URL) para volver a la ficha.
- Datos por indicador: `{ id, tema, titulo, valor, unidad, fuente, fechaCorte, periodicidad, tendencia?, estado: 'ok'|'retrasado'|'proximamente' }`.

## Design Tokens
Fuente de verdad: `design/tokens/*.css`.
- **Base:** papel #f3f2f2 · piedra #eae9e9 · tinta #201f1d (15.9:1) · tinta suave #5b5853 (6.3:1) · borde de control #8a8680 (3.3:1) · divisor = tinta al 16%.
- **Marca:** Oro #b68235 (3.0:1, solo trazos, iconos y texto de 24px o más) · Oro texto #7d5411 (6.0:1) · oro-100 #fff3e4 · oro-200 #ffe3bf · oro-600 #a06f24 · Sabana #5b7a45 / texto #3d5a2c / 100 #eef2e6 · Cerro #56707f / texto #3e5566 / 100 #e8eef1.
- **Datos, secuencial "Sabana":** #f4ecc8 · #d9dc9b · #a9c486 · #74a67a · #3f7a6c · #2c5f66 · #1f4256. Texto oscuro sobre los pasos 1–4 y blanco sobre los pasos 5–7. Para 5 clases se usan seq-2…seq-6.
- **Datos, divergente "Oro–Cerro":** #6e4a10 · #b68235 · #e3c48e · #ebe7e0 (centro) · #a9c7d3 · #5a8fa8 · #24506b.
- **Sin dato:** rayado a 45° #d7d3d3 / #f3f2f2, en bandas de 3px. **Selección:** contorno oro.
- Ninguna paleta usa rojo ni el eje rojo–verde (ver `screenshots/20`).
- **Tipografía:** Cormorant Garamond (400/600) para titulares y cifras; Lora (400/600) para el cuerpo; ambas de Google Fonts. Escala: 12 · 14 · 16 · 18 · 22 · 28 · 32 · 48; cuerpo de 16px en móvil. Todas las cifras de datos en `font-variant-numeric: tabular-nums lining-nums`, aplicado **solo a la cifra o la fecha** (`.tnum`), no a párrafos (en Lora abre el espaciado entre palabras).
- **Espaciado:** 4.6 · 9.2 · 13.8 · 18.4 · 27.6 · 36.8 px. Área táctil de 48px como mínimo.
- **Radios:** 2 / 4 / 7 px.
- **Sombras:** sm `0 1px 2px rgba(45,43,43,.14)` · md `0 3px 10px rgba(45,43,43,.16)` · lg `0 12px 32px rgba(45,43,43,.22)`. Solo en popovers y diálogos; las tarjetas no llevan sombra.
- **Formato es-CO:** `1.284,5` · `92,4 %` · `24 sep 2026`.

## Content rules
Tuteo, mayúscula solo al inicio de la frase, sin emoji ni signos de exclamación, sin lenguaje de ventanilla ni de alarma. Toda cifra lleva su fuente y su fecha de corte. Las tendencias se describen, no se juzgan. Detalle completo en `design/DESIGN_SYSTEM.md`.

## Assets
- **Iconos:** Lucide (https://lucide.dev), trazo 1.75: search, wind, route, shield, wallet, map, arrow-right, map-pin, chevron-down, trending-up, trending-down, minus, clock, info. Usar `lucide-react` o el paquete equivalente.
- **Logotipo:** no existe. La marca se compone solo con tipografía, como se describe arriba.
- **Fotografía e ilustración:** no hay.

## Files
- `screenshots/`: PNGs de la portada móvil y de escritorio, la ficha, los 4 componentes y la simulación de daltonismo de las paletas.
- `design/Portada.dc.html`: portada (1a móvil, 1b escritorio) con el buscador funcionando.
- `design/ui_kits/movil/index.html`: ficha de localidad interactiva.
- `design/styles.css` + `design/tokens/` + `design/components/components.css`: CSS portable.
- `design/components/**`: componentes React de referencia (.jsx, .d.ts, .prompt.md) y tarjetas de muestra (.card.html).
- `design/guidelines/`: muestras de color, tipo y espaciado.
- `design/DESIGN_SYSTEM.md`: guía completa (contenido, fundamentos visuales, iconografía).
- `SKILL.md`: para usar el sistema como skill de Claude Code.
