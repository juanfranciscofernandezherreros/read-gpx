"""Módulo de visualización para rutas GPX exportadas a CSV."""

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


def procesar_csv(archivo_csv: str, prefijo_salida: str = "") -> None:
    """Carga un CSV generado por ``read-gpx`` y produce el mapa y el perfil.

    Args:
        archivo_csv: Ruta al fichero CSV con los datos de la ruta.
        prefijo_salida: Prefijo opcional para los ficheros de salida.
    """
    df = pd.read_csv(archivo_csv)
    df = calcular_distancia_acumulada(df)

    distancia_total = df["distancia_km"].max()
    desnivel = df["elevacion"].max() - df["elevacion"].min()
    print(f"Distancia total calculada: {distancia_total:.2f} km")
    print(f"Desnivel máximo: {desnivel:.2f} m")

    mapa_html = f"{prefijo_salida}mapa_interactivo.html" if prefijo_salida else "mapa_interactivo.html"
    perfil_png = f"{prefijo_salida}perfil_elevacion.png" if prefijo_salida else "perfil_elevacion.png"

    crear_mapa_interactivo(df, mapa_html)
    crear_perfil_elevacion(df, perfil_png)

    print("\n--- PROCESO COMPLETADO ---")
    print(f"1. Abre '{mapa_html}' para ver la ruta en el mapa.")
    print(f"2. Revisa '{perfil_png}' para el gráfico de altitud.")
