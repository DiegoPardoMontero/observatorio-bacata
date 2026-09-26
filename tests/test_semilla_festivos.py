"""Pruebas de scripts/semilla_festivos.py: Pascua y festivos de Colombia."""

import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from semilla_festivos import festivos, pascua  # noqa: E402


@pytest.mark.parametrize(
    "anio, domingo",
    [(2008, date(2008, 3, 23)), (2011, date(2011, 4, 24)), (2019, date(2019, 4, 21)),
     (2025, date(2025, 4, 20)), (2026, date(2026, 4, 5)), (2035, date(2035, 3, 25))],
)
def test_pascua(anio, domingo):
    assert pascua(anio) == domingo


def test_festivos_de_2026():
    fechas = [f for f, _ in festivos(2026)]
    assert len(fechas) == 19
    # Trasladados al lunes: Reyes (6 ene, martes), Asunción (15 ago, sábado), Todos los Santos (1 nov, domingo)
    assert {date(2026, 1, 12), date(2026, 8, 17), date(2026, 11, 2)} <= set(fechas)
    # De la Pascua: Jueves y Viernes Santo, Ascensión, Corpus y Sagrado Corazón
    assert {date(2026, 4, 2), date(2026, 4, 3), date(2026, 5, 18), date(2026, 6, 8), date(2026, 6, 15)} <= set(fechas)
    # Ley 2578 de 2026: el 9 de julio (jueves) pasa al lunes 13
    assert (date(2026, 7, 13), "Nuestra Señora del Rosario de Chiquinquirá") in festivos(2026)
    # Los fijos no se mueven aunque no caigan en lunes
    assert date(2026, 12, 8) in fechas and date(2026, 12, 8).weekday() == 1


def test_antes_de_2026_son_18_y_pueden_coincidir():
    lista = festivos(2025)
    assert len(lista) == 18
    assert not any("Chiquinquirá" in nombre for _, nombre in lista)
    # San Pedro (29 jun, domingo) pasa al lunes 30, el mismo día del Sagrado Corazón
    assert [n for f, n in lista if f == date(2025, 6, 30)] == ["Sagrado Corazón", "San Pedro y San Pablo"]


def test_los_trasladables_caen_en_lunes():
    for anio in range(2005, 2036):
        for fecha, nombre in festivos(anio):
            if nombre not in {"Año Nuevo", "Día del Trabajo", "Día de la Independencia", "Batalla de Boyacá",
                              "Inmaculada Concepción", "Navidad", "Jueves Santo", "Viernes Santo"}:
                assert fecha.weekday() == 0, (fecha, nombre)
