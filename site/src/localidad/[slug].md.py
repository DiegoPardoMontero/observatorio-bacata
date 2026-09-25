"""Ficha de una localidad (RF-06): genera la página de cada una de las 20 localidades.

Framework corre este page loader una vez por ruta de `dynamicPaths` con --slug=<slug>.
Se genera el Markdown (y no una sola página con parámetros) para que cada ficha
tenga su propio título, que es el que aparece al compartirla.
"""

import argparse
import csv
from pathlib import Path

SEMILLA = Path(__file__).resolve().parents[3] / "transform" / "seeds" / "localidad.csv"

parser = argparse.ArgumentParser()
parser.add_argument("--slug", required=True)
slug = parser.parse_args().slug
localidad = next(fila for fila in csv.DictReader(SEMILLA.open(encoding="utf-8")) if fila["slug"] == slug)

PAGINA = r'''---
title: __NOMBRE__, en cifras
---

```js
import {fecha, hora, fechaHora, mes, numero, porcentaje, MESES, MESES_LARGOS, conCodigo} from "../components/formato.js";
import {tarjetaIndicador, tarjetaProximamente, aviso, categoriaIboca, icono} from "../components/ui.js";

const catalogo = FileAttachment("../data/catalogo.json").json();
const indicadores = (await FileAttachment("../data/indicadores.csv").csv({typed: true})).map(conCodigo);
const estado = FileAttachment("../data/estado_aire.json").json();
```

```js
const ID = "__ID__";
const localidad = catalogo.localidades.find((l) => l.localidad_id === ID);
const propios = indicadores.filter((d) => d.localidad_id === ID);
const serie = (indicadorId) => propios.filter((d) => d.indicador_id === indicadorId).sort((a, b) => a.mes - b.mes);
const pm25 = serie("aire_pm25_promedio");
const diasOms = serie("aire_pm25_dias_sobre_guia_oms");
const actual = pm25.at(-1);
const anterior = pm25.at(-2);
const estacionesLocalidad = catalogo.estaciones.filter((e) => e.localidad_id === ID);
const estadoPorEstacion = new Map(estado.map((d) => [d.estacion_id, d]));
```

```js
const selector = html`<div class="loc selector">
  <label class="loc-label" for="localidad">Localidad</label>
  <div class="loc-control">
    ${icono("pin")}
    <select id="localidad" class="loc-select">${catalogo.localidades.map((l) => html`<option value=${l.slug} selected=${l.localidad_id === ID}>${l.localidad_id} · ${l.nombre}</option>`)}</select>
    ${icono("abajo")}
  </div>
</div>`;
selector.querySelector("select").addEventListener("change", (e) => (location.href = `./${e.target.value}`));
display(selector);
```

# __NOMBRE__, en cifras

```js
if (localidad.es_rural) {
  display(html`<div class="avisos">${aviso({
    tono: "info",
    titulo: "Una localidad rural",
    cuerpo: "Sumapaz es rural, tiene poca población y ocupa casi tres cuartas partes del área de Bogotá. Sus cifras se leen aparte: comparadas con las de las localidades urbanas pueden confundir."
  })}</div>`);
}
```

<div class="seccion-encabezado"><h2>Los cuatro temas</h2><span>Localidad ${localidad.localidad_id}</span></div>

<div class="tarjetas tarjetas-4">
  ${actual ? tarjetaIndicador({
    kicker: "Aire",
    icono: "aire",
    localidad: localidad.nombre,
    titulo: "Partículas finas en el aire",
    valor: numero(actual.valor),
    unidad: "µg/m³ de PM2.5",
    frase: `Promedio de ${MESES_LARGOS[actual.mes.getUTCMonth()]}${actual.fecha_corte_fuente < new Date(Date.UTC(actual.mes.getUTCFullYear(), actual.mes.getUTCMonth() + 1, 0)) ? `, hasta el ${fecha(actual.fecha_corte_fuente)}` : ""}, en ${actual.n_observaciones === 1 ? "su estación" : `sus ${actual.n_observaciones} estaciones`}.`,
    tendencia: anterior ? {
      direccion: Math.abs(actual.valor - anterior.valor) < 0.5 ? "igual" : actual.valor > anterior.valor ? "sube" : "baja",
      texto: `${Math.abs(actual.valor - anterior.valor) < 0.5 ? "" : `${numero(Math.abs(actual.valor - anterior.valor))} `}frente a ${MESES_LARGOS[anterior.mes.getUTCMonth()]}`
    } : null,
    comparacion: `Bogotá: ${numero(actual.valor_ciudad)} µg/m³`,
    fuente: "RMCAB",
    corte: fecha(actual.fecha_corte_fuente)
  }) : html`<article class="ind">
    <header class="ind-head"><span class="ind-kicker ind-kicker-icono">${icono("aire", 14)}Aire</span><span class="ind-loc">${localidad.nombre}</span></header>
    <h3 class="ind-title">Partículas finas en el aire</h3>
    <div class="ind-value"><span class="iboca iboca-sin-dato"><span class="iboca-muestra" aria-hidden="true"></span>Sin medición</span></div>
    <p class="ind-compare">${localidad.nombre} no tiene una estación fija de la red de monitoreo. No estimamos su aire con el de otras zonas.</p>
    <p class="ind-frase"><a href="../aire">Ver las estaciones de la ciudad</a></p>
  </article>`}
  ${tarjetaProximamente({kicker: "Movilidad", icono: "movilidad", subtitulo: "Tiempos de viaje"})}
  ${tarjetaProximamente({kicker: "Seguridad", icono: "seguridad", subtitulo: "Convivencia y seguridad"})}
  ${tarjetaProximamente({kicker: "Costo de vida", icono: "costo", subtitulo: "Precios del hogar"})}
</div>

## Aire en __NOMBRE__

```js
if (estacionesLocalidad.length === 0) {
  display(html`<p>La Red de Monitoreo de Calidad del Aire no tiene estaciones fijas en ${localidad.nombre}. En el <a href="../mapa">mapa</a> puedes ver las localidades que sí tienen medición.</p>`);
} else {
  display(html`<p>${estacionesLocalidad.length === 1 ? "Su estación" : "Sus estaciones"} de la red de monitoreo, con el IBOCA más reciente:</p>`);
  display(html`<ul class="estaciones">${estacionesLocalidad.map((e) => {
    const d = estadoPorEstacion.get(e.estacion_id);
    return html`<li class="estacion">
      <span class="estacion-nombre">${e.nombre}${e.es_movil ? " (móvil)" : ""}</span>
      <span class="estacion-valor"><span class="tnum">${d ? numero(d.pm25_nowcast) : "–"}</span> µg/m³</span>
      <span class="estacion-localidad">${e.direccion}</span>
      ${d ? categoriaIboca(d.iboca_categoria, d.iboca_color_hex) : categoriaIboca(null)}
      <span class="estacion-hora">${d ? fechaHora(new Date(d.fecha_hora)) : ""}</span>
    </li>`;
  })}</ul>`);
}
```

```js
if (pm25.length > 0) {
  const masAlto = d3.greatest(pm25, (d) => d.valor);
  const masBajo = d3.least(pm25, (d) => d.valor);
  display(html`<h3>¿Cómo ha cambiado el PM2.5 mes a mes?</h3>`);
  display(html`<p>Entre ${mes(pm25[0].mes)} y ${mes(pm25.at(-1).mes)}, el mes más alto en ${localidad.nombre} fue ${MESES_LARGOS[masAlto.mes.getUTCMonth()]}, con ${numero(masAlto.valor)} µg/m³, y el más bajo fue ${MESES_LARGOS[masBajo.mes.getUTCMonth()]}, con ${numero(masBajo.valor)}. ${pm25.at(-1).valor > pm25.at(-1).valor_ciudad ? "El último mes estuvo por encima" : "El último mes estuvo por debajo"} del promedio de Bogotá.</p>`);
  display(html`<ul class="leyenda-referencias" aria-label="Qué muestra cada línea">
    <li><span class="clave-linea" aria-hidden="true"></span>${localidad.nombre}</li>
    <li><span class="clave-linea is-ciudad" aria-hidden="true"></span>Bogotá</li>
  </ul>`);
  display(html`<div class="grafico">${resize((width) => Plot.plot({
    width,
    height: 220,
    marginLeft: 32,
    marginRight: 12,
    style: {fontFamily: "var(--font-body)", fontSize: "12px", color: "var(--color-text-muted)", background: "transparent"},
    ariaLabel: `PM2.5 promedio mensual en ${localidad.nombre} y en Bogotá`,
    x: {type: "utc", label: null, tickFormat: (d) => MESES[d.getUTCMonth()], ticks: "month"},
    y: {label: "µg/m³", grid: true, nice: true, zero: true},
    marks: [
      Plot.ruleY([0], {stroke: "var(--color-divider)", strokeOpacity: 1}),
      Plot.lineY(pm25, {x: "mes", y: "valor_ciudad", stroke: "var(--color-text-muted)", strokeWidth: 1.5}),
      Plot.lineY(pm25, {x: "mes", y: "valor", stroke: "var(--data-seq-6)", strokeWidth: 2}),
      Plot.dot(pm25, {x: "mes", y: "valor", r: 4, fill: "var(--data-seq-6)", stroke: "var(--color-bg)", strokeWidth: 2}),
      Plot.tip(pm25, Plot.pointerX({x: "mes", y: "valor", title: (d) => `${mes(d.mes)}\n${localidad.nombre}: ${numero(d.valor)} µg/m³\nBogotá: ${numero(d.valor_ciudad)} µg/m³`}))
    ]
  }))}</div>`);
  const ultimoOms = diasOms.at(-1);
  if (ultimoOms) {
    display(html`<p>En ${MESES_LARGOS[ultimoOms.mes.getUTCMonth()]}, ${porcentaje(ultimoOms.valor)} de los días ${localidad.nombre} pasó la guía diaria de la OMS (15 µg/m³). En toda Bogotá fue ${porcentaje(ultimoOms.valor_ciudad)}.</p>`);
  }
  display(html`<p class="fuente">Fuente: <b><a href="http://rmcab.ambientebogota.gov.co/Report/HourlyReports">RMCAB</a></b>, Secretaría Distrital de Ambiente · Corte: <span class="tnum">${fecha(pm25.at(-1).fecha_corte_fuente)}</span> · Solo estaciones fijas; un mes cuenta si hay datos en al menos el 75 % de los días. <a href="../metodologia#aire">Cómo se calculó</a></p>`);
}
```
'''

print(PAGINA.replace("__NOMBRE__", localidad["nombre"]).replace("__ID__", localidad["localidad_id"]))
