"""Tests para el módulo parser de read-gpx."""

import os
import tempfile

import pandas as pd
import pytest

from read_gpx.parser import extraer_datos_gpx

SAMPLE_GPX = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test"
     xmlns="http://www.topografix.com/GPX/1/1"
     xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1">
  <trk>
    <name>Test Track</name>
    <trkseg>
      <trkpt lat="40.4168" lon="-3.7038">
        <ele>650</ele>
        <time>2024-01-15T10:00:00Z</time>
        <extensions>
          <gpxtpx:TrackPointExtension>
            <gpxtpx:hr>142</gpxtpx:hr>
            <gpxtpx:cad>80</gpxtpx:cad>
            <gpxtpx:atemp>18</gpxtpx:atemp>
          </gpxtpx:TrackPointExtension>
        </extensions>
      </trkpt>
      <trkpt lat="40.4170" lon="-3.7040">
        <ele>652</ele>
        <time>2024-01-15T10:00:05Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
"""

MINIMAL_GPX = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test"
     xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>Minimal</name>
    <trkseg>
      <trkpt lat="0.0" lon="0.0">
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
def minimal_gpx_file(tmp_path):
    """Crea un archivo GPX temporal con datos mínimos."""
    gpx_path = tmp_path / "minimal.gpx"
    gpx_path.write_text(MINIMAL_GPX)
    return str(gpx_path)


def test_extraer_datos_gpx_returns_dataframe(sample_gpx_file):
    """Verifica que la función devuelve un DataFrame."""
    result = extraer_datos_gpx(sample_gpx_file)
    assert isinstance(result, pd.DataFrame)


def test_extraer_datos_gpx_columns(sample_gpx_file):
    """Verifica que el DataFrame contiene las columnas esperadas."""
    df = extraer_datos_gpx(sample_gpx_file)
    expected_columns = {"latitud", "longitud", "elevacion", "tiempo", "nombre_track"}
    assert expected_columns.issubset(set(df.columns))


def test_extraer_datos_gpx_row_count(sample_gpx_file):
    """Verifica que se extraen todos los puntos del archivo."""
    df = extraer_datos_gpx(sample_gpx_file)
    assert len(df) == 2


def test_extraer_datos_gpx_coordinates(sample_gpx_file):
    """Verifica que las coordenadas se extraen correctamente."""
    df = extraer_datos_gpx(sample_gpx_file)
    assert df.iloc[0]["latitud"] == pytest.approx(40.4168)
    assert df.iloc[0]["longitud"] == pytest.approx(-3.7038)


def test_extraer_datos_gpx_track_name(sample_gpx_file):
    """Verifica que el nombre del track se extrae correctamente."""
    df = extraer_datos_gpx(sample_gpx_file)
    assert df.iloc[0]["nombre_track"] == "Test Track"


def test_extraer_datos_gpx_extensions(sample_gpx_file):
    """Verifica que las extensiones de fitness se extraen correctamente."""
    df = extraer_datos_gpx(sample_gpx_file)
    assert "hr" in df.columns
    assert df.iloc[0]["hr"] == "142"
    assert df.iloc[0]["cad"] == "80"
    assert df.iloc[0]["atemp"] == "18"


def test_extraer_datos_gpx_time_parsing(sample_gpx_file):
    """Verifica que el campo tiempo se convierte a datetime."""
    df = extraer_datos_gpx(sample_gpx_file)
    assert pd.api.types.is_datetime64_any_dtype(df["tiempo"])


def test_extraer_datos_gpx_minimal(minimal_gpx_file):
    """Verifica que funciona con un GPX sin extensiones ni elevación."""
    df = extraer_datos_gpx(minimal_gpx_file)
    assert len(df) == 1
    assert df.iloc[0]["latitud"] == 0.0
    assert df.iloc[0]["longitud"] == 0.0


def test_extraer_datos_gpx_file_not_found():
    """Verifica que lanza error si el archivo no existe."""
    with pytest.raises(FileNotFoundError):
        extraer_datos_gpx("/tmp/no_existe.gpx")
