"""Genera transform/seeds/festivo.csv: los festivos de Colombia de 2005 a 2035 (SPEC §8, dim_fecha).

Hasta 2025 son 18 al año, según la Ley 51 de 1983 (Ley Emiliani):
- Seis fijos, que no se mueven.
- Siete que, si no caen en lunes, pasan al lunes siguiente.
- Cinco que dependen de la Pascua: Jueves y Viernes Santo, que no se mueven, y la
  Ascensión, el Corpus Christi y el Sagrado Corazón, que se celebran en lunes.

La Ley 2578 de 2026 agrega desde 2026 el Día de Nuestra Señora del Rosario de
Chiquinquirá (9 de julio, trasladable al lunes siguiente): desde ese año son 19.

Cuando la Pascua cae tarde, el Sagrado Corazón coincide con San Pedro y San Pablo
trasladado al mismo lunes (2011, 2014, 2019, 2025 y 2030). La ley no mueve ninguno, así
que ese año tiene 17 días festivos y la fecha lleva los dos nombres.

Se vuelve a correr si cambia la ley (por ejemplo, si la Corte Constitucional tumba la
Ley 2578, que está demandada) o si se amplía el rango de años:
    python scripts/semilla_festivos.py
"""

import csv
from datetime import date, timedelta
from pathlib import Path

SALIDA = Path("transform/seeds/festivo.csv")
ANIOS = range(2005, 2036)

FIJOS = [(1, 1, "Año Nuevo"), (5, 1, "Día del Trabajo"), (7, 20, "Día de la Independencia"),
         (8, 7, "Batalla de Boyacá"), (12, 8, "Inmaculada Concepción"), (12, 25, "Navidad")]
TRASLADABLES = [(1, 6, "Reyes Magos"), (3, 19, "San José"), (6, 29, "San Pedro y San Pablo"),
                (8, 15, "Asunción de la Virgen"), (10, 12, "Día de la Diversidad Étnica y Cultural"),
                (11, 1, "Todos los Santos"), (11, 11, "Independencia de Cartagena")]
# Festivos creados después de 1983: (desde el año, mes, día, nombre); todos trasladables
POSTERIORES = [(2026, 7, 9, "Nuestra Señora del Rosario de Chiquinquirá")]  # Ley 2578 de 2026
# Días después del domingo de Pascua; los de la Ley Emiliani ya caen en lunes
DE_PASCUA = [(-3, "Jueves Santo"), (-2, "Viernes Santo"), (43, "Ascensión del Señor"),
             (64, "Corpus Christi"), (71, "Sagrado Corazón")]


def pascua(anio: int) -> date:
    """Domingo de Pascua en el calendario gregoriano (algoritmo de Meeus, Jones y Butcher)."""
    a, b, c = anio % 19, anio // 100, anio % 100
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7  # noqa: E741 (nombre del algoritmo)
    m = (a + 11 * h + 22 * l) // 451
    mes, dia = divmod(h + l - 7 * m + 114, 31)
    return date(anio, mes, dia + 1)


def al_lunes(fecha: date) -> date:
    return fecha + timedelta(days=(7 - fecha.weekday()) % 7)


def festivos(anio: int) -> list[tuple[date, str]]:
    domingo = pascua(anio)
    lista = [(date(anio, m, d), nombre) for m, d, nombre in FIJOS]
    lista += [(al_lunes(date(anio, m, d)), nombre) for m, d, nombre in TRASLADABLES]
    lista += [(domingo + timedelta(days=n), nombre) for n, nombre in DE_PASCUA]
    lista += [(al_lunes(date(anio, m, d)), nombre) for desde, m, d, nombre in POSTERIORES if anio >= desde]
    return sorted(lista)


def main() -> None:
    por_fecha: dict[date, list[str]] = {}
    for anio in ANIOS:
        for fecha, nombre in festivos(anio):
            por_fecha.setdefault(fecha, []).append(nombre)
    with SALIDA.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["fecha", "nombre"])
        escritor.writerows((f.isoformat(), "; ".join(nombres)) for f, nombres in sorted(por_fecha.items()))
    coincidencias = [f.isoformat() for f, nombres in sorted(por_fecha.items()) if len(nombres) > 1]
    print(f"{len(por_fecha)} días festivos de {ANIOS[0]} a {ANIOS[-1]} -> {SALIDA}")
    print(f"Fechas con dos festivos: {', '.join(coincidencias)}")


if __name__ == "__main__":
    main()
