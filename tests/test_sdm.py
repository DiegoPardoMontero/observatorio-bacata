"""Pruebas del extractor de siniestros (extract/sdm.py). Las de la fuente real van con -m red."""

import copy
import json
from datetime import date, datetime, timezone
from pathlib import Path

import duckdb
import httpx
import pytest

from extract import sdm
from extract.sdm import COLUMNAS, ContratoSDMRoto, anios_a_bajar, codigos_localidad, extraer_anio, guardar_bronze, parsear

# Recortes reales de las capas MUERTO y LESIONADO de 2026, bajados el 26 sep 2026 con los
# campos que pide el extractor. Los heridos incluyen CANDELARIA y ANTONIO NARIÑO.
FIXTURES = Path(__file__).parent / "fixtures" / "sdm"
AHORA = datetime(2026, 9, 26, 12, tzinfo=timezone.utc)


@pytest.fixture
def muertos() -> dict:
    return json.loads((FIXTURES / "muerto_2026.json").read_text(encoding="utf-8"))


@pytest.fixture
def heridos() -> dict:
    return json.loads((FIXTURES / "herido_2026.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def codigos() -> dict:
    return codigos_localidad()


def test_una_fila_por_victima(heridos, muertos, codigos):
    df = parsear(heridos, 1, 2026, codigos, AHORA)
    assert list(df.columns) == COLUMNAS
    assert len(df) == len(heridos["features"])
    assert set(df["capa"]) == {"LESIONADO"}
    assert df["muerte_posterior"].isna().all()
    df_m = parsear(muertos, 0, 2026, codigos, AHORA)
    assert set(df_m["capa"]) == {"MUERTO"}
    assert set(df_m["muerte_posterior"]) <= {"S", "N"}


def test_no_guarda_datos_personales(heridos, codigos):
    df = parsear(heridos, 1, 2026, codigos, AHORA)
    assert not {"genero", "edad", "direccion", "GENERO", "EDAD", "DIRECCION"} & set(df.columns)


def test_la_localidad_se_convierte_en_codigo(heridos, codigos):
    df = parsear(heridos, 1, 2026, codigos, AHORA)
    pares = dict(zip(df["localidad_nombre"], df["localidad_codigo"]))
    assert pares["CANDELARIA"] == "17"
    assert pares["ANTONIO NARIÑO"] == "15"
    assert pares["LOS MARTIRES"] == "14"


def test_la_fecha_es_el_dia_local_sin_convertir(heridos, codigos):
    df = parsear(heridos, 1, 2026, codigos, AHORA)
    # 1770768000000 = 2026-02-11T00:00Z: el día es el 11, no el 10 de Bogotá
    fila = df[df["codigo_accidentado"] == "14472020"].iloc[0]
    assert fila["fecha_ocurrencia"] == date(2026, 2, 11)


def test_un_campo_nuevo_rompe_el_contrato(heridos, codigos):
    heridos["fields"].append({"name": "GENERO", "type": "esriFieldTypeString"})
    with pytest.raises(ContratoSDMRoto, match="campos inesperados"):
        parsear(heridos, 1, 2026, codigos, AHORA)


def test_una_localidad_desconocida_rompe_el_contrato(heridos, codigos):
    heridos["features"][0]["attributes"]["LOCALIDAD"] = "SOACHA"
    with pytest.raises(ContratoSDMRoto, match="localidad desconocida 'SOACHA'"):
        parsear(heridos, 1, 2026, codigos, AHORA)


def test_un_tipo_de_actor_desconocido_rompe_el_contrato(heridos, codigos):
    heridos["features"][0]["attributes"]["CONDICION"] = "PATINETA"
    with pytest.raises(ContratoSDMRoto, match="tipo de actor"):
        parsear(heridos, 1, 2026, codigos, AHORA)


def test_una_victima_de_otro_anio_rompe_el_contrato(heridos, codigos):
    with pytest.raises(ContratoSDMRoto, match="se pidió 2025"):
        parsear(heridos, 1, 2025, codigos, AHORA)


class ServidorFalso:
    """Imita el FeatureServer: cuenta, pagina con exceededTransferLimit y devuelve las fixtures."""

    def __init__(self, respuestas: dict[int, dict], cuenta_extra: int = 0):
        self.respuestas = respuestas
        self.cuenta_extra = cuenta_extra
        self.pedidos = []

    def __call__(self, peticion: httpx.Request) -> httpx.Response:
        capa = int(peticion.url.path.split("/")[-2])
        p = dict(peticion.url.params)
        self.pedidos.append((capa, p))
        base = self.respuestas[capa]
        if p.get("returnCountOnly") == "true":
            return httpx.Response(200, json={"count": len(base["features"]) + self.cuenta_extra})
        desde, n = int(p["resultOffset"]), int(p["resultRecordCount"])
        pagina = copy.deepcopy(base)
        pagina["features"] = base["features"][desde:desde + n]
        pagina["exceededTransferLimit"] = desde + n < len(base["features"])
        return httpx.Response(200, json=pagina)


def test_pagina_y_junta_las_dos_capas(monkeypatch, heridos, muertos, codigos):
    monkeypatch.setattr(sdm, "PAGINA", 2)
    servidor = ServidorFalso({0: muertos, 1: heridos})
    with httpx.Client(transport=httpx.MockTransport(servidor)) as cliente:
        df = extraer_anio(cliente, 2026, codigos)
    assert len(df) == len(muertos["features"]) + len(heridos["features"])
    paginas_heridos = [p for c, p in servidor.pedidos if c == 1 and "resultOffset" in p]
    assert [p["resultOffset"] for p in paginas_heridos] == ["0", "2", "4"]
    # Nunca se piden los campos personales
    assert all("GENERO" not in p.get("outFields", "") for _, p in servidor.pedidos)


def test_si_faltan_filas_frente_al_conteo_se_detiene(monkeypatch, heridos, muertos, codigos):
    monkeypatch.setattr(sdm, "PAGINA", 2)
    servidor = ServidorFalso({0: muertos, 1: heridos}, cuenta_extra=1)
    with httpx.Client(transport=httpx.MockTransport(servidor)) as cliente:
        with pytest.raises(ContratoSDMRoto, match="el servidor cuenta"):
            extraer_anio(cliente, 2026, codigos)


def test_un_codigo_repetido_entre_capas_se_detiene(heridos, muertos, codigos):
    muertos["features"][0]["attributes"]["CODIGO_ACCIDENTADO"] = heridos["features"][0]["attributes"]["CODIGO_ACCIDENTADO"]
    with httpx.Client(transport=httpx.MockTransport(ServidorFalso({0: muertos, 1: heridos}))) as cliente:
        with pytest.raises(ContratoSDMRoto, match="repetidos"):
            extraer_anio(cliente, 2026, codigos)


def test_guardar_bronze_reemplaza_el_archivo_del_anio(tmp_path, heridos, codigos):
    df = parsear(heridos, 1, 2026, codigos, AHORA)
    ruta = guardar_bronze(df, 2026, tmp_path)
    assert ruta == tmp_path / "anio_ocurrencia=2026" / "victimas.parquet"
    guardar_bronze(df.head(2), 2026, tmp_path)
    assert duckdb.sql(f"SELECT count(*) FROM '{ruta}'").fetchone() == (2,)
    assert list(tmp_path.rglob("*.tmp")) == []


def test_la_corrida_diaria_completa_los_anios_que_faltan(tmp_path):
    # Bronze vacío (primera corrida en CI): todos desde 2021
    assert anios_a_bajar(2026, None, tmp_path) == [2021, 2022, 2023, 2024, 2025, 2026]
    for anio in (2021, 2022, 2024):
        (tmp_path / f"anio_ocurrencia={anio}").mkdir()
        (tmp_path / f"anio_ocurrencia={anio}" / "victimas.parquet").touch()
    # Falta 2023; 2025 y 2026 se bajan siempre porque se siguen digitando
    assert anios_a_bajar(2026, None, tmp_path) == [2023, 2025, 2026]
    assert anios_a_bajar(2026, 2019, tmp_path) == [2021, 2022, 2023, 2024, 2025, 2026]


@pytest.mark.red
def test_red_la_fuente_cumple_el_contrato():
    """Baja las víctimas del año anterior de la fuente real y valida todo el contrato."""
    anio = datetime.now(timezone.utc).year - 1
    with httpx.Client(headers={"User-Agent": sdm.USER_AGENT}, timeout=120.0) as cliente:
        df = extraer_anio(cliente, anio, codigos_localidad())
    assert len(df) > 10_000
    assert set(df["condicion"]) == sdm.CONDICIONES
