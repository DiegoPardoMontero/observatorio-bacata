# Observatorio Bacatá — sistema de diseño

Sitio cívico y gratuito que muestra datos abiertos de Bogotá por localidad a vecinos, periodistas y estudiantes, sobre todo desde el celular. *Bacatá* es el nombre muisca de Bogotá.

**Fuentes.** Brief del usuario (sin código, Figma ni logotipo). Base visual: sistema **Classical** (Cormorant Garamond + Lora, reglas finas, color como trazo), extendido aquí para marca y datos.

## Índice
- `styles.css` — entrada única (sólo `@import`).
- `tokens/` — `classical.css` (base heredada), `colors.css`, `data.css`, `typography.css`, `spacing.css`.
- `components/components.css` — clases `.ind`, `.legend`, `.loc`, `.notice`.
- Componentes React: `components/data/IndicatorCard`, `components/legend/MapLegend`, `components/forms/LocalitySelector`, `components/feedback/DataDelayNotice` (cada uno con `.d.ts` y `.prompt.md`).
- `guidelines/` — tarjetas de fundamentos.
- `ui_kits/movil/` — ficha de localidad interactiva.
- `SKILL.md`.

## CONTENT FUNDAMENTALS
- **Tono:** confiable, sereno, cercano. Tuteo ("elige tu localidad", "puedes citarla"). Nada de lenguaje de ventanilla ("se informa a la ciudadanía") ni de alarma ("¡Atención!", "crisis").
- **Casing:** frase en español — sólo mayúscula inicial y nombres propios. Versalitas sólo en el *kicker* de tema.
- **Cifras:** formato es-CO — `1.284,5`, `92,4 %` (espacio antes de %), `30 jun 2026`. Siempre fuente y fecha de corte junto a la cifra.
- **Tendencias:** describir, no juzgar: "Sube 3 frente a 2025", "Baja 4 min". No "mejora"/"empeora" salvo que la fuente lo defina.
- **Retrasos:** decir qué corte mostramos, cuál esperábamos y qué hacemos. Ej.: "El Acueducto publicó su último corte el 31 mar 2026. Esperábamos uno nuevo el 30 jun; mientras llega, mostramos el más reciente."
- **Sin emoji.** Sin signos de exclamación.

## VISUAL FOUNDATIONS
- **Color de marca:** Oro (#b68235, orfebrería muisca) como trazo, icono y marca de selección; Oro texto (#7d5411) para texto. Sabana (#3d5a2c) y Cerro (#3e5566) como tintas secundarias. Fondo papel #f3f2f2, tinta #201f1d.
- **Datos:** secuencial *Sabana* (7 pasos, crema → verde sabana → azul cerro) y divergente *Oro–Cerro* (oro ↔ piedra ↔ azul). Luminosidad monótona, sin eje rojo–verde, sin rojo. Divergente sólo con una referencia real (promedio, meta, cero). "Sin dato" es rayado piedra, nunca un color de la escala. Localidad elegida: contorno oro de 2–3px.
- **Semánticos:** no hay rojo ni verde de estado. Retraso = oro (borde + tinte oro‑100). Informativo = cerro. Tendencia = tinta cerro con icono y palabra.
- **Tipo:** Cormorant Garamond para titulares y cifras grandes (400 en display, 600 en títulos); Lora para cuerpo a 16px en móvil. Todo dato en `tabular-nums lining-nums`; la prosa conserva cifras de texto.
- **Espacio:** escala ×1.15 de Classical (4.6 … 36.8). Margen lateral 18.4px. Área táctil ≥ 48px.
- **Superficies:** tarjetas sin relleno con borde hairline (16% tinta), radio 4px. Sin sombras en contenido; `--shadow-lg` sólo en diálogos.
- **Fondos e imagen:** papel liso; sin degradados, texturas ni ilustración. Fotografías (si las hay) en `.plate`.
- **Movimiento:** mínimo — cambios de estado instantáneos o fundidos ≤150ms. Sin rebotes.
- **Hover / press:** tinte oro 10–22% en botones fantasma/outline; borde oro en controles. Foco: anillo oro 2px, offset 2px.
- **Transparencia/blur:** no se usan, salvo el velo de diálogos.
- **Contraste AA:** tinta 15.9:1, tinta suave 6.3:1, oro texto 6.0:1, oro 3.0:1 (sólo trazos/≥24px). El gris 55% de Classical se reemplaza por `--color-text-muted` porque no llegaba a 4.5:1.

## ICONOGRAPHY
Lucide (trazo 1.75, esquinas redondeadas), a 18px en interfaz y 24px destacado. Los componentes llevan embebidos los trazos que usan (map-pin, trending-up/down, minus, clock, info, chevron-down); para otros, usar Lucide por CDN. Sin emoji ni caracteres unicode como iconos.

## Logotipo
No se entregó logotipo; el nombre se compone en tipo ("Observatorio" en versalitas Lora + "Bacatá" en Cormorant 400). No crear un símbolo sin material de marca.

## Intentional additions
- Los cuatro componentes pedidos. No se añadieron más; botones, campos, tablas y diálogos vienen de la base Classical (`.btn`, `.input`, `.table`, `.dialog`).

## Excepción: colores del IBOCA
El IBOCA es el índice oficial de calidad del aire de Bogotá, y la Resolución conjunta 2840 de 2023 (Tabla 2) fija sus colores: verde, amarillo, naranja, rojo y morado. Es el código que la ciudadanía ya ve en la Secretaría de Ambiente y en los medios, así que en el Observatorio el IBOCA usa esos colores y no la paleta de Bacatá. Para que no dependa del color ni del eje rojo–verde, la categoría va **siempre escrita** ("Moderado") y el color aparece solo en una muestra pequeña con borde (`.iboca-muestra`), nunca como texto ni como relleno grande. La excepción aplica solo al IBOCA; el resto de datos de aire usa las paletas de Bacatá. Pendiente de aprobación del dueño del sistema de diseño (25 sep 2026).
