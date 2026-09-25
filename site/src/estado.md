---
title: Estado de los datos
---

```js
import {ahoraBogota, fechaHora, hace, numero} from "./components/formato.js";
import {aviso} from "./components/ui.js";

const catalogo = FileAttachment("data/catalogo.json").json();
```

```js
const construido = new Date(catalogo.construido);
const fuentes = catalogo.fuentes.map((f) => {
  const dato = new Date(f.dato_mas_reciente);
  return {...f, dato, extraccion: new Date(f.ultima_extraccion), retrasado: ahoraBogota() - dato > f.limite_retraso_horas * 3.6e6};
});
const retrasadas = fuentes.filter((f) => f.retrasado);
const sitioViejo = ahoraBogota() - construido > 3 * 3.6e6;
```

# Estado de los datos

<p class="entradilla">Cuándo se cargó cada fuente y si alguna llega con retraso. El sitio se vuelve a construir cada hora.</p>

```js
if (sitioViejo) {
  display(html`<div class="avisos">${aviso({
    titulo: "El sitio no se ha actualizado",
    cuerpo: `La última construcción fue ${hace(construido)} (${fechaHora(construido)}). Debería ocurrir cada hora; puede haber un problema con el proceso automático.`,
    enlace: "https://github.com/DiegoPardoMontero/observatorio-bacata/actions",
    textoEnlace: "Ver las últimas ejecuciones"
  })}</div>`);
}
for (const f of retrasadas) {
  display(html`<div class="avisos">${aviso({
    titulo: `${f.fuente}: datos con retraso`,
    cuerpo: `El dato más reciente es de ${fechaHora(f.dato)}, ${hace(f.dato)}. Esperábamos uno nuevo ${f.periodicidad.toLowerCase()}; mientras llega, el sitio muestra el más reciente.`
  })}</div>`);
}
```

<p>Última construcción del sitio: <span class="tnum">${fechaHora(construido)}</span> (${hace(construido)}). ${retrasadas.length === 0 ? "Todas las fuentes están al día." : `${retrasadas.length === 1 ? "Una fuente llega" : `${retrasadas.length} fuentes llegan`} con retraso.`}</p>

<div class="tabla-desplazable">
<table class="datos">
  <thead><tr><th scope="col">Fuente</th><th scope="col">Periodicidad</th><th scope="col">Última carga</th><th scope="col">Dato más reciente</th><th scope="col">Estado</th></tr></thead>
  <tbody>${fuentes.map((f) => html`<tr>
    <th scope="row">${f.fuente}<br><span class="fuente">${f.contenido}</span></th>
    <td>${f.periodicidad}</td>
    <td class="tnum">${fechaHora(f.extraccion)}</td>
    <td class="tnum">${fechaHora(f.dato)}</td>
    <td><span class="estado-fuente" data-estado=${f.retrasado ? "retrasado" : "al-dia"}>${f.retrasado ? "Con retraso" : "Al día"}</span></td>
  </tr>`)}</tbody>
</table>
</div>

<p class="fuente">Una fuente se considera con retraso si su dato más reciente tiene más de 3 horas (aire, según el requisito de frescura del proyecto) o si pasan 60 días sin un corte nuevo (seguridad, que publica cada mes). El historial de ejecuciones está en <a href="https://github.com/DiegoPardoMontero/observatorio-bacata/actions">GitHub Actions</a>.</p>
