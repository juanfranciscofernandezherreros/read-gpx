"""read-gpx: Librería Python para extraer y visualizar datos de archivos GPX.

Uso rápido::

    from read_gpx import extraer_datos_gpx

    df = extraer_datos_gpx("mi_actividad.gpx")
    print(df.head())

Pipeline completo en una sola llamada::

    from read_gpx import procesar_gpx

    rutas = procesar_gpx("mi_actividad.gpx")
    # Genera: mi_actividad_data.csv, mi_actividad_mapa.html, mi_actividad_elevacion.png

Funciones principales exportadas:
    - :func:`extraer_datos_gpx` – parsea un GPX y devuelve un DataFrame.
    - :func:`procesar_gpx` – pipeline completo: GPX → CSV + mapa + perfil.
    - :func:`calcular_distancia_acumulada` – añade la columna ``distancia_km``.
    - :func:`crear_mapa_interactivo` – genera un mapa HTML con la ruta.
    - :func:`crear_perfil_elevacion` – genera un PNG con el perfil de elevación.
    - :func:`procesar_csv` – pipeline CSV → mapa + perfil.
"""

from read_gpx.parser import extraer_datos_gpx
from read_gpx.visualizer import (
    calcular_distancia_acumulada,
    crear_mapa_interactivo,
    crear_perfil_elevacion,
    procesar_csv,
    procesar_gpx,
)

__version__ = "0.1.0"

__all__ = [
    "extraer_datos_gpx",
    "calcular_distancia_acumulada",
    "crear_mapa_interactivo",
    "crear_perfil_elevacion",
    "procesar_csv",
    "procesar_gpx",
    "__version__",
]
