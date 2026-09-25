---
title: Los datos de tu localidad, claros y gratis
---

```js
import {fecha, hora, numero, MESES_LARGOS, conCodigo} from "./components/formato.js";
import {tarjetaIndicador, tarjetaProximamente, icono} from "./components/ui.js";
import {buscador} from "./components/buscador.js";

const catalogo = FileAttachment("data/catalogo.json").json();
const indicadores = (await FileAttachment("data/indicadores.csv").csv({typed: true})).map(conCodigo);
const estado = FileAttachment("data/estado_aire.json").json();
```

```js
// RF-01: PM2.5 de la ciudad en el mes en curso, frente al mes anterior
const porMes = d3
  .groups(indicadores.filter((d) => d.indicador_id === "aire_pm25_promedio"), (d) => +d.mes)
  .map(([, filas]) => ({mes: filas[0].mes, valor: filas[0].valor_ciudad, corte: d3.max(filas, (d) => d.fecha_corte_fuente)}))
  .sort((a, b) => a.mes - b.mes);
const actual = porMes.at(-1);
const anterior = porMes.at(-2);
const diferencia = anterior ? actual.valor - anterior.valor : null;
const tendencia =
  diferencia === null
    ? null
    : {
        direccion: Math.abs(diferencia) < 0.5 ? "igual" : diferencia > 0 ? "sube" : "baja",
        texto: `${Math.abs(diferencia) < 0.5 ? "" : `${numero(Math.abs(diferencia))} `}frente a ${MESES_LARGOS[anterior.mes.getUTCMonth()]}`
      };

const ultimaHora = d3.max(estado, (d) => new Date(d.fecha_hora));
const ahora = d3.rollup(estado.filter((d) => +new Date(d.fecha_hora) === +ultimaHora), (v) => v.length, (d) => d.iboca_categoria);
const resumenAhora = [...ahora].sort((a, b) => d3.descending(a[1], b[1])).map(([c, n]) => `${n} en ${c.toLowerCase()}`);
```

# Los datos de tu localidad, claros y gratis

<p class="entradilla">Cifras públicas de Bogotá, contadas localidad por localidad. Cada dato dice de dónde viene y hasta qué fecha llega.</p>

${buscador(catalogo.localidades)}

<p class="fuente">O elige en el <a href="/mapa">mapa</a> entre las 20 localidades.</p>

<div class="seccion-encabezado"><h2>Toda Bogotá</h2><span>4 temas</span></div>

<div class="tarjetas tarjetas-4">
  ${tarjetaIndicador({
    kicker: "Aire",
    icono: "aire",
    titulo: "Partículas finas en el aire",
    valor: numero(actual.valor),
    unidad: "µg/m³ de PM2.5",
    frase: `Promedio de la ciudad en ${MESES_LARGOS[actual.mes.getUTCMonth()]}, hasta el ${fecha(actual.corte)}. Cuanto más bajo, más limpio el aire.`,
    tendencia,
    comparacion: resumenAhora.length ? `Ahora, a las ${hora(ultimaHora)}: ${resumenAhora.join(" y ")} según el IBOCA.` : null,
    fuente: "RMCAB",
    corte: fecha(actual.corte),
    enlace: "./aire"
  })}
  ${tarjetaProximamente({kicker: "Movilidad", icono: "movilidad", subtitulo: "Tiempos de viaje"})}
  ${tarjetaProximamente({kicker: "Seguridad", icono: "seguridad", subtitulo: "Convivencia y seguridad"})}
  ${tarjetaProximamente({kicker: "Costo de vida", icono: "costo", subtitulo: "Precios del hogar"})}
</div>

<a class="acceso-mapa" href="./mapa">
  <span class="acceso-mapa-titulo">${icono("mapa")}<span>Ver el mapa</span>${icono("flecha")}</span>
  <p>Compara las 20 localidades de un vistazo.</p>
  <span class="tira-escala" aria-hidden="true">
    <span style="background: var(--data-seq-2)"></span><span style="background: var(--data-seq-3)"></span><span style="background: var(--data-seq-4)"></span><span style="background: var(--data-seq-5)"></span><span style="background: var(--data-seq-6)"></span>
  </span>
</a>
