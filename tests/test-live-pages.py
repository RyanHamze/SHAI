#!/usr/bin/env python3
"""Live Setup/SHEALTH page smoke test. Never applies Setup or package changes."""
import importlib.machinery
from gi.repository import Gio

setup = importlib.machinery.SourceFileLoader('setup_pages', '/usr/bin/shai-setup').load_module()
app = setup.SetupApplication()
app.set_flags(app.get_flags() | Gio.ApplicationFlags.NON_UNIQUE)
assert app.register(None)
window = setup.SetupWindow(app)
for index, name in enumerate(window.STEPS):
    window.show_step(index)
    assert window.stack.get_visible_child() is not None
    print('PASS Setup page', name, flush=True)
window.destroy()

health = importlib.machinery.SourceFileLoader('health_pages', '/usr/bin/shai-health').load_module()
app = health.HealthApplication()
app.set_flags(app.get_flags() | Gio.ApplicationFlags.NON_UNIQUE)
assert app.register(None)
window = health.HealthWindow(app)
for name in window.TABS:
    window.show_tab(name)
    assert window.pages[name].get_first_child() is not None, name
    print('PASS SHEALTH page', name, flush=True)
window.destroy()
