import json
import os
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.management.utils import get_random_secret_key

STORAGE_CONFIG_FILE_NAME = "storage.json"
SECRET_KEY_FILE_NAME = ".secret_key"
_PROJECT_DIR = Path(__file__).resolve().parent.parent


def get_storage_config_path() -> Path:
    return _PROJECT_DIR.parent / STORAGE_CONFIG_FILE_NAME


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
    return os.getenv("DJANGO_MEDIA_ROOT", str(_PROJECT_DIR / "media"))


def get_database_path(config_path=None) -> str:
    database_path = _read_config(config_path).get("database_path")
    if database_path:
        return str(database_path)
    return os.getenv("DJANGO_DB_PATH", str(_PROJECT_DIR / "db.sqlite3"))


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
    save_media_root(path)
    settings.MEDIA_ROOT = path
    default_storage._wrapped = FileSystemStorage()


def get_secret_key_path() -> Path:
    return _PROJECT_DIR.parent / SECRET_KEY_FILE_NAME


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
