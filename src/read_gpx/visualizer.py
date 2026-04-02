"""Módulo de visualización para rutas GPX exportadas a CSV.

Proporciona tres funciones independientes y una función de pipeline:

* :func:`calcular_distancia_acumulada` – calcula la distancia acumulada.
* :func:`crear_mapa_interactivo` – genera un mapa HTML interactivo.
* :func:`crear_perfil_elevacion` – genera un gráfico PNG de elevación.
* :func:`procesar_csv` – pipeline completo: CSV → mapa + perfil.

Ejemplo::

    from read_gpx import procesar_csv

    procesar_csv("mi_actividad_data.csv")
"""

import pandas as pd
import folium
from folium import plugins
import matplotlib.pyplot as plt
from geopy.distance import geodesic


def calcular_distancia_acumulada(df: pd.DataFrame) -> pd.DataFrame:
    """Añade una columna ``distancia_km`` con la distancia acumulada en km.

    Usa la fórmula geodésica (Haversine) para medir con precisión la
    curvatura de la Tierra entre puntos consecutivos.

    Args:
        df: DataFrame con columnas ``latitud`` y ``longitud``.

    Returns:
        El mismo DataFrame con la columna ``distancia_km`` añadida.
    """
    distancias = [0.0]
    distancia_total = 0.0

    for i in range(1, len(df)):
        punto_ant = (df.loc[i - 1, "latitud"], df.loc[i - 1, "longitud"])
        punto_act = (df.loc[i, "latitud"], df.loc[i, "longitud"])
        distancia_total += geodesic(punto_ant, punto_act).kilometers
        distancias.append(distancia_total)

    df = df.copy()
    df["distancia_km"] = distancias
    return df


def crear_mapa_interactivo(df: pd.DataFrame, archivo_salida: str = "mapa_interactivo.html") -> str:
    """Genera un mapa HTML interactivo con la ruta y capas satélite/topográfica.

    Args:
        df: DataFrame con columnas ``latitud``, ``longitud`` y ``nombre_track``.
        archivo_salida: Ruta donde se guardará el fichero HTML.

    Returns:
        La ruta del fichero HTML generado.
    """
    centro_lat = df["latitud"].mean()
    centro_lon = df["longitud"].mean()

    m = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=14,
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ),
        attr="Esri World Imagery",
    )

    folium.TileLayer(
        "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="OpenTopoMap",
        name="Relieve Topográfico",
    ).add_to(m)

    puntos_ruta = df[["latitud", "longitud"]].values.tolist()
    folium.PolyLine(
        puntos_ruta,
        color="#FF8C00",
        weight=6,
        opacity=0.9,
        tooltip="Ver detalles",
    ).add_to(m)

    nombre_track = df["nombre_track"].iloc[0] if "nombre_track" in df.columns else "Inicio"

    folium.Marker(
        puntos_ruta[0],
        popup=f"<b>INICIO:</b> {nombre_track}",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(m)

    folium.Marker(
        puntos_ruta[-1],
        popup=f"<b>FIN:</b> {nombre_track}",
        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
    ).add_to(m)

    plugins.Fullscreen().add_to(m)
    folium.LayerControl().add_to(m)

    m.save(archivo_salida)
    return archivo_salida


def crear_perfil_elevacion(df: pd.DataFrame, archivo_salida: str = "perfil_elevacion.png") -> str:
    """Genera un gráfico PNG con el perfil de elevación de la ruta.

    El DataFrame debe contener las columnas ``distancia_km`` y ``elevacion``.
    Si no existe ``distancia_km``, se llama primero a
    :func:`calcular_distancia_acumulada`.

    Args:
        df: DataFrame con los datos de la ruta.
        archivo_salida: Ruta donde se guardará el fichero PNG.

    Returns:
        La ruta del fichero PNG generado.
    """
    if "distancia_km" not in df.columns:
        df = calcular_distancia_acumulada(df)

    nombre_track = df["nombre_track"].iloc[0] if "nombre_track" in df.columns else "Ruta"

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.fill_between(df["distancia_km"], df["elevacion"], color="#FF8C00", alpha=0.3)
    ax.plot(df["distancia_km"], df["elevacion"], color="#FF4500", linewidth=2.5)

    nombre_track_str = str(nombre_track)
    titulo = (
        f"Perfil de Elevación - {nombre_track_str[:30]}"
        + ("..." if len(nombre_track_str) > 30 else "")
    )
    ax.set_title(titulo, fontsize=14, fontweight="bold")
    ax.set_xlabel("Distancia (Kilómetros)", fontsize=12)
    ax.set_ylabel("Elevación (msnm)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.set_xlim(0, df["distancia_km"].max())
    ax.set_ylim(df["elevacion"].min() - 20, df["elevacion"].max() + 50)

    fig.tight_layout()
    fig.savefig(archivo_salida, dpi=300)
    plt.close(fig)
    return archivo_salida


def procesar_csv(
    archivo_csv: str,
    prefijo_salida: str = "",
    archivo_mapa: str | None = None,
    archivo_perfil: str | None = None,
) -> None:
    """Carga un CSV generado por ``read-gpx`` y produce el mapa y el perfil.

    Args:
        archivo_csv: Ruta al fichero CSV con los datos de la ruta.
        prefijo_salida: Prefijo opcional para los ficheros de salida (ignorado
            si se proporcionan ``archivo_mapa`` o ``archivo_perfil``).
        archivo_mapa: Ruta explícita para el fichero HTML del mapa. Si no se
            indica, se deriva de ``prefijo_salida`` o se usa el valor por
            defecto ``mapa_interactivo.html``.
        archivo_perfil: Ruta explícita para el fichero PNG del perfil. Si no
            se indica, se deriva de ``prefijo_salida`` o se usa el valor por
            defecto ``perfil_elevacion.png``.
    """
    df = pd.read_csv(archivo_csv)
    df = calcular_distancia_acumulada(df)

    distancia_total = df["distancia_km"].max()
    desnivel = df["elevacion"].max() - df["elevacion"].min()
    print(f"Distancia total calculada: {distancia_total:.2f} km")
    print(f"Desnivel máximo: {desnivel:.2f} m")

    if archivo_mapa is None:
        archivo_mapa = f"{prefijo_salida}mapa_interactivo.html" if prefijo_salida else "mapa_interactivo.html"
    if archivo_perfil is None:
        archivo_perfil = f"{prefijo_salida}perfil_elevacion.png" if prefijo_salida else "perfil_elevacion.png"

    crear_mapa_interactivo(df, archivo_mapa)
    crear_perfil_elevacion(df, archivo_perfil)

    print("\n--- PROCESO COMPLETADO ---")
    print(f"1. Abre '{archivo_mapa}' para ver la ruta en el mapa.")
    print(f"2. Revisa '{archivo_perfil}' para el gráfico de altitud.")


def procesar_gpx(
    archivo_gpx: str,
    archivo_csv: str | None = None,
    archivo_mapa: str | None = None,
    archivo_perfil: str | None = None,
) -> dict:
    """Pipeline completo: GPX → CSV + mapa HTML + perfil de elevación PNG.

    Lee el archivo GPX, guarda los datos en CSV y genera el mapa interactivo
    y el perfil de elevación en un único paso.

    Args:
        archivo_gpx: Ruta al fichero ``.gpx`` de entrada.
        archivo_csv: Ruta para el CSV de salida. Si no se indica, se deriva
            del nombre del GPX sustituyendo la extensión por ``_data.csv``.
        archivo_mapa: Ruta para el fichero HTML del mapa. Si no se indica,
            se deriva del nombre del GPX añadiendo ``_mapa.html``.
        archivo_perfil: Ruta para el PNG del perfil de elevación. Si no se
            indica, se deriva del nombre del GPX añadiendo ``_elevacion.png``.

    Returns:
        Diccionario con las rutas de los ficheros generados bajo las claves
        ``csv``, ``mapa`` y ``perfil``.

    Examples:
        >>> from read_gpx import procesar_gpx
        >>> rutas = procesar_gpx("mi_actividad.gpx")
        >>> print(rutas["mapa"])   # mi_actividad_mapa.html
        >>> print(rutas["csv"])    # mi_actividad_data.csv
    """
    import os  # noqa: PLC0415

    from read_gpx.parser import extraer_datos_gpx  # noqa: PLC0415

    base = os.path.splitext(os.path.basename(archivo_gpx))[0]

    if archivo_csv is None:
        archivo_csv = os.path.join(os.path.dirname(archivo_gpx) or ".", f"{base}_data.csv")
    if archivo_mapa is None:
        archivo_mapa = os.path.join(os.path.dirname(archivo_gpx) or ".", f"{base}_mapa.html")
    if archivo_perfil is None:
        archivo_perfil = os.path.join(os.path.dirname(archivo_gpx) or ".", f"{base}_elevacion.png")

    df = extraer_datos_gpx(archivo_gpx)
    df.to_csv(archivo_csv, index=False)
    print(f"CSV guardado en: {archivo_csv}")

    df = calcular_distancia_acumulada(df)

    distancia_total = df["distancia_km"].max()
    desnivel = df["elevacion"].max() - df["elevacion"].min()
    print(f"Distancia total calculada: {distancia_total:.2f} km")
    print(f"Desnivel máximo: {desnivel:.2f} m")

    crear_mapa_interactivo(df, archivo_mapa)
    crear_perfil_elevacion(df, archivo_perfil)

    print("\n--- PROCESO COMPLETADO ---")
    print(f"1. CSV:      {archivo_csv}")
    print(f"2. Mapa:     {archivo_mapa}")
    print(f"3. Perfil:   {archivo_perfil}")

    return {"csv": archivo_csv, "mapa": archivo_mapa, "perfil": archivo_perfil}
