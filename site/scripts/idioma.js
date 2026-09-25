// Framework no permite fijar el idioma del documento, así que después del build
// se agrega lang="es" a cada página (WCAG 3.1.1, idioma de la página).
import {readdirSync, readFileSync, writeFileSync} from "node:fs";
import {join} from "node:path";

for (const archivo of readdirSync("dist", {recursive: true})) {
  if (!archivo.endsWith(".html")) continue;
  const ruta = join("dist", archivo);
  const pagina = readFileSync(ruta, "utf8");
  if (!pagina.includes("<html>")) throw new Error(`${ruta}: no se encontró <html>`);
  writeFileSync(ruta, pagina.replace("<html>", '<html lang="es">'));
}
