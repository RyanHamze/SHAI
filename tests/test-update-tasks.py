#!/usr/bin/env python3
"""Maintenance contracts with all external commands mocked."""
import importlib.machinery
import json
from pathlib import Path
from types import SimpleNamespace
import subprocess
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
u = importlib.machinery.SourceFileLoader('maintenance_test', str(ROOT / 'installer/src/shai-update-apply')).load_module()
ACCOUNT = SimpleNamespace(pw_name='tester', pw_uid=1000, pw_dir='/home/tester')

class Tasks(unittest.TestCase):
    def test_catalog_and_allowlist_agree(self):
        data = json.loads((ROOT / 'installer/catalog/shapp-updates.json').read_text())
        self.assertEqual([task['id'] for task in data['tasks']], list(u.ORDER))
        self.assertTrue(all(task['command'] and task['description'] for task in data['tasks']))

    def test_order_and_rejections(self):
        self.assertEqual(u.validate_tasks(['apt-dist-upgrade', 'apt-refresh']), ['apt-refresh', 'apt-dist-upgrade'])
        for tasks in (['apt-refresh'] * 2, ['arbitrary shell'], ['apt-refresh', 5], 'apt-refresh'):
            with self.subTest(tasks=tasks), self.assertRaises(ValueError):
                u.validate_tasks(tasks)

    def test_upgrade_refuses_removals(self):
        preview = SimpleNamespace(stdout='Remv gdm3 [1]\n')
        with patch.object(u.shutil, 'which', return_value='/usr/bin/apt-get'), patch.object(u, 'invoke', return_value=preview) as invoke:
            with self.assertRaises(ValueError):
                u.execute_task('apt-dist-upgrade', ACCOUNT)
        self.assertEqual(invoke.call_count, 1)

    def test_autoremove_preserves_kernels_and_exact_targets(self):
        responses = [SimpleNamespace(stdout='Remv linux-image-old [1]\nRemv unused-library [1]\n'),
                     SimpleNamespace(stdout='Remv unused-library [1]\n'), SimpleNamespace(stdout='')]
        with patch.object(u, 'protected', side_effect=lambda name: name.startswith('linux-')), patch.object(u, 'invoke', side_effect=responses) as invoke:
            u.guarded_autoremove()
        self.assertEqual(invoke.call_args.args[0][-3:], ['remove', '--', 'unused-library'])
        self.assertNotIn('linux-image-old', invoke.call_args.args[0])

    def test_autoremove_refuses_collateral_removal(self):
        responses = [SimpleNamespace(stdout='Remv unused-library [1]\n'),
                     SimpleNamespace(stdout='Remv unused-library [1]\nRemv gdm3 [1]\n')]
        with patch.object(u, 'protected', return_value=False), patch.object(u, 'invoke', side_effect=responses) as invoke:
            with self.assertRaises(ValueError):
                u.guarded_autoremove()
        self.assertEqual(invoke.call_count, 2)

    def test_flatpak_system_and_user_contexts(self):
        with patch.object(u.shutil, 'which', return_value='/usr/bin/flatpak'), patch.object(u, 'invoke') as invoke, patch.object(u, 'audit'):
            u.execute_task('flatpak-update', ACCOUNT)
        self.assertEqual(invoke.call_args_list[0].args[0], ['flatpak', 'update', '--system', '-y'])
        self.assertIn('tester', invoke.call_args_list[1].args[0])
        self.assertIn('HOME=/home/tester', invoke.call_args_list[1].args[0])
        self.assertEqual(invoke.call_args_list[1].args[0][-4:], ['flatpak', 'update', '--user', '-y'])

    def test_missing_tool_is_logged_without_install(self):
        with patch.object(u.shutil, 'which', return_value=None), patch.object(u, 'invoke') as invoke, patch.object(u, 'audit') as audit:
            u.execute_task('flatpak-update', ACCOUNT)
        invoke.assert_not_called()
        self.assertEqual(audit.call_args.args[1], 'SKIPPED')

    def test_firmware_no_reboot_and_failure_not_hidden(self):
        self.assertIn('--no-reboot-check', u.COMMANDS['firmware-update'][0])
        self.assertIn('--no-unreported-check', u.COMMANDS['firmware-update'][0])
        with patch.object(u.subprocess, 'run', return_value=SimpleNamespace(returncode=2, stdout='')):
            u.invoke(['fwupdmgr', 'update'], codes=(0, 2))
        with patch.object(u.subprocess, 'run', return_value=SimpleNamespace(returncode=1, stdout='broken')):
            with self.assertRaises(subprocess.CalledProcessError):
                u.invoke(['fwupdmgr', 'update'], codes=(0, 2))

    def test_health_check_is_read_only(self):
        self.assertEqual(u.COMMANDS['apt-check'][-1], ['dpkg', '--audit'])
        self.assertTrue(all('install' not in cmd and 'remove' not in cmd for cmd in u.COMMANDS['apt-check']))

if __name__ == '__main__':
    unittest.main()
