import os
import socket
import sys
import threading
import time

import django
import webview
from django.core.management import call_command


HOST = "0.0.0.0"
LOAD_HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{LOAD_HOST}:{PORT}"


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


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(base_dir, "idea_collector")
    os.chdir(app_dir)
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idea_collector.settings")

    django.setup()
    call_command("migrate", interactive=False, verbosity=1)

    server = threading.Thread(
        target=call_command,
        args=("runserver", f"{HOST}:{PORT}", "--noreload"),
        daemon=True,
    )
    server.start()

    if not wait_for_server(LOAD_HOST, PORT):
        print(f"Could not start server at {URL}")
        sys.exit(1)

    icon_path = os.path.join(app_dir, "main", "static", "main", "favicon.ico")
    webview.create_window("", URL, width=1200, height=800)
    webview.start(icon=icon_path if os.path.isfile(icon_path) else None)
    os._exit(0)


if __name__ == "__main__":
    main()
