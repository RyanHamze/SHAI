#!/usr/bin/env python3
"""Live GTK workflow test; captures terminal invocation without executing installs."""
import importlib.machinery
import json
import os
from pathlib import Path
import tempfile
import unittest.mock

ui = importlib.machinery.SourceFileLoader('shapp_live', '/usr/bin/shai-shapp').load_module()
app = ui.ShappApplication() if hasattr(ui, 'ShappApplication') else None
if app is None:
    # Keep class naming independent of the packaged UI entry point.
    app_class = next(cls for name, cls in vars(ui).items() if isinstance(cls, type) and cls is not ui.Gtk.Application and issubclass(cls, ui.Gtk.Application))
    app = app_class()
app.set_flags(app.get_flags() | ui.Gio.ApplicationFlags.NON_UNIQUE)
assert app.register(None)
window_class = next(cls for name, cls in vars(ui).items() if isinstance(cls, type) and cls is not ui.Gtk.ApplicationWindow and issubclass(cls, ui.Gtk.ApplicationWindow))
window = window_class(app)
window.architecture_mode = 'direct-host'
voice = next(x for x in window.catalog if x['id'] == 'wyoming')
assert window.backend_available(voice)
window.desired['managed:wyoming'] = True
installs, _ = window.changes()
assert any(x['id'] == 'wyoming' for x in installs)
captured = []
with unittest.mock.patch.object(ui.subprocess, 'Popen', side_effect=lambda args, **kwargs: captured.append(args)):
    window.apply_changes(None)
assert captured and any('bash' in str(x) for x in captured[0]), captured
plans = sorted((Path.home() / '.cache/shai').glob('shapp-*.json'), key=lambda x: x.stat().st_mtime)
plan = json.loads(plans[-1].read_text())
assert plan['schema'] == 4 and 'wyoming' in plan['install'] and 'remove_managed' in plan
window.architecture_mode = 'managed-stack'
for app_id in ['jellyfin','node-red','openhab','navidrome','plex','emby','adguard-home','pi-hole']:
    assert window.backend_available(next(x for x in window.catalog if x['id'] == app_id))
print('PASS host/container backend selection, cart mapping, schema-4 plan, automatic visible-terminal command construction; no installs launched')
window.destroy()
