"""Tests para el módulo smart_html de read-gpx."""

import os

import pandas as pd
import pytest

from read_gpx.parser import extraer_datos_gpx
from read_gpx.smart_html import (
    _calcular_estadisticas,
    _formatear_duracion,
    _generar_mapa_html,
    _generar_perfil_base64,
    crear_html_inteligente,
)
from read_gpx.visualizer import calcular_distancia_acumulada

SAMPLE_GPX = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test"
     xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>Test Track</name>
    <trkseg>
      <trkpt lat="40.4168" lon="-3.7038">
        <ele>650</ele>
        <time>2024-01-15T10:00:00Z</time>
      </trkpt>
      <trkpt lat="40.4170" lon="-3.7040">
        <ele>652</ele>
        <time>2024-01-15T10:00:05Z</time>
      </trkpt>
      <trkpt lat="40.4172" lon="-3.7042">
        <ele>655</ele>
        <time>2024-01-15T10:00:10Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""


@pytest.fixture
def sample_gpx_file(tmp_path):
    """Crea un archivo GPX temporal de ejemplo."""
    gpx_path = tmp_path / "test.gpx"
    gpx_path.write_text(SAMPLE_GPX)
    return str(gpx_path)


@pytest.fixture
def sample_df(sample_gpx_file):
    """DataFrame de ejemplo con distancia calculada."""
    df = extraer_datos_gpx(sample_gpx_file)
    return calcular_distancia_acumulada(df)


def test_formatear_duracion_horas():
    """Verifica formato con horas, minutos y segundos."""
    assert _formatear_duracion(3661) == "1h 1m 1s"


def test_formatear_duracion_horas_sin_minutos():
    """Verifica formato con horas y segundos pero sin minutos."""
    assert _formatear_duracion(3605) == "1h 5s"


def test_formatear_duracion_minutos():
    """Verifica formato solo con minutos y segundos."""
    assert _formatear_duracion(125) == "2m 5s"


def test_formatear_duracion_segundos():
    """Verifica formato solo con segundos."""
    assert _formatear_duracion(45) == "45s"


def test_calcular_estadisticas_distancia(sample_df):
    """Verifica que la distancia se calcula correctamente."""
    stats = _calcular_estadisticas(sample_df)
    assert stats["distancia_km"] > 0


def test_calcular_estadisticas_elevacion(sample_df):
    """Verifica que las estadísticas de elevación se calculan."""
    stats = _calcular_estadisticas(sample_df)
    assert stats["elevacion_min"] == 650
    assert stats["elevacion_max"] == 655
    assert stats["desnivel_positivo"] > 0


def test_calcular_estadisticas_duracion(sample_df):
    """Verifica que la duración se calcula."""
    stats = _calcular_estadisticas(sample_df)
    assert stats["duracion_segundos"] == 10
    assert "10s" in stats["duracion_texto"]


def test_calcular_estadisticas_velocidad(sample_df):
    """Verifica que la velocidad media se calcula."""
    stats = _calcular_estadisticas(sample_df)
    assert stats["velocidad_media_kmh"] > 0


def test_calcular_estadisticas_nombre_track(sample_df):
    """Verifica que el nombre del track se extrae."""
    stats = _calcular_estadisticas(sample_df)
    assert stats["nombre_track"] == "Test Track"


def test_generar_perfil_base64(sample_df):
    """Verifica que el perfil se genera como base64 válido de imagen PNG."""
    import base64 as b64mod

    b64 = _generar_perfil_base64(sample_df)
    assert isinstance(b64, str)
    assert len(b64) > 100  # debe ser una imagen real

    # Validar que es base64 decodificable y empieza con la firma PNG
    raw = b64mod.b64decode(b64)
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"


def test_generar_mapa_html(sample_df):
    """Verifica que el mapa se genera como HTML."""
    html = _generar_mapa_html(sample_df)
    assert "<div" in html or "<iframe" in html.lower() or "leaflet" in html.lower()


def test_crear_html_inteligente_genera_fichero(sample_df, tmp_path):
    """Verifica que se crea el fichero HTML de resumen."""
    salida = str(tmp_path / "resumen.html")
    resultado = crear_html_inteligente(sample_df, salida)
    assert resultado == salida
    assert os.path.exists(salida)


def test_crear_html_inteligente_contenido(sample_df, tmp_path):
    """Verifica que el HTML contiene las secciones esperadas."""
    salida = str(tmp_path / "resumen.html")
    crear_html_inteligente(sample_df, salida)

    with open(salida, encoding="utf-8") as f:
        contenido = f.read()

    # Debe contener estadísticas
    assert "Distancia" in contenido
    assert "Desnivel" in contenido

    # Debe contener el mapa embebido
    assert "iframe" in contenido.lower() or "leaflet" in contenido.lower()

    # Debe contener el perfil de elevación en base64
    assert "data:image/png;base64," in contenido

    # Debe contener el nombre del track
    assert "Test Track" in contenido


def test_crear_html_inteligente_sin_distancia_km(sample_gpx_file, tmp_path):
    """Verifica que funciona aunque el DF no tenga distancia_km."""
    df = extraer_datos_gpx(sample_gpx_file)
    assert "distancia_km" not in df.columns

    salida = str(tmp_path / "resumen2.html")
    resultado = crear_html_inteligente(df, salida)
    assert os.path.exists(resultado)


def test_procesar_gpx_genera_resumen(sample_gpx_file, tmp_path):
    """Verifica que procesar_gpx ahora también genera el resumen HTML."""
    from read_gpx.visualizer import procesar_gpx

    csv_path = str(tmp_path / "out.csv")
    mapa_path = str(tmp_path / "out.html")
    perfil_path = str(tmp_path / "out.png")
    resumen_path = str(tmp_path / "out_resumen.html")

    rutas = procesar_gpx(
        sample_gpx_file,
        archivo_csv=csv_path,
        archivo_mapa=mapa_path,
        archivo_perfil=perfil_path,
        archivo_resumen=resumen_path,
    )

    assert rutas["resumen"] == resumen_path
    assert os.path.exists(resumen_path), "El resumen HTML no se generó"
