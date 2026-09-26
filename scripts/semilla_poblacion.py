"""Genera transform/seeds/poblacion_localidad.csv: habitantes por localidad y año (ADR 0005).

La fuente son las proyecciones y retroproyecciones de población 2005-2035 que hicieron
el DANE, la Secretaría Distrital de Planeación y la Región Metropolitana en agosto de
2025 (contrato interadministrativo 500 de 2025). Las publica la Secretaría Distrital de
Salud en Datos Abiertos Bogotá, en formato largo por localidad, año, sexo y edad; aquí se
suman sexos y edades.

La población es el denominador de todas las tasas por 100.000 habitantes (SPEC §9), así
que el script se detiene si la fuente no trae las 20 localidades y el total de Bogotá en
cada año, si la suma de las localidades no da el total de la ciudad o si un nombre no
coincide con la semilla de localidades.

Se vuelve a correr solo si la fuente publica una revisión:
    python scripts/semilla_poblacion.py
"""

import csv
import io
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

import httpx

PAQUETE = "https://datosabiertos.bogota.gov.co/api/3/action/package_show?id=piramide-poblacional-bogota-d-c"
RECURSO = "Población en Bogotá D.C por Localidad"
SEMILLA_LOCALIDADES = Path("transform/seeds/localidad.csv")
SALIDA = Path("transform/seeds/poblacion_localidad.csv")
ANIOS = range(2005, 2036)
COLUMNAS = ["ANO", "CODIGO_LOCALIDAD", "NOMBRE_LOCALIDAD", "SEXO", "EDAD", "CURSODEVIDA", "GRUPOEDAD", "POBLACION"]
BOGOTA = 0


def normalizar(nombre: str) -> str:
    sin_tildes = unicodedata.normalize("NFD", nombre)
    return " ".join("".join(c for c in sin_tildes if unicodedata.category(c) != "Mn").lower().split())


def url_recurso(cliente: httpx.Client) -> str:
    """El recurso se busca por nombre, no por identificador, por si el portal lo reemplaza."""
    recursos = cliente.get(PAQUETE).raise_for_status().json()["result"]["resources"]
    candidatos = [r["url"] for r in recursos if normalizar(r["name"]).startswith(normalizar(RECURSO))]
    if len(candidatos) != 1:
        raise SystemExit(f"Se esperaba un recurso {RECURSO!r} y hay {len(candidatos)}")
    return candidatos[0]


def sumar(texto: str) -> tuple[dict[tuple[int, int], int], dict[int, str]]:
    """Suma sexos y edades: {(código de localidad, año): habitantes} y los nombres de la fuente."""
    lector = csv.DictReader(io.StringIO(texto), delimiter=";")
    if lector.fieldnames != COLUMNAS:
        raise SystemExit(f"Columnas inesperadas: {lector.fieldnames}")
    poblacion: dict[tuple[int, int], int] = defaultdict(int)
    nombres: dict[int, str] = {}
    for fila in lector:
        codigo, anio = int(fila["CODIGO_LOCALIDAD"]), int(fila["ANO"])
        poblacion[codigo, anio] += int(fila["POBLACION"])
        nombres[codigo] = fila["NOMBRE_LOCALIDAD"]
    return poblacion, nombres


def validar(poblacion: dict[tuple[int, int], int], nombres: dict[int, str], semilla: dict[int, str]) -> None:
    esperadas = {(codigo, anio) for codigo in [BOGOTA, *semilla] for anio in ANIOS}
    if set(poblacion) != esperadas:
        faltan = sorted(esperadas - set(poblacion))[:5]
        sobran = sorted(set(poblacion) - esperadas)[:5]
        raise SystemExit(f"Localidades o años inesperados. Faltan: {faltan}. Sobran: {sobran}")
    for codigo, nombre in semilla.items():
        if normalizar(nombres[codigo]) != normalizar(nombre):
            raise SystemExit(f"Localidad {codigo:02d}: la fuente dice {nombres[codigo]!r} y la semilla {nombre!r}")
    for anio in ANIOS:
        suma = sum(poblacion[codigo, anio] for codigo in semilla)
        if suma != poblacion[BOGOTA, anio]:
            raise SystemExit(f"{anio}: las localidades suman {suma} y Bogotá tiene {poblacion[BOGOTA, anio]}")


def main() -> None:
    with SEMILLA_LOCALIDADES.open(encoding="utf-8") as archivo:
        semilla = {int(f["localidad_id"]): f["nombre"] for f in csv.DictReader(archivo)}
    with httpx.Client(headers={"User-Agent": "ObservatorioBacata/0.1"}, timeout=120, follow_redirects=True) as cliente:
        respuesta = cliente.get(url_recurso(cliente)).raise_for_status()
    poblacion, nombres = sumar(respuesta.content.decode("utf-8-sig"))
    validar(poblacion, nombres, semilla)

    with SALIDA.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["localidad_id", "anio", "poblacion"])
        for codigo in semilla:
            for anio in ANIOS:
                escritor.writerow([f"{codigo:02d}", anio, poblacion[codigo, anio]])
    print(f"{len(semilla)} localidades x {len(ANIOS)} años -> {SALIDA}")
    anio = date.today().year
    print(f"Bogotá en {anio}: {poblacion[BOGOTA, anio]:,} habitantes".replace(",", "."))


if __name__ == "__main__":
    main()
