#!/usr/bin/env bash
# procesar_directorio.sh – Procesa todos los archivos GPX de un directorio.
#
# Uso:
#     bash procesar_directorio.sh [DIRECTORIO_GPX] [-o DIRECTORIO_SALIDA]
#
# Si no se indica DIRECTORIO_GPX se usa el directorio actual.
# Cada GPX genera su propia subcarpeta dentro de DIRECTORIO_SALIDA (o junto
# al directorio de entrada si no se especifica -o).
#
# Ejemplos:
#     bash procesar_directorio.sh mis_rutas/
#     bash procesar_directorio.sh mis_rutas/ -o resultados/
#     bash procesar_directorio.sh                # usa el directorio actual

set -euo pipefail

# ── Colores para la salida ────────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # Sin color

# ── Valores por defecto ──────────────────────────────────────────────────
DIR_GPX="."
DIR_SALIDA=""

# ── Parsear argumentos ───────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output-dir)
            DIR_SALIDA="$2"
            shift 2
            ;;
        -h|--help)
            echo "Uso: $0 [DIRECTORIO_GPX] [-o DIRECTORIO_SALIDA]"
            echo ""
            echo "Procesa todos los archivos .gpx de un directorio con read-gpx."
            echo ""
            echo "Opciones:"
            echo "  -o, --output-dir DIR   Directorio base para los resultados"
            echo "  -h, --help             Muestra esta ayuda"
            exit 0
            ;;
        -*)
            echo -e "${RED}Error: opción desconocida '$1'${NC}" >&2
            echo "Usa '$0 --help' para ver las opciones disponibles." >&2
            exit 1
            ;;
        *)
            DIR_GPX="$1"
            shift
            ;;
    esac
done

# ── Verificar que el directorio existe ────────────────────────────────────
if [[ ! -d "$DIR_GPX" ]]; then
    echo -e "${RED}Error: el directorio '$DIR_GPX' no existe.${NC}" >&2
    exit 1
fi

# ── Verificar que read-gpx está disponible ────────────────────────────────
if ! command -v read-gpx &>/dev/null; then
    # Intentar con el venv local
    if [[ -x ".venv/bin/read-gpx" ]]; then
        READ_GPX=".venv/bin/read-gpx"
    else
        echo -e "${RED}Error: no se encontró el comando 'read-gpx'.${NC}" >&2
        echo "Instálalo con:  pip install -e .  (o:  make setup)" >&2
        exit 1
    fi
else
    READ_GPX="read-gpx"
fi

# ── Buscar archivos GPX ──────────────────────────────────────────────────
mapfile -t GPX_FILES < <(find "$DIR_GPX" -maxdepth 1 -iname '*.gpx' -type f | sort)

TOTAL=${#GPX_FILES[@]}

if [[ $TOTAL -eq 0 ]]; then
    echo -e "${YELLOW}No se encontraron archivos .gpx en '$DIR_GPX'.${NC}"
    exit 0
fi

echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Procesando $TOTAL archivo(s) GPX en: $DIR_GPX${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
echo ""

EXITOSOS=0
FALLIDOS=0

for i in "${!GPX_FILES[@]}"; do
    archivo="${GPX_FILES[$i]}"
    numero=$((i + 1))
    nombre=$(basename "$archivo")

    echo -e "${CYAN}[$numero/$TOTAL]${NC} Procesando: ${nombre}"

    # Construir argumentos para read-gpx
    ARGS=("$archivo")
    if [[ -n "$DIR_SALIDA" ]]; then
        base="${nombre%.*}"
        ARGS+=("-o" "${DIR_SALIDA}/${base}_salida")
    fi

    if $READ_GPX "${ARGS[@]}"; then
        echo -e "  ${GREEN}✔ Completado${NC}"
        EXITOSOS=$((EXITOSOS + 1))
    else
        echo -e "  ${RED}✘ Error al procesar ${nombre}${NC}"
        FALLIDOS=$((FALLIDOS + 1))
    fi
    echo ""
done

# ── Resumen final ────────────────────────────────────────────────────────
echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Resumen${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
echo -e "  Total:    $TOTAL"
echo -e "  ${GREEN}Exitosos: $EXITOSOS${NC}"
if [[ $FALLIDOS -gt 0 ]]; then
    echo -e "  ${RED}Fallidos: $FALLIDOS${NC}"
fi
echo ""

if [[ $FALLIDOS -gt 0 ]]; then
    exit 1
fi
