# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


PROJECT_ROOT = Path(SPECPATH)
APP_PROJECT_DIR = PROJECT_ROOT / "idea_collector"

if str(APP_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(APP_PROJECT_DIR))

hiddenimports = []
for package in (
    "main",
    "idea_collector",
    "django_ckeditor_5",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
):
    hiddenimports += collect_submodules(package)

hiddenimports = [
    module
    for module in hiddenimports
    if not (module == "main.tests" or module.startswith("main.test_"))
]

hiddenimports += [
    "django.core.management.commands.migrate",
    "django.core.management.commands.runserver",
    "django.db.backends.sqlite3",
]

if sys.platform == "win32":
    hiddenimports += [
        "clr",
        "webview.platforms.edgechromium",
        "webview.platforms.mshtml",
        "webview.platforms.winforms",
    ]
elif sys.platform == "darwin":
    hiddenimports += [
        "AppKit",
        "Foundation",
        "PyObjCTools.AppHelper",
        "Quartz",
        "WebKit",
        "objc",
        "webview.platforms.cocoa",
    ]
else:
    hiddenimports += [
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtNetwork",
        "PyQt6.QtWebChannel",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWidgets",
        "qtpy",
        "webview.platforms.qt",
    ]

datas = [
    (str(APP_PROJECT_DIR / "main" / "migrations"), "main/migrations"),
    (str(APP_PROJECT_DIR / "main" / "static"), "main/static"),
    (str(APP_PROJECT_DIR / "main" / "templates"), "main/templates"),
]
datas += collect_data_files("django")
datas += collect_data_files("django_ckeditor_5")
datas += collect_data_files("tzdata")
datas += collect_data_files("webview")

excludes = [
    "pytest",
]

icon = None
if sys.platform == "win32":
    icon = str(APP_PROJECT_DIR / "main" / "static" / "main" / "favicon.ico")
elif sys.platform == "darwin":
    icon_png = APP_PROJECT_DIR / "main" / "static" / "main" / "icon-512.png"
    icon_icns = PROJECT_ROOT / "build" / "icon.icns"
    if icon_png.is_file():
        try:
            from PIL import Image

            icon_icns.parent.mkdir(parents=True, exist_ok=True)
            Image.open(icon_png).save(icon_icns, format="ICNS")
            icon = str(icon_icns)
        except Exception:
            icon = None

a = Analysis(
    [str(PROJECT_ROOT / "run_desktop.py")],
    pathex=[str(APP_PROJECT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="IdeaCollector",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="IdeaCollector",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="IdeaCollector.app",
        icon=icon,
        bundle_identifier="com.ideacollector.app",
        info_plist={
            "CFBundleName": "Idea Collector",
            "CFBundleDisplayName": "Idea Collector",
            "NSHighResolutionCapable": True,
        },
    )
