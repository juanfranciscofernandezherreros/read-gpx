"""Punto de entrada CLI para la librería read-gpx.

Expone un único comando instalable vía ``pyproject.toml``:

* ``read-gpx`` – lee un GPX y genera CSV, mapa HTML y perfil de elevación
  en un directorio de salida.

Uso::

    read-gpx actividad.gpx
    read-gpx actividad.gpx -o mi_salida/
"""

import argparse
import os
import sys


def main():
    """Procesa un archivo GPX y guarda CSV, mapa HTML y perfil en un directorio.

    Uso::

        read-gpx <archivo.gpx> [-o DIRECTORIO_SALIDA]

    Si no se indica ``-o``, los ficheros se guardan en un directorio llamado
    ``<nombre_gpx>_salida/`` creado junto al archivo GPX.
    """
    parser = argparse.ArgumentParser(
        prog="read-gpx",
        description="Lee un GPX y genera CSV + mapa HTML + perfil de elevación en un directorio.",
    )
    parser.add_argument("archivo", help="Ruta al fichero .gpx de entrada")
    parser.add_argument(
        "-o", "--output-dir",
        dest="output_dir",
        default=None,
        help="Directorio donde guardar los ficheros generados (se crea si no existe)",
    )
    args = parser.parse_args()

    archivo = args.archivo

    if not os.path.exists(archivo):
        print(f"Error: no se encontró el archivo '{archivo}'")
        sys.exit(1)

    base = os.path.splitext(os.path.basename(archivo))[0]
    gpx_dir = os.path.dirname(os.path.abspath(archivo))

    if args.output_dir:
        directorio_salida = args.output_dir
    else:
        directorio_salida = os.path.join(gpx_dir, f"{base}_salida")

    os.makedirs(directorio_salida, exist_ok=True)

    archivo_csv = os.path.join(directorio_salida, f"{base}_data.csv")
    archivo_mapa = os.path.join(directorio_salida, f"{base}_mapa.html")
    archivo_perfil = os.path.join(directorio_salida, f"{base}_elevacion.png")

    print(f"Procesando: {archivo}")
    print(f"Directorio de salida: {directorio_salida}")

    from read_gpx.parser import extraer_datos_gpx  # noqa: PLC0415
    from read_gpx.visualizer import calcular_distancia_acumulada, crear_mapa_interactivo, crear_perfil_elevacion  # noqa: PLC0415

    df = extraer_datos_gpx(archivo)
    df.to_csv(archivo_csv, index=False)
    print(f"  CSV guardado:   {archivo_csv}")

    df = calcular_distancia_acumulada(df)
    crear_mapa_interactivo(df, archivo_mapa)
    print(f"  Mapa guardado:  {archivo_mapa}")

    crear_perfil_elevacion(df, archivo_perfil)
    print(f"  Perfil guardado: {archivo_perfil}")

    print("\n¡Listo! Todos los ficheros están en:", directorio_salida)


if __name__ == "__main__":
    main()
