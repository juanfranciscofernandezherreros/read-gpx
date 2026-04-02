import gpxpy
import pandas as pd
import os

def extraer_datos_gpx(archivo_entrada):
    # Abrir y parsear el archivo
    with open(archivo_entrada, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    datos = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                # Datos básicos
                punto_dict = {
                    'latitud': point.latitude,
                    'longitud': point.longitude,
                    'elevacion': point.elevation,
                    'tiempo': point.time,
                    'nombre_track': track.name
                }

                # Extraer extensiones (Frecuencia cardíaca, Cadencia, etc.)
                # Estos suelen estar bajo el namespace de Garmin 'TrackPointExtension'
                if point.extensions:
                    for extension in point.extensions:
                        # Buscamos etiquetas comunes en archivos de fitness
                        for child in extension.iter():
                            tag_name = child.tag.split('}')[-1] # Limpiar el namespace XML
                            if tag_name in ['hr', 'atemp', 'cad']:
                                punto_dict[tag_name] = child.text

                datos.append(punto_dict)

    # Crear el DataFrame
    df = pd.DataFrame(datos)
    
    # Convertir tiempo a objeto datetime para facilitar análisis posterior
    if 'tiempo' in df.columns:
        df['tiempo'] = pd.to_datetime(df['tiempo'])

    return df

if __name__ == "__main__":
    # Nombre del archivo GPX (cambia 'ruta_al_archivo.gpx' por el tuyo)
    archivo = 'actividad.gpx' 
    
    if os.path.exists(archivo):
        print(f"--- Procesando {archivo} ---")
        df_final = extraer_datos_gpx(archivo)
        
        # Mostrar los primeros resultados en consola
        print(df_final.head())
        
        # Guardar todo a un CSV para abrir en Excel o LibreOffice
        nombre_csv = archivo.replace('.gpx', '_data.csv')
        df_final.to_csv(nombre_csv, index=False)
        print(f"\n--- Extracción completada. Datos guardados en: {nombre_csv} ---")
    else:
        print(f"Error: No se encontró el archivo '{archivo}'")
