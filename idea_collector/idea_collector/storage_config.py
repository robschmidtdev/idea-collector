import json
import os
import sys
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.management.utils import get_random_secret_key

STORAGE_CONFIG_FILE_NAME = "storage.json"
SECRET_KEY_FILE_NAME = ".secret_key"
APP_DIR_NAME = "IdeaCollector"
_PROJECT_DIR = Path(__file__).resolve().parent.parent


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_data_dir() -> Path:
    """Return the writable directory for the database, media files and config."""
    override = os.getenv("IDEACOLLECTOR_DATA_DIR")
    if override:
        path = Path(override).expanduser().resolve()
    elif is_frozen():
        if sys.platform == "win32":
            base = os.getenv("APPDATA") or Path.home() / "AppData" / "Roaming"
            path = Path(base) / APP_DIR_NAME
        elif sys.platform == "darwin":
            path = Path.home() / "Library" / "Application Support" / APP_DIR_NAME
        else:
            base = os.getenv("XDG_DATA_HOME") or Path.home() / ".local" / "share"
            path = Path(base) / "idea-collector"
    else:
        return _PROJECT_DIR

    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_dir() -> Path:
    if os.getenv("IDEACOLLECTOR_DATA_DIR") or is_frozen():
        return get_data_dir()
    return _PROJECT_DIR.parent


def get_storage_config_path() -> Path:
    return get_config_dir() / STORAGE_CONFIG_FILE_NAME


def _read_config(config_path=None) -> dict:
    path = get_storage_config_path() if config_path is None else Path(config_path)
    if path.is_file():
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(config, dict):
                return config
        except (OSError, ValueError):
            pass
    return {}


def _write_config(config: dict, config_path=None) -> None:
    target = get_storage_config_path() if config_path is None else Path(config_path)
    target.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def get_media_root(config_path=None) -> str:
    media_root = _read_config(config_path).get("media_root")
    if media_root:
        return str(media_root)
    return os.getenv("DJANGO_MEDIA_ROOT", str(get_data_dir() / "media"))


def get_database_path(config_path=None) -> str:
    database_path = _read_config(config_path).get("database_path")
    if database_path:
        return str(database_path)
    return os.getenv("DJANGO_DB_PATH", str(get_data_dir() / "db.sqlite3"))


def save_media_root(path, config_path=None) -> str:
    config = _read_config(config_path)
    config["media_root"] = path
    _write_config(config, config_path)
    return path


def save_database_path(path, config_path=None) -> str:
    config = _read_config(config_path)
    config["database_path"] = path
    _write_config(config, config_path)
    return path


def apply_media_root(path) -> None:
    path = os.path.abspath(os.path.expanduser(str(path)))
    os.makedirs(path, exist_ok=True)
    save_media_root(path)
    settings.MEDIA_ROOT = path
    default_storage._wrapped = FileSystemStorage(location=path, base_url=settings.MEDIA_URL)


def get_secret_key_path() -> Path:
    return get_config_dir() / SECRET_KEY_FILE_NAME


def get_or_create_secret_key(config_path=None) -> str:
    path = get_secret_key_path() if config_path is None else Path(config_path)
    if path.is_file():
        secret_key = path.read_text(encoding="utf-8").strip()
        if secret_key:
            return secret_key
    secret_key = get_random_secret_key()
    path.write_text(secret_key + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return secret_key
