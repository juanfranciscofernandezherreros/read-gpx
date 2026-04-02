"""Tests para el módulo visualizer de read-gpx."""

import os

import pandas as pd
import pytest

from read_gpx.visualizer import (
    calcular_distancia_acumulada,
    procesar_gpx,
)

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


def test_calcular_distancia_acumulada():
    """Verifica que se añade la columna distancia_km correctamente."""
    df = pd.DataFrame(
        {
            "latitud": [40.4168, 40.4170, 40.4172],
            "longitud": [-3.7038, -3.7040, -3.7042],
        }
    )
    result = calcular_distancia_acumulada(df)
    assert "distancia_km" in result.columns
    assert result["distancia_km"].iloc[0] == pytest.approx(0.0)
    assert result["distancia_km"].iloc[-1] > 0.0


def test_procesar_gpx_genera_todos_los_ficheros(sample_gpx_file, tmp_path):
    """Verifica que procesar_gpx crea CSV, HTML, PNG y resumen HTML."""
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

    assert rutas["csv"] == csv_path
    assert rutas["mapa"] == mapa_path
    assert rutas["perfil"] == perfil_path
    assert rutas["resumen"] == resumen_path

    assert os.path.exists(csv_path), "El CSV no se generó"
    assert os.path.exists(mapa_path), "El mapa HTML no se generó"
    assert os.path.exists(perfil_path), "El perfil PNG no se generó"
    assert os.path.exists(resumen_path), "El resumen HTML no se generó"


def test_procesar_gpx_csv_tiene_datos(sample_gpx_file, tmp_path):
    """Verifica que el CSV generado tiene las columnas correctas."""
    csv_path = str(tmp_path / "datos.csv")
    procesar_gpx(
        sample_gpx_file,
        archivo_csv=csv_path,
        archivo_mapa=str(tmp_path / "mapa.html"),
        archivo_perfil=str(tmp_path / "perfil.png"),
        archivo_resumen=str(tmp_path / "resumen.html"),
    )

    df = pd.read_csv(csv_path)
    assert len(df) == 3
    assert {"latitud", "longitud", "elevacion"}.issubset(set(df.columns))


def test_procesar_gpx_rutas_por_defecto(sample_gpx_file):
    """Verifica que procesar_gpx genera rutas de salida por defecto."""
    rutas = procesar_gpx(sample_gpx_file)

    try:
        base = os.path.splitext(os.path.basename(sample_gpx_file))[0]
        assert rutas["csv"].endswith("_data.csv")
        assert rutas["mapa"].endswith(f"{base}_mapa.html")
        assert rutas["perfil"].endswith(f"{base}_elevacion.png")
        assert rutas["resumen"].endswith(f"{base}_resumen.html")
    finally:
        for key in rutas:
            if os.path.exists(rutas[key]):
                os.remove(rutas[key])


def test_procesar_gpx_file_not_found():
    """Verifica que lanza FileNotFoundError si el GPX no existe."""
    with pytest.raises(FileNotFoundError):
        procesar_gpx("/tmp/no_existe.gpx")
