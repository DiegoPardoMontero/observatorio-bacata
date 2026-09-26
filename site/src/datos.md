---
title: Datos abiertos
---

```js
import {fecha, fechaHora} from "./components/formato.js";
import {icono} from "./components/ui.js";

const catalogo = FileAttachment("data/catalogo.json").json();
```

```js
const rmcab = catalogo.fuentes.find((f) => f.fuente_id === "rmcab");
const corte = fechaHora(new Date(rmcab.dato_mas_reciente));
```

# Datos abiertos

<p class="entradilla">Todo lo que ves en el sitio se puede descargar, con la misma fuente y la misma fecha de corte. Puedes reutilizarlo citando al Observatorio Bacatá y a la fuente original.</p>

<ul class="descargas">
  <li>
    <a href="data/indicadores.csv" download="bacata_indicadores_localidad_mes.csv">${icono("descargar")}Indicadores por localidad y mes (CSV)</a>
    <p>Un valor por localidad, mes e indicador, con el de toda Bogotá al lado. Es la tabla que alimenta el mapa y las fichas. Corte: ${corte}.</p>
  </li>
  <li>
    <a href="data/pm25_diario.csv" download="bacata_pm25_diario.csv">${icono("descargar")}PM2.5 diario por estación (CSV)</a>
    <p>Promedio de cada día en cada estación de la RMCAB desde enero de 2026, con las horas válidas de ese día. Corte: ${corte}.</p>
  </li>
  <li>
    <a href="data/pm25_horario.csv" download="bacata_pm25_horario_7_dias.csv">${icono("descargar")}PM2.5 horario de los últimos 7 días (CSV)</a>
    <p>El dato de cada hora y el promedio ponderado de 12 horas que usa el IBOCA. Corte: ${corte}.</p>
  </li>
  <li>
    <a href="data/gold.zip" download="bacata_gold.zip">${icono("descargar")}Dataset completo (Parquet, zip)</a>
    <p>Todas las tablas Gold: dimensiones de localidad, estación e indicador; población por localidad y año de 2005 a 2035; calendario con los festivos de Colombia; aire por hora, por día y con IBOCA; indicadores por localidad y mes, y estado de las fuentes. Unos 6 MB.</p>
  </li>
</ul>

## Cómo leer los archivos

- Las fechas y horas están en hora de Bogotá (UTC−5). En los CSV, las horas llevan una "Z" al final por formato, pero son de Bogotá: `2026-09-25T09:00:00Z` son las 9 a. m. en Bogotá y es la hora que va de 9:00 a 10:00.
- Los decimales usan punto. Los valores vacíos son datos que faltan o que la fuente no marcó como válidos.
- Los códigos de localidad son los oficiales, de `01` (Usaquén) a `20` (Sumapaz).

## Licencia

Los datos derivados se publican bajo [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es), porque varias fuentes son *share-alike*. Cita así: *Observatorio Bacatá, con datos de la RMCAB (Secretaría Distrital de Ambiente)*. El código del sitio está bajo licencia MIT en [GitHub](https://github.com/DiegoPardoMontero/observatorio-bacata).
