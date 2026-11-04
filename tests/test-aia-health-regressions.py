#!/usr/bin/env python3
"""Source-only regressions. No GTK display, credentials, downloads or host writes."""
import contextlib
import http.client
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

SOURCE = Path(__file__).resolve().parents[1] / "installer/src"


def load(name):
    loader = importlib.machinery.SourceFileLoader(name.replace("-", "_"), str(SOURCE / name))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
    # Only UI construction needs GTK. Exercise the real backend and callback bodies.
    repository = types.ModuleType("gi.repository")
    repository.Gtk = types.SimpleNamespace(ApplicationWindow=object, Application=object,
                                           ResponseType=types.SimpleNamespace(OK=1))
    repository.GLib = types.SimpleNamespace(idle_add=Mock())
    repository.Gdk = repository.Gio = types.SimpleNamespace()
    gi = types.ModuleType("gi")
    gi.require_version = lambda *_: None
    with patch.dict(sys.modules, {"gi": gi, "gi.repository": repository}):
        loader.exec_module(module)
    return module


aia = load("shai-aia")
health = load("shai-health")
store_secret = load("shai-secret-store")
migrate = load("shai-secret-migrate")


class AIARegressions(unittest.TestCase):
    def test_service_properties_are_not_positional(self):
        window = types.SimpleNamespace(active_path=lambda: Path("/tmp/model.gguf"), server_ready=lambda: True)
        output = "MainPID=123\nSubState=running\nActiveState=active"
        with patch.object(aia, "run", return_value=(0, output)), patch.object(Path, "read_bytes", return_value=b"llama-server\0--model\0/tmp/model.gguf\0"):
            self.assertEqual(aia.AIAWindow.service_status(window)[0], "ready")

    def test_bad_completion_payloads_are_errors(self):
        for payload in (None, {}, {"choices": None}, {"choices": []},
                        {"choices": [{"message": {"content": None}}]},
                        {"choices": [{"message": {"content": 123}}]}):
            with self.subTest(payload=payload):
                response = Mock()
                response.__enter__ = Mock(return_value=response)
                response.__exit__ = Mock(return_value=False)
                response.read.return_value = json.dumps(payload).encode()
                with patch.object(aia, "ensure_server_key", return_value="test-only"), patch.object(aia.LOCAL_HTTP, "open", return_value=response):
                    with self.assertRaises(ValueError):
                        aia.AIAWindow.request_completion(object(), [])

    def test_inference_failures_always_schedule_finish(self):
        for error in (TypeError("bad payload"), http.client.RemoteDisconnected("closed"), OSError("key unavailable")):
            window = types.SimpleNamespace(server_ready=Mock(return_value=True), system_prompt=lambda: "test",
                                           request_completion=Mock(side_effect=error), finish_inference=Mock())
            if isinstance(error, OSError) and not isinstance(error, http.client.HTTPException):
                window.server_ready.side_effect = error
            with self.subTest(error=type(error).__name__), patch.object(aia.GLib, "idle_add") as idle:
                aia.AIAWindow.run_inference(window, "test", [])
                self.assertEqual(idle.call_count, 1)
                self.assertEqual(idle.call_args.args[0], window.finish_inference)
                self.assertTrue(idle.call_args.args[2])

    def test_status_prompt_is_not_audited(self):
        window = types.SimpleNamespace(busy=False, chat_entry=Mock(), chat_messages=[],
                                       render_chat=Mock(), record_chat=Mock(), local_status_answer=lambda _: "local status")
        window.chat_entry.get_text.return_value = "private home assistant status question"
        with patch.object(aia, "audit") as audit:
            aia.AIAWindow.send_chat(window, None)
        self.assertNotIn("private home", repr(audit.call_args_list))

    def test_missing_gui_executable_is_reported(self):
        window = types.SimpleNamespace(error=Mock())
        window.launch_command = lambda args: aia.AIAWindow.launch_command(window, args)
        with patch.object(aia.subprocess, "Popen", side_effect=FileNotFoundError("missing")):
            aia.AIAWindow.open_integration(window, {"kind": "exiftool"})
        window.error.assert_called_once()

    def test_vault_test_identifies_the_desktop_user(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b'{"success": true, "detail": "OK"}'
        opener = Mock()
        opener.open.return_value = response
        with patch.object(aia.urllib.request, "build_opener", return_value=opener):
            self.assertTrue(aia.AIAWindow.test_integration(object(), {"kind": "ha"}, {"secret_ref": "vault://test"})[1])
        request = opener.open.call_args.args[0]
        self.assertEqual(request.get_header("X-shai-user"), aia.pwd.getpwuid(os.getuid()).pw_name)


class HealthRegressions(unittest.TestCase):
    def test_unusable_snapshots_fail_closed(self):
        for payload in (None, [], {"observer": {}, "containers": [None]},
                        {"generated_at": 1, "observer": {"available": True}, "containers": []}):
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "snapshot.json"
                path.write_text(json.dumps(payload))
                with patch.object(health, "NETWORK_SNAPSHOT", path):
                    self.assertFalse(health.docker_snapshot()["available"])

    def test_starting_container_is_not_healthy(self):
        payload = {"generated_at": int(health.time.time()), "observer": {"available": True},
                   "containers": [{"name": "test", "status": "running", "health": "starting"}]}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "snapshot.json"
            path.write_text(json.dumps(payload))
            with patch.object(health, "NETWORK_SNAPSHOT", path):
                self.assertEqual(health.docker_snapshot()["healthy"], 0)

    def test_guest_cpu_time_is_not_counted_twice(self):
        with patch.object(health, "read_text", return_value="cpu 100 20 30 400 5 6 7 8 90 10\n"):
            self.assertEqual(health.cpu_counters(), (576, 405))

    def test_duplicate_timestamp_does_not_inflate_rollup(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.multiple(health, STATE=root, DAILY=root / "daily", DB=root / "health.sqlite3"):
                store = health.HealthStore()
                try:
                    sample = dict(ts=int(health.time.time()), cpu=20, ram=30, swap=0, disk=40,
                                  rx=0, tx=0, energy_wh=1, docker_total=0, docker_healthy=0)
                    store.add_sample(sample, health.DEFAULTS)
                    store.add_sample(sample, health.DEFAULTS)
                    row = store.db.execute("SELECT * FROM hourly").fetchone()
                    self.assertEqual(row["samples"], 1)
                    self.assertEqual(row["energy_wh"], 1)
                finally:
                    store.db.close()


class SecretRegressions(unittest.TestCase):
    def test_migration_rejects_traversal_and_config_symlinks(self):
        for symlink in (None, "aia.json", "shai", ".config"):
            with self.subTest(symlink=symlink), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                home = root / "home"
                directory = home / ".config/shai"
                directory.mkdir(parents=True)
                vault = root / "vault"
                vault.mkdir()
                config = directory / "aia.json"
                config.write_text(json.dumps({"integrations": {"../../escaped": {"token": "test-only"}}}))
                original = config.read_text()
                if symlink:
                    target = {"aia.json": config, "shai": directory, ".config": home / ".config"}[symlink]
                    outside = root / "outside"
                    target.rename(outside)
                    target.symlink_to(outside, target_is_directory=symlink != "aia.json")
                account = types.SimpleNamespace(pw_dir=str(home), pw_name="test", pw_uid=os.getuid(), pw_gid=os.getgid())
                with patch.object(migrate, "VAULT", vault):
                    self.assertEqual(migrate.migrate_account(account), 0)
                self.assertEqual(config.read_text(), original)
                self.assertEqual(list(vault.iterdir()), [])
                self.assertFalse((root / "escaped.json").exists())

    def test_valid_migration_keeps_existing_vault_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            directory = root / "home/.config/shai"
            directory.mkdir(parents=True)
            vault = root / "vault"
            (vault / "test").mkdir(parents=True)
            config = directory / "aia.json"
            config.write_text(json.dumps({"integrations": {"mqtt": {"token": "new-test-only", "host": "localhost"}}}))
            target = vault / "test/mqtt.json"
            target.write_text(json.dumps({"values": {"password": "keep-test-only"}}))
            account = types.SimpleNamespace(pw_dir=str(root / "home"), pw_name="test", pw_uid=os.getuid(), pw_gid=os.getgid())
            with patch.object(migrate, "VAULT", vault):
                self.assertEqual(migrate.migrate_account(account), 1)
            saved = json.loads(config.read_text())["integrations"]["mqtt"]
            self.assertNotIn("token", saved)
            self.assertEqual(saved["secret_ref"], "vault://aia/test/mqtt")
            self.assertEqual(json.loads(target.read_text())["values"], {"token": "new-test-only", "password": "keep-test-only"})
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)

    def test_partial_update_preserves_other_credentials(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "test/mqtt.json"
            target.parent.mkdir()
            target.write_text(json.dumps({"values": {"token": "old-test-only", "password": "keep-test-only"}}))
            with patch.object(store_secret, "VAULT", root), patch.object(os, "geteuid", return_value=0), patch.object(sys, "argv", ["store", "test", "mqtt"]), patch.object(sys, "stdin", io.StringIO('{"token":"new-test-only"}')), contextlib.redirect_stdout(io.StringIO()):
                store_secret.main()
            self.assertEqual(json.loads(target.read_text())["values"], {"token": "new-test-only", "password": "keep-test-only"})


if __name__ == "__main__":
    unittest.main()
