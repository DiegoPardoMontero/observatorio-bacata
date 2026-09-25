"""Genera transform/seeds/estacion.csv: las estaciones de la RMCAB con su localidad.

El portal de la RMCAB identifica cada estación con un número (1 = Usaquén) y el
dataset de estaciones de la Secretaría de Ambiente con una sigla (USQ). No hay
llave común, así que el cruce se hace una vez por nombre normalizado (sin
tildes, espacios ni mayúsculas) y queda fijo en la semilla. La localidad sale
de ubicar el punto de la estación dentro de los polígonos de Catastro; cuando
el dataset de la SDA trae la localidad (sect_loc), debe coincidir.

Se vuelve a correr solo si cambian las estaciones:
    python scripts/semilla_estaciones.py
"""

import csv
import json
import unicodedata
from pathlib import Path

import duckdb
import httpx

URL_ESTACIONES = (
    "https://datosabiertos.bogota.gov.co/dataset/f0705b60-9ba4-49a5-88f2-d9d4fa5bbfeb/"
    "resource/b6068373-be9f-4373-b8e8-bff16fb82a76/download/estacion_calidad_aire.geojson"
)
URL_LOCALIDADES = (
    "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/ordenamientoterritorial/"
    "localidad/MapServer/0/query?where=1%3D1&outFields=LOCCODIGO&outSR=4326&f=geojson"
)
BRONZE_RMCAB = "data/bronze/rmcab__horario/*/*.parquet"
SALIDA = Path("transform/seeds/estacion.csv")
# Nombres que la fuente escribe sin tilde
NOMBRES = {"Usaquen": "Usaquén", "San Cristobal": "San Cristóbal"}


def normalizar(nombre: str) -> str:
    sin_tildes = unicodedata.normalize("NFD", nombre)
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.lower().split())


def main() -> None:
    with httpx.Client(headers={"User-Agent": "ObservatorioBacata/0.1"}, timeout=120, follow_redirects=True) as cliente:
        estaciones = cliente.get(URL_ESTACIONES).json()["features"]
        localidades = cliente.get(URL_LOCALIDADES).json()["features"]

    con = duckdb.connect()
    con.install_extension("spatial")
    con.load_extension("spatial")
    con.execute("CREATE TABLE localidad (codigo VARCHAR, geom GEOMETRY)")
    for f in localidades:
        con.execute(
            "INSERT INTO localidad VALUES (?, ST_GeomFromGeoJSON(?))",
            [f["properties"]["LOCCODIGO"], json.dumps(f["geometry"])],
        )

    portal = dict(
        con.execute(
            f"SELECT DISTINCT estacion_nombre, estacion_codigo FROM '{BRONZE_RMCAB}'"
        ).fetchall()
    )
    portal_normalizado = {normalizar(n): (n, c) for n, c in portal.items()}
    parametros = {
        c: sorted(p)
        for c, p in con.execute(
            f"SELECT estacion_codigo, list(DISTINCT parametro) FROM '{BRONZE_RMCAB}' GROUP BY 1"
        ).fetchall()
    }

    filas = []
    for f in estaciones:
        p = f["properties"]
        clave = normalizar(p["estacion"])
        if clave not in portal_normalizado:
            raise SystemExit(f"La estación {p['estacion']!r} de la SDA no aparece en el portal de la RMCAB")
        _, codigo_rmcab = portal_normalizado.pop(clave)
        lon, lat = f["geometry"]["coordinates"]
        (localidad,) = con.execute(
            "SELECT codigo FROM localidad WHERE ST_Contains(geom, ST_Point(?, ?))", [lon, lat]
        ).fetchone()
        if p.get("sect_loc") and p["sect_loc"] != localidad:
            raise SystemExit(f"{p['estacion']}: la SDA dice localidad {p['sect_loc']} y el punto cae en {localidad}")
        movil = clave.startswith("movil")
        filas.append(
            {
                "estacion_id": codigo_rmcab,
                "sigla_sda": p["cod_estac"].strip(),
                "nombre": NOMBRES.get(p["estacion"].strip(), p["estacion"].strip()),
                "localidad_id": localidad,
                "latitud": round(lat, 6),
                "longitud": round(lon, 6),
                "es_movil": str(movil).lower(),
                "mide_pm25": str("PM2.5" in parametros.get(codigo_rmcab, [])).lower(),
                "mide_pm10": str("PM10" in parametros.get(codigo_rmcab, [])).lower(),
                "direccion": p.get("dir_estac", "").strip(),
            }
        )
    if portal_normalizado:
        raise SystemExit(f"Estaciones del portal sin pareja en la SDA: {sorted(portal_normalizado)}")

    filas.sort(key=lambda f: f["estacion_id"])
    with SALIDA.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"{len(filas)} estaciones -> {SALIDA}")


if __name__ == "__main__":
    main()
