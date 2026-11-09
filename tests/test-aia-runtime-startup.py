#!/usr/bin/env python3
"""Fresh model/runtime installation contracts; no package or service changes."""
import importlib.machinery
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch
import subprocess

ROOT = Path(__file__).resolve().parents[1]
base = importlib.machinery.SourceFileLoader('startup_regression_loader', str(ROOT / 'tests/test-aia-health-regressions.py')).load_module()
aia = base.aia
server = base.load('shai-aia-server')

class Startup(unittest.TestCase):
    def test_normal_window_start_initializes_shared_memory_without_model(self):
        window = SimpleNamespace(config={}, active_path=lambda: None)
        with patch.object(aia, 'ensure_server_key'), patch.object(aia, 'run', return_value=(0, '')) as run:
            aia.AIAWindow.ensure_model_service(window)
        self.assertTrue(any(str(aia.CONTEXT_HELPER) in call.args[0] and '--refresh' in call.args[0]
                            for call in run.call_args_list))
        self.assertTrue(any(aia.CONTEXT_GATEWAY in call.args[0] for call in run.call_args_list))

    def test_prepare_private_key_and_preserve_existing_key(self):
        with tempfile.TemporaryDirectory() as directory:
            key = Path(directory) / 'state/server-api-key'
            with patch.object(server, 'KEY_FILE', key):
                server.prepare_key()
                original = key.read_text()
                self.assertGreater(len(original.strip()), 32)
                self.assertEqual(key.stat().st_mode & 0o777, 0o600)
                self.assertEqual(key.parent.stat().st_mode & 0o777, 0o700)
                server.prepare_key()
                self.assertEqual(key.read_text(), original)

    def test_prepare_rejects_symlink_without_altering_target(self):
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory) / 'outside'
            outside.write_text('leave-unchanged')
            key = Path(directory) / 'state/server-api-key'
            key.parent.mkdir()
            key.symlink_to(outside)
            with patch.object(server, 'KEY_FILE', key), self.assertRaises(SystemExit) as raised:
                server.prepare_key()
            self.assertEqual(raised.exception.code, 78)
            self.assertEqual(outside.read_text(), 'leave-unchanged')

    def test_configuration_errors_do_not_restart_forever(self):
        unit = (ROOT / 'installer/systemd/shai-aia-model.service').read_text()
        self.assertIn('RestartPreventExitStatus=78', unit)
        self.assertIn('StartLimitBurst=3', unit)
        with self.assertRaises(SystemExit) as raised:
            server.fail('test-only missing configuration')
        self.assertEqual(raised.exception.code, 78)

    def window(self):
        window = object.__new__(aia.AIAWindow)
        window.config = {'online_installs': True, 'save_chat': False}
        window.fit = Mock(return_value=(True, 'fits'))
        window.error = Mock()
        window.launch_terminal = Mock()
        return window

    def validate_script(self, path):
        body = path.read_text()
        self.assertLess(body.index('--prepare-key'), body.index('systemctl --user restart'))
        self.assertLess(body.index('/v1/chat/completions'), body.index('Installation complete') if 'Installation complete' in body else body.index('Runtime installed.'))
        self.assertIn('ProxyHandler({})', body)
        self.assertIn("'Authorization': 'Bearer ' + key", body)
        subprocess.run(['bash', '-n', str(path)], check=True)
        fragment = body.split("<<'AIA_HEALTH'\n", 1)[1].split('\nAIA_HEALTH', 1)[0]
        compile(fragment, '<generated health probe>', 'exec')

    def test_fresh_online_model_script_prepares_key_before_start(self):
        window = self.window()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(aia, 'STATE_DIR', root / 'state'), patch.object(aia, 'DATA_DIR', root / 'models'), patch.object(aia, 'SERVER_KEY', root / 'state/key'), patch.object(aia, 'CONFIG_FILE', root / 'config/aia.json'), patch.object(aia, 'hardware', return_value={}), patch.object(aia, 'save_config') as save, patch.object(aia, 'audit'), patch.object(aia.Gtk, 'ResponseType', SimpleNamespace(OK=1), create=True):
                window.install_response(Mock(), 1, aia.MODELS[0])
                script = window.launch_terminal.call_args.args[0]
                self.validate_script(script)
                save.assert_called_once_with(window.config)
                self.assertEqual(script.stat().st_mode & 0o777, 0o700)

    def test_runtime_only_install_prepares_key_after_explicit_approval(self):
        window = self.window()
        dialog = Mock()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(aia, 'STATE_DIR', root), patch.object(aia.Gtk, 'ResponseType', SimpleNamespace(OK=1), create=True), patch.object(aia.Gtk, 'ButtonsType', SimpleNamespace(OK_CANCEL=1), create=True), patch.object(aia.Gtk, 'MessageDialog', return_value=dialog, create=True):
                window.confirm_runtime_install(None)
                window.launch_terminal.assert_not_called()
                callback = dialog.connect.call_args.args[1]
                callback(dialog, 0)
                self.assertEqual(list(root.glob('*.sh')), [])
                callback(dialog, 1)
                self.validate_script(window.launch_terminal.call_args.args[0])

if __name__ == '__main__':
    unittest.main()
