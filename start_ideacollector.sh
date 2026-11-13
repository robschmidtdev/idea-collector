#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/idea_collector"

HOST="127.0.0.1"
PORT="8000"
URL="http://$HOST:$PORT"

if [ -x "../venv/bin/python" ]; then
    PYTHON="../venv/bin/python"
elif [ -x "../.venv/bin/python" ]; then
    PYTHON="../.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
    echo "No virtual environment found. Using system Python."
    echo "Make sure the dependencies from requirements.txt are installed."
    echo
else
    echo "Python 3 was not found. Please install Python 3 and try again."
    exit 1
fi

echo "Starting Idea Collector at $URL"
echo "Open this address in your browser."
echo "To stop the server, close this terminal or press Ctrl+C."
echo

exec "$PYTHON" manage.py runserver "$HOST:$PORT"
