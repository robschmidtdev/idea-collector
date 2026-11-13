#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
if [ -x "$ROOT/.venv/bin/python" ]; then
    VENV="$ROOT/.venv"
else
    VENV="$ROOT/venv"
fi

HOST="127.0.0.1"
LOAD_UP_HOST="127.0.0.1"
PORT="8000"
URL="http://$LOAD_UP_HOST:$PORT"

if [ ! -x "$VENV/bin/python" ]; then
    if ! command -v python3 >/dev/null 2>&1; then
        echo "Python 3 was not found. Please install Python 3 and try again."
        exit 1
    fi

    echo "Creating virtual environment. This only takes time on the first start..."
    if ! python3 -m venv "$VENV"; then
        echo
        echo "Could not create the virtual environment."
        echo "On Debian/Ubuntu install the venv package first:"
        echo "  sudo apt install python3-venv"
        exit 1
    fi
fi

if ! "$VENV/bin/python" -m pip --version >/dev/null 2>&1; then
    echo "pip is missing in the virtual environment. Bootstrapping pip..."
    if ! "$VENV/bin/python" -m ensurepip --upgrade; then
        echo
        echo "Could not bootstrap pip in the virtual environment."
        echo "On Debian/Ubuntu install the venv and pip packages first:"
        echo "  sudo apt install python3-venv python3-pip"
        echo "Then remove the broken environment and start again:"
        echo "  rm -rf \"$VENV\""
        exit 1
    fi
fi

if ! "$VENV/bin/python" -c "import django" >/dev/null 2>&1; then
    echo "Installing dependencies from requirements.txt..."
    "$VENV/bin/python" -m pip install --upgrade pip
    "$VENV/bin/python" -m pip install -r "$ROOT/requirements.txt"
fi

PYTHON="$VENV/bin/python"
cd "$ROOT/idea_collector"

echo "Applying database migrations..."
"$PYTHON" manage.py migrate

echo
echo "Starting Idea Collector at $URL"
echo "Open this address in your browser."
echo "To stop the server, close this terminal or press Ctrl+C."
echo

exec "$PYTHON" manage.py runserver "$HOST:$PORT"
