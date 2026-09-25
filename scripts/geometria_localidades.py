"""Genera site/src/data/localidades.geojson: los polígonos de las 20 localidades, simplificados para el mapa.

La fuente (Catastro, "Localidad. Bogotá D.C.", CC BY 4.0) pesa 2,3 MB y no se
actualiza desde 2022, así que se simplifica una vez y el resultado queda en el
repositorio. ST_CoverageSimplify simplifica las 20 localidades juntas y conserva
los bordes compartidos: no quedan huecos ni traslapes entre vecinas.

Se vuelve a correr solo si cambia la fuente:
    python scripts/geometria_localidades.py
"""

import json
from pathlib import Path

import duckdb
import httpx

URL = (
    "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/ordenamientoterritorial/"
    "localidad/MapServer/0/query?where=1%3D1&outFields=LOCCODIGO&outSR=4326&f=geojson"
)
SALIDA = Path("site/src/data/localidades.geojson")
TOLERANCIA = 0.0006  # grados, unos 65 m: invisible a la escala de la ciudad
DECIMALES = 4  # unos 11 m


def _area_con_signo(anillo: list) -> float:
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(anillo, anillo[1:])) / 2


def para_d3(geometria: dict) -> dict:
    """d3-geo (Observable Plot) quiere el anillo exterior en sentido horario y los huecos al
    revés, lo contrario de RFC 7946. Con el sentido equivocado pinta todo el globo."""
    poligonos = geometria["coordinates"] if geometria["type"] == "MultiPolygon" else [geometria["coordinates"]]
    for poligono in poligonos:
        for i, anillo in enumerate(poligono):
            horario = _area_con_signo(anillo) < 0
            if horario != (i == 0):
                anillo.reverse()
    return geometria


def main() -> None:
    fuente = httpx.get(URL, timeout=120, headers={"User-Agent": "ObservatorioBacata/0.1"}).json()
    codigos = [f["properties"]["LOCCODIGO"] for f in fuente["features"]]
    if sorted(codigos) != [f"{n:02d}" for n in range(1, 21)]:
        raise SystemExit(f"Localidades inesperadas: {sorted(codigos)}")

    con = duckdb.connect()
    con.install_extension("spatial")
    con.load_extension("spatial")
    con.execute("CREATE TABLE localidad (localidad_id VARCHAR, geom GEOMETRY)")
    for f in fuente["features"]:
        con.execute(
            "INSERT INTO localidad VALUES (?, ST_GeomFromGeoJSON(?))",
            [f["properties"]["LOCCODIGO"], json.dumps(f["geometry"])],
        )
    # El agregado simplifica todas juntas y devuelve una colección. Cada parte se asigna a su
    # localidad por el polígono original que contiene un punto interior de la parte.
    filas = con.execute(
        f"""
        WITH simplificada AS (
            SELECT unnest(ST_Dump(ST_CoverageSimplify_Agg(geom, {TOLERANCIA}))) AS parte FROM localidad
        )
        SELECT l.localidad_id, ST_AsGeoJSON(ST_ReducePrecision(s.parte.geom, {10 ** -DECIMALES}))
        FROM simplificada s
        JOIN localidad l ON ST_Contains(l.geom, ST_PointOnSurface(s.parte.geom))
        """
    ).fetchall()
    if sorted(i for i, _ in filas) != sorted(codigos):
        raise SystemExit("La simplificación no conservó una parte por localidad")

    geojson = {
        "type": "FeatureCollection",
        "fuente": "Localidad. Bogotá D.C. — Catastro Distrital / IDECA, CC BY 4.0, datos de 2022",
        "features": [
            {"type": "Feature", "properties": {"localidad_id": i}, "geometry": para_d3(json.loads(g))}
            for i, g in sorted(filas)
        ],
    }
    if len(geojson["features"]) != 20:
        raise SystemExit(f"Se esperaban 20 polígonos y salieron {len(geojson['features'])}")
    SALIDA.write_text(json.dumps(geojson, separators=(",", ":")), encoding="utf-8")
    print(f"20 localidades -> {SALIDA} ({SALIDA.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
