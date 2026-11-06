#!/usr/bin/env python3
"""Cross-platform launcher for Idea Collector."""

import argparse
import json
import os
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from pathlib import Path


APP_NAME = "Idea Collector"
ROOT = Path(__file__).resolve().parent
PROJECT_DIR = ROOT / "idea_collector"
DEFAULT_PORT = int(os.environ.get("IDEA_COLLECTOR_PORT", "8000"))
PID_FILE = Path(
    os.environ.get("IDEA_COLLECTOR_PIDFILE", str(ROOT / ".idea-collector.pid"))
)
LOG_FILE = Path(
    os.environ.get("IDEA_COLLECTOR_LOGFILE", str(ROOT / ".idea-collector.log"))
)
ICON_ICO = ROOT / "idea_collector" / "main" / "static" / "main" / "favicon.ico"
ICON_SVG = ROOT / "idea_collector" / "main" / "static" / "main" / "favicon.svg"
ICON_PNG = ROOT / "idea_collector" / "main" / "static" / "main" / "icon-512.png"
ICON_PNG_LARGE = (
    ROOT / "idea_collector" / "main" / "static" / "main" / "icon-1024.png"
)

DIALOGS = True


def print_message(message, error=False):
    stream = sys.stderr if error else sys.stdout
    if stream is None:
        stream = sys.stdout or sys.stderr
    if stream is not None:
        try:
            print(message, file=stream)
        except Exception:
            pass


def show_message(message, title=APP_NAME, error=False):
    if not DIALOGS:
        print_message(message, error=error)
        return

    if os.name == "nt":
        try:
            import ctypes

            flags = 0x10 if error else 0x40
            ctypes.windll.user32.MessageBoxW(0, message, title, flags)
            return
        except Exception:
            pass

    if sys.platform == "darwin":
        try:
            script = (
                "display dialog %s buttons {\"OK\"} default button \"OK\" "
                "with title %s"
            ) % (json.dumps(message), json.dumps(title))
            subprocess.run(
                ["osascript", "-e", script],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except Exception:
            pass

    commands = [
        ["zenity", "--error" if error else "--info", "--title", title, "--text", message],
        ["kdialog", "--title", title, "--error" if error else "--msgbox", message],
    ]
    for command in commands:
        if shutil.which(command[0]):
            subprocess.run(
                command,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return

    print_message(message, error=error)


def venv_python():
    names = ("Scripts/python.exe", "bin/python") if os.name == "nt" else ("bin/python",)
    for folder in ("venv", ".venv"):
        for name in names:
            candidate = ROOT / folder / name
            if candidate.exists():
                return candidate
    return Path(sys.executable)


def port_open(port, host="127.0.0.1", timeout=0.5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def read_pid():
    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def pid_alive(pid):
    if not pid:
        return False
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True,
                text=True,
                check=False,
            )
            return str(pid) in result.stdout
        except Exception:
            return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def pid_is_ours(pid):
    if not pid:
        return False
    if os.name == "nt":
        script = (
            "$p = Get-CimInstance Win32_Process -Filter "
            f"\"ProcessId = {pid}\"; if ($p) {{ $p.CommandLine }}"
        )
        try:
            command = subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                capture_output=True,
                text=True,
                check=False,
            ).stdout
        except Exception:
            return False
    else:
        try:
            command = (
                Path(f"/proc/{pid}/cmdline")
                .read_bytes()
                .replace(b"\0", b" ")
                .decode("utf-8", "replace")
            )
        except OSError:
            command = subprocess.run(
                ["ps", "-p", str(pid), "-o", "command="],
                capture_output=True,
                text=True,
                check=False,
            ).stdout
    command = (command or "").lower()
    return "launcher.py" in command or "manage.py" in command


def open_browser(port):
    webbrowser.open(f"http://127.0.0.1:{port}/")


def set_console_title(title):
    if os.name != "nt":
        return
    try:
        import ctypes

        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except Exception:
        pass


def wait_for_server_and_open(port, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if port_open(port):
            open_browser(port)
            return
        time.sleep(0.2)


def tail_log(lines=20):
    try:
        content = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(content[-lines:])
    except OSError:
        return ""


def ensure_venv():
    if os.name == "nt":
        candidate = ROOT / "venv" / "Scripts" / "python.exe"
    else:
        candidate = ROOT / "venv" / "bin" / "python"
    if candidate.exists():
        return True
    result = subprocess.run(
        [sys.executable, "-m", "venv", str(ROOT / "venv")],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and candidate.exists()


def install_requirements():
    python = venv_python()
    result = subprocess.run(
        [str(python), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def run_manage(*args):
    python = venv_python()
    return subprocess.run(
        [str(python), "manage.py", *args],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
        check=False,
    )


def start(port, open_browser_after=True):
    if PID_FILE.exists():
        pid = read_pid()
        if pid_alive(pid) and pid_is_ours(pid) and port_open(port):
            if open_browser_after:
                open_browser(port)
            return 0
        try:
            PID_FILE.unlink()
        except OSError:
            pass

    if port_open(port):
        if open_browser_after:
            open_browser(port)
        return 0

    manage_py = PROJECT_DIR / "manage.py"
    if not manage_py.exists():
        show_message(f"manage.py not found:\n{manage_py}", error=True)
        return 1

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8", errors="replace") as log:
        log.write(
            "\n--- %s starting on port %s ---\n"
            % (time.strftime("%Y-%m-%d %H:%M:%S"), port)
        )
        log.flush()
        command = [
            str(venv_python()),
            "manage.py",
            "runserver",
            "--insecure",
            "--noreload",
            f"127.0.0.1:{port}",
        ]
        options = {
            "cwd": str(PROJECT_DIR),
            "stdout": log,
            "stderr": subprocess.STDOUT,
            "stdin": subprocess.DEVNULL,
            "close_fds": True,
        }
        if os.name == "nt":
            options["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        else:
            options["start_new_session"] = True
        try:
            process = subprocess.Popen(command, **options)
        except Exception as exc:
            show_message(f"Could not start the server:\n{exc}", error=True)
            return 1

    PID_FILE.write_text(str(process.pid), encoding="utf-8")

    deadline = time.time() + 30
    while time.time() < deadline:
        if process.poll() is not None:
            show_message(
                "The server stopped unexpectedly.\n\n" + tail_log(), error=True
            )
            try:
                PID_FILE.unlink()
            except OSError:
                pass
            return 1
        if port_open(port):
            if open_browser_after:
                open_browser(port)
            return 0
        time.sleep(0.2)

    show_message(
        "The server did not become ready within 30 seconds.\n\n" + tail_log(),
        error=True,
    )
    stop(port, show_feedback=False)
    return 1


def start_foreground(port, open_browser_after=True):
    if PID_FILE.exists():
        pid = read_pid()
        if not pid_alive(pid) or not pid_is_ours(pid):
            try:
                PID_FILE.unlink()
            except OSError:
                pass

    if port_open(port):
        if open_browser_after:
            open_browser(port)
        return 0

    manage_py = PROJECT_DIR / "manage.py"
    if not manage_py.exists():
        show_message(f"manage.py not found:\n{manage_py}", error=True)
        return 1

    set_console_title(APP_NAME)
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")

    if open_browser_after:
        threading.Thread(
            target=wait_for_server_and_open,
            args=(port,),
            daemon=True,
        ).start()

    command = [
        str(venv_python()),
        "manage.py",
        "runserver",
        "--insecure",
        "--noreload",
        f"127.0.0.1:{port}",
    ]
    try:
        result = subprocess.call(command, cwd=str(PROJECT_DIR))
    except KeyboardInterrupt:
        result = 0
    finally:
        if read_pid() == os.getpid():
            try:
                PID_FILE.unlink()
            except OSError:
                pass

    if result not in (0, None) and os.name == "nt":
        try:
            input("The server stopped with an error. Press Enter to close...")
        except (EOFError, KeyboardInterrupt):
            pass
    return result


def bootstrap(port, generate_data=False):
    if not ensure_venv():
        show_message("Could not create the virtual environment.", error=True)
        return 1
    if not install_requirements():
        show_message("Could not install the Python requirements.", error=True)
        return 1
    result = run_manage("migrate")
    if result.returncode != 0:
        show_message(
            "Database migration failed.\n\n" + result.stdout + result.stderr,
            error=True,
        )
        return 1
    if generate_data:
        result = run_manage("generate_test_data", "--items", "1", "--tags", "30")
        if result.returncode != 0:
            show_message(
                "Could not generate test data.\n\n" + result.stdout + result.stderr,
                error=True,
            )
            return 1
    install_result = install()
    if install_result != 0:
        return install_result
    return start_foreground(port, True)


def stop_by_port(port):
    if os.name == "nt":
        script = (
            "$c = Get-NetTCPConnection -LocalPort %d -State Listen "
            "-ErrorAction SilentlyContinue | Select-Object -First 1;"
            "if ($c) {"
            " $p = Get-CimInstance Win32_Process -Filter "
            "\"ProcessId=$($c.OwningProcess)\";"
            " if ($p -and $p.CommandLine -match 'manage\\.py.*runserver') {"
            "  taskkill /PID $($c.OwningProcess) /T /F | Out-Null;"
            "  Write-Output 'stopped'"
            " }"
            "}"
        ) % port
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                capture_output=True,
                text=True,
                check=False,
            )
            return "stopped" in result.stdout
        except Exception:
            return False

    for tool in ("lsof", "fuser"):
        if shutil.which(tool) is None:
            continue
        if tool == "lsof":
            result = subprocess.run(
                ["lsof", "-ti", f"tcp:{port}"],
                capture_output=True,
                text=True,
                check=False,
            )
            pids = result.stdout.split()
        else:
            result = subprocess.run(
                ["fuser", f"{port}/tcp"],
                capture_output=True,
                text=True,
                check=False,
            )
            pids = [p for p in result.stdout.split() if p.isdigit()]
        stopped = False
        for pid in pids:
            command = subprocess.run(
                ["ps", "-p", pid, "-o", "command="],
                capture_output=True,
                text=True,
                check=False,
            ).stdout
            if "manage.py" in command and "runserver" in command:
                subprocess.run(["kill", "-TERM", pid], check=False)
                stopped = True
        if stopped:
            return True
    return False


def stop(port, show_feedback=True):
    pid = read_pid()
    stopped = False
    killed = False

    if pid and pid_alive(pid) and pid_is_ours(pid):
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                check=False,
            )
        else:
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
            except Exception:
                try:
                    os.kill(pid, signal.SIGTERM)
                except Exception:
                    pass
        killed = True

    if killed:
        deadline = time.time() + 5
        while time.time() < deadline and port_open(port):
            time.sleep(0.2)

    if port_open(port):
        stopped = stop_by_port(port)
    else:
        stopped = killed

    try:
        PID_FILE.unlink()
    except OSError:
        pass

    if show_feedback:
        if stopped:
            show_message("Idea Collector has been stopped.")
        else:
            show_message("Idea Collector is not running.", error=True)
    return 0 if stopped else 1


def status(port):
    pid = read_pid()
    running = bool(pid and pid_alive(pid) and pid_is_ours(pid))
    listening = port_open(port)
    if running and listening:
        message = f"Idea Collector is running on http://127.0.0.1:{port}/."
    elif listening:
        message = (
            f"Port {port} is in use, but it was not started by this launcher."
        )
    elif running:
        message = "The launcher process exists, but the server is not responding."
    else:
        message = "Idea Collector is not running."
    show_message(message, error=not listening)
    return 0 if listening else 1


def ps_literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def install_windows():
    python = venv_python()
    icon = ICON_ICO
    launcher = ROOT / "launcher.py"
    arguments = chr(34) + str(launcher) + chr(34) + " start"
    script = "\n".join(
        [
            "$ErrorActionPreference = 'Stop'",
            "$desktop = [Environment]::GetFolderPath('Desktop')",
            "$shell = New-Object -ComObject WScript.Shell",
            "$path = Join-Path $desktop 'Idea Collector.lnk'",
            "$shortcut = $shell.CreateShortcut($path)",
            f"$shortcut.TargetPath = {ps_literal(python)}",
            f"$shortcut.Arguments = {ps_literal(arguments)}",
            f"$shortcut.WorkingDirectory = {ps_literal(ROOT)}",
            f"$shortcut.IconLocation = {ps_literal(str(icon) + ',0')}",
            f"$shortcut.Description = {ps_literal(APP_NAME)}",
            "$shortcut.WindowStyle = 1",
            "$shortcut.Save()",
            "$oldStop = Join-Path $desktop 'Idea Collector beenden.lnk'",
            "if (Test-Path $oldStop) { Remove-Item $oldStop -Force }",
            "Write-Output $path",
        ]
    )
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        show_message(
            "Could not create the desktop shortcut.\n\n" + result.stderr,
            error=True,
        )
        return 1
    show_message(
        "Desktop shortcut created:\n\n"
        + result.stdout.strip()
        + "\n\nDouble-click 'Idea Collector' to start.\n"
        "Close the Idea Collector window to stop the server."
    )
    return 0


def desktop_quote(value):
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def linux_desktop_directory():
    if shutil.which("xdg-user-dir"):
        result = subprocess.run(
            ["xdg-user-dir", "DESKTOP"],
            capture_output=True,
            text=True,
            check=False,
        )
        path = Path(result.stdout.strip())
        if result.stdout.strip() and path.exists():
            return path
    path = Path.home() / "Desktop"
    return path if path.exists() else None


def write_desktop_entry(path, name, comment, executable, arguments, icon, terminal=False):
    command = " ".join(
        [desktop_quote(executable)]
        + [desktop_quote(argument) for argument in arguments]
    )
    content = "\n".join(
        [
            "[Desktop Entry]",
            "Type=Application",
            "Version=1.0",
            f"Name={name}",
            f"Comment={comment}",
            f"Exec={command}",
            f"Icon={icon}",
            f"Terminal={str(terminal).lower()}",
            "StartupNotify=false",
            "Categories=Office;Utility;",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def install_linux():
    executable = venv_python()
    launcher = ROOT / "launcher.py"
    icon = ICON_PNG if ICON_PNG.exists() else ICON_SVG
    icons = Path.home() / ".local" / "share" / "icons"
    if ICON_PNG.exists():
        icons.mkdir(parents=True, exist_ok=True)
        installed_icon = icons / "idea-collector.png"
        shutil.copy2(ICON_PNG, installed_icon)
        icon = installed_icon
    applications = Path.home() / ".local" / "share" / "applications"
    applications.mkdir(parents=True, exist_ok=True)

    start_entry = applications / "idea-collector.desktop"
    stop_entry = applications / "idea-collector-stop.desktop"
    write_desktop_entry(
        start_entry,
        APP_NAME,
        "Start Idea Collector",
        executable,
        [launcher, "start", "--foreground"],
        icon,
        terminal=True,
    )
    try:
        stop_entry.unlink()
    except OSError:
        pass

    desktop = linux_desktop_directory()
    created = [start_entry]
    if desktop:
        target = desktop / start_entry.name
        shutil.copy2(start_entry, target)
        target.chmod(0o755)
        if shutil.which("gio"):
            subprocess.run(
                ["gio", "set", str(target), "metadata::trusted", "true"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        created.append(target)
        stop_target = desktop / stop_entry.name
        if stop_target.exists():
            stop_target.unlink()

    show_message(
        "Launcher created:\n\n"
        + "\n".join(str(path) for path in created)
        + "\n\nDouble-click 'Idea Collector' to start.\nClose the terminal window to stop the server."
    )
    return 0


def create_icns(source_png, target_icns):
    if sys.platform != "darwin":
        return False
    if not shutil.which("iconutil") or not shutil.which("sips"):
        return False
    if ICON_PNG_LARGE.exists():
        source_png = ICON_PNG_LARGE
    if not source_png.exists():
        return False

    with tempfile.TemporaryDirectory() as temporary:
        iconset = Path(temporary) / "AppIcon.iconset"
        iconset.mkdir()
        sizes = [
            (16, "icon_16x16.png"),
            (32, "icon_16x16@2x.png"),
            (32, "icon_32x32.png"),
            (64, "icon_32x32@2x.png"),
            (128, "icon_128x128.png"),
            (256, "icon_128x128@2x.png"),
            (256, "icon_256x256.png"),
            (512, "icon_256x256@2x.png"),
            (512, "icon_512x512.png"),
            (1024, "icon_512x512@2x.png"),
        ]
        for size, name in sizes:
            subprocess.run(
                [
                    "sips",
                    "-z",
                    str(size),
                    str(size),
                    str(source_png),
                    "--out",
                    str(iconset / name),
                ],
                capture_output=True,
                check=False,
            )
        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset), "-o", str(target_icns)],
            capture_output=True,
            check=False,
        )
    return target_icns.exists()


def macos_app(destination, name, arguments, open_command=None):
    executable = venv_python()
    launcher = ROOT / "launcher.py"
    contents = destination / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"
    macos.mkdir(parents=True, exist_ok=True)
    resources.mkdir(parents=True, exist_ok=True)

    executable_name = "IdeaCollector" + ("Stop" if "stop" in arguments else "")
    run_script = macos / executable_name
    nl = chr(10)
    if open_command is not None:
        bs = chr(92)
        escaped = str(open_command).replace(bs, bs * 2).replace('"', bs + '"')
        run_script.write_text(
            "#!/bin/bash" + nl
            + "cat > /tmp/idea_collector_terminal.applescript <<'APPLESCRIPT'" + nl
            + 'tell application "Terminal" to do script "'
            + escaped
            + '"' + nl
            + "APPLESCRIPT" + nl
            + "osascript /tmp/idea_collector_terminal.applescript" + nl
            + "rm -f /tmp/idea_collector_terminal.applescript" + nl,
            encoding="utf-8",
        )
    else:
        command = " ".join(
            [shlex.quote(str(executable)), shlex.quote(str(launcher))] + arguments
        )
        run_script.write_text(
            "#!/bin/bash" + nl + "exec " + command + nl, encoding="utf-8"
        )
    run_script.chmod(0o755)

    bundle_id = "info.ideacollector." + (
        "stop" if "stop" in arguments else "start"
    )
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>{name}</string>
  <key>CFBundleDisplayName</key><string>{name}</string>
  <key>CFBundleIdentifier</key><string>{bundle_id}</string>
  <key>CFBundleVersion</key><string>1.0</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleExecutable</key><string>{executable_name}</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>LSMinimumSystemVersion</key><string>10.13</string>
  <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
"""
    (contents / "Info.plist").write_text(plist, encoding="utf-8")
    create_icns(ICON_PNG, resources / "AppIcon.icns")
    return destination


def install_macos():
    applications = Path.home() / "Applications"
    applications.mkdir(parents=True, exist_ok=True)
    start_app = applications / f"{APP_NAME}.app"
    stop_app = applications / f"{APP_NAME} beenden.app"
    command_script = (
        Path.home() / "Library" / "Application Support" / APP_NAME / "Start.command"
    )
    command_script.parent.mkdir(parents=True, exist_ok=True)
    command_body = (
        "#!/bin/bash"
        + chr(10)
        + "cd "
        + shlex.quote(str(ROOT))
        + chr(10)
        + "exec "
        + shlex.quote(str(venv_python()))
        + " "
        + shlex.quote(str(ROOT / "launcher.py"))
        + " start --foreground"
        + chr(10)
    )
    command_script.write_text(command_body, encoding="utf-8")
    command_script.chmod(0o755)
    macos_app(start_app, APP_NAME, ["start"], open_command=command_script)
    shutil.rmtree(stop_app, ignore_errors=True)

    desktop = Path.home() / "Desktop"
    created = [start_app]
    if desktop.exists():
        target = desktop / start_app.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(start_app, target)
        created.append(target)
        stop_target = desktop / stop_app.name
        if stop_target.exists():
            shutil.rmtree(stop_target)

    show_message(
        "Launcher created:\n\n"
        + "\n".join(str(path) for path in created)
        + "\n\nDouble-click the Idea Collector app to start.\nClose the Terminal window to stop the server."
    )
    return 0


def install():
    if os.name == "nt":
        return install_windows()
    if sys.platform == "darwin":
        return install_macos()
    return install_linux()


def main():
    global DIALOGS

    parser = argparse.ArgumentParser(description="Idea Collector launcher")
    parser.add_argument(
        "action",
        nargs="?",
        choices=("start", "stop", "restart", "status", "install", "bootstrap"),
        default="bootstrap",
        help="Action to perform (default: bootstrap)",
    )
    arguments = parser.parse_args()

    DIALOGS = True

    if arguments.action == "start":
        return start_foreground(DEFAULT_PORT, True)
    if arguments.action == "bootstrap":
        return bootstrap(DEFAULT_PORT, True)
    if arguments.action == "stop":
        return stop(DEFAULT_PORT)
    if arguments.action == "restart":
        stop(DEFAULT_PORT, show_feedback=False)
        time.sleep(0.5)
        return start(DEFAULT_PORT, True)
    if arguments.action == "status":
        return status(DEFAULT_PORT)
    return install()


if __name__ == "__main__":
    sys.exit(main())
