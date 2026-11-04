#!/usr/bin/env python3
"""Live GTK completion-page geometry test; never applies Setup."""
import importlib.machinery
import time

setup = importlib.machinery.SourceFileLoader('completion_test', '/usr/bin/shai-setup').load_module()
app = setup.SetupApplication()
app.set_flags(app.get_flags() | setup.Gio.ApplicationFlags.NON_UNIQUE)
assert app.register(None)
window = setup.SetupWindow(app)
window.complete_summary.get_buffer().set_text('\n'.join(f'System summary line {n}' for n in range(1000)))
window.show_step(5)
for width, height in ((800, 600), (1024, 768)):
    window.set_default_size(width, height)
    window.present()
    deadline = time.monotonic() + 0.6
    while time.monotonic() < deadline:
        while setup.GLib.MainContext.default().pending():
            setup.GLib.MainContext.default().iteration(False)
        time.sleep(0.01)
    assert window.finish.get_visible()
    for button in (window.finish, window.cancel):
        success, bounds = button.compute_bounds(window)
        assert success
        assert bounds.get_y() >= 0
        assert bounds.get_y() + bounds.get_height() <= window.get_height(), (width, height, bounds)
    adjustment = window.summary_scroll.get_vadjustment()
    assert adjustment.get_upper() > adjustment.get_page_size()
    adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())
    assert adjustment.get_value() > 0
    print(f'PASS {width}x{height}: footer visible, long summary independently scrollable', flush=True)
window.destroy()
