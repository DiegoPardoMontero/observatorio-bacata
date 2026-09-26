// Componentes del sistema de diseño (docs/diseno/design/components/), en HTML plano.
// Las clases CSS (.ind, .notice, .loc, .legend) vienen de components.css.
import {html, svg} from "npm:htl";

// Trazos de Lucide (trazo 1,75) tomados del paquete de diseño
const ICONOS = {
  buscar: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  aire: '<path d="M12.8 19.6A2 2 0 1 0 14 16H2"/><path d="M17.5 8a2.5 2.5 0 1 1 2 4H2"/><path d="M9.8 4.4A2 2 0 1 1 11 8H2"/>',
  movilidad: '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
  seguridad: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
  costo: '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
  mapa: '<path d="M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0z"/><path d="M15 5.764v15"/><path d="M9 3.236v15"/>',
  flecha: '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
  sube: '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
  baja: '<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/>',
  igual: '<path d="M5 12h14"/>',
  reloj: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
  pin: '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
  abajo: '<path d="m6 9 6 6 6-6"/>',
  descargar: '<path d="M12 15V3"/><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/>'
};

export function icono(nombre, tamano) {
  const s = svg`<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"></svg>`;
  s.innerHTML = ICONOS[nombre];
  if (tamano) s.style.width = s.style.height = `${tamano}px`;
  return s;
}

const PALABRA = {sube: "Sube", baja: "Baja", igual: "Sin cambio"};

/**
 * Tarjeta de indicador (IndicatorCard). La tendencia se describe en palabras y en color
 * cerro, nunca en verde o rojo. Sin fuente y corte no se publica una cifra.
 */
export function tarjetaIndicador({kicker, icono: nombreIcono, localidad, titulo, valor, unidad, frase, tendencia, comparacion, fuente, corte, retrasado = false, enlace}) {
  const tarjeta = html`<article class="ind">
    <header class="ind-head">
      ${kicker ? html`<span class="ind-kicker ind-kicker-icono">${nombreIcono ? icono(nombreIcono, 14) : null}${kicker}</span>` : null}
      ${localidad ? html`<span class="ind-loc">${localidad}</span>` : null}
    </header>
    <h3 class="ind-title">${titulo}</h3>
    ${retrasado ? html`<span class="ind-flag">${icono("reloj")}Datos con retraso</span>` : null}
    <div class="ind-value"><span class="ind-num">${valor}</span>${unidad ? html`<span class="ind-unit">${unidad}</span>` : null}</div>
    ${frase ? html`<p class="ind-frase">${frase}</p>` : null}
    ${tendencia ? html`<p class="ind-trend">${icono(tendencia.direccion)}${PALABRA[tendencia.direccion]}${tendencia.texto ? ` ${tendencia.texto}` : ""}</p>` : null}
    ${comparacion ? html`<p class="ind-compare">${comparacion}</p>` : null}
    <footer class="ind-meta"><span>Fuente: <b>${fuente}</b></span><span>Corte: <span class="tnum">${corte}</span></span></footer>
  </article>`;
  return enlace ? html`<a class="ind-enlace" href=${enlace}>${tarjeta}</a>` : tarjeta;
}

/** Tarjeta de un tema que todavía no tiene datos. No es interactiva ni lleva enlace. */
export function tarjetaProximamente({kicker, icono: nombreIcono, subtitulo}) {
  return html`<article class="ind ind-fila" data-state="soon">
    ${icono(nombreIcono)}
    <div class="ind-fila-texto">
      <span class="ind-kicker ind-kicker-gris">${kicker}</span>
      <span class="ind-fila-subtitulo">${subtitulo}</span>
    </div>
    <span class="ind-soon">Próximamente</span>
  </article>`;
}

/** Aviso (DataDelayNotice). Tono "delay" (oro) para retrasos, "info" (cerro) para contexto. */
export function aviso({tono = "delay", titulo, cuerpo, enlace, textoEnlace}) {
  return html`<aside class="notice" data-tone=${tono} role="status">
    ${icono(tono === "info" ? "info" : "reloj")}
    <div>
      <p class="notice-title">${titulo ?? (tono === "info" ? "Sobre estos datos" : "Estos datos llegan con retraso")}</p>
      <p class="notice-body">${cuerpo}</p>
      ${enlace ? html`<a class="notice-link" href=${enlace}>${textoEnlace}</a>` : null}
    </div>
  </aside>`;
}

/**
 * Categoría del IBOCA: el nombre siempre en texto y el color oficial (Res. 2840 de 2023,
 * Tabla 2) solo en una muestra con borde, para que nunca dependa del color.
 */
export function categoriaIboca(categoria, colorHex) {
  if (!categoria) return html`<span class="iboca iboca-sin-dato"><span class="iboca-muestra" aria-hidden="true"></span>Sin dato</span>`;
  return html`<span class="iboca"><span class="iboca-muestra" style=${{background: colorHex}} aria-hidden="true"></span>${categoria}</span>`;
}

/**
 * Observable Plot pone aria-label en cada grupo de marcas ("line", "rule", "tip"). No le
 * dice nada a quien usa un lector de pantalla y ARIA no lo permite en un <g> sin rol, así
 * que se quita. Un gráfico no interactivo queda como una imagen con su ariaLabel; el
 * resumen en texto que lo acompaña lleva las cifras (RNF-05).
 */
export function accesible(grafico, {interactivo = false} = {}) {
  const svgs = grafico.tagName.toLowerCase() === "svg" ? [grafico] : [...grafico.querySelectorAll("svg")];
  for (const svg of svgs) {
    svg.querySelectorAll("g[aria-label]").forEach((g) => g.removeAttribute("aria-label"));
    if (!interactivo && svg.hasAttribute("aria-label")) svg.setAttribute("role", "img");
  }
  return grafico;
}

/** Valores de tokens de color (--data-seq-2…) para escalas de Plot, que necesitan colores reales. */
export function colores(...tokens) {
  const estilo = getComputedStyle(document.documentElement);
  return tokens.map((t) => estilo.getPropertyValue(`--${t}`).trim());
}
