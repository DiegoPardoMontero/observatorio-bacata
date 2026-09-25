// Buscador de localidad (RF-02): combobox que filtra las 20 localidades al escribir, sin
// distinguir tildes ni mayúsculas, con máximo 5 sugerencias. Flechas, Enter y Escape.
import {html} from "npm:htl";
import {normalizar} from "./formato.js";
import {icono} from "./ui.js";

const MAXIMO = 5;

export function buscador(localidades, {base = ".", etiqueta = "Busca tu localidad", id = "buscar-localidad"} = {}) {
  const entrada = html`<input id=${id} type="search" autocomplete="off" role="combobox" aria-autocomplete="list"
    aria-expanded="false" aria-controls=${`${id}-lista`} placeholder="Ej.: Kennedy, Suba…">`;
  const lista = html`<ul id=${`${id}-lista`} class="sugerencias" role="listbox" hidden></ul>`;
  const vacio = html`<p class="sin-coincidencias" hidden>No encontramos esa localidad. Prueba con otro nombre.</p>`;
  let activa = -1;

  function opciones() {
    return [...lista.querySelectorAll("a")];
  }

  function marcar(indice) {
    const todas = opciones();
    activa = todas.length === 0 ? -1 : (indice + todas.length) % todas.length;
    todas.forEach((a, i) => a.setAttribute("aria-selected", String(i === activa)));
    entrada.setAttribute("aria-activedescendant", activa >= 0 ? todas[activa].id : "");
  }

  function actualizar() {
    const texto = normalizar(entrada.value);
    const coinciden = texto ? localidades.filter((l) => normalizar(l.nombre).includes(texto)).slice(0, MAXIMO) : [];
    lista.replaceChildren(
      ...coinciden.map((l, i) => html`<li role="presentation"><a id=${`${id}-op-${i}`} role="option" aria-selected="false"
        href=${`${base}/localidad/${l.slug}`}><span>${l.nombre}</span><span class="codigo">Localidad ${l.localidad_id}</span></a></li>`)
    );
    lista.hidden = coinciden.length === 0;
    vacio.hidden = !texto || coinciden.length > 0;
    entrada.setAttribute("aria-expanded", String(!lista.hidden));
    activa = -1;
  }

  entrada.addEventListener("input", actualizar);
  entrada.addEventListener("keydown", (evento) => {
    if (evento.key === "ArrowDown") (evento.preventDefault(), marcar(activa + 1));
    else if (evento.key === "ArrowUp") (evento.preventDefault(), marcar(activa - 1));
    else if (evento.key === "Enter") {
      const destino = opciones()[activa >= 0 ? activa : 0];
      if (destino) (evento.preventDefault(), (location.href = destino.href));
    } else if (evento.key === "Escape") {
      entrada.value = "";
      actualizar();
    }
  });

  return html`<div class="buscador">
    <label for=${id}>${etiqueta}</label>
    <div class="loc-control">${icono("buscar")}${entrada}</div>
    ${lista}${vacio}
  </div>`;
}
