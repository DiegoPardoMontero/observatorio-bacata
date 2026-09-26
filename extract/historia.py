"""Historia de Bronze entre corridas, guardada como un asset de GitHub Releases.

Cada corrida de GitHub Actions empieza sin datos. Antes de extraer se baja la
historia (`bajar`) y, después de extraer, se sube de nuevo con lo nuevo
(`subir`). Todo Bronze va en un solo archivo, bronze.tar, en la release
`bronze` del repositorio. Decisión en docs/decisiones/0004-historia-en-github-releases.md.

Para no perder la historia si una subida falla a medias, el archivo nuevo se
sube primero con otro nombre y solo después reemplaza al vigente, que queda
como bronze-anterior.tar: siempre hay una copia de la corrida previa.

Dos barreras más, porque perder la historia no tiene arreglo (los cortes mensuales
de seguridad no se pueden volver a bajar):
- Solo "release not found" cuenta como que no hay historia. Cualquier otro error de
  `gh` (red, permisos, límite de la API) detiene la corrida: si se tomara como
  historia vacía, se subiría un Bronze con solo el día actual.
- La historia solo crece. `subir` se niega a reemplazar el archivo vigente por uno
  mucho más pequeño (menos del 90 %), salvo con --forzar.

Uso (necesita el CLI `gh` autenticado, o GH_TOKEN en Actions):
    python -m extract.historia bajar
    python -m extract.historia subir [--forzar]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path

RELEASE = "bronze"
ASSET = "bronze.tar"
ASSET_NUEVO = "bronze-nuevo.tar"
ASSET_ANTERIOR = "bronze-anterior.tar"
DIR_DATOS = Path("data")
DIR_BRONZE = DIR_DATOS / "bronze"
# El archivo nuevo no puede pesar menos que esta fracción del vigente
FRACCION_MINIMA = 0.9


def _gh(*args: str, capturar: bool = False) -> str:
    resultado = subprocess.run(["gh", *args], check=True, text=True, capture_output=capturar)
    return resultado.stdout if capturar else ""


def _assets() -> dict[str, dict] | None:
    """Nombre -> {"id", "bytes"} de los assets de la release, o None si la release no existe."""
    try:
        salida = _gh("release", "view", RELEASE, "--json", "assets", capturar=True)
    except subprocess.CalledProcessError as error:
        if "release not found" in (error.stderr or ""):
            return None
        raise SystemExit(f"No se pudo consultar la release {RELEASE!r}: {(error.stderr or '').strip()}") from error
    return {
        a["name"]: {"id": a["apiUrl"].rsplit("/", 1)[-1], "bytes": a["size"]}
        for a in json.loads(salida)["assets"]
    }


def bajar() -> None:
    assets = _assets() or {}
    # Si una subida se cortó después de subir el nuevo y antes de renombrarlo, vale el nuevo
    nombre = next((n for n in (ASSET_NUEVO, ASSET, ASSET_ANTERIOR) if n in assets), None)
    if nombre is None:
        print(f"La release {RELEASE!r} no tiene historia todavía: se empieza sin datos")
        return
    with tempfile.TemporaryDirectory() as tmp:
        _gh("release", "download", RELEASE, "--pattern", nombre, "--dir", tmp)
        with tarfile.open(Path(tmp) / nombre) as tar:
            tar.extractall(DIR_DATOS, filter="data")
    archivos = sum(1 for _ in DIR_BRONZE.rglob("*.parquet"))
    print(f"Historia bajada de {RELEASE}/{nombre}: {archivos} archivos en {DIR_BRONZE}")


def subir(forzar: bool = False) -> None:
    if not DIR_BRONZE.exists():
        raise SystemExit(f"No hay {DIR_BRONZE} para subir")
    with tempfile.TemporaryDirectory() as tmp:
        nuevo = Path(tmp) / ASSET_NUEVO
        with tarfile.open(nuevo, "w") as tar:
            tar.add(DIR_BRONZE, arcname="bronze")
        previos = _assets()
        vigente = (previos or {}).get(ASSET)
        if vigente and nuevo.stat().st_size < FRACCION_MINIMA * vigente["bytes"] and not forzar:
            raise SystemExit(
                f"El Bronze nuevo pesa {nuevo.stat().st_size / 1e6:.1f} MB y el vigente "
                f"{vigente['bytes'] / 1e6:.1f} MB. La historia solo crece, así que no se reemplaza: "
                "¿falló la bajada? Si la reducción es intencional, usa --forzar."
            )
        if previos is None:
            _gh(
                "release", "create", RELEASE, "--prerelease", "--title", "Historia de Bronze",
                "--notes", "Datos crudos de las fuentes entre corridas del pipeline (ADR 0004). No es una versión del sitio.",
            )
        _gh("release", "upload", RELEASE, str(nuevo), "--clobber")
        assets = _assets()
        repo = _gh("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner", capturar=True).strip()

        def renombrar(de: str, a: str) -> None:
            _gh("api", "-X", "PATCH", f"repos/{repo}/releases/assets/{assets[de]['id']}", "-f", f"name={a}", capturar=True)

        if ASSET in assets:
            if ASSET_ANTERIOR in assets:
                _gh("api", "-X", "DELETE", f"repos/{repo}/releases/assets/{assets[ASSET_ANTERIOR]['id']}", capturar=True)
            renombrar(ASSET, ASSET_ANTERIOR)
        renombrar(ASSET_NUEVO, ASSET)
        megas = nuevo.stat().st_size / 1e6
    print(f"Historia subida a {RELEASE}/{ASSET}: {megas:.1f} MB")


def main() -> None:
    parser = argparse.ArgumentParser(description="Baja o sube la historia de Bronze (GitHub Releases).")
    parser.add_argument("accion", choices=["bajar", "subir"])
    parser.add_argument("--forzar", action="store_true", help="subir aunque el Bronze nuevo sea más pequeño que el vigente")
    args = parser.parse_args()
    if args.accion == "bajar":
        bajar()
    else:
        subir(forzar=args.forzar)


if __name__ == "__main__":
    main()
