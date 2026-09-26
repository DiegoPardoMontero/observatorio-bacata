// Términos técnicos explicados al pasar el cursor o al tocar (RNF-11).
//
// Cada término es un botón con la definición en una burbuja. Pasar el cursor la muestra
// mientras dura; tocar, hacer clic o Enter la dejan fija hasta que se vuelve a tocar, se
// pulsa Escape, se toca fuera o el foco sale del término. La definición
// también es la descripción accesible del botón, así que un lector de pantalla la lee sin
// abrir nada. La burbuja se puede recorrer con el cursor (WCAG 1.4.13).
import {html} from "npm:htl";

export const GLOSARIO = {
  pm25: "Partículas en el aire de menos de 2,5 micras, unas 30 veces más delgadas que un cabello. Llegan hasta los pulmones y la sangre. Vienen sobre todo del tráfico, la industria y las quemas.",
  microgramos: "Microgramos por metro cúbico: cuántas millonésimas de gramo de partículas hay en un metro cúbico de aire.",
  iboca: "Índice Bogotano de Calidad del Aire y Riesgo en Salud. Traduce la contaminación a cinco categorías, de Bajo a Peligroso, cada una con sus recomendaciones. Lo definen las secretarías de Ambiente y de Salud.",
  nowcast: "Promedio de las últimas 12 horas que pesa más las recientes. Así el índice reacciona rápido cuando el aire empeora, pero no salta por una sola hora atípica.",
  oms: "La Organización Mundial de la Salud recomienda que el promedio de 24 horas de PM2.5 no pase de 15 µg/m³ más de 3 o 4 días al año. Es más exigente que la norma colombiana.",
  norma: "La Resolución 2254 de 2017 del Ministerio de Ambiente fija 37 µg/m³ como máximo para el promedio de 24 horas de PM2.5.",
  mediana: "El valor del medio: la mitad de las localidades con medición está por encima y la otra mitad por debajo. A diferencia del promedio, no la mueve una localidad con un valor extremo.",
  proyeccion: "Estimación de cuántas personas viven en cada localidad cada año, hecha a partir del último censo (2018) con los nacimientos, las muertes y las migraciones."
};

const MARGEN = 8;
let contador = 0;
let abierto = null;

function cerrar() {
  if (!abierto) return;
  abierto.boton.setAttribute("aria-expanded", "false");
  abierto.burbuja.hidden = true;
  abierto = null;
}

function abrir(boton, burbuja, fijo) {
  if (abierto?.burbuja === burbuja) {
    abierto.fijo ||= fijo;
    return;
  }
  cerrar();
  burbuja.style.left = "0";
  burbuja.hidden = false;
  boton.setAttribute("aria-expanded", "true");
  abierto = {boton, burbuja, fijo};
  // Que no se salga por la derecha en pantallas angostas
  const {left, right} = burbuja.getBoundingClientRect();
  const ancho = document.documentElement.clientWidth;
  let desplazamiento = Math.min(0, ancho - MARGEN - right);
  if (left + desplazamiento < MARGEN) desplazamiento = MARGEN - left;
  burbuja.style.left = `${desplazamiento}px`;
}

if (typeof document !== "undefined") {
  document.addEventListener("keydown", (e) => e.key === "Escape" && cerrar());
  document.addEventListener("click", (e) => abierto && !e.target.closest(".termino") && cerrar());
}

/** termino("pm25", "PM2.5"): el texto visible es el segundo argumento (o la clave). */
export function termino(clave, texto = clave) {
  const definicion = GLOSARIO[clave];
  if (!definicion) throw new Error(`Término sin definición: ${clave}`);
  const id = `termino-${++contador}`;
  const burbuja = html`<span class="termino-def" id=${id} role="tooltip" hidden>${definicion}</span>`;
  const boton = html`<button type="button" class="termino-boton" aria-expanded="false" aria-describedby=${id}>${texto}</button>`;
  const envoltura = html`<span class="termino">${boton}${burbuja}</span>`;
  boton.addEventListener("click", () => (abierto?.burbuja === burbuja && abierto.fijo ? cerrar() : abrir(boton, burbuja, true)));
  if (matchMedia("(hover: hover)").matches) {
    envoltura.addEventListener("mouseenter", () => abrir(boton, burbuja, false));
    envoltura.addEventListener("mouseleave", () => abierto?.burbuja === burbuja && !abierto.fijo && cerrar());
  }
  envoltura.addEventListener("focusout", (e) => !envoltura.contains(e.relatedTarget) && abierto?.burbuja === burbuja && cerrar());
  return envoltura;
}
