// Configuración del sitio. Documentación: https://observablehq.com/framework/config
import {existsSync} from "node:fs";

// Los data loaders en Python usan el entorno del proyecto si existe (.venv en la
// raíz del repo); en CI, el python3 donde se instaló el paquete.
const python = process.env.PYTHON ?? (existsSync("../.venv/bin/python") ? "../.venv/bin/python" : "python3");

export default {
  title: "Observatorio Bacatá",
  root: "src",
  // Se publica en https://diegopardomontero.github.io/observatorio-bacata/
  base: "/observatorio-bacata/",
  style: "estilo/bacata.css",
  interpreters: {".py": [python]},
  head: '<meta name="description" content="Los datos abiertos de Bogotá, claros y por localidad.">',
  header: `<a class="marca" href="./" aria-label="Observatorio Bacatá, inicio">
    <span class="marca-sup">Observatorio</span>
    <span class="marca-nombre">Bacatá</span>
  </a>
  <a class="nav-enlace" href="#como-se-calculo">Metodología</a>`,
  footer: `Datos abiertos de Bogotá · Sitio gratuito ·
    <a href="https://github.com/DiegoPardoMontero/observatorio-bacata">Código</a> bajo MIT,
    datos derivados bajo CC BY-SA 4.0`,
  sidebar: false,
  toc: false,
  pager: false,
  search: false
};
