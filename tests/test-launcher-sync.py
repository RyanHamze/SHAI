#!/usr/bin/env python3
"""Launcher security/lifecycle tests; never trust real desktop files."""
import importlib.machinery
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
m = importlib.machinery.SourceFileLoader('launcher_test', str(ROOT / 'installer/src/shai-launcher-sync')).load_module()

class Launchers(unittest.TestCase):
    def file(self, uid=1000, mode=0o644, content=b'launcher'):
        obj = Mock()
        obj.is_symlink.return_value = False
        obj.is_file.return_value = True
        obj.stat.return_value = SimpleNamespace(st_uid=uid, st_mode=mode)
        obj.read_bytes.return_value = content
        return obj

    def test_only_exact_root_owned_safe_source_is_trusted(self):
        self.assertTrue(m.trusted_candidate(self.file(), self.file(uid=0), 1000))
        for target, source in ((self.file(content=b'changed'), self.file(uid=0)),
                               (self.file(mode=0o666), self.file(uid=0)),
                               (self.file(), self.file(uid=1000)),
                               (self.file(uid=2000), self.file(uid=0))):
            self.assertFalse(m.trusted_candidate(target, source, 1000))
        target = self.file()
        target.is_symlink.return_value = True
        self.assertFalse(m.trusted_candidate(target, self.file(uid=0), 1000))

    def test_cleanup_is_exact_and_preserves_modified_launchers(self):
        with tempfile.TemporaryDirectory() as folder:
            desktop = Path(folder)
            home = desktop / 'shai-home.desktop'
            home.write_text('[Desktop Entry]\nExec=shai-wave-a-shell home\n')
            custom = desktop / 'shai-appearance.desktop'
            custom.write_text('[Desktop Entry]\nExec=my-custom-command\n')
            m.remove_known(home, m.LEGACY[home.name])
            m.remove_known(custom, m.LEGACY[custom.name])
            self.assertFalse(home.exists())
            self.assertTrue(custom.exists())

    def test_completed_setup_removed_but_menu_source_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            desktop = home / 'Desktop'
            desktop.mkdir()
            state = home / 'state'
            state.mkdir()
            (state / 'applied-version').write_text('0.13.1')
            setup = desktop / 'shai-setup.desktop'
            setup.write_text('[Desktop Entry]\nExec=shai-setup\n')
            with patch.object(m.Path, 'home', return_value=home), patch.object(m, 'STATE', state), patch.object(m.shutil, 'which', return_value=None), patch.object(m.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='@as []')):
                m.sync_user()
            self.assertFalse(setup.exists())
            menu = ROOT / 'installer/share/applications/shai-setup.desktop'
            self.assertIn('Name=SHAI Setup', menu.read_text())

    def test_web_offline_is_in_trust_allowlist(self):
        self.assertIn('shai-web-connectivity-toggle.desktop', m.LAUNCHERS)

if __name__ == '__main__':
    unittest.main()
