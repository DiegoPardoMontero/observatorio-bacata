// Formatos es-CO del sistema de diseño: 1.284,5 · 92,4 % · 24 sep 2026.
//
// Las horas de los datos son de Bogotá y llegan marcadas como UTC ("…T09:00:00Z" son las
// 9 a. m. en Bogotá; ver site/src/data/_gold.py). Por eso todo se formatea en UTC.

export const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
export const MESES_LARGOS = [
  "enero", "febrero", "marzo", "abril", "mayo", "junio",
  "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
];
export const DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"];

const HORA_BOGOTA_MS = 5 * 60 * 60 * 1000;

/** Ahora, en hora de Bogotá con la misma convención que los datos. */
export function ahoraBogota() {
  return new Date(Date.now() - HORA_BOGOTA_MS);
}

export function fecha(d) {
  return `${d.getUTCDate()} ${MESES[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

export function mes(d) {
  return `${MESES_LARGOS[d.getUTCMonth()]} de ${d.getUTCFullYear()}`;
}

export function hora(d) {
  const h = d.getUTCHours();
  const h12 = h % 12 === 0 ? 12 : h % 12;
  return `${h12}:00 ${h < 12 ? "a. m." : "p. m."}`;
}

export function fechaHora(d) {
  return `${fecha(d)}, ${hora(d)}`;
}

export function numero(x, decimales = 1) {
  if (x == null || Number.isNaN(x)) return "–";
  return x.toLocaleString("es-CO", {minimumFractionDigits: decimales, maximumFractionDigits: decimales});
}

export function porcentaje(x, decimales = 0) {
  return x == null ? "–" : `${numero(x, decimales)} %`;
}

/** "hace 2 horas", "hace 3 días", para el aviso de datos retrasados. */
export function hace(d, ahora = ahoraBogota()) {
  const horas = Math.floor((ahora - d) / 3.6e6);
  if (horas < 1) return "hace menos de una hora";
  if (horas < 48) return horas === 1 ? "hace una hora" : `hace ${horas} horas`;
  const dias = Math.floor(horas / 24);
  return `hace ${dias} días`;
}

/** Quita tildes y mayúsculas para buscar ("bolivar" encuentra "Ciudad Bolívar"). */
export function normalizar(texto) {
  return texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
}

/**
 * d3.autoType convierte el código de localidad "08" en el número 8. Esto lo devuelve a su
 * forma oficial de dos dígitos, que es la que usan el catálogo y los polígonos.
 */
export function conCodigo(fila) {
  return {...fila, localidad_id: String(fila.localidad_id).padStart(2, "0")};
}

/** ["a", "b", "c"] -> "a, b y c". */
export function lista(xs) {
  return xs.length < 2 ? xs.join("") : `${xs.slice(0, -1).join(", ")} y ${xs.at(-1)}`;
}
