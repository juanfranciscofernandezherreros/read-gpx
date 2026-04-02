# read-gpx

Herramienta en Python para extraer datos de archivos GPX y convertirlos a CSV.

Lee tracks de archivos GPX y extrae coordenadas, elevación, tiempo y extensiones
de dispositivos de fitness (frecuencia cardíaca, cadencia y temperatura).

## Requisitos

- Python 3.9 o superior

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/juanfranciscofernandezherreros/read-gpx.git
cd read-gpx

# Instalar dependencias
pip install -r requirements.txt

# O instalar como paquete
pip install .
```

## Uso

### Línea de comandos

```bash
# Procesar un archivo GPX concreto
read-gpx mi_actividad.gpx

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
# Instalar dependencias de desarrollo
pip install -e ".[dev]"

# Ejecutar tests
pytest
```

## Estructura del proyecto

```
read-gpx/
├── src/
│   └── read_gpx/
│       ├── __init__.py
│       ├── parser.py      # Lógica de extracción de datos GPX
│       └── cli.py          # Punto de entrada de línea de comandos
├── tests/
│   └── test_parser.py     # Tests unitarios
├── extraer_gpx.py          # Script original independiente
├── pyproject.toml           # Configuración del proyecto
├── requirements.txt         # Dependencias
└── README.md
```
