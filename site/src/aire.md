---
title: ¿Cómo está el aire ahora?
---

```js
import {ahoraBogota, fecha, fechaHora, hora, hace, numero, DIAS, MESES} from "./components/formato.js";
import {aviso, categoriaIboca, colores} from "./components/ui.js";
import {termino} from "./components/glosario.js";

const catalogo = FileAttachment("data/catalogo.json").json();
const estado = FileAttachment("data/estado_aire.json").json();
const horario = FileAttachment("data/pm25_horario.csv").csv({typed: true});
const diario = FileAttachment("data/pm25_diario.csv").csv({typed: true});
const patron = FileAttachment("data/pm25_patron.csv").csv({typed: true});
```

```js
// Referencias normativas para el promedio de 24 horas
const LIMITE_NORMA = 37; // Resolución 2254 de 2017, MinAmbiente, desde el 1 jul 2018
const GUIA_OMS = 15; // Guías de calidad del aire de la OMS, 2021
const LIMITE_RETRASO_H = 3; // RNF-02

const estaciones = new Map(catalogo.estaciones.map((e) => [e.estacion_id, e]));
const rmcab = catalogo.fuentes.find((f) => f.fuente_id === "rmcab");
const datoMasReciente = new Date(rmcab.dato_mas_reciente);
const retrasado = ahoraBogota() - datoMasReciente > LIMITE_RETRASO_H * 3.6e6;
const ultimaHora = d3.max(estado, (d) => new Date(d.fecha_hora));

const filas = estado
  .map((d) => ({...d, fecha_hora: new Date(d.fecha_hora), estacion: estaciones.get(d.estacion_id)}))
  .sort((a, b) => d3.ascending(a.estacion.nombre, b.estacion.nombre));
const conteo = d3.rollup(filas.filter((d) => +d.fecha_hora === +ultimaHora), (v) => v.length, (d) => d.iboca_categoria);
```

```js
if (retrasado) {
  display(html`<div class="avisos">${aviso({
    cuerpo: `La RMCAB publicó su último dato ${hace(datoMasReciente)} (${fechaHora(datoMasReciente)}). Esperábamos uno cada hora; mientras llega, mostramos el más reciente.`
  })}</div>`);
}
```

# ¿Cómo está el aire ahora?

<p class="entradilla">El ${termino("iboca", "IBOCA")} es el índice oficial de calidad del aire de Bogotá. Para las partículas finas (${termino("pm25", "PM2.5")}) usa el ${termino("nowcast", "promedio ponderado de las últimas 12 horas")} en cada estación, que pesa más las horas recientes.</p>

<div class="seccion-encabezado"><h2>Estado por estación</h2><span class="tnum">${fechaHora(ultimaHora)}</span></div>

<p class="fuente">Cada valor es el promedio ponderado de 12 horas de PM2.5, en ${termino("microgramos", "µg/m³")}.</p>

${resumenEstado()}

```js
function resumenEstado() {
  const partes = [...conteo].sort((a, b) => d3.descending(a[1], b[1])).map(([c, n]) => `${n} en ${c.toLowerCase()}`);
  const texto = partes.length === 0 ? "Ninguna estación tiene dato en la última hora." : `De las estaciones con dato a las ${hora(ultimaHora)}: ${partes.join(", ")}.`;
  return html`<p>${texto}</p>`;
}
```

${listaEstaciones(filas.filter((d) => !d.estacion.es_movil))}

<h3>Estaciones móviles</h3>
<p class="fuente">Cambian de sitio según las campañas de la Secretaría de Ambiente, así que no se usan en los promedios por localidad.</p>

${listaEstaciones(filas.filter((d) => d.estacion.es_movil))}

```js
function listaEstaciones(lista) {
  return html`<ul class="estaciones">${lista.map((d) => {
    const reciente = ultimaHora - d.fecha_hora <= LIMITE_RETRASO_H * 3.6e6;
    return html`<li class="estacion" data-reciente=${reciente}>
      <span class="estacion-nombre">${d.estacion.nombre}</span>
      <span class="estacion-valor"><span class="tnum">${numero(d.pm25_nowcast)}</span> µg/m³</span>
      <span class="estacion-localidad">${d.estacion.localidad}</span>
      ${categoriaIboca(d.iboca_categoria, d.iboca_color_hex)}
      <span class="estacion-hora">${reciente ? hora(d.fecha_hora) : `Último dato: ${fechaHora(d.fecha_hora)}`}</span>
    </li>`;
  })}</ul>`;
}
```

<details class="tabla">
  <summary>Qué significa cada categoría del IBOCA</summary>
  <table class="datos">
    <thead><tr><th scope="col">Categoría</th><th scope="col" class="num">PM2.5 (µg/m³)</th><th scope="col">Nivel de actuación</th></tr></thead>
    <tbody>
      <tr><td>${categoriaIboca("Bajo", "#00e400")}</td><td class="num">0 – 12,0</td><td>Prevención</td></tr>
      <tr><td>${categoriaIboca("Moderado", "#ffff00")}</td><td class="num">12,1 – 35,4</td><td>Prevención</td></tr>
      <tr><td>${categoriaIboca("Regular", "#ff7e00")}</td><td class="num">35,5 – 55,4</td><td>Alerta fase 1</td></tr>
      <tr><td>${categoriaIboca("Alto", "#ff0000")}</td><td class="num">55,5 – 151,2</td><td>Alerta fase 2</td></tr>
      <tr><td>${categoriaIboca("Peligroso", "#8f3f97")}</td><td class="num">151,3 o más</td><td>Emergencia</td></tr>
    </tbody>
  </table>
  <p class="fuente">Resolución conjunta 2840 de 2023 de las secretarías de Ambiente y de Salud. Los colores son los oficiales del IBOCA.</p>
</details>

<p class="fuente">Fuente: <b><a href="http://rmcab.ambientebogota.gov.co/Report/HourlyReports">RMCAB</a></b>, Secretaría Distrital de Ambiente · Corte: <span class="tnum">${fechaHora(datoMasReciente)}</span> · Cálculo del IBOCA: Observatorio Bacatá, con la metodología oficial. <a href="/metodologia#aire">Cómo se calculó</a></p>

## ¿Cómo ha cambiado el PM2.5 en cada estación?

```js
const conPm25 = catalogo.estaciones.filter((e) => e.mide_pm25 && !e.es_movil);
const selector = html`<div class="loc selector">
  <label class="loc-label" for="estacion">Estación</label>
  <div class="loc-control">
    <select id="estacion" class="loc-select">${conPm25.map((e) => html`<option value=${e.estacion_id} selected=${e.nombre === "Kennedy"}>${e.nombre} · ${e.localidad}</option>`)}</select>
  </div>
</div>`;
const estacionId = Generators.input(selector.querySelector("select"));
display(selector);
```

```js
const estacion = estaciones.get(+estacionId);
const semana = horario.filter((d) => d.estacion_id === estacion.estacion_id);
const dias = diario.filter((d) => d.estacion_id === estacion.estacion_id);
const diasConPromedio = dias.filter((d) => d.pm25 !== null);
const maximo = d3.greatest(diasConPromedio, (d) => d.pm25);
const sobreNorma = diasConPromedio.filter((d) => d.pm25 > LIMITE_NORMA).length;
const sobreOms = diasConPromedio.filter((d) => d.pm25 > GUIA_OMS).length;
```

### Los últimos 7 días, hora a hora

<ul class="leyenda-referencias" aria-label="Qué muestra cada línea">
  <li><span class="clave-linea is-fina" aria-hidden="true"></span>PM2.5 de cada hora</li>
  <li><span class="clave-linea" aria-hidden="true"></span>Promedio ponderado de 12 horas (el que usa el IBOCA)</li>
</ul>

<div class="grafico">${resize((width) => graficoSemana(width))}</div>

```js
function graficoSemana(width) {
  return Plot.plot({
    width,
    height: 220,
    marginLeft: 32,
    marginRight: 8,
    style: {fontFamily: "var(--font-body)", fontSize: "12px", color: "var(--color-text-muted)", background: "transparent"},
    ariaLabel: `PM2.5 horario de los últimos 7 días en ${estacion.nombre}`,
    x: {type: "utc", label: null, tickFormat: (d) => `${d.getUTCDate()} ${MESES[d.getUTCMonth()]}`, ticks: "day"},
    y: {label: "µg/m³", grid: true, nice: true},
    marks: [
      Plot.ruleY([0], {stroke: "var(--color-divider)", strokeOpacity: 1}),
      Plot.lineY(semana, {x: "fecha_hora", y: "pm25", stroke: "var(--data-seq-3)", strokeWidth: 1}),
      Plot.lineY(semana, {x: "fecha_hora", y: "pm25_nowcast", stroke: "var(--data-seq-6)", strokeWidth: 2}),
      Plot.tip(semana, Plot.pointerX({
        x: "fecha_hora",
        y: "pm25_nowcast",
        title: (d) => `${fechaHora(d.fecha_hora)}\nPM2.5 de la hora: ${d.pm25 === null ? "sin dato válido" : `${numero(d.pm25)} µg/m³`}\nPromedio de 12 horas: ${numero(d.pm25_nowcast)} µg/m³`
      }))
    ]
  });
}
```

### Promedio de cada día

<p>${diasConPromedio.length === 0 ? "Esta estación no tiene días con suficientes horas válidas." : `Desde el ${fecha(diasConPromedio[0].fecha)}, ${estacion.nombre} tiene ${diasConPromedio.length} días con promedio. El más alto fue el ${fecha(maximo.fecha)}, con ${numero(maximo.pm25)} µg/m³. ${sobreNorma === 0 ? `Ningún día pasó el límite diario de la norma colombiana (${LIMITE_NORMA} µg/m³)` : `${sobreNorma === 1 ? "Un día pasó" : `${sobreNorma} días pasaron`} el límite diario de la norma colombiana (${LIMITE_NORMA} µg/m³)`}, y ${sobreOms === 0 ? "ninguno pasó" : sobreOms === 1 ? "un día pasó" : `${sobreOms} días pasaron`} la guía de la OMS (${GUIA_OMS} µg/m³).`}</p>

<ul class="leyenda-referencias" aria-label="Qué muestra cada línea">
  <li><span class="clave-linea" aria-hidden="true"></span>Promedio diario de PM2.5</li>
  <li><span class="clave-linea is-norma" aria-hidden="true"></span>Límite diario de la ${termino("norma", "norma colombiana")}: ${LIMITE_NORMA} µg/m³</li>
  <li><span class="clave-linea is-oms" aria-hidden="true"></span>${termino("oms", "Guía diaria de la OMS")}: ${GUIA_OMS} µg/m³</li>
</ul>

<div class="grafico">${resize((width) => graficoDiario(width))}</div>

```js
function graficoDiario(width) {
  return Plot.plot({
    width,
    height: 240,
    marginLeft: 32,
    marginRight: 8,
    style: {fontFamily: "var(--font-body)", fontSize: "12px", color: "var(--color-text-muted)", background: "transparent"},
    ariaLabel: `Promedio diario de PM2.5 en ${estacion.nombre}`,
    x: {type: "utc", label: null, tickFormat: (d) => MESES[d.getUTCMonth()], ticks: "month"},
    y: {label: "µg/m³", ticks: [0, 15, 37], domain: [0, Math.max(45, d3.max(dias, (d) => d.pm25) ?? 0)]},
    marks: [
      Plot.ruleY([0], {stroke: "var(--color-divider)", strokeOpacity: 1}),
      Plot.ruleY([GUIA_OMS], {stroke: "var(--color-text-muted)", strokeWidth: 1.25, strokeDasharray: "4 3"}),
      Plot.ruleY([LIMITE_NORMA], {stroke: "var(--color-oro)", strokeWidth: 1.25, strokeDasharray: "4 3"}),
      Plot.lineY(dias, {x: "fecha", y: "pm25", stroke: "var(--data-seq-6)", strokeWidth: 1.5}),
      Plot.tip(dias, Plot.pointerX({
        x: "fecha",
        y: "pm25",
        title: (d) => `${fecha(d.fecha)}\n${d.pm25 === null ? "Sin promedio: pocas horas válidas" : `${numero(d.pm25)} µg/m³`}\n${d.horas_validas} de 24 horas válidas`
      }))
    ]
  });
}
```

### ¿A qué hora hay más partículas finas?

```js
const celdas = patron.filter((d) => d.estacion_id === estacion.estacion_id && d.horas >= 4);
const pico = d3.greatest(celdas, (d) => d.pm25);
```

<p>${pico ? `En los últimos 90 días, en ${estacion.nombre} el promedio más alto fue los ${["lunes","martes","miércoles","jueves","viernes","sábados","domingos"][pico.dia_semana - 1]} a las ${pico.hora}:00, con ${numero(pico.pm25)} µg/m³. Cada casilla es el promedio de esa hora en ese día de la semana.` : "No hay suficientes datos de los últimos 90 días."}</p>

<div class="grafico">${resize((width) => graficoPatron(width))}</div>

```js
function graficoPatron(width) {
  return Plot.plot({
    width,
    height: 7 * 26 + 56,
    marginLeft: 36,
    marginRight: 4,
    marginBottom: 40,
    padding: 0.06,
    style: {fontFamily: "var(--font-body)", fontSize: "12px", color: "var(--color-text-muted)", background: "transparent"},
    ariaLabel: `PM2.5 promedio por hora del día y día de la semana en ${estacion.nombre}`,
    x: {domain: d3.range(24), label: "Hora del día", tickFormat: (h) => (h % 3 === 0 ? `${h}` : "")},
    y: {domain: d3.range(1, 8), tickFormat: (d) => DIAS[d - 1], label: null},
    color: {
      type: "quantize",
      n: 5,
      range: colores("data-seq-2", "data-seq-3", "data-seq-4", "data-seq-5", "data-seq-6"),
      legend: true,
      label: "PM2.5 promedio (µg/m³)",
      tickFormat: (d) => numero(d, 0)
    },
    marks: [
      Plot.cell(celdas, {x: "hora", y: "dia_semana", fill: "pm25", inset: 0.5, tip: {format: {x: (h) => `${h}:00`, y: (d) => DIAS[d - 1], fill: (v) => `${numero(v)} µg/m³`}}})
    ]
  });
}
```

<p class="fuente">Fuente: <b><a href="http://rmcab.ambientebogota.gov.co/Report/HourlyReports">RMCAB</a></b>, Secretaría Distrital de Ambiente · Corte: <span class="tnum">${fechaHora(datoMasReciente)}</span> · <a href="/datos">Descargar los datos</a> · <a href="/metodologia#aire">Cómo se calculó</a></p>
