#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/idea_collector"

if [ -x "../../venv/bin/python" ]; then
    exec "../../venv/bin/python" manage.py runserver --insecure 0.0.0.0:8000
elif [ -x "../../.venv/bin/python" ]; then
    exec "../../.venv/bin/python" manage.py runserver --insecure 0.0.0.0:8000
else
    exec python3 manage.py runserver --insecure 0.0.0.0:8000
fi
