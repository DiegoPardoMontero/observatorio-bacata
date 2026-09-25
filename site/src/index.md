---
title: ¿Cómo estuvo el aire en agosto?
---

```js
const pm25 = FileAttachment("data/pm25_diario.csv").csv({typed: true});
```

```js
// Referencias normativas para el promedio de 24 horas
const LIMITE_NORMA = 37; // Resolución 2254 de 2017, MinAmbiente, desde el 1 jul 2018
const GUIA_OMS = 15; // Guías de calidad del aire de la OMS, 2021

const ESTACIONES = ["Kennedy", "Tunal", "Usaquén"];
const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
const fecha = (d) => `${d.getUTCDate()} ${MESES[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
const numero = (x) => x.toLocaleString("es-CO", {minimumFractionDigits: 1, maximumFractionDigits: 1});
```

```js
const localidad = new Map(pm25.map((d) => [d.estacion, d.localidad]));
// "Tunal (Tunjuelito)"; si la estación se llama como su localidad, basta el nombre
const nombre = (e) => (localidad.get(e) === e ? e : `${e} (${localidad.get(e)})`);
const dias = (n) => (n === 1 ? "un día" : `${n} días`);
const lista = (xs) => (xs.length < 2 ? xs.join("") : `${xs.slice(0, -1).join(", ")} y ${xs.at(-1)}`);
const corte = d3.max(pm25, (d) => d.fecha);
const resumen = ESTACIONES.map((estacion) => {
  const conPromedio = pm25.filter((d) => d.estacion === estacion && d.pm25 !== null);
  return {
    estacion,
    promedio: d3.mean(conPromedio, (d) => d.pm25),
    maximo: d3.greatest(conPromedio, (d) => d.pm25),
    sobreOms: conPromedio.filter((d) => d.pm25 > GUIA_OMS).length,
    sobreNorma: conPromedio.filter((d) => d.pm25 > LIMITE_NORMA).length
  };
});
```

```js
// Resumen en texto del gráfico (RNF-05): la respuesta primero, después las cifras
function respuesta() {
  const norma = resumen.filter((r) => r.sobreNorma > 0);
  const oms = resumen.filter((r) => r.sobreOms > 0);
  const frases = [
    norma.length === 0
      ? `No. Ninguna de las tres estaciones pasó el límite diario de la norma colombiana, que es de ${LIMITE_NORMA} µg/m³.`
      : `Sí. El límite diario de la norma colombiana (${LIMITE_NORMA} µg/m³) lo ${norma.length === 1 ? "pasó" : "pasaron"} ${lista(norma.map((r) => `${r.estacion} ${dias(r.sobreNorma)}`))}.`,
    oms.length === 0
      ? `Tampoco pasaron la guía de la OMS, que es más estricta (${GUIA_OMS} µg/m³).`
      : `La guía de la OMS, que es más estricta (${GUIA_OMS} µg/m³), la ${oms.length === 1 ? "pasó" : "pasaron"} ${lista(oms.map((r) => `${r.estacion} ${dias(r.sobreOms)}`))}.`
  ];
  return html`<p>${frases.join(" ")}</p>
    <ul class="cifras">${resumen.map((r) => html`<li><b>${nombre(r.estacion)}:</b> promedio del mes de ${numero(r.promedio)} µg/m³. El día más alto fue el ${fecha(r.maximo.fecha)}, con ${numero(r.maximo.pm25)}.</li>`)}</ul>`;
}
```

<div class="notice" data-tone="info" role="status">
  <svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
  <div>
    <p class="notice-title">Página de prueba</p>
    <p class="notice-body">El Observatorio está en construcción. Esta página muestra un mes cerrado, no el aire de hoy.</p>
  </div>
</div>

# ¿Cómo estuvo el aire en agosto?

<p class="entradilla">Las partículas finas (PM2.5) son el contaminante del aire que más afecta la salud: son tan pequeñas que llegan hasta los pulmones. Estas son tres de las 19 estaciones de la red de monitoreo de Bogotá, una en el norte, una en el suroccidente y una en el sur.</p>

## ¿Algún día de agosto pasó el límite de partículas finas?

<div class="respuesta">${respuesta()}</div>

<ul class="leyenda-referencias" aria-label="Qué muestra cada línea">
  <li><span class="clave-linea" aria-hidden="true"></span>Promedio diario de PM2.5</li>
  <li><span class="clave-linea is-norma" aria-hidden="true"></span>Límite diario de la norma colombiana: ${LIMITE_NORMA} µg/m³</li>
  <li><span class="clave-linea is-oms" aria-hidden="true"></span>Guía diaria de la OMS: ${GUIA_OMS} µg/m³</li>
</ul>

<div class="grafico">${resize((width) => grafico(width))}</div>

<p class="fuente">Fuente: <b><a href="http://rmcab.ambientebogota.gov.co/Report/HourlyReports">RMCAB</a></b>, Secretaría Distrital de Ambiente · Corte: <span class="tnum">${fecha(corte)}</span> · Cifras en µg/m³ · <a href="data/pm25_diario.csv" download="pm25_diario_agosto_2026.csv">Descargar los datos (CSV)</a></p>

```js
function grafico(width) {
  return Plot.plot({
    width,
    height: ESTACIONES.length * 130 + 32,
    marginTop: 8,
    marginLeft: 28,
    marginRight: 8,
    marginBottom: 28,
    style: {fontFamily: "var(--font-body)", fontSize: "12px", color: "var(--color-text-muted)", background: "transparent"},
    ariaLabel: "Promedio diario de PM2.5 en agosto de 2026 en Kennedy, Tunal y Usaquén",
    fy: {domain: ESTACIONES, axis: null, padding: 0.22},
    x: {
      type: "utc",
      domain: [new Date("2026-08-01"), new Date("2026-08-31")],
      ticks: [1, 8, 15, 22, 29].map((dia) => new Date(Date.UTC(2026, 7, dia))),
      tickFormat: (d) => `${d.getUTCDate()} ago`,
      label: null
    },
    y: {domain: [0, 47], ticks: [0, 15, 37], label: null},
    marks: [
      Plot.ruleY([0], {stroke: "var(--color-divider)", strokeOpacity: 1}),
      Plot.ruleY([GUIA_OMS], {stroke: "var(--color-text-muted)", strokeWidth: 1.25, strokeDasharray: "4 3"}),
      Plot.ruleY([LIMITE_NORMA], {stroke: "var(--color-oro)", strokeWidth: 1.25, strokeDasharray: "4 3"}),
      Plot.lineY(pm25, {x: "fecha", y: "pm25", fy: "estacion", stroke: "var(--data-seq-6)", strokeWidth: 2}),
      Plot.dot(resumen, {x: (r) => r.maximo.fecha, y: (r) => r.maximo.pm25, fy: "estacion", r: 4, fill: "var(--data-seq-6)", stroke: "var(--color-bg)", strokeWidth: 2}),
      Plot.text(resumen, {
        x: (r) => r.maximo.fecha,
        y: (r) => r.maximo.pm25,
        fy: "estacion",
        text: (r) => `Máx. ${numero(r.maximo.pm25)}`,
        // A la izquierda del punto, para que un máximo a fin de mes no se salga por la derecha
        textAnchor: "end",
        dx: -7,
        dy: -9,
        fill: "var(--color-text)",
        stroke: "var(--color-bg)",
        strokeWidth: 3,
        fontSize: 11
      }),
      Plot.text(ESTACIONES, {fy: (d) => d, text: nombre, frameAnchor: "top-left", dx: 2, fill: "var(--color-text)", stroke: "var(--color-bg)", strokeWidth: 3, fontSize: 13, fontWeight: 600}),
      Plot.tip(pm25, Plot.pointerX({
        x: "fecha",
        y: "pm25",
        fy: "estacion",
        title: (d) => `${d.estacion}, ${fecha(d.fecha)}\n${d.pm25 === null ? "Sin promedio: pocas horas válidas" : `${numero(d.pm25)} µg/m³`}\n${d.horas_validas} de 24 horas válidas`
      }))
    ]
  });
}
```

<details class="tabla">
  <summary>Ver los datos en una tabla</summary>
  ${tabla()}
</details>

```js
function tabla() {
  const porDia = d3.groups(pm25, (d) => +d.fecha);
  return html`<table>
    <caption class="fuente">Promedio diario de PM2.5 (µg/m³). Un guion indica que ese día no tuvo suficientes horas válidas.</caption>
    <thead><tr><th scope="col">Día</th>${ESTACIONES.map((e) => html`<th scope="col">${e}</th>`)}</tr></thead>
    <tbody>${porDia.map(([, filas]) => html`<tr>
      <th scope="row" class="tnum">${fecha(filas[0].fecha)}</th>
      ${ESTACIONES.map((e) => {
        const fila = filas.find((d) => d.estacion === e);
        return html`<td class="num">${fila?.pm25 == null ? "–" : numero(fila.pm25)}</td>`;
      })}
    </tr>`)}</tbody>
  </table>`;
}
```

<h2 id="como-se-calculo">Cómo se calculó</h2>

- **Fuente:** el [reporte horario de la RMCAB](http://rmcab.ambientebogota.gov.co/Report/HourlyReports), la red de monitoreo de la Secretaría Distrital de Ambiente. Lo descargamos un día a la vez.
- **Horas válidas:** usamos solo las horas que el portal marca como válidas. Las horas con valor −9999 o con otro código de estado se descartan.
- **Promedio diario:** es el promedio de las horas válidas de ese día, de la 01:00 a la medianoche, porque la fuente marca cada hora por su final. Si un día tiene menos de 18 horas válidas (75 %, la regla del portal), no calculamos su promedio.
- **Referencias:** el límite de ${LIMITE_NORMA} µg/m³ para 24 horas es el de la Resolución 2254 de 2017 del Ministerio de Ambiente, vigente desde el 1 de julio de 2018. La guía de ${GUIA_OMS} µg/m³ es la de la Organización Mundial de la Salud (2021).
- **Limitaciones:** cada estación mide el aire de su entorno. No es el promedio de la localidad ni de la ciudad.
