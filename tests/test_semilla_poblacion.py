"""Pruebas de scripts/semilla_poblacion.py sin conexión, con una fuente sintética."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from semilla_poblacion import ANIOS, COLUMNAS, sumar, validar  # noqa: E402

SEMILLA = {1: "Usaquén", 2: "Chapinero"}


def fuente(filas_extra: list[str] | None = None, quitar: tuple[int, int] | None = None, bogota_mas: int = 0) -> str:
    """Dos localidades, dos sexos y dos edades por año; Bogotá es la suma."""
    lineas = [";".join(COLUMNAS)]
    for anio in ANIOS:
        for codigo, nombre, base in [(0, "Bogotá", None), (1, "Usaquen", 100), (2, "Chapinero", 10)]:
            if (codigo, anio) == quitar:
                continue
            for sexo in ["Hombres", "Mujeres"]:
                for edad in [0, 1]:
                    valor = 110 + bogota_mas if base is None else base
                    lineas.append(f"{anio};{codigo};{nombre};{sexo};{edad};Infancia;00 a 11;{valor}")
    return "\r\n".join(lineas + (filas_extra or []))


def test_suma_sexos_y_edades():
    poblacion, nombres = sumar(fuente())
    assert poblacion[1, 2026] == 400
    assert poblacion[2, 2026] == 40
    assert poblacion[0, 2026] == 440
    assert nombres[1] == "Usaquen"


def test_fuente_valida_pasa_aunque_falten_tildes():
    validar(*sumar(fuente()), SEMILLA)


def test_falla_si_falta_una_localidad_en_un_anio():
    with pytest.raises(SystemExit, match="Faltan: \\[\\(2, 2030\\)\\]"):
        validar(*sumar(fuente(quitar=(2, 2030))), SEMILLA)


def test_falla_si_las_localidades_no_suman_bogota():
    with pytest.raises(SystemExit, match="las localidades suman 440 y Bogotá tiene 444"):
        validar(*sumar(fuente(bogota_mas=1)), SEMILLA)


def test_falla_si_un_nombre_no_coincide():
    with pytest.raises(SystemExit, match="Localidad 02"):
        validar(*sumar(fuente()), {1: "Usaquén", 2: "Santa Fe"})


def test_falla_si_cambian_las_columnas():
    with pytest.raises(SystemExit, match="Columnas inesperadas"):
        sumar(fuente().replace("POBLACION", "PERSONAS", 1))
