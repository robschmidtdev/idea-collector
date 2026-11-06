#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ -x "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
elif [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="$(command -v python3 || command -v python || true)"
fi

if [ -z "$PYTHON" ]; then
    echo "Python was not found. Please set up the virtual environment first." >&2
    exit 1
fi

exec "$PYTHON" launcher.py stop "$@"
