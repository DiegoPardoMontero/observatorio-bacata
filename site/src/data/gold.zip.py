"""Dataset Gold completo en Parquet, en un zip (RF-17)."""

import io
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _gold import GOLD  # noqa: E402

LEEME = """Observatorio Bacatá — dataset Gold
https://diegopardomontero.github.io/observatorio-bacata/

Tablas en Parquet. La metodología está en la página de metodología del sitio
y en https://github.com/DiegoPardoMontero/observatorio-bacata.

Licencia: CC BY-SA 4.0. Fuentes: RMCAB (Secretaría Distrital de Ambiente),
Delito de Alto Impacto (Secretaría Distrital de Seguridad, Convivencia y
Justicia, CC BY-SA 4.0) y Localidad. Bogotá D.C. (Catastro Distrital, CC BY 4.0).
Las horas están en hora de Bogotá (UTC−5) y marcan el inicio de cada hora.
"""

memoria = io.BytesIO()
with zipfile.ZipFile(memoria, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("LEEME.txt", LEEME)
    for archivo in sorted(GOLD.glob("*.parquet")):
        z.write(archivo, archivo.name)
sys.stdout.buffer.write(memoria.getvalue())
