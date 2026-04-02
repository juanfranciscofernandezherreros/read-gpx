"""Punto de entrada CLI para read-gpx."""

import os
import sys

from read_gpx.parser import extraer_datos_gpx


def main(archivo=None, visualizar=False):
    """Procesa un archivo GPX y genera un CSV con los datos extraídos.

    Cuando se llama desde la línea de comandos acepta los siguientes
    argumentos posicionales/opcionales::

        read-gpx [archivo.gpx] [--visualize]

    Args:
        archivo: Ruta al archivo GPX. Si no se proporciona, se usa el
            primer argumento de la línea de comandos o ``actividad.gpx``
            por defecto.
        visualizar: Si es ``True``, ejecuta también la generación del mapa
            y el perfil de elevación tras guardar el CSV.
    """
    args = sys.argv[1:]

    if archivo is None:
        positional = [a for a in args if not a.startswith("--")]
        archivo = positional[0] if positional else "actividad.gpx"

    if not visualizar:
        visualizar = "--visualize" in args

    if not os.path.exists(archivo):
        print(f"Error: No se encontró el archivo '{archivo}'")
        sys.exit(1)

    print(f"--- Procesando {archivo} ---")
    df_final = extraer_datos_gpx(archivo)

    print(df_final.head())

    nombre_csv = archivo.replace(".gpx", "_data.csv")
    df_final.to_csv(nombre_csv, index=False)
    print(f"\n--- Extracción completada. Datos guardados en: {nombre_csv} ---")

    if visualizar:
        from read_gpx.visualizer import procesar_csv  # noqa: PLC0415

        base = os.path.splitext(os.path.basename(archivo))[0]
        print("\n--- Iniciando visualización ---")
        procesar_csv(
            nombre_csv,
            archivo_mapa=f"{base}_mapa.html",
            archivo_perfil=f"{base}_elevacion.png",
        )


def dibujar_ruta(archivo_csv=None):
    """Genera el mapa interactivo y el perfil de elevación desde un CSV.

    Acepta la ruta al CSV como primer argumento de la línea de comandos.

    Args:
        archivo_csv: Ruta al fichero CSV generado por ``read-gpx``. Si no
            se proporciona, se usa el primer argumento de la línea de
            comandos.
    """
    import glob  # noqa: PLC0415

    from read_gpx.visualizer import procesar_csv  # noqa: PLC0415

    if archivo_csv is None:
        if len(sys.argv) > 1:
            archivo_csv = sys.argv[1]
        else:
            candidatos = glob.glob("*_data.csv")
            if not candidatos:
                print("Error: no se encontró ningún fichero *_data.csv.")
                print("Uso: dibujar-ruta <archivo.csv>")
                sys.exit(1)
            archivo_csv = candidatos[0]
            print(f"Usando fichero: {archivo_csv}")

    base = os.path.splitext(os.path.basename(archivo_csv))[0]
    if base.endswith("_data"):
        base = base[:-5]
    procesar_csv(
        archivo_csv,
        archivo_mapa=f"{base}_mapa.html",
        archivo_perfil=f"{base}_elevacion.png",
    )


if __name__ == "__main__":
    main()
