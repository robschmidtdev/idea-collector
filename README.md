<p align="center">
  <img src="idea_collector/main/static/main/favicon.svg" alt="Idea Collector icon" width="120" height="120">
</p>

<h1 align="center">Idea Collector</h1>

<p align="center">
  <strong>This app is intended for local use only!</strong>
</p>

## What you can do

Idea Collector is a private workspace for your ideas. Capture thoughts as rich-text
notes, organize them with colored tags, and connect related ideas so you can find
them again later.

- **Capture ideas** with a title, formatted description, color, and tags.
- **Attach media** such as videos and audio recordings to an idea.
- **Link ideas** by referencing related items.
- **Pin and reorder** important ideas at the top of the list.
- **Find things fast** with tag, color, media, and pinned filters, custom filters,
  and sorting by name or date.
- **Use it from other devices** – open the app on your phone or tablet in a trusted
  local network (see [Access from phone or tablet](#access-from-phone-or-tablet)).
- **Protect your data** with an optional local account and login.
- **Customize** the site title, accent color, and where the database and media
  files are stored.

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

## Access from phone or tablet

By default the app only listens on `127.0.0.1`, so it is reachable only on the
computer that runs it. To use it from a phone or tablet in your own trusted
network, make these changes:

1. **Let the server listen on your network interface.** In the start script for
   your OS, change `HOST` from `127.0.0.1` to `0.0.0.0`:
   - Windows: `start_ideacollector.bat`, the line `set "HOST=127.0.0.1"`
   - Linux / macOS: `start_ideacollector.sh`, the line `HOST="127.0.0.1"`
2. **Allow the device's address.** Find the local IP address of the computer
   running Idea Collector (Windows: `ipconfig`; Linux: `hostname -I`;
   macOS: `ipconfig getifaddr en0`) and add it to `ALLOWED_HOSTS` in
   `idea_collector/idea_collector/settings.py`:

   ```python
   ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.1.50']
   ```

   Use your own IP address (or hostname) instead of `192.168.1.50`.
3. **Allow the port through the firewall** of the host computer (TCP port
   `8000`). On Windows, confirm the firewall prompt when Python starts or add an
   inbound rule for the port.
4. **Restart the app** and open `http://<computer-ip>:8000` on the other device,
   for example `http://192.168.1.50:8000`.

Create an account first under **Settings** so the app asks for a login. Only do
this in a trusted network and never expose the server directly to the internet -
it runs with Django's development server and `DEBUG` enabled.

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
