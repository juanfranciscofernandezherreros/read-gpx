# read-gpx

Herramienta en Python para extraer datos de archivos GPX y convertirlos a CSV
y generar automáticamente un mapa interactivo y un perfil de elevación.

Lee tracks de archivos GPX y extrae coordenadas, elevación, tiempo y extensiones
de dispositivos de fitness (frecuencia cardíaca, cadencia y temperatura).

## Pipeline completo (un solo comando)

Pasa tu archivo GPX y el programa hace todo: extrae los datos a CSV **y** genera
el mapa web y el gráfico de elevación.

```bash
read-gpx mi_actividad.gpx --visualize
```

Esto genera tres ficheros en el mismo directorio:

| Fichero                      | Descripción                              |
|------------------------------|------------------------------------------|
| `mi_actividad_data.csv`      | Todos los puntos del track en CSV        |
| `mi_actividad_mapa.html`     | Mapa interactivo (abre en el navegador)  |
| `mi_actividad_elevacion.png` | Gráfico del perfil de elevación          |

También puedes usar el atajo de `make`:

```bash
make run-all GPX=mi_actividad.gpx
```

## Requisitos

- Python 3.9 o superior

## Instalación

Los sistemas Debian/Ubuntu modernos (Python 3.12+) gestionan el entorno de Python de forma externa y no permiten instalar paquetes con `pip` directamente. Usa un entorno virtual:

```bash
# Clonar el repositorio
git clone https://github.com/juanfranciscofernandezherreros/read-gpx.git
cd read-gpx

# Opción 1 – script automático (crea .venv e instala todo)
bash setup.sh
source .venv/bin/activate

# Opción 2 – usando make
make setup
source .venv/bin/activate

# Opción 3 – manualmente
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

## Uso

### Línea de comandos

```bash
# Pipeline completo: GPX → CSV + mapa HTML + gráfico de elevación
read-gpx mi_actividad.gpx --visualize

# Solo extraer datos a CSV
read-gpx mi_actividad.gpx

# Generar mapa y gráfico a partir de un CSV ya existente
dibujar-ruta mi_actividad_data.csv

# O ejecutar directamente el script original
python extraer_gpx.py
```

### Como librería

```python
from read_gpx.parser import extraer_datos_gpx

df = extraer_datos_gpx("mi_actividad.gpx")
print(df.head())
```

El DataFrame resultante contiene las columnas:

| Columna        | Descripción                              |
|----------------|------------------------------------------|
| `latitud`      | Latitud del punto                        |
| `longitud`     | Longitud del punto                       |
| `elevacion`    | Elevación en metros                      |
| `tiempo`       | Marca de tiempo (`datetime`)             |
| `nombre_track` | Nombre del track                         |
| `hr`           | Frecuencia cardíaca (si está disponible) |
| `cad`          | Cadencia (si está disponible)            |
| `atemp`        | Temperatura ambiente (si está disponible)|

## Desarrollo

```bash
# Crear el entorno virtual e instalar dependencias de desarrollo
bash setup.sh          # o: make setup
source .venv/bin/activate

# Ejecutar tests
pytest                 # o: make test
```

## Estructura del proyecto

```
read-gpx/
├── src/
│   └── read_gpx/
│       ├── __init__.py
│       ├── parser.py      # Lógica de extracción de datos GPX
│       ├── visualizer.py  # Generación de mapa HTML y perfil de elevación
│       └── cli.py         # Punto de entrada de línea de comandos
├── tests/
│   └── test_parser.py     # Tests unitarios
├── extraer_gpx.py          # Script original independiente
├── dibujar_ruta.py         # Script original de visualización
├── Makefile                # Atajos (setup, test, run-all…)
├── pyproject.toml          # Configuración del proyecto
├── requirements.txt        # Dependencias
└── README.md
```
