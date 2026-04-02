#!/usr/bin/env bash
# setup.sh – Configura el entorno de desarrollo en Linux desde cero.
set -euo pipefail

PYTHON=${PYTHON:-python3}
VENV_DIR=".venv"

echo "==> Verificando Python (se requiere >= 3.9)..."
$PYTHON -c "import sys; assert sys.version_info >= (3,9), 'Se requiere Python 3.9 o superior'"
$PYTHON --version

echo "==> Creando entorno virtual en ${VENV_DIR}..."
$PYTHON -m venv "$VENV_DIR"

echo "==> Actualizando pip..."
"$VENV_DIR/bin/pip" install --upgrade pip

echo "==> Instalando dependencias del proyecto (modo editable + dev)..."
"$VENV_DIR/bin/pip" install -e ".[dev]"

echo ""
echo "✅  Entorno listo."
echo "   Activa el entorno con:  source ${VENV_DIR}/bin/activate"
echo "   Ejecuta los tests con:  pytest   (o: make test)"
