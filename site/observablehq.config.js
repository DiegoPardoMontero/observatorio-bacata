// Configuración del sitio. Documentación: https://observablehq.com/framework/config
import {existsSync, readFileSync} from "node:fs";

// Los data loaders en Python usan el entorno del proyecto si existe (.venv en la
// raíz del repo); en CI, el python3 donde se instaló el paquete.
const python = process.env.PYTHON ?? (existsSync("../.venv/bin/python") ? "../.venv/bin/python" : "python3");

// Una ficha por localidad (RF-06): las rutas salen de la semilla de dbt
const slugs = readFileSync("../transform/seeds/localidad.csv", "utf8")
  .trim()
  .split("\n")
  .slice(1)
  .map((fila) => fila.split(",")[2]);

export default {
  title: "Observatorio Bacatá",
  root: "src",
  // Se publica en https://diegopardomontero.github.io/observatorio-bacata/
  base: "/observatorio-bacata/",
  style: "estilo/bacata.css",
  // Las fuentes vienen de estilo/bacata.css; no se carga la de Framework
  globalStylesheets: [],
  interpreters: {".py": [python]},
  dynamicPaths: slugs.map((slug) => `/localidad/${slug}`),
  head: '<meta name="description" content="Los datos abiertos de Bogotá, claros y por localidad: calidad del aire, movilidad, seguridad y costo de vida.">',
  header: `<a class="marca" href="/" aria-label="Observatorio Bacatá, inicio">
    <span class="marca-sup">Observatorio</span>
    <span class="marca-nombre">Bacatá</span>
  </a>
  <nav class="nav" aria-label="Secciones">
    <a href="/aire">Aire</a>
    <a href="/mapa">Mapa</a>
    <a href="/datos">Datos</a>
    <a href="/metodologia">Metodología</a>
  </nav>`,
  footer: `<p>Datos abiertos de Bogotá · Sitio gratuito · <a href="/estado">Estado de los datos</a></p>
  <p><a href="https://github.com/DiegoPardoMontero/observatorio-bacata">Código</a> bajo MIT ·
    datos derivados bajo CC BY-SA 4.0</p>`,
  sidebar: false,
  toc: false,
  pager: false,
  search: false
};
