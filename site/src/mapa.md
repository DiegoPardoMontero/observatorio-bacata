---
title: Mapa de las localidades
---

```js
import {fecha, mes, numero, conCodigo} from "./components/formato.js";
import {colores} from "./components/ui.js";

const catalogo = FileAttachment("data/catalogo.json").json();
const indicadores = (await FileAttachment("data/indicadores.csv").csv({typed: true})).map(conCodigo);
const geo = FileAttachment("data/localidades.geojson").json();
```

# Mapa de las localidades

<p class="entradilla">Elige un tema y un indicador. Toca una localidad para ver su valor y compararla con las demás.</p>

```js
const temas = [
  {id: "aire", nombre: "Aire"},
  {id: "movilidad", nombre: "Movilidad (próximamente)", deshabilitado: true},
  {id: "seguridad", nombre: "Seguridad (próximamente)", deshabilitado: true},
  {id: "costo", nombre: "Costo de vida (próximamente)", deshabilitado: true}
];
const selectorTema = html`<select id="tema">${temas.map((t) => html`<option value=${t.id} disabled=${t.deshabilitado}>${t.nombre}</option>`)}</select>`;
const tema = Generators.input(selectorTema);
```

```js
const deTema = catalogo.indicadores.filter((i) => i.tema === tema);
const selectorIndicador = html`<select id="indicador">${deTema.map((i) => html`<option value=${i.indicador_id}>${i.nombre}</option>`)}</select>`;
const indicadorId = Generators.input(selectorIndicador);
```

```js
const indicador = catalogo.indicadores.find((i) => i.indicador_id === indicadorId);
const filasIndicador = indicadores.filter((d) => d.indicador_id === indicadorId);
const meses = d3.sort(d3.union(filasIndicador.map((d) => +d.mes)), (m) => -m).map((m) => new Date(m));
const cortes = d3.rollup(filasIndicador, (v) => d3.max(v, (d) => d.fecha_corte_fuente), (d) => +d.mes);
const selectorMes = html`<select id="mes">${meses.map((m) => html`<option value=${+m}>${mes(m)}${cortes.get(+m) < new Date(Date.UTC(m.getUTCFullYear(), m.getUTCMonth() + 1, 0)) ? " (en curso)" : ""}</option>`)}</select>`;
const mesElegido = Generators.input(selectorMes);
```

<div class="mapa-controles">
  <label for="tema">Tema ${selectorTema}</label>
  <label for="indicador">Indicador ${selectorIndicador}</label>
  <label for="mes">Mes ${selectorMes}</label>
</div>

```js
// El selector devuelve el mes como texto (milisegundos)
const mesActual = new Date(+mesElegido);
const valores = new Map(filasIndicador.filter((d) => +d.mes === +mesActual).map((d) => [d.localidad_id, d]));
const corte = cortes.get(+mesActual);
const mediana = d3.median(valores.values(), (d) => d.valor);
const localidades = new Map(catalogo.localidades.map((l) => [l.localidad_id, l]));
// Sumapaz es rural y ocupa casi tres cuartas partes del área de Bogotá: va aparte (SPEC §9)
const urbano = geo.features.filter((f) => f.properties.localidad_id !== "20");
// La escala es la misma para todos los meses del indicador, para que se puedan comparar
const escala = d3.scaleQuantize(d3.extent(filasIndicador, (d) => d.valor), colores("data-seq-2", "data-seq-3", "data-seq-4", "data-seq-5", "data-seq-6")).nice();
const seleccion = Mutable(null);
const elegir = (id) => (seleccion.value = id);
```

<div class="mapa">${resize((width) => mapa(width, seleccion))}</div>

${leyenda()}

```js
function mapa(width, elegida) {
  const svg = Plot.plot({
    width,
    height: Math.round(width * 1.25),
    margin: 4,
    style: {background: "transparent"},
    ariaLabel: `Mapa de ${indicador.nombre} por localidad, ${mes(mesActual)}`,
    projection: {type: "mercator", domain: {type: "FeatureCollection", features: urbano}},
    color: {type: "identity"},
    marks: [
      Plot.geo(urbano, {
        fill: (f) => (valores.has(f.properties.localidad_id) ? escala(valores.get(f.properties.localidad_id).valor) : "url(#sin-medicion)"),
        stroke: "var(--color-bg)",
        strokeWidth: 1.5
      }),
      Plot.geo(urbano.filter((f) => f.properties.localidad_id === elegida), {fill: "none", stroke: "var(--color-oro)", strokeWidth: 3}),
      Plot.tip(urbano, Plot.pointer(Plot.geoCentroid({
        title: (f) => {
          const l = localidades.get(f.properties.localidad_id);
          const v = valores.get(f.properties.localidad_id);
          return `${l.nombre}\n${v ? `${numero(v.valor)} ${indicador.unidad}` : "Sin medición"}`;
        }
      })))
    ]
  });
  // Patrón "sin medición" del sistema de diseño: rayado a 45°, nunca un color de la escala
  svg.insertAdjacentHTML("afterbegin", `<defs><pattern id="sin-medicion" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="#f3f2f2"/><rect width="3" height="6" fill="#d7d3d3"/></pattern></defs>`);
  svg.querySelectorAll('g[aria-label="geo"]:first-of-type path').forEach((path) => {
    const f = urbano[path.__data__];
    path.setAttribute("data-localidad", f.properties.localidad_id);
    path.addEventListener("click", () => elegir(f.properties.localidad_id));
  });
  return svg;
}

function leyenda() {
  const umbrales = escala.thresholds();
  const [minimo, maximo] = escala.domain();
  return html`<div class="legend">
    <p class="legend-title">${indicador.nombre}</p>
    <p class="legend-unit">${indicador.unidad} · ${mes(mesActual)}</p>
    <div class="legend-scale">${escala.range().map((c) => html`<span style=${{background: c}}></span>`)}</div>
    <div class="legend-ticks">${[minimo, ...umbrales, maximo].map((t) => html`<span>${numero(t, 0)}</span>`)}</div>
    <div class="legend-ends"><span>Menos</span><span>Más</span></div>
    <div class="legend-extra">
      <span class="legend-key"><span class="legend-swatch is-nodata"></span>Sin medición</span>
      <span class="legend-key"><span class="legend-swatch is-selected"></span>Localidad elegida</span>
    </div>
  </div>`;
}
```

${panel(seleccion)}

```js
function panel(id) {
  if (!id) return html`<p class="fuente">Toca una localidad en el mapa o elígela en la lista de abajo.</p>`;
  const l = localidades.get(id);
  const v = valores.get(id);
  const posicion = !v || mediana === undefined ? null
    : Math.abs(v.valor - mediana) < 0.05 ? "igual a la mediana"
    : v.valor > mediana ? "por encima de la mediana" : "por debajo de la mediana";
  return html`<article class="ind panel-localidad">
    <header class="ind-head"><span class="ind-kicker">${indicador.nombre}</span><span class="ind-loc">Localidad ${l.localidad_id}</span></header>
    <h3 class="ind-title">${l.nombre}</h3>
    ${v
      ? html`<div class="ind-value"><span class="ind-num">${numero(v.valor)}</span><span class="ind-unit">${indicador.unidad}</span></div>
        <p class="ind-compare">Está ${posicion} de las localidades con medición (${numero(mediana)}). Bogotá: ${numero(v.valor_ciudad)}.</p>`
      : html`<p class="ind-compare">Sin medición: esta localidad no tiene una estación fija de la RMCAB. No interpolamos datos de otras zonas.</p>`}
    <p><a href=${`./localidad/${l.slug}`}>Ver la ficha de ${l.nombre}</a></p>
    <footer class="ind-meta"><span>Fuente: <b>${indicador.fuente}</b></span><span>Corte: <span class="tnum">${fecha(corte)}</span></span></footer>
  </article>`;
}
```

<p class="fuente">Sumapaz no aparece en el mapa: es rural y ocupa casi tres cuartas partes del área de Bogotá, así que dibujarla dejaría las demás localidades diminutas. ${valores.has("20") ? `Su valor: ${numero(valores.get("20").valor)} ${indicador.unidad}.` : "No tiene medición en este indicador."} <a href="./localidad/sumapaz">Ver la ficha de Sumapaz</a>.</p>

<details class="tabla">
  <summary>Ver las 20 localidades en una tabla</summary>
  ${tabla()}
</details>

```js
function tabla() {
  return html`<div class="tabla-desplazable"><table class="datos">
    <caption class="fuente">${indicador.nombre} (${indicador.unidad}), ${mes(mesActual)}. En orden de código de localidad.</caption>
    <thead><tr><th scope="col">Localidad</th><th scope="col" class="num">Valor</th><th scope="col">Frente a la mediana</th></tr></thead>
    <tbody>${catalogo.localidades.map((l) => {
      const v = valores.get(l.localidad_id);
      return html`<tr>
        <th scope="row"><a href=${`./localidad/${l.slug}`}>${l.localidad_id} · ${l.nombre}</a></th>
        <td class="num">${v ? numero(v.valor) : "Sin medición"}</td>
        <td>${v ? (v.valor > mediana ? "Por encima" : v.valor < mediana ? "Por debajo" : "Igual") : "–"}</td>
      </tr>`;
    })}</tbody>
  </table></div>`;
}
```

<p class="fuente">Fuente: <b>${indicador.fuente}</b> · Corte: <span class="tnum">${fecha(corte)}</span> · Polígonos: Catastro Distrital (IDECA), CC BY 4.0 · ${indicador.descripcion} <a href="./metodologia#aire">Cómo se calculó</a></p>
