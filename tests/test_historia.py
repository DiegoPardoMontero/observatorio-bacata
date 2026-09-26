"""Pruebas de extract/historia.py con un `gh` falso que guarda la release en memoria (ADR 0004)."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from extract import historia


class GhFalso:
    """Imita los comandos de `gh` que usa historia.py sobre una release en memoria."""

    def __init__(self, existe: bool = False):
        self.assets: dict[str, dict] | None = {} if existe else None  # nombre -> {"id", "datos"}
        self.siguiente_id = 100
        self.error_transitorio = False

    def _no_encontrada(self, args):
        raise subprocess.CalledProcessError(1, ["gh", *args], stderr="release not found\n")

    def __call__(self, *args: str, capturar: bool = False) -> str:
        if args[:2] == ("release", "view"):
            if self.error_transitorio:
                raise subprocess.CalledProcessError(1, ["gh", *args], stderr="HTTP 502: Bad Gateway\n")
            if self.assets is None:
                self._no_encontrada(args)
            return json.dumps({"assets": [
                {"name": n, "size": len(a["datos"]), "apiUrl": f"https://api.github.com/repos/d/r/releases/assets/{a['id']}"}
                for n, a in self.assets.items()
            ]})
        if args[:2] == ("release", "create"):
            self.assets = {}
            return ""
        if args[:2] == ("release", "upload"):
            ruta = Path(args[3])
            self.assets[ruta.name] = {"id": self.siguiente_id, "datos": ruta.read_bytes()}
            self.siguiente_id += 1
            return ""
        if args[:2] == ("release", "download"):
            nombre, destino = args[4], Path(args[6])
            (destino / nombre).write_bytes(self.assets[nombre]["datos"])
            return ""
        if args[:2] == ("repo", "view"):
            return "d/r\n"
        if args[0] == "api":
            metodo, ruta = args[2], args[3]
            id_asset = int(ruta.rsplit("/", 1)[-1])
            nombre = next(n for n, a in self.assets.items() if a["id"] == id_asset)
            if metodo == "DELETE":
                del self.assets[nombre]
            else:
                self.assets[args[5].removeprefix("name=")] = self.assets.pop(nombre)
            return ""
        raise AssertionError(f"Comando de gh no esperado: {args}")


@pytest.fixture
def gh(monkeypatch, tmp_path):
    falso = GhFalso()
    monkeypatch.setattr(historia, "_gh", falso)
    monkeypatch.setattr(historia, "DIR_DATOS", tmp_path / "data")
    monkeypatch.setattr(historia, "DIR_BRONZE", tmp_path / "data" / "bronze")
    return falso


def escribir(nombre: str, contenido: bytes = b"x" * 1000) -> None:
    ruta = historia.DIR_BRONZE / "rmcab__horario" / "fecha_carga=2026-09-25" / nombre
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(contenido)


def archivos_locales() -> list[str]:
    return sorted(p.name for p in historia.DIR_BRONZE.rglob("*.parquet"))


def test_ciclo_completo_conserva_la_corrida_anterior(gh):
    escribir("2026-09-24.parquet")
    historia.subir()
    assert set(gh.assets) == {"bronze.tar"}

    escribir("2026-09-25.parquet")
    historia.subir()
    assert set(gh.assets) == {"bronze.tar", "bronze-anterior.tar"}
    primera = gh.assets["bronze-anterior.tar"]["datos"]

    escribir("2026-09-26.parquet")
    historia.subir()
    assert set(gh.assets) == {"bronze.tar", "bronze-anterior.tar"}
    assert gh.assets["bronze-anterior.tar"]["datos"] != primera  # la más vieja se descarta

    shutil.rmtree(historia.DIR_DATOS)
    historia.bajar()
    assert archivos_locales() == ["2026-09-24.parquet", "2026-09-25.parquet", "2026-09-26.parquet"]


def test_sin_release_se_empieza_sin_datos(gh, capsys):
    historia.bajar()
    assert "no tiene historia todavía" in capsys.readouterr().out
    assert not historia.DIR_BRONZE.exists()


def test_un_error_de_gh_no_se_confunde_con_historia_vacia(gh):
    escribir("2026-09-24.parquet")
    historia.subir()
    shutil.rmtree(historia.DIR_DATOS)
    gh.error_transitorio = True
    with pytest.raises(SystemExit, match="502"):
        historia.bajar()
    # Aunque la corrida siguiera y extrajera el día, no se sube nada
    escribir("2026-09-25.parquet")
    with pytest.raises(SystemExit, match="502"):
        historia.subir()
    assert set(gh.assets) == {"bronze.tar"}


def test_si_la_subida_se_corto_vale_el_archivo_nuevo(gh, monkeypatch):
    escribir("2026-09-24.parquet")
    historia.subir()
    escribir("2026-09-25.parquet")

    # Se sube bronze-nuevo.tar y la corrida se corta antes de renombrarlo
    def cortar_en_el_renombre(*args, capturar=False):
        if args[0] == "api":
            raise subprocess.CalledProcessError(1, ["gh", *args], stderr="se cortó\n")
        return gh(*args, capturar=capturar)

    monkeypatch.setattr(historia, "_gh", cortar_en_el_renombre)
    with pytest.raises(subprocess.CalledProcessError):
        historia.subir()
    assert set(gh.assets) == {"bronze.tar", "bronze-nuevo.tar"}

    monkeypatch.setattr(historia, "_gh", gh)
    shutil.rmtree(historia.DIR_DATOS)
    historia.bajar()
    assert archivos_locales() == ["2026-09-24.parquet", "2026-09-25.parquet"]

    historia.subir()
    assert set(gh.assets) == {"bronze.tar", "bronze-anterior.tar"}


def test_no_reemplaza_la_historia_por_una_mucho_mas_pequena(gh):
    for dia in range(1, 11):
        escribir(f"2026-09-{dia:02d}.parquet", b"x" * 50_000)
    historia.subir()
    vigente = gh.assets["bronze.tar"]["datos"]

    shutil.rmtree(historia.DIR_DATOS)
    escribir("2026-09-25.parquet", b"x" * 50_000)
    with pytest.raises(SystemExit, match="La historia solo crece"):
        historia.subir()
    assert gh.assets["bronze.tar"]["datos"] == vigente
    assert "bronze-nuevo.tar" not in gh.assets

    historia.subir(forzar=True)
    assert gh.assets["bronze-anterior.tar"]["datos"] == vigente
