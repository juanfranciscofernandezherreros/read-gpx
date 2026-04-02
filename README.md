# read-gpx

**Librería Python** para extraer, analizar y visualizar datos de archivos GPX.

Lee tracks de archivos GPX y devuelve un `DataFrame` de pandas con coordenadas,
elevación, tiempo y extensiones de dispositivos de fitness (frecuencia cardíaca,
cadencia y temperatura). Incluye además herramientas para generar mapas
interactivos y perfiles de elevación.

---

## Instalación

### Desde el repositorio (modo editable)

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
pip install -e .
```

### Requisitos

- Python 3.9 o superior
- Las dependencias se instalan automáticamente: `gpxpy`, `pandas`, `folium`,
  `matplotlib`, `geopy`

---

## Uso como librería Python

### Extraer datos de un GPX

```python
from read_gpx import extraer_datos_gpx

df = extraer_datos_gpx("mi_actividad.gpx")
print(df.head())
```

El DataFrame devuelto contiene las siguientes columnas:

| Columna        | Tipo               | Descripción                               |
|----------------|--------------------|-------------------------------------------|
| `latitud`      | `float`            | Latitud decimal del punto                 |
| `longitud`     | `float`            | Longitud decimal del punto                |
| `elevacion`    | `float` / `None`   | Elevación en metros                       |
| `tiempo`       | `datetime64` / NaT | Marca de tiempo UTC                       |
| `nombre_track` | `str`              | Nombre del track en el fichero GPX        |
| `hr`           | `str` *(opcional)* | Frecuencia cardíaca en bpm                |
| `cad`          | `str` *(opcional)* | Cadencia en rpm                           |
| `atemp`        | `str` *(opcional)* | Temperatura ambiente en °C                |

### Calcular distancia acumulada

```python
from read_gpx import extraer_datos_gpx, calcular_distancia_acumulada

df = extraer_datos_gpx("mi_actividad.gpx")
df = calcular_distancia_acumulada(df)
print(f"Distancia total: {df['distancia_km'].max():.2f} km")
```

### Generar mapa interactivo

```python
from read_gpx import extraer_datos_gpx, calcular_distancia_acumulada, crear_mapa_interactivo

df = extraer_datos_gpx("mi_actividad.gpx")
df = calcular_distancia_acumulada(df)
crear_mapa_interactivo(df, "mapa.html")
```

### Generar perfil de elevación

```python
from read_gpx import extraer_datos_gpx, crear_perfil_elevacion

df = extraer_datos_gpx("mi_actividad.gpx")
crear_perfil_elevacion(df, "perfil.png")
```

### Pipeline completo desde un CSV

```python
from read_gpx import procesar_csv

# Genera mapa HTML + PNG de elevación a partir de un CSV ya existente
procesar_csv("mi_actividad_data.csv")

# Con rutas de salida personalizadas
procesar_csv(
    "mi_actividad_data.csv",
    archivo_mapa="mi_mapa.html",
    archivo_perfil="mi_perfil.png",
)
```

---

## Uso desde la línea de comandos

### Pipeline completo: GPX → CSV + mapa + perfil

```bash
read-gpx mi_actividad.gpx --visualize
```

Genera tres ficheros en el directorio actual:

| Fichero                      | Descripción                              |
|------------------------------|------------------------------------------|
| `mi_actividad_data.csv`      | Todos los puntos del track en CSV        |
| `mi_actividad_mapa.html`     | Mapa interactivo (abrir en el navegador) |
| `mi_actividad_elevacion.png` | Gráfico del perfil de elevación          |

### Solo extraer datos a CSV

```bash
read-gpx mi_actividad.gpx
```

### Generar mapa y perfil desde un CSV ya existente

```bash
dibujar-ruta mi_actividad_data.csv
```

### Atajos con make

```bash
# Pipeline completo
make run-all GPX=mi_actividad.gpx

# Solo visualización desde un CSV
make visualize CSV=mi_actividad_data.csv
```

---

## Referencia de la API pública

### `extraer_datos_gpx(archivo_entrada)`

Parsea un fichero GPX y devuelve un `pandas.DataFrame`.

| Parámetro        | Tipo  | Descripción                |
|------------------|-------|----------------------------|
| `archivo_entrada` | `str` | Ruta al fichero `.gpx`    |

**Raises:** `FileNotFoundError` si el fichero no existe.

---

### `calcular_distancia_acumulada(df)`

Añade la columna `distancia_km` al DataFrame usando la fórmula geodésica
(Haversine).

| Parámetro | Tipo               | Descripción                              |
|-----------|--------------------|------------------------------------------|
| `df`      | `pd.DataFrame`     | DataFrame con columnas `latitud`/`longitud` |

**Returns:** una copia del DataFrame con la columna `distancia_km` añadida.

---

### `crear_mapa_interactivo(df, archivo_salida)`

Genera un mapa HTML interactivo con capas satélite y topográfica.

| Parámetro        | Tipo           | Por defecto              |
|------------------|----------------|--------------------------|
| `df`             | `pd.DataFrame` | —                        |
| `archivo_salida` | `str`          | `"mapa_interactivo.html"` |

**Returns:** ruta del fichero HTML generado.

---

### `crear_perfil_elevacion(df, archivo_salida)`

Genera un gráfico PNG con el perfil de elevación de la ruta.

| Parámetro        | Tipo           | Por defecto             |
|------------------|----------------|-------------------------|
| `df`             | `pd.DataFrame` | —                       |
| `archivo_salida` | `str`          | `"perfil_elevacion.png"` |

**Returns:** ruta del fichero PNG generado.

---

### `procesar_csv(archivo_csv, archivo_mapa, archivo_perfil)`

Pipeline completo: carga el CSV y genera el mapa y el perfil de elevación.

| Parámetro       | Tipo            | Por defecto                |
|-----------------|-----------------|----------------------------|
| `archivo_csv`   | `str`           | —                          |
| `archivo_mapa`  | `str` / `None`  | `"mapa_interactivo.html"`  |
| `archivo_perfil`| `str` / `None`  | `"perfil_elevacion.png"`   |

---

## Desarrollo

```bash
# Configurar entorno y dependencias de desarrollo
bash setup.sh          # o: make setup
source .venv/bin/activate

# Ejecutar la suite de tests
pytest                 # o: make test
```

### Estructura del proyecto

```
read-gpx/
├── src/
│   └── read_gpx/
│       ├── __init__.py      # API pública de la librería
│       ├── parser.py        # Extracción de datos GPX → DataFrame
│       ├── visualizer.py    # Mapa HTML y perfil de elevación
│       └── cli.py           # Comandos de línea de comandos
├── tests/
│   └── test_parser.py       # Tests unitarios del parser
├── extraer_gpx.py           # Script original (standalone)
├── dibujar_ruta.py          # Script original de visualización (standalone)
├── Makefile                 # Atajos: setup, test, run-all, visualize
├── pyproject.toml           # Metadatos del paquete y dependencias
├── requirements.txt         # Dependencias (referencia)
├── setup.sh                 # Script de configuración del entorno
└── README.md
```

