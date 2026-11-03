#!/usr/bin/env python3
"""Exercise Save configuration with isolated config; never contacts an endpoint."""
import importlib.machinery
import json
import tempfile
from pathlib import Path

aia = importlib.machinery.SourceFileLoader("custom_config_test", "/usr/bin/shai-aia").load_module()
app = aia.AIAApplication()
app.set_flags(app.get_flags() | aia.Gio.ApplicationFlags.NON_UNIQUE)
assert app.register(None)
assert not app.get_is_remote(), "GUI tests require a local application instance"
window = aia.AIAWindow(app)
with tempfile.TemporaryDirectory() as directory:
    aia.CONFIG_FILE = Path(directory) / "aia.json"
    spec = {"id": "custom-test", "name": "Local test app", "kind": "custom", "port": 0, "description": "Isolated configuration test",
            "fields": [{"key": "host", "secret": False}, {"key": "port", "secret": False}]}
    window.config["custom_integrations"] = [spec]
    entries = {"host": aia.Gtk.Entry(), "port": aia.Gtk.Entry()}
    entries["host"].set_text("127.0.0.1")
    entries["port"].set_text("12345")
    def forbidden(*_args):
        raise AssertionError("Save must not run a connection test")
    window.test_integration = forbidden
    window.integration_response(aia.Gtk.Dialog(), aia.Gtk.ResponseType.OK, spec, entries)
    saved = json.loads(aia.CONFIG_FILE.read_text())
    assert saved["integrations"]["custom-test"]["port"] == "12345"
    assert saved["integrations"]["custom-test"]["_health"] == "not-tested"
    window.build_integrations()
    print("PASS custom fields saved to isolated configuration, no network test invoked")
window.destroy()
