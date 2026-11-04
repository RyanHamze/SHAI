#!/usr/bin/env python3
"""Source-only AIA install controls and firewall status regressions. No host changes."""
import importlib.machinery
import sys
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
base = importlib.machinery.SourceFileLoader('aia_regression_loader', str(ROOT / 'tests/test-aia-health-regressions.py')).load_module()
aia, health = base.aia, base.health
snapshot = base.load('shai-network-snapshot')

class Controls(unittest.TestCase):
    def window(self):
        window = object.__new__(aia.AIAWindow)
        window.config = {'online_installs': False, 'save_chat': False, 'imported_models': []}
        window.model_chooser = None
        for method in ('error', 'ensure_model_service', 'update_active_header', 'build_models'):
            setattr(window, method, Mock())
        return window

    def test_online_toggle_does_not_require_chat_history(self):
        for online, history in ((True, False), (False, True)):
            window = self.window()
            window.config['save_chat'] = history
            with patch.object(aia, 'save_config'), patch.object(aia, 'audit'):
                window.online_changed(SimpleNamespace(get_active=lambda: online), None)
            self.assertIs(window.config['online_installs'], online)
            self.assertIs(window.config['save_chat'], history)

    def test_model_download_rechecks_offline_policy_before_script_creation(self):
        window = self.window()
        with patch.object(aia.Gtk, 'ResponseType', SimpleNamespace(OK=1), create=True), patch.object(aia.Path, 'mkdir', side_effect=AssertionError('must not create install scripts')):
            window.install_response(Mock(), 1, aia.MODELS[0])
        window.error.assert_called_once()

    def test_cancelled_import_closes_and_releases_chooser(self):
        window = self.window()
        chooser = Mock()
        window.model_chooser = chooser
        with patch.object(aia.Gtk, 'ResponseType', SimpleNamespace(ACCEPT=1), create=True):
            window.import_response(chooser, 0)
        self.assertIsNone(window.model_chooser)
        chooser.get_file.assert_not_called()
        chooser.destroy.assert_called_once()

    def test_native_dialog_has_persistent_reference_and_reuses_it(self):
        window = self.window()
        chooser = Mock()
        with patch.object(aia.Gtk, 'FileChooserNative', SimpleNamespace(new=Mock(return_value=chooser)), create=True), patch.object(aia.Gtk, 'FileChooserAction', SimpleNamespace(OPEN=1), create=True), patch.object(aia.Gtk, 'FileFilter', return_value=Mock(), create=True):
            window.import_model(None)
            self.assertIs(window.model_chooser, chooser)
            window.import_model(None)
        self.assertEqual(chooser.show.call_count, 2)
        chooser.connect.assert_called_once()

    def test_missing_or_remote_selection_shows_error(self):
        for selected in (None, SimpleNamespace(get_path=lambda: None)):
            window = self.window()
            chooser = Mock()
            chooser.get_file.return_value = selected
            with patch.object(aia.Gtk, 'ResponseType', SimpleNamespace(ACCEPT=1), create=True):
                window.import_response(chooser, 1)
            window.error.assert_called_once()
            chooser.destroy.assert_called_once()
            self.assertIsNone(window.model_chooser)

    def test_offline_local_model_import_does_not_download(self):
        window = self.window()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'local.gguf'
            source.write_bytes(b'GGUFtest-only')
            chooser = Mock()
            chooser.get_file.return_value = SimpleNamespace(get_path=lambda: str(source))
            with patch.object(aia.Gtk, 'ResponseType', SimpleNamespace(ACCEPT=1), create=True), patch.object(aia, 'save_config') as save, patch.object(aia, 'audit'), patch.object(aia.shutil, 'which', return_value=None), patch.object(aia.subprocess, 'Popen', side_effect=AssertionError('no download')):
                window.import_response(chooser, 1)
            self.assertEqual(window.config['imported_models'][0]['path'], str(source))
            self.assertFalse(window.config['online_installs'])
            self.assertIn('llama.cpp is missing', window.error.call_args.args[0])
            save.assert_called_once()
            chooser.destroy.assert_called_once()

    def test_import_save_failure_cleans_dialog_and_restores_config(self):
        window = self.window()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'local.gguf'
            source.write_bytes(b'GGUFtest-only')
            chooser = Mock()
            chooser.get_file.return_value = SimpleNamespace(get_path=lambda: str(source))
            with patch.object(aia.Gtk, 'ResponseType', SimpleNamespace(ACCEPT=1), create=True), patch.object(aia, 'save_config', side_effect=OSError('disk full')):
                window.import_response(chooser, 1)
            self.assertEqual(window.config['imported_models'], [])
            self.assertIn('disk full', window.error.call_args.args[0])
            chooser.destroy.assert_called_once()

    def test_explicit_disabled_and_enabled_model_button_labels(self):
        source = (ROOT / 'installer/src/shai-aia').read_text()
        self.assertIn("Gtk.Button(label=\"Install from online\" if self.config.get('online_installs') else 'Enable online from Settings')", source)
        self.assertIn('Chat-history saving is optional and unrelated.', source)

class Firewall(unittest.TestCase):
    def test_ufw_snapshot_does_not_infer_from_service_state(self):
        with patch.object(snapshot.shutil, 'which', return_value='/usr/sbin/ufw'), patch.object(snapshot, 'run', return_value=(0, 'Status: inactive')):
            self.assertEqual(snapshot.firewall_snapshot()['state'], 'inactive')
        with patch.object(snapshot.shutil, 'which', return_value='/usr/sbin/ufw'), patch.object(snapshot, 'run', return_value=(1, '')):
            self.assertEqual(snapshot.firewall_snapshot()['state'], 'unknown')

    def test_health_reads_root_snapshot_and_fails_unknown_on_permission_error(self):
        with patch.object(health, 'read_snapshot', return_value={'firewall': {'state': 'active', 'detail': 'Status: active'}}), patch.object(health, 'run', side_effect=AssertionError('no privileged prompt')):
            self.assertEqual(health.firewall_status()[0], 'active')
        with patch.object(health, 'read_snapshot', side_effect=ValueError('stale')), patch.object(health.shutil, 'which', return_value='/usr/sbin/ufw'), patch.object(health, 'run', return_value=(1, '', 'permission denied')):
            self.assertEqual(health.firewall_status()[0], 'unknown')

if __name__ == '__main__':
    unittest.main()
