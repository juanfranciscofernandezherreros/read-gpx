"""Script de visualización de rutas GPX exportadas a CSV.

Uso:
    python dibujar_ruta.py <archivo.csv>

Si no se proporciona un argumento, se busca el primer fichero .csv en el
directorio actual cuyo nombre termine en ``_data.csv``.

Genera:
    mapa_interactivo.html  - Mapa interactivo con capas satélite/topográfica.
    perfil_elevacion.png   - Gráfico del perfil de elevación.
"""

from read_gpx.cli import dibujar_ruta

if __name__ == "__main__":
    dibujar_ruta()
