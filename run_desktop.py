import argparse
import importlib
import os
import socket
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path

if sys.platform.startswith("linux") and getattr(sys, "frozen", False):
    os.environ["PYWEBVIEW_GUI"] = "qt"
    os.environ["QT_API"] = "pyqt6"

import django
import webview
from django.core.management import call_command


HOST = os.getenv("IDEACOLLECTOR_HOST", "127.0.0.1")
LOAD_HOST = "127.0.0.1" if HOST in ("0.0.0.0", "::") else HOST
PORT = int(os.getenv("IDEACOLLECTOR_PORT", "8000"))
URL = f"http://{LOAD_HOST}:{PORT}"


def is_frozen():
    return bool(getattr(sys, "frozen", False))


def get_base_dir():
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent


def get_icon_path(base_dir):
    if is_frozen():
        icon_path = base_dir / "main" / "static" / "main" / "favicon.ico"
    else:
        icon_path = base_dir / "idea_collector" / "main" / "static" / "main" / "favicon.ico"
    return icon_path if icon_path.is_file() else None


def wait_for_server(host, port, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect((host, port))
                return True
            except OSError:
                time.sleep(0.2)
    return False


def wait_for_http(url, timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(0.5)
    return False


def start_django(base_dir):
    if is_frozen():
        sys.path.insert(0, str(base_dir))
    else:
        app_dir = base_dir / "idea_collector"
        os.chdir(app_dir)
        sys.path.insert(0, str(app_dir))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idea_collector.settings")
    django.setup()
    call_command("migrate", interactive=False, verbosity=1)


def start_server():
    errors = []

    def target():
        try:
            call_command("runserver", f"{HOST}:{PORT}", "--noreload")
        except BaseException as exc:
            errors.append(exc)
            traceback.print_exc()

    server = threading.Thread(target=target, daemon=True)
    server.start()
    return server, errors


def run_self_test():
    checks = [
        f"{URL}/",
        f"{URL}/static/main/vendor/bootstrap/bootstrap.min.css",
        f"{URL}/static/django_ckeditor_5/dist/bundle.js",
    ]
    for url in checks:
        if not wait_for_http(url):
            print(f"Self-test failed: {url} is not reachable", file=sys.stderr)
            return 1
        print(f"OK: {url}")
    print("Self-test passed")
    return 0


def run_gui_self_test():
    try:
        from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
        from PyQt6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
        import qtpy
    except Exception:
        traceback.print_exc()
        print_gui_diagnostics()
        print("GUI self-test failed", file=sys.stderr)
        return 1
    print(
        f"GUI self-test passed: Qt {QT_VERSION_STR}, "
        f"PyQt {PYQT_VERSION_STR}, qtpy {qtpy.QT_VERSION}"
    )
    return 0


def print_gui_diagnostics():
    print("GUI backend check:", file=sys.stderr)
    for module in ("qtpy", "PyQt6.QtCore", "PyQt6.QtWebEngineWidgets", "gi"):
        try:
            importlib.import_module(module)
        except BaseException as exc:
            print(f"  {module}: {type(exc).__name__}: {exc}", file=sys.stderr)
        else:
            print(f"  {module}: ok", file=sys.stderr)


def serve_forever(url):
    print(f"Server running at {url}. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Idea Collector desktop application")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="start the local server, check the bundled app and exit",
    )
    parser.add_argument(
        "--no-window",
        action="store_true",
        help="run the local server without opening a desktop window",
    )
    parser.add_argument(
        "--gui-self-test",
        action="store_true",
        help="check that the bundled Qt bindings load and exit",
    )
    args = parser.parse_args(argv)

    if args.gui_self_test:
        return run_gui_self_test()

    base_dir = get_base_dir()
    start_django(base_dir)
    server, server_errors = start_server()

    if args.self_test:
        return run_self_test()

    startup_timeout = int(os.getenv("IDEACOLLECTOR_STARTUP_TIMEOUT", "30"))
    if not wait_for_server(LOAD_HOST, PORT, timeout=startup_timeout):
        print(f"Could not start server at {URL}")
        for exc in server_errors:
            print(f"Server thread error: {exc!r}", file=sys.stderr)
        return 1

    if args.no_window:
        return serve_forever(URL)

    icon_path = get_icon_path(base_dir)
    try:
        webview.create_window("Idea Collector", URL, width=1200, height=800)
        webview.start(icon=str(icon_path) if icon_path else None)
    except webview.WebViewException as exc:
        print(f"Could not open the desktop window: {exc}", file=sys.stderr)
        print_gui_diagnostics()
        if sys.platform.startswith("linux"):
            print(
                "Install the Qt runtime libraries, for example on Debian/Ubuntu:\n"
                "  sudo apt install libgl1 libegl1 libxkbcommon-x11-0 libdbus-1-3 "
                "libxcb-cursor0 libnss3 libasound2",
                file=sys.stderr,
            )
        print(f"The app stays available in a browser at {URL}", file=sys.stderr)
        return serve_forever(URL)
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exit_code)
