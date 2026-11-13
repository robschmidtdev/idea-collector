<p align="center">
  <img src="idea_collector/main/static/main/favicon.svg" alt="Idea Collector icon" width="120" height="120">
</p>

<h1 align="center">Idea Collector</h1>

<p align="center">
  <strong>This app is intended for local use only!</strong>
</p>

## Requirements

- Python 3.11 or newer (must be available in `PATH`)
- On Debian/Ubuntu: `sudo apt install python3-venv python3-pip`

## Windows

Double-click `start_ideacollector.bat`. On first start it automatically:

1. creates the `venv` virtual environment,
2. installs the dependencies from `requirements.txt`,
3. applies database migrations,
4. starts the server at `http://127.0.0.1:8000` and opens the browser.

To stop the server, close the console window or press `Ctrl+C`.

## Linux / macOS

```bash
./start_ideacollector.sh
```

On first start it automatically:

1. creates a `venv` virtual environment (or reuses an existing `venv`/`.venv`),
2. installs the dependencies from `requirements.txt`,
3. applies database migrations,
4. starts the server at `http://127.0.0.1:8000`.

To stop the server, close the terminal or press `Ctrl+C`.

On Linux, make the script executable once with `chmod +x start_ideacollector.sh`.
On macOS, double-clicking a `.sh` file usually opens an editor instead of a terminal;
run it from Terminal with `./start_ideacollector.sh` or rename it to `.command` and
double-click that file.

## Manual start (for Developers)

```bash
python -m venv venv
```

Windows:

```bat
venv\Scripts\python -m pip install -r requirements.txt
cd idea_collector
..\venv\Scripts\python manage.py migrate
..\venv\Scripts\python manage.py runserver 127.0.0.1:8000
```

Linux / macOS:

```bash
venv/bin/python -m pip install -r requirements.txt
cd idea_collector
../venv/bin/python manage.py migrate
../venv/bin/python manage.py runserver 127.0.0.1:8000
```

## Test data

```bash
cd idea_collector
python manage.py generate_test_data --items 500 --tags 30
python manage.py generate_test_data --flush
```
