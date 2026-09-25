import io
import json
import zipfile
from datetime import date
from pathlib import Path

import duckdb
import httpx
import pandas as pd
import pytest

from extract.sdscj import (
    COLUMNAS,
    DELITOS,
    USER_AGENT,
    ContratoSDSCJRoto,
    fecha_corte,
    guardar_bronze,
    leer_geojson,
    listar_recursos,
    parsear,
)

# Recurso real "Ene-Ago (2025vs2026)" descargado el 25 sep 2026, sin la geometría.
FIXTURE = Path(__file__).parent / "fixtures" / "sdscj" / "DAILoc_ene-ago_2026.geojson"


@pytest.fixture
def geojson() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture
def df(geojson):
    return parsear(geojson, {"id": "aba0e25d", "name": "GeoJSON Enero - Agosto"})


def _fila(df, localidad, campo):
    return df[(df["localidad_codigo"] == localidad) & (df["campo"] == campo)].iloc[0]


def test_una_fila_por_localidad_y_campo(df):
    assert list(df.columns) == COLUMNAS
    # 11 delitos × (9 años de 2018 a 2026 + variación + total de la ciudad) × 21 localidades
    assert len(df) == 11 * (9 + 2) * 21
    assert not df.duplicated(["localidad_codigo", "campo"]).any()
    assert set(df["localidad_codigo"]) == {f"{n:02d}" for n in range(1, 21)} | {"99"}
    assert set(df["delito_codigo"]) == set(DELITOS)


def test_el_acumulado_trae_fecha_de_corte(df):
    assert set(df["periodo_fuente"]) == {"Ene-Ago (2025vs2026)"}
    assert set(df["fecha_corte"]) == {date(2026, 8, 31)}


def test_valores_conocidos(df):
    homicidios_2026 = _fila(df, "09", "CMH26CONT")
    assert (homicidios_2026["medida"], homicidios_2026["delito_codigo"], homicidios_2026["anio"]) == (
        "conteo",
        "H",
        2026,
    )
    assert homicidios_2026["valor"] == 20
    assert _fila(df, "09", "CMH25CONT")["valor"] == 28
    # La variación y el total de la ciudad no tienen año
    variacion = _fila(df, "09", "CMHVAR")
    assert (variacion["medida"], variacion["valor"]) == ("variacion_pct", -28.57)
    assert pd.isna(variacion["anio"])
    assert _fila(df, "09", "CMHTOTAL")["medida"] == "total_ciudad"


def test_nombres_cortados_por_el_shapefile(df):
    celulares = _fila(df, "09", "CMHCE18CON")
    assert (celulares["delito_codigo"], celulares["anio"]) == ("HCE", 2018)


def test_el_total_de_la_ciudad_es_la_suma_de_las_localidades(df):
    conteos_2026 = df[(df["medida"] == "conteo") & (df["anio"] == 2026) & (df["delito_codigo"] == "H")]
    total = df[(df["medida"] == "total_ciudad") & (df["delito_codigo"] == "H")]["valor"].unique()
    assert list(total) == [conteos_2026["valor"].sum()] == [740]


def test_conserva_valores_crudos(df):
    # La fuente publica lesiones personales de 2026 en cero en las 21 localidades
    # (el servicio REST las trae nulas). Bronze no corrige nada.
    lesiones_2026 = df[(df["delito_codigo"] == "LP") & (df["anio"] == 2026)]
    assert len(lesiones_2026) == 21
    assert (lesiones_2026["valor"] == 0).all()


def test_fecha_corte():
    assert fecha_corte("Ene-Ago (2025vs2026)") == date(2026, 8, 31)
    assert fecha_corte("Ene-Dic (2024vs2025)") == date(2025, 12, 31)
    assert fecha_corte("Ene-Feb (2027vs2028)") == date(2028, 2, 29)
    with pytest.raises(ContratoSDSCJRoto, match="periodo desconocido"):
        fecha_corte("Agosto 2026")
    with pytest.raises(ContratoSDSCJRoto, match="años seguidos"):
        fecha_corte("Ene-Ago (2024vs2026)")


def test_campo_desconocido_rompe_el_contrato(geojson):
    geojson["features"][0]["properties"]["CMHOMICIDIOS26"] = 3.0
    with pytest.raises(ContratoSDSCJRoto, match="campo desconocido"):
        parsear(geojson)


def test_delito_nuevo_rompe_el_contrato(geojson):
    geojson["features"][0]["properties"]["CMEX26CONT"] = 3.0
    with pytest.raises(ContratoSDSCJRoto, match="delito desconocido"):
        parsear(geojson)


def test_localidad_faltante_rompe_el_contrato(geojson):
    geojson["features"].pop()
    with pytest.raises(ContratoSDSCJRoto, match="localidades inesperadas"):
        parsear(geojson)


def test_periodos_mezclados_rompen_el_contrato(geojson):
    geojson["features"][0]["properties"]["CMMES"] = "Ene-Jul (2025vs2026)"
    with pytest.raises(ContratoSDSCJRoto, match="mezcla periodos"):
        parsear(geojson)


def test_anio_faltante_rompe_el_contrato(geojson):
    del geojson["features"][3]["properties"]["CMHP21CONT"]
    with pytest.raises(ContratoSDSCJRoto, match="HP: años"):
        parsear(geojson)


def test_conteo_duplicado_rompe_el_contrato(geojson):
    # Si un día llegan los dos nombres, el cortado y el completo, no se sabe cuál vale.
    geojson["features"][0]["properties"]["CMHCE18CONT"] = 1.0
    with pytest.raises(ContratoSDSCJRoto, match="más de un conteo"):
        parsear(geojson)


def test_valor_no_numerico_rompe_el_contrato(geojson):
    geojson["features"][0]["properties"]["CMH26CONT"] = "veinte"
    with pytest.raises(ContratoSDSCJRoto, match="no numérico"):
        parsear(geojson)


def _zip(archivos: dict[str, str]) -> bytes:
    memoria = io.BytesIO()
    with zipfile.ZipFile(memoria, "w") as z:
        for nombre, contenido in archivos.items():
            z.writestr(nombre, contenido)
    return memoria.getvalue()


def test_leer_geojson_del_zip(geojson):
    assert leer_geojson(_zip({"DAILoc.geojson": json.dumps(geojson)})) == geojson
    with pytest.raises(ContratoSDSCJRoto, match="un .geojson"):
        leer_geojson(_zip({"a.geojson": "{}", "b.geojson": "{}"}))
    with pytest.raises(ContratoSDSCJRoto, match="un .geojson"):
        leer_geojson(_zip({"DAILoc.shp": ""}))


def test_guardar_bronze_escribe_parquet_particionado(df, tmp_path):
    ruta = guardar_bronze(df, date(2026, 9, 25), tmp_path)
    assert ruta == tmp_path / "fecha_carga=2026-09-25" / "2026-08-31.parquet"
    filas, corte, nulos_anio = duckdb.sql(
        f"SELECT count(*), any_value(fecha_corte), count(*) FILTER (anio IS NULL) "
        f"FROM '{ruta.as_posix()}'"
    ).fetchone()
    assert filas == len(df)
    assert corte == date(2026, 8, 31)
    assert nulos_anio == 11 * 2 * 21


@pytest.mark.red
def test_fuente_real_cumple_el_contrato():
    # CKAN no garantiza el orden de los recursos: se validan todos
    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=120.0) as cliente:
        cortes = [
            parsear(leer_geojson(cliente.get(r["url"], follow_redirects=True).content), r)[
                "fecha_corte"
            ].iloc[0]
            for r in listar_recursos(cliente)
        ]
    assert max(cortes) >= date(2026, 8, 31)
