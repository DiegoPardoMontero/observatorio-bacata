from datetime import date, timedelta
from pathlib import Path

import duckdb
import httpx
import pytest

from extract.rmcab import (
    COLUMNAS,
    USER_AGENT,
    ContratoRMCABRoto,
    descargar_dia,
    guardar_bronze,
    parsear_dia,
)

FECHA = date(2026, 8, 15)
FIXTURE = Path(__file__).parent / "fixtures" / "rmcab" / "reporte_horario_2026-08-15.html"


@pytest.fixture
def pagina() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture
def df(pagina):
    return parsear_dia(pagina, FECHA)


def test_una_fila_por_estacion_parametro_y_hora(df):
    assert list(df.columns) == COLUMNAS
    # 3 series completas de 24 horas y Jazmín con 19 (faltan de 14:00 a 18:00)
    assert len(df) == 3 * 24 + 19
    assert not df.duplicated(["estacion_codigo", "parametro", "fecha_hora_fuente"]).any()
    assert set(df["estacion_nombre"]) == {"Centro de Alto Rendimiento", "Jazmin", "Ciudad Bolivar"}


def test_el_parametro_sale_del_registro_y_no_del_canal(df):
    car = df[df["estacion_codigo"] == 5].groupby("canal")["parametro"].first().to_dict()
    assert car == {1: "PM10", 18: "PM2.5"}
    assert set(df["unidad"]) == {"µg/m3"}


def test_valor_conocido(df):
    fila = df[
        (df["estacion_codigo"] == 5)
        & (df["parametro"] == "PM10")
        & (df["fecha_hora_fuente"] == "2026-08-15T01:00:00")
    ].iloc[0]
    assert fila["valor"] == pytest.approx(4.369421)
    assert fila["estado"] == 1
    assert fila["estado_valido_portal"]


def test_horas_marcadas_por_su_final(df):
    assert df["fecha_hora_fuente"].min() == "2026-08-15T01:00:00"
    assert df["fecha_hora_fuente"].max() == "2026-08-16T00:00:00"


def test_conserva_faltantes_y_estados_crudos(df):
    ciudad_bolivar = df[df["estacion_codigo"] == 37]
    assert (ciudad_bolivar["valor"] == -9999).all()
    assert (ciudad_bolivar["estado"] == 0).all()
    assert not ciudad_bolivar["estado_valido_portal"].any()

    pm10_car = df[(df["estacion_codigo"] == 5) & (df["parametro"] == "PM10")]
    assert pm10_car["estado"].value_counts().to_dict() == {1: 14, 4: 10}
    assert not pm10_car.loc[pm10_car["estado"] == 4, "estado_valido_portal"].any()


def test_fecha_distinta_a_la_pedida_rompe_el_contrato(pagina):
    # Si el portal ignora la fecha pedida, no se puede guardar con otra etiqueta.
    with pytest.raises(ContratoRMCABRoto, match="devolvió"):
        parsear_dia(pagina, FECHA + timedelta(days=1))


def test_pagina_sin_series_rompe_el_contrato(pagina):
    solo_estados = pagina.split("<table>")[0]
    with pytest.raises(ContratoRMCABRoto, match="ninguna serie"):
        parsear_dia(solo_estados, FECHA)


def test_pagina_sin_diccionario_de_estados_rompe_el_contrato():
    with pytest.raises(ContratoRMCABRoto, match="StatusDic"):
        parsear_dia("<html><body>Mantenimiento</body></html>", FECHA)


def test_guardar_bronze_escribe_parquet_particionado(df, tmp_path):
    ruta = guardar_bronze(df, FECHA, date(2026, 9, 25), tmp_path)
    assert ruta == tmp_path / "fecha_carga=2026-09-25" / "2026-08-15.parquet"
    filas, fecha_reporte = duckdb.sql(
        f"SELECT count(*), any_value(fecha_reporte) FROM '{ruta.as_posix()}'"
    ).fetchone()
    assert filas == len(df)
    assert fecha_reporte == FECHA


@pytest.mark.red
def test_portal_real_cumple_el_contrato():
    ayer = date.today() - timedelta(days=1)
    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=60.0) as cliente:
        contenido = descargar_dia(ayer, cliente)
    df = parsear_dia(contenido.decode("utf-8"), ayer)
    assert df["estacion_codigo"].nunique() >= 10
    assert "PM2.5" in set(df["parametro"])
