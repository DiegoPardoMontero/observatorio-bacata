---
title: Metodología
---

```js
import {fechaHora, lista} from "./components/formato.js";

const catalogo = FileAttachment("data/catalogo.json").json();
```

```js
const fuente = (id) => catalogo.fuentes.find((f) => f.fuente_id === id);
const rmcab = fuente("rmcab");
const sinEstacion = catalogo.localidades.filter((l) => l.n_estaciones_aire === 0);
const conMovil = new Set(catalogo.estaciones.filter((e) => e.es_movil).map((e) => e.localidad_id));
```

# Metodología

<p class="entradilla">De dónde viene cada cifra, qué le hacemos y qué no se puede concluir con ella. El código completo está en <a href="https://github.com/DiegoPardoMontero/observatorio-bacata">GitHub</a>.</p>

## Cómo funciona el sitio

Cada hora, un proceso automático descarga los datos de las fuentes, los limpia y prueba, calcula los indicadores y vuelve a publicar el sitio. Si una prueba de calidad falla, no se publica nada nuevo y queda la versión anterior. Si una fuente no responde, se publica con lo que hay y el sitio avisa del retraso. Puedes ver cuándo fue la última carga en [Estado de los datos](/estado).

<h2 id="aire">Aire</h2>

**Fuente.** El [reporte horario de la RMCAB](http://rmcab.ambientebogota.gov.co/Report/HourlyReports), la Red de Monitoreo de Calidad del Aire de la Secretaría Distrital de Ambiente. Tiene 19 estaciones, dos de ellas móviles. La fuente no tiene API: leemos el reporte de cada día en el portal. Última carga: ${fechaHora(new Date(rmcab.ultima_extraccion))}. Dato más reciente: ${fechaHora(new Date(rmcab.dato_mas_reciente))}. La licencia de estos datos está por confirmar con la Secretaría.

**Qué hacemos con los datos**

- **Horas válidas.** Usamos solo las horas que el portal marca como válidas. Las que vienen con −9999 o con otro código de estado se descartan.
- **La hora.** El portal marca cada hora por su final: el dato de las 10:00 es el promedio de 9:00 a 10:00. En el sitio, cada hora se nombra por su inicio y está en hora de Bogotá.
- **Promedio diario.** Es el promedio de las horas válidas del día. Si un día tiene menos de 18 horas válidas (75 %, la regla del portal), no calculamos su promedio.
- **IBOCA.** Seguimos la [Resolución conjunta 2840 de 2023](https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=152203) de las secretarías de Ambiente y de Salud. Para PM2.5 se usa el promedio ponderado (NowCast) de las últimas 12 horas, incluida la actual. El peso es *w* = mínimo ÷ máximo de esas 12 horas, con un piso de 0,5, y cada hora hacia atrás pesa *w* veces menos que la siguiente. Hace falta dato en al menos 2 de las 3 horas más recientes. La resolución no dice cómo redondear: truncamos a un decimal, como hace la EPA de Estados Unidos, en la que se basa el método. El valor cae en una categoría según la Tabla 1 de la resolución. Los colores son los oficiales del IBOCA, y la categoría siempre va escrita.
- **Por localidad.** Una estación entra en el promedio del mes si tiene promedio diario en al menos el 75 % de los días del mes, o de los días transcurridos si el mes está en curso. El día en curso entra cuando completa 18 horas válidas, hacia las 7 p. m., y su promedio se sigue ajustando hasta medianoche. El valor de la localidad es el promedio de sus estaciones fijas, y el de Bogotá, el de todas. Las estaciones móviles no se usan en los promedios, porque cambian de sitio.
- **Referencias.** El límite de 37 µg/m³ para el promedio de 24 horas es el de la [Resolución 2254 de 2017](https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=82634) del Ministerio de Ambiente, vigente desde el 1 de julio de 2018. La guía de 15 µg/m³ es la de la Organización Mundial de la Salud (2021).

**Limitaciones**

- Cada estación mide el aire de su entorno. **${sinEstacion.length} localidades no tienen estación fija**: ${lista(sinEstacion.map((l) => (conMovil.has(l.localidad_id) ? `${l.nombre} (solo una móvil)` : l.nombre)))}. En ellas decimos "sin medición". No estimamos su aire con el de otras zonas, porque daría una precisión que no existe.
- Las localidades con una sola estación dependen de lo que pase alrededor de ese punto.
- El histórico empieza en enero de 2026. Algunas estaciones tienen meses con pocos datos válidos, por ejemplo Ciudad Bolívar, y esos meses no entran en los promedios.
- Todavía no sabemos qué significa cada código de estado del portal. Se lo preguntamos a la Secretaría de Ambiente.

<h2 id="seguridad">Seguridad</h2>

En preparación. La fuente es [Delito de Alto Impacto](https://datosabiertos.bogota.gov.co/dataset/delito-de-alto-impacto-bogota-d-c), de la Secretaría de Seguridad (CC BY-SA 4.0), y ya la descargamos todos los días. Antes de publicarla faltan tres cosas:

1. La población de cada localidad por año, para mostrar tasas por 100.000 habitantes y no conteos, que harían ver peor a las localidades más pobladas.
2. Que la Secretaría aclare por qué tres tipos de hurto no cuadran entre sus dos archivos. Ya se lo preguntamos.
3. Una serie mensual: la fuente publica acumulados del año y no meses.

Cuando se publique, seguirá estas reglas: siempre tasas, nunca rankings de "localidades peligrosas", cada localidad comparada primero consigo misma, un aviso de que son delitos registrados y nada por debajo de localidad.

<h2 id="movilidad">Movilidad</h2>

En preparación. Ya descargamos todos los días las víctimas de siniestros viales de la [Secretaría Distrital de Movilidad](https://datos.movilidadbogota.gov.co/search?tags=siniestralidad) (base SIGAT) desde 2021: cada persona muerta o herida, con la localidad donde ocurrió el siniestro y si iba a pie, en bicicleta, en moto, manejando o como pasajero. Las cifras por localidad ya están en el [dataset completo](/datos). No descargamos el género, la edad ni la dirección de las víctimas.

Antes de mostrarlas en el sitio falta decidir cómo comparar localidades. Un siniestro se cuenta donde ocurrió y no donde vive la víctima, así que una tasa por habitantes haría ver peor a las localidades céntricas, con grandes vías y poca población, aunque sus vecinos no sean los afectados. Además, los dos meses más recientes se siguen digitando: las cifras de esos meses todavía van a subir.

Las validaciones de TransMilenio por estación también están al día, y serán lo siguiente.

<h2 id="costo">Costo de vida</h2>

En exploración. El índice de precios al consumidor del DANE no tiene detalle por localidad.

<h2 id="poblacion">Población</h2>

**Fuente.** Las proyecciones y retroproyecciones de población de 2005 a 2035 por localidad que hicieron el DANE, la Secretaría Distrital de Planeación y la Región Metropolitana Bogotá-Cundinamarca, publicadas en agosto de 2025. Las tomamos del archivo que publica la Secretaría Distrital de Salud en [Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/dataset/piramide-poblacional-bogota-d-c) (CC BY 4.0), que trae la población por localidad, año, sexo y edad. Sumamos sexos y edades.

**Para qué la usamos.** Es el denominador de las tasas por 100.000 habitantes, que son la única forma en que el sitio mostrará temas como la seguridad: comparar conteos haría ver peor a las localidades más pobladas. Por ahora aparece en las fichas de cada localidad.

**Limitaciones**

- Todos los años son estimaciones, incluidos los anteriores al último censo (2018). Si el DANE publica una revisión, las tasas de años pasados pueden cambiar.
- Antes de usarla verificamos que estén las 20 localidades en cada año y que su suma dé exactamente el total de Bogotá.
- La Secretaría de Planeación publica otra versión, de marzo de 2025. Hasta 2017 las dos son idénticas. De 2018 a 2026, casi todas las localidades difieren menos de 4 %; las excepciones son Los Mártires (la versión de agosto da hasta 11 % menos) y Sumapaz (hasta 9 % menos). Usamos la más reciente.

## Mapas

Los polígonos de las localidades son los de [Catastro Distrital (IDECA)](https://datosabiertos.bogota.gov.co/dataset/localidad-bogota-d-c), CC BY 4.0, con datos de 2022. Los simplificamos para que el mapa cargue rápido desde el celular, sin cambiar los bordes entre localidades vecinas.
