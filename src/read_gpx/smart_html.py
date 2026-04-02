"""Módulo de generación de HTML inteligente para rutas GPX.

Proporciona :func:`crear_html_inteligente`, que genera un único fichero HTML
con un dashboard completo: mapa interactivo, perfil de elevación incrustado,
y estadísticas de la ruta (distancia, desnivel, duración, velocidad, etc.).
"""

import base64
import io

import folium
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from folium import plugins
from geopy.distance import geodesic


def _calcular_estadisticas(df: pd.DataFrame) -> dict:
    """Calcula las estadísticas principales de la ruta.

    Args:
        df: DataFrame con columnas ``latitud``, ``longitud``, ``elevacion``,
            ``distancia_km`` y opcionalmente ``tiempo``.

    Returns:
        Diccionario con las estadísticas calculadas.
    """
    stats: dict = {}

    # Distancia
    stats["distancia_km"] = df["distancia_km"].max()

    # Elevación
    elevaciones = df["elevacion"].dropna()
    if not elevaciones.empty:
        stats["elevacion_min"] = elevaciones.min()
        stats["elevacion_max"] = elevaciones.max()
        stats["desnivel_total"] = stats["elevacion_max"] - stats["elevacion_min"]

        # Desnivel positivo y negativo acumulado
        diffs = elevaciones.diff().dropna()
        stats["desnivel_positivo"] = diffs[diffs > 0].sum()
        stats["desnivel_negativo"] = abs(diffs[diffs < 0].sum())
    else:
        stats["elevacion_min"] = 0
        stats["elevacion_max"] = 0
        stats["desnivel_total"] = 0
        stats["desnivel_positivo"] = 0
        stats["desnivel_negativo"] = 0

    # Coordenadas inicio y fin
    stats["inicio_lat"] = df.iloc[0]["latitud"]
    stats["inicio_lon"] = df.iloc[0]["longitud"]
    stats["fin_lat"] = df.iloc[-1]["latitud"]
    stats["fin_lon"] = df.iloc[-1]["longitud"]

    # Duración y velocidad
    if "tiempo" in df.columns:
        tiempos = df["tiempo"].dropna()
        if len(tiempos) >= 2:
            t_inicio = pd.Timestamp(tiempos.iloc[0])
            t_fin = pd.Timestamp(tiempos.iloc[-1])
            duracion = t_fin - t_inicio
            stats["duracion_segundos"] = duracion.total_seconds()
            horas = stats["duracion_segundos"] / 3600
            stats["duracion_texto"] = _formatear_duracion(stats["duracion_segundos"])
            if horas > 0:
                stats["velocidad_media_kmh"] = stats["distancia_km"] / horas
            else:
                stats["velocidad_media_kmh"] = 0
        else:
            stats["duracion_segundos"] = 0
            stats["duracion_texto"] = "N/D"
            stats["velocidad_media_kmh"] = 0
    else:
        stats["duracion_segundos"] = 0
        stats["duracion_texto"] = "N/D"
        stats["velocidad_media_kmh"] = 0

    # Nombre del track
    stats["nombre_track"] = (
        str(df["nombre_track"].iloc[0]) if "nombre_track" in df.columns else "Ruta"
    )

    # Número de puntos
    stats["num_puntos"] = len(df)

    return stats


def _formatear_duracion(segundos: float) -> str:
    """Convierte segundos a formato ``Xh Ym Zs``."""
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    partes = []
    if h > 0:
        partes.append(f"{h}h")
    if m > 0 or h > 0:
        partes.append(f"{m}m")
    partes.append(f"{s}s")
    return " ".join(partes)


def _generar_perfil_base64(df: pd.DataFrame) -> str:
    """Genera el perfil de elevación como imagen PNG codificada en base64.

    Args:
        df: DataFrame con columnas ``distancia_km`` y ``elevacion``.

    Returns:
        Cadena base64 de la imagen PNG.
    """
    matplotlib.use("Agg")

    fig, ax = plt.subplots(figsize=(14, 4))

    ax.fill_between(df["distancia_km"], df["elevacion"], color="#FF8C00", alpha=0.3)
    ax.plot(df["distancia_km"], df["elevacion"], color="#FF4500", linewidth=2)

    ax.set_xlabel("Distancia (km)", fontsize=11)
    ax.set_ylabel("Elevación (m)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_xlim(0, df["distancia_km"].max())

    elev_min = df["elevacion"].min()
    elev_max = df["elevacion"].max()
    margen = max((elev_max - elev_min) * 0.1, 10)
    ax.set_ylim(elev_min - margen, elev_max + margen)

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _generar_mapa_html(df: pd.DataFrame) -> str:
    """Genera el HTML del mapa folium como cadena (sin fichero).

    Args:
        df: DataFrame con columnas ``latitud``, ``longitud`` y ``nombre_track``.

    Returns:
        Cadena HTML del mapa.
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

    nombre_track = (
        df["nombre_track"].iloc[0] if "nombre_track" in df.columns else "Inicio"
    )

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

    return m._repr_html_()


def crear_html_inteligente(
    df: pd.DataFrame,
    archivo_salida: str = "resumen_ruta.html",
) -> str:
    """Genera un HTML inteligente con mapa, perfil de elevación y estadísticas.

    Produce un único fichero HTML autocontenido que incluye:

    * **Cabecera** con el nombre del track.
    * **Tarjetas de estadísticas** (distancia, desnivel, duración, velocidad…).
    * **Mapa interactivo** con la ruta trazada, marcadores de inicio/fin y
      capas satélite y topográfica.
    * **Perfil de elevación** incrustado como imagen PNG en base64.

    Args:
        df: DataFrame con al menos las columnas ``latitud``, ``longitud`` y
            ``elevacion``. Si no contiene ``distancia_km``, se calcula
            automáticamente.
        archivo_salida: Ruta donde se guardará el fichero HTML.

    Returns:
        La ruta del fichero HTML generado.
    """
    from read_gpx.visualizer import calcular_distancia_acumulada  # noqa: PLC0415

    if "distancia_km" not in df.columns:
        df = calcular_distancia_acumulada(df)

    stats = _calcular_estadisticas(df)
    mapa_html = _generar_mapa_html(df)
    perfil_b64 = _generar_perfil_base64(df)

    nombre = stats["nombre_track"]
    nombre_corto = nombre[:40] + ("…" if len(nombre) > 40 else "")

    html = f"""\
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Resumen – {nombre_corto}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                 'Helvetica Neue', Arial, sans-serif;
    background: #f0f2f5;
    color: #333;
  }}
  .header {{
    background: linear-gradient(135deg, #FF4500, #FF8C00);
    color: #fff;
    padding: 24px 32px;
    text-align: center;
  }}
  .header h1 {{ font-size: 1.6em; font-weight: 700; }}
  .header p {{ font-size: 0.9em; opacity: 0.85; margin-top: 4px; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
  .stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
    margin-bottom: 20px;
  }}
  .stat-card {{
    background: #fff;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }}
  .stat-card .icon {{ font-size: 1.6em; margin-bottom: 4px; }}
  .stat-card .value {{ font-size: 1.4em; font-weight: 700; color: #FF4500; }}
  .stat-card .label {{ font-size: 0.8em; color: #888; margin-top: 2px; }}
  .section {{
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 20px;
    overflow: hidden;
  }}
  .section-title {{
    padding: 14px 20px;
    font-size: 1.05em;
    font-weight: 600;
    border-bottom: 1px solid #eee;
  }}
  .map-wrapper {{ width: 100%; height: 480px; }}
  .map-wrapper iframe {{ width: 100%; height: 100%; border: none; }}
  .profile-img {{
    width: 100%;
    display: block;
    padding: 12px;
  }}
  .footer {{
    text-align: center;
    padding: 16px;
    font-size: 0.8em;
    color: #aaa;
  }}
</style>
</head>
<body>

<div class="header">
  <h1>🗺️ {nombre_corto}</h1>
  <p>Resumen inteligente de la ruta</p>
</div>

<div class="container">

  <!-- Estadísticas -->
  <div class="stats-grid">
    <div class="stat-card">
      <div class="icon">📏</div>
      <div class="value">{stats['distancia_km']:.2f} km</div>
      <div class="label">Distancia</div>
    </div>
    <div class="stat-card">
      <div class="icon">⬆️</div>
      <div class="value">{stats['desnivel_positivo']:.0f} m</div>
      <div class="label">Desnivel +</div>
    </div>
    <div class="stat-card">
      <div class="icon">⬇️</div>
      <div class="value">{stats['desnivel_negativo']:.0f} m</div>
      <div class="label">Desnivel −</div>
    </div>
    <div class="stat-card">
      <div class="icon">⛰️</div>
      <div class="value">{stats['elevacion_max']:.0f} m</div>
      <div class="label">Altitud máx.</div>
    </div>
    <div class="stat-card">
      <div class="icon">🕳️</div>
      <div class="value">{stats['elevacion_min']:.0f} m</div>
      <div class="label">Altitud mín.</div>
    </div>
    <div class="stat-card">
      <div class="icon">⏱️</div>
      <div class="value">{stats['duracion_texto']}</div>
      <div class="label">Duración</div>
    </div>
    <div class="stat-card">
      <div class="icon">🚀</div>
      <div class="value">{stats['velocidad_media_kmh']:.1f} km/h</div>
      <div class="label">Velocidad media</div>
    </div>
    <div class="stat-card">
      <div class="icon">📍</div>
      <div class="value">{stats['num_puntos']}</div>
      <div class="label">Puntos GPS</div>
    </div>
  </div>

  <!-- Mapa interactivo -->
  <div class="section">
    <div class="section-title">🗺️ Mapa interactivo</div>
    <div class="map-wrapper">
      <iframe srcdoc='{mapa_html.replace("'", "&#39;")}'></iframe>
    </div>
  </div>

  <!-- Perfil de elevación -->
  <div class="section">
    <div class="section-title">📈 Perfil de elevación</div>
    <img class="profile-img" src="data:image/png;base64,{perfil_b64}"
         alt="Perfil de elevación">
  </div>

</div>

<div class="footer">
  Generado por <strong>read-gpx</strong>
</div>

</body>
</html>"""

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(html)

    return archivo_salida
