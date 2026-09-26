// Ajustes de accesibilidad al HTML que genera Framework, después de cada build:
// - lang="es" en <html>: Framework no permite fijar el idioma (WCAG 3.1.1).
// - Sin maximum-scale en el viewport: Framework lo fija en 1 y eso impide ampliar la
//   página en Android (WCAG 1.4.4).
import {readdirSync, readFileSync, writeFileSync} from "node:fs";
import {join} from "node:path";

const VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">';
const VIEWPORT_ACCESIBLE = '<meta name="viewport" content="width=device-width, initial-scale=1">';

for (const archivo of readdirSync("dist", {recursive: true})) {
  if (!archivo.endsWith(".html")) continue;
  const ruta = join("dist", archivo);
  const pagina = readFileSync(ruta, "utf8");
  if (!pagina.includes("<html>")) throw new Error(`${ruta}: no se encontró <html>`);
  if (!pagina.includes(VIEWPORT)) throw new Error(`${ruta}: cambió el viewport de Framework; revisa este script`);
  writeFileSync(ruta, pagina.replace("<html>", '<html lang="es">').replace(VIEWPORT, VIEWPORT_ACCESIBLE));
}
