<p align="center">
  <img src="idea_collector/main/static/main/favicon.svg" alt="Idea Collector icon" width="120" height="120">
</p>

<h1 align="center">Idea Collector</h1>



Idea Collector is a private workspace for your ideas. Capture thoughts as rich-text
notes, organize them with colored tags, and connect related ideas so you can find
them again later.

- **Capture ideas** with a title, formatted description, color, and tags.
- **Attach files** such as videos, audio recordings, and other files to an idea.
- **Link ideas** by referencing related items.
- **Pin and reorder** important ideas at the top of the list.
- **Find things fast** with tag, color, media, and pinned filters, custom filters,
  and sorting by name or date.
- **Use it from other devices** – open the app on your phone or tablet in a trusted
  local network (see [Access from phone or tablet](#access-from-phone-or-tablet)).
- **Protect your data** with an optional local account and login.
- **Customize** the site title, accent color, and where the database and media
  files are stored.

## Install the packaged desktop app

Download the ZIP for your platform from the
[GitHub releases](https://github.com/robschmidtdev/idea-collector/releases) and
unpack it:

- Windows: run `IdeaCollector.exe`
- macOS: run `IdeaCollector.app`
- Linux: run `IdeaCollector/IdeaCollector`

The Linux ZIP keeps the executable bit. If your extraction tool drops it, run
`chmod +x IdeaCollector/IdeaCollector` once.

The Linux build uses Qt (QtWebEngine). It needs a few system libraries that are
not part of the ZIP, and Linux builds are made on Ubuntu 22.04, so glibc 2.35 or
newer is required (Ubuntu 22.04, Debian 12, Fedora 36 or newer):

```bash
sudo apt install libgl1 libegl1 libxkbcommon-x11-0 libdbus-1-3 libxcb-cursor0 \
  libnss3 libasound2
```

If the window does not open, the app prints which Qt module failed to load and
keeps serving the app in a browser. `IdeaCollector --gui-self-test` checks the
bundled Qt libraries without opening a window.

Python is included in these builds, so it does not have to be installed
separately. On Windows, the Microsoft Edge WebView2 runtime is required (already
included in Windows 11 and recent Windows 10 versions). The app keeps its
database, media files, secret key, and `storage.json` in a per-user data
directory; set `IDEACOLLECTOR_DATA_DIR` to override it.

## Requirements for running from source

- Python 3.11 or newer (must be available in `PATH`)
- On Debian/Ubuntu: `sudo apt install python3-venv python3-pip`

The packaged app does not need Python. See [Run from source](#run-from-source).

## Access from phone or tablet

By default the app only listens on `127.0.0.1` and only allows that host. The
network settings can be changed at runtime with environment variables, so no
rebuild is required - also not for the packaged application:

- `IDEACOLLECTOR_HOST` - interface to bind (`127.0.0.1` = local only,
  `0.0.0.0` = all network interfaces).
- `DJANGO_ALLOWED_HOSTS` - comma-separated list of allowed host names and IP
  addresses.
- `IDEACOLLECTOR_PORT` - port (`8000`).

Set the variables in the terminal before starting the packaged app.

Windows (cmd):

```bat
set IDEACOLLECTOR_HOST=0.0.0.0
set DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.50
IdeaCollector.exe
```

Linux:

```bash
IDEACOLLECTOR_HOST=0.0.0.0 \
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.50 \
./IdeaCollector/IdeaCollector
```

macOS:

```bash
IDEACOLLECTOR_HOST=0.0.0.0 \
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.50 \
./IdeaCollector.app/Contents/MacOS/IdeaCollector
```

When running from source, start `venv\Scripts\python.exe run_desktop.py`
(Windows) or `venv/bin/python run_desktop.py` (Linux/macOS) from the same terminal
instead of the packaged executable.

To use it from a phone or tablet in your own trusted network:

1. **Find the computer's address.** Use `ipconfig` on Windows, `hostname -I` on
   Linux, or `ipconfig getifaddr en0` on macOS, and add it to
   `DJANGO_ALLOWED_HOSTS` instead of `192.168.1.50`.
2. **Allow the port through the firewall** of the host computer (TCP port
   `8000`). On Windows, confirm the firewall prompt when the app starts or add an
   inbound rule for the port.
3. **Start the app** with the environment variables above and open
   `http://<computer-ip>:8000` on the other device, for example
   `http://192.168.1.50:8000`.

Create an account first under **Settings** so the app asks for a login. Only do
this in a trusted network and never expose the server directly to the internet -
it runs with Django's development server and `DEBUG` enabled.

## Run from source

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

## Build desktop executables

The app can be packaged as a desktop application with PyInstaller for Windows,
macOS, and Linux. The `Desktop build` workflow in
`.github/workflows/build.yml` builds and smoke-tests all three platforms on every
push and pull request. The release workflow attaches the packaged builds to
GitHub releases.

Windows:

```bat
python -m venv venv
venv\Scripts\python -m pip install -r requirements-build.txt
venv\Scripts\python -m PyInstaller --noconfirm --clean idea-collector.spec
```

Linux / macOS:

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements-build.txt
venv/bin/python -m PyInstaller --noconfirm --clean idea-collector.spec
```

The packaged application is written to `dist/`. On Linux the build uses Qt
(PyQt6), on macOS PyObjC, and on Windows Microsoft Edge WebView2. The frozen app
keeps its database, media files, secret key, and `storage.json` in the per-user
data directory; set `IDEACOLLECTOR_DATA_DIR` to override it. The host and allowed
hosts can be changed at runtime with `IDEACOLLECTOR_HOST` and
`DJANGO_ALLOWED_HOSTS`.

Run the packaged application or `run_desktop.py --self-test` to start the local
server, check the templates and static files, and exit without opening a window.

## Test data

```bash
cd idea_collector
python manage.py generate_test_data --items 500 --tags 30
python manage.py generate_test_data --flush
```
