"""Módulo de parsing de archivos GPX para la librería read-gpx.

Proporciona :func:`extraer_datos_gpx`, la función principal de la librería,
que lee un fichero GPX y devuelve un :class:`pandas.DataFrame` listo para
su análisis o visualización.
"""

import gpxpy
import pandas as pd


def extraer_datos_gpx(archivo_entrada: str) -> pd.DataFrame:
    """Lee un archivo GPX y devuelve un DataFrame con los datos de los puntos.

    Extrae latitud, longitud, elevación, tiempo y nombre del track.
    Si el fichero contiene extensiones de dispositivos de fitness Garmin
    (``TrackPointExtension``), también extrae frecuencia cardíaca (``hr``),
    cadencia (``cad``) y temperatura ambiente (``atemp``).

    Args:
        archivo_entrada (str): Ruta al fichero GPX que se desea procesar.

    Returns:
        pandas.DataFrame: DataFrame con una fila por punto del track y las
        siguientes columnas:

        * ``latitud`` – latitud decimal del punto.
        * ``longitud`` – longitud decimal del punto.
        * ``elevacion`` – elevación en metros (``None`` si no está disponible).
        * ``tiempo`` – marca de tiempo como ``datetime64`` (``NaT`` si no
          está disponible).
        * ``nombre_track`` – nombre del track dentro del GPX.
        * ``hr`` *(opcional)* – frecuencia cardíaca en bpm.
        * ``cad`` *(opcional)* – cadencia en rpm.
        * ``atemp`` *(opcional)* – temperatura ambiente en °C.

    Raises:
        FileNotFoundError: Si ``archivo_entrada`` no existe en el sistema de
            ficheros.

    Examples:
        >>> from read_gpx import extraer_datos_gpx
        >>> df = extraer_datos_gpx("mi_actividad.gpx")
        >>> df[["latitud", "longitud", "elevacion"]].head()
    """
    with open(archivo_entrada, "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    datos = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                punto_dict = {
                    "latitud": point.latitude,
                    "longitud": point.longitude,
                    "elevacion": point.elevation,
                    "tiempo": point.time,
                    "nombre_track": track.name,
                }

                if point.extensions:
                    for extension in point.extensions:
                        for child in extension.iter():
                            tag_name = child.tag.split("}")[-1]
                            if tag_name in ["hr", "atemp", "cad"]:
                                punto_dict[tag_name] = child.text

                datos.append(punto_dict)

    df = pd.DataFrame(datos)

    if "tiempo" in df.columns:
        df["tiempo"] = pd.to_datetime(df["tiempo"])

    return df
