#!/usr/bin/env python3
"""Live Update All/cart smoke test. Terminal execution is mocked; no updates run."""
import importlib.machinery
import json
from pathlib import Path
from unittest.mock import patch

ui = importlib.machinery.SourceFileLoader('updates_live', '/usr/bin/shai-shapp').load_module()
app = ui.ShappApplication()
app.set_flags(app.get_flags() | ui.Gio.ApplicationFlags.NON_UNIQUE)
assert app.register(None)
window = ui.ShappWindow(app)
window.show_tab('updates')
assert not window.selected_updates
assert window.cart_title.get_text() == '0 pending changes'
window.update_checks['apt-refresh'].set_active(True)
window.update_checks['apt-autoclean'].set_active(True)
assert window.cart_title.get_text() == '2 pending changes'
window.show_tab('optional')
assert window.selected_updates == {'apt-refresh', 'apt-autoclean'}
window.cart_items.get_first_child().get_last_child().emit('clicked')
assert len(window.selected_updates) == 1
assert window.cart_title.get_text() == '1 pending change'
window.update_checks['apt-refresh'].set_active(True)
window.update_checks['apt-autoclean'].set_active(True)
captured = []
with patch.object(ui.subprocess, 'Popen', side_effect=lambda command, **kwargs: captured.append(command)), patch.object(ui, 'append_log'):
    window.apply_changes(None)
assert captured, 'Update-only cart must open the approved visible terminal'
plan = Path.home() / '.cache/shai' / f'shapp-{window.plan_id}.json'
data = json.loads(plan.read_text())
assert data['schema'] == 5
assert data['updates'] == ['apt-autoclean', 'apt-refresh']
assert data['install'] == [] and data['remove_apt'] == []
assert plan.stat().st_mode & 0o777 == 0o600
print('PASS Update All checkboxes, cross-tab cart, remove X, update-only terminal plan; NO updates executed', flush=True)
window.destroy()
