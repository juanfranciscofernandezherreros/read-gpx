"""Punto de entrada CLI para read-gpx."""

import os
import sys

from read_gpx.parser import extraer_datos_gpx


def main(archivo=None):
    """Procesa un archivo GPX y genera un CSV con los datos extraídos.

    Args:
        archivo: Ruta al archivo GPX. Si no se proporciona, se usa el
            primer argumento de la línea de comandos o ``actividad.gpx``
            por defecto.
    """
    if archivo is None:
        archivo = sys.argv[1] if len(sys.argv) > 1 else "actividad.gpx"

    if not os.path.exists(archivo):
        print(f"Error: No se encontró el archivo '{archivo}'")
        sys.exit(1)

    print(f"--- Procesando {archivo} ---")
    df_final = extraer_datos_gpx(archivo)

    print(df_final.head())

    nombre_csv = archivo.replace(".gpx", "_data.csv")
    df_final.to_csv(nombre_csv, index=False)
    print(f"\n--- Extracción completada. Datos guardados en: {nombre_csv} ---")


if __name__ == "__main__":
    main()
