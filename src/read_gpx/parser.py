import gpxpy
import pandas as pd


def extraer_datos_gpx(archivo_entrada):
    """Lee un archivo GPX y devuelve un DataFrame con los datos de los puntos.

    Extrae latitud, longitud, elevación, tiempo, nombre del track y
    extensiones comunes de dispositivos de fitness (frecuencia cardíaca,
    temperatura y cadencia).

    Args:
        archivo_entrada: Ruta al archivo GPX.

    Returns:
        Un ``pandas.DataFrame`` con los datos extraídos.
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
