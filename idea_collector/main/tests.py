import json
import tempfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.test import TestCase, override_settings

from idea_collector import storage_config


class StorageConfigTests(TestCase):
    def test_get_media_root_falls_back_to_env_without_config_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "storage.json"
            with mock.patch.dict("os.environ", {"DJANGO_MEDIA_ROOT": "/tmp/media-fallback"}):
                self.assertEqual(
                    storage_config.get_media_root(config_path=config_path),
                    "/tmp/media-fallback",
                )

    def test_get_database_path_falls_back_to_env_without_config_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "storage.json"
            with mock.patch.dict("os.environ", {"DJANGO_DB_PATH": "/tmp/db-fallback.sqlite3"}):
                self.assertEqual(
                    storage_config.get_database_path(config_path=config_path),
                    "/tmp/db-fallback.sqlite3",
                )

    def test_get_paths_read_storage_json(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "storage.json"
            config_path.write_text(
                json.dumps(
                    {
                        "media_root": "/tmp/media-from-json",
                        "database_path": "/tmp/db-from-json.sqlite3",
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                storage_config.get_media_root(config_path=config_path),
                "/tmp/media-from-json",
            )
            self.assertEqual(
                storage_config.get_database_path(config_path=config_path),
                "/tmp/db-from-json.sqlite3",
            )

    def test_save_media_root_preserves_database_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "storage.json"
            config_path.write_text(
                json.dumps({"database_path": "/tmp/db.sqlite3"}),
                encoding="utf-8",
            )
            storage_config.save_media_root("/tmp/new-media", config_path=config_path)
            config = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["media_root"], "/tmp/new-media")
            self.assertEqual(config["database_path"], "/tmp/db.sqlite3")

    def test_save_database_path_preserves_media_root(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "storage.json"
            config_path.write_text(
                json.dumps({"media_root": "/tmp/media"}),
                encoding="utf-8",
            )
            storage_config.save_database_path("/tmp/new.sqlite3", config_path=config_path)
            config = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["database_path"], "/tmp/new.sqlite3")
            self.assertEqual(config["media_root"], "/tmp/media")


    def test_get_or_create_secret_key_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / ".secret_key"
            self.assertFalse(config_path.exists())
            secret_key = storage_config.get_or_create_secret_key(config_path=config_path)
            self.assertTrue(config_path.exists())
            self.assertEqual(secret_key, config_path.read_text(encoding="utf-8").strip())
            self.assertGreaterEqual(len(secret_key), 50)

    def test_get_or_create_secret_key_reuses_existing_value(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / ".secret_key"
            config_path.write_text("existing-key\n", encoding="utf-8")
            self.assertEqual(
                storage_config.get_or_create_secret_key(config_path=config_path),
                "existing-key",
            )

class MediaRootSettingsTests(TestCase):
    def setUp(self):
        self.original_media_root = str(settings.MEDIA_ROOT)

    def tearDown(self):
        settings.MEDIA_ROOT = self.original_media_root

    def test_settings_page_renders_media_root_field(self):
        response = self.client.get("/settings/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Media Root")

    def test_save_media_root_updates_path_and_storage(self):
        new_media_root = tempfile.mkdtemp()
        with mock.patch("idea_collector.storage_config.save_media_root") as save_mock:
            response = self.client.post(
                "/settings/",
                {
                    "media_root": new_media_root,
                    "save_storage": "",
                },
                follow=True,
            )
        save_mock.assert_called_once_with(new_media_root)
        self.assertEqual(str(settings.MEDIA_ROOT), new_media_root)
        self.assertEqual(str(default_storage.location), new_media_root)
        self.assertContains(response, f"Media root changed to {new_media_root}")

    def test_save_media_root_warns_when_directory_missing(self):
        missing_media_root = "/tmp/does-not-exist-ideacollector-media"
        with mock.patch("idea_collector.storage_config.save_media_root") as save_mock:
            response = self.client.post(
                "/settings/",
                {
                    "media_root": missing_media_root,
                    "save_storage": "",
                },
                follow=True,
            )
        save_mock.assert_called_once_with(missing_media_root)
        self.assertContains(response, "does not exist yet")

    def test_save_settings_does_not_touch_storage(self):
        original_media_root = str(settings.MEDIA_ROOT)
        with mock.patch("idea_collector.storage_config.save_media_root") as save_mock:
            response = self.client.post(
                "/settings/",
                {
                    "title": "Changed",
                    "primary_color": "#ff0000",
                    "media_root": "/tmp/ignored-media-root",
                    "database_path": "/tmp/ignored.sqlite3",
                    "save_settings": "",
                },
                follow=True,
            )
        save_mock.assert_not_called()
        self.assertEqual(str(settings.MEDIA_ROOT), original_media_root)
        self.assertContains(response, "Settings saved successfully!")

class DatabasePathSettingsTests(TestCase):
    def test_settings_page_renders_database_path_field(self):
        response = self.client.get("/settings/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Database Path")

    def test_save_database_path_does_not_apply_before_restart(self):
        new_database_path = str(Path(tempfile.mkdtemp()) / "new.sqlite3")
        original_database_path = str(settings.DATABASES["default"]["NAME"])
        with mock.patch("idea_collector.storage_config.save_database_path") as save_mock:
            response = self.client.post(
                "/settings/",
                {
                    "media_root": str(settings.MEDIA_ROOT),
                    "database_path": new_database_path,
                    "save_storage": "",
                },
                follow=True,
            )
        save_mock.assert_called_once_with(new_database_path)
        self.assertEqual(str(settings.DATABASES["default"]["NAME"]), original_database_path)
        self.assertContains(response, "Restart the app")


class LanAccessTests(TestCase):
    remote_addr = "203.0.113.9"

    def test_remote_anonymous_cannot_create_account(self):
        response = self.client.post(
            "/settings/",
            {
                "username": "remote-user",
                "password1": "a-strong-password-123",
                "password2": "a-strong-password-123",
                "create_account": "",
            },
            REMOTE_ADDR=self.remote_addr,
        )
        self.assertRedirects(response, "/settings/")
        self.assertFalse(User.objects.exists())

    def test_remote_anonymous_cannot_change_storage(self):
        new_media_root = tempfile.mkdtemp()
        with mock.patch(
            "idea_collector.storage_config.save_media_root"
        ) as media_mock, mock.patch(
            "idea_collector.storage_config.save_database_path"
        ) as database_mock:
            response = self.client.post(
                "/settings/",
                {
                    "media_root": new_media_root,
                    "database_path": str(Path(new_media_root) / "new.sqlite3"),
                    "save_storage": "",
                },
                REMOTE_ADDR=self.remote_addr,
            )
        self.assertRedirects(response, "/settings/")
        media_mock.assert_not_called()
        database_mock.assert_not_called()

    def test_remote_anonymous_settings_hide_admin_sections(self):
        response = self.client.get("/settings/", REMOTE_ADDR=self.remote_addr)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Create Account")
        self.assertNotContains(response, "Save Storage")
        self.assertNotContains(response, "Media Root")
        self.assertContains(
            response, "Accounts can only be created on the host machine."
        )


class MediaServingTests(TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        self.override = override_settings(MEDIA_ROOT=self.tmp_dir.name)
        self.override.enable()
        self.addCleanup(self.override.disable)

    def test_media_is_served_when_debug_is_disabled(self):
        self.assertFalse(settings.DEBUG)
        probe = Path(self.tmp_dir.name) / "probe.txt"
        probe.write_text("ok", encoding="utf-8")
        response = self.client.get(f"{settings.MEDIA_URL}probe.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"ok")


class PathBrowserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("path-browser", password="test-pass-123")
        self.client.force_login(self.user)

    def test_lists_directories(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            (Path(tmp_dir) / "media-folder").mkdir()
            response = self.client.get("/settings/browse/", {"path": tmp_dir})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(Path(data["path"]), Path(tmp_dir))
            names = [entry["name"] for entry in data["directories"]]
            self.assertIn("media-folder", names)

    def test_lists_sqlite_files_when_requested(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            (Path(tmp_dir) / "data.sqlite3").write_text("", encoding="utf-8")
            (Path(tmp_dir) / "notes.txt").write_text("", encoding="utf-8")
            response = self.client.get("/settings/browse/", {"path": tmp_dir, "files": "1"})
            self.assertEqual(response.status_code, 200)
            names = [entry["name"] for entry in response.json()["files"]]
            self.assertIn("data.sqlite3", names)
            self.assertNotIn("notes.txt", names)

    def test_anonymous_remote_request_is_forbidden(self):
        self.client.logout()
        User.objects.all().delete()
        response = self.client.get("/settings/browse/", REMOTE_ADDR="203.0.113.9")
        self.assertEqual(response.status_code, 403)

    def test_anonymous_local_request_may_browse(self):
        self.client.logout()
        User.objects.all().delete()
        response = self.client.get("/settings/browse/", REMOTE_ADDR="127.0.0.1")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_may_browse(self):
        response = self.client.get("/settings/browse/", REMOTE_ADDR="203.0.113.9")
        self.assertEqual(response.status_code, 200)
