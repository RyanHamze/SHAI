#!/usr/bin/env python3
"""Source-only lifecycle regressions. All external commands fail closed unless mocked."""
import importlib.machinery
import importlib.util
import fcntl
import json
import shlex
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
REAL_RUN = subprocess.run
REAL_POPEN = subprocess.Popen


def load(name):
    loader = importlib.machinery.SourceFileLoader(name.replace('-', '_'), str(ROOT / 'installer/src' / name))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


gi = ModuleType('gi')
gi.require_version = lambda *args: None
repository = ModuleType('gi.repository')
repository.Gtk = SimpleNamespace(ApplicationWindow=object, Application=object, ResponseType=SimpleNamespace(OK=1))
repository.Gdk = repository.Gio = repository.GLib = SimpleNamespace()
with patch.dict(sys.modules, {'gi': gi, 'gi.repository': repository}):
    setup = load('shai-setup')
    ui = load('shai-shapp')
apply = load('shai-shapp-apply')
host = load('shai-app-install')
source = load('shai-source-install')
stack = load('shai-stack-apply')
CATALOG = ROOT / 'installer/catalog/shapp-apps.json'
STACK_CATALOG = ROOT / 'installer/catalog/shai-stack-services.json'


class Isolated(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.tmp = Path(self.temporary.name)
        for name in ('run', 'Popen', 'check_output'):
            self.enterContext(patch.object(subprocess, name, side_effect=AssertionError('unmocked external command')))
        self.enterContext(patch.object(ui, 'append_log'))
        self.enterContext(patch.object(apply, 'STATE', self.tmp / 'apply-state'))
        self.enterContext(patch.object(ui, 'STACK_CATALOG', STACK_CATALOG))


class SetupCallbacks(Isolated):
    def test_handoff_is_independent_and_waits_before_closing(self):
        window = object.__new__(setup.SetupWindow)
        window.show_message = Mock()
        window.close = Mock()
        with patch.object(setup.shutil, 'which', side_effect=lambda name: '/usr/bin/' + name), patch.object(setup.subprocess, 'run') as run, patch.object(setup.GLib, 'timeout_add', create=True) as later:
            window.close_home_open_shapp(None)
        command = run.call_args.args[0]
        self.assertEqual(command[0], '/usr/bin/systemd-run')
        self.assertIn('--user', command)
        self.assertEqual(command[-1], '/usr/bin/shai-shapp')
        later.assert_called_once()
        window.close.assert_not_called()

    def test_failed_handoff_leaves_setup_open(self):
        window = object.__new__(setup.SetupWindow)
        window.show_message = Mock()
        window.close = Mock()
        with patch.object(setup.shutil, 'which', return_value='/usr/bin/test'), patch.object(setup.subprocess, 'run', side_effect=OSError('session unavailable')):
            window.close_home_open_shapp(None)
        window.show_message.assert_called_once()
        window.close.assert_not_called()

    def test_successful_handoff_closes_setup(self):
        window = object.__new__(setup.SetupWindow)
        window.show_message = Mock()
        window.close = Mock()
        with patch.object(setup.subprocess, 'run', return_value=SimpleNamespace(returncode=0)):
            self.assertFalse(window.finish_shapp_handoff('test-unit'))
        window.close.assert_called_once()

    def test_existing_shapp_window_counts_as_success(self):
        window = object.__new__(setup.SetupWindow)
        window.show_message = Mock()
        window.close = Mock()
        with patch.object(setup.subprocess, 'run', side_effect=[SimpleNamespace(returncode=3), SimpleNamespace(returncode=0, stdout='(true,)\n')]):
            self.assertFalse(window.finish_shapp_handoff('exited-launcher'))
        window.close.assert_called_once()
        window.show_message.assert_not_called()

    def test_handoff_launches_real_shapp(self):
        with patch.object(setup.shutil, 'which', side_effect=lambda name: '/usr/bin/' + name), patch.object(setup.subprocess, 'Popen') as launch:
            setup.SetupWindow.launch_shell('shapp')
        self.assertEqual(launch.call_args.args[0], ['/usr/bin/shai-shapp'])

    def test_failed_terminal_launch_recovers(self):
        window = object.__new__(setup.SetupWindow)
        window.plan = Mock(return_value={'plan_id': 'audit'})
        window.terminal_command = Mock(return_value=['terminal'])
        window.apply_button = Mock()
        window.apply_status = Mock()
        window.show_message = Mock()
        with patch.object(Path, 'home', return_value=self.tmp), patch.object(setup.subprocess, 'Popen', side_effect=OSError('terminal failed')):
            window.start_apply(None)
        window.apply_button.set_sensitive.assert_called_with(True)


class ShappCallbacks(Isolated):
    def window(self):
        window = object.__new__(ui.ShappWindow)
        window.catalog = json.loads(CATALOG.read_text())['apps']
        window.architecture_mode = 'direct-host'
        window.baseline = {}
        window.desired = {}
        window.installed_apps = []
        window.applying = False
        window.completion_path = None
        window.show_status = Mock()
        window.apply_button = Mock()
        return window

    def test_apply_rechecks_capacity(self):
        window = self.window()
        window.desired['managed:wyoming'] = True
        window.update_capacity_controls = Mock(return_value=False)
        with patch.object(ui, 'system_capacity_mb', return_value=(100, 100, 100, 100)), patch.object(Path, 'home', return_value=self.tmp):
            window.apply_changes(None)
        self.assertFalse(list(self.tmp.rglob('shapp-*.json')))

    def test_apply_does_not_launch_twice(self):
        window = self.window()
        window.applying = True
        window.changes = Mock(side_effect=AssertionError('must ignore duplicate apply'))
        window.apply_changes(None)

    def test_refresh_keeps_apply_disabled_while_running(self):
        window = self.window()
        window.applying = True
        window.changes = Mock(return_value=([{'name': 'Test', 'disk_mb': 1, 'ram_mb': 1}], []))
        window.change_totals = Mock(return_value=(1, 1, {}))
        window.cart_items = Mock()
        window.cart_items.get_first_child.return_value = None
        window.pending_row = Mock()
        window.cart_title = Mock()
        window.update_capacity_controls = Mock(return_value=True)
        with patch.object(ui, 'system_capacity_mb', return_value=(0, 100, 0, 100)):
            window.refresh_cart()
        window.apply_button.set_sensitive.assert_called_with(False)

    def test_shared_package_uncheck_appears_in_cart(self):
        window = self.window()
        window.baseline = {'apt:borgbackup': True, 'apt:cryptsetup': True}
        window.desired = {'apt:borgbackup': True, 'apt:cryptsetup': False}
        _, removals = window.changes()
        self.assertEqual([app.package for app in removals], ['cryptsetup'])

    def test_container_removal_does_not_credit_preserved_disk(self):
        window = self.window()
        app = ui.InstalledApp('container', 'jellyfin', 'Jellyfin', '', 2048, 1200, False)
        disk, _, _ = window.change_totals([], [app])
        self.assertEqual(disk, 0)

    def test_cancelled_auth_allows_retry(self):
        window = self.window()
        window.applying = True
        window.plan_id = 'cancelled'
        window.completion_path = self.tmp / 'cancelled.exit'
        window.completion_path.write_text('1\n')
        window.refresh_cart = Mock()
        with patch.object(ui, 'RESULT', self.tmp / 'missing.json'):
            self.assertFalse(window.poll_result())
        self.assertFalse(window.applying)
        window.refresh_cart.assert_called_once()

    def test_missing_result_alone_does_not_unlock(self):
        window = self.window()
        window.applying = True
        window.plan_id = 'running'
        window.completion_path = self.tmp / 'running.exit'
        with patch.object(ui, 'RESULT', self.tmp / 'missing.json'):
            self.assertTrue(window.poll_result())
        self.assertTrue(window.applying)

    def test_terminal_writes_status_before_waiting_for_enter(self):
        window = self.window()
        plan = self.tmp / "space and 'quote.json"
        with patch.object(ui.shutil, 'which', return_value='/usr/bin/ptyxis'):
            command = window.terminal_command(plan)
        script = command[-1]
        self.assertLess(script.index('trap - EXIT; echo;'), script.index('read;'))
        self.assertIn(str(plan.with_suffix('.exit')).split('/')[-1].split("'")[0], script)
        self.assertIn("trap 'exit 129' HUP", script)

    def test_terminal_completion_marker_with_quoted_path(self):
        window = self.window()
        plan = self.tmp / "space and 'quote.json"
        with patch.object(ui.shutil, 'which', return_value='/usr/bin/ptyxis'):
            script = window.terminal_command(plan)[-1]
        invocation = f'sudo /usr/bin/shai-shapp-apply {shlex.quote(str(plan))}'
        self.assertEqual(script.count(invocation), 1)
        for harmless, code in [('false', 1), ('true', 0), ('kill -HUP $$', 129)]:
            with patch.object(subprocess, 'Popen', REAL_POPEN):
                result = REAL_RUN(['bash', '-c', script.replace(invocation, harmless, 1)], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            self.assertEqual(result.returncode, code, result.stderr)
            self.assertEqual(plan.with_suffix('.exit').read_text().strip(), str(code))

    def test_docker_reserves_include_dependency(self):
        window = self.window()
        window.architecture_mode = 'managed-stack'
        window.desired['container:zigbee2mqtt'] = True
        with patch.object(ui.shutil, 'disk_usage', return_value=SimpleNamespace(free=11000 * 1024 ** 2)):
            failures = window.stack_capacity_restrictions(2300)
        self.assertTrue(any('2368 MB RAM' in value for value in failures))
        self.assertTrue(any('11520 MB free' in value for value in failures))

    def test_removal_only_not_blocked_by_docker_reserves(self):
        window = self.window()
        window.architecture_mode = 'managed-stack'
        window.baseline['container:jellyfin'] = True
        window.desired['container:jellyfin'] = False
        self.assertEqual(window.stack_capacity_restrictions(100), [])

    def test_docker_reserves_fit(self):
        window = self.window()
        window.architecture_mode = 'managed-stack'
        window.desired['container:jellyfin'] = True
        with patch.object(ui.shutil, 'disk_usage', return_value=SimpleNamespace(free=20000 * 1024 ** 2)):
            self.assertEqual(window.stack_capacity_restrictions(8000), [])

    def test_architecture_availability(self):
        window = self.window()
        crypt = next(item for item in window.catalog if item['id'] == 'veracrypt')
        jellyfin = next(item for item in window.catalog if item['id'] == 'jellyfin')
        with patch.object(ui.platform, 'machine', return_value='aarch64'):
            self.assertFalse(window.backend_available(crypt))
        window.architecture_mode = 'managed-stack'
        with patch.object(ui.platform, 'machine', return_value='i686'):
            self.assertFalse(window.backend_available(jellyfin))
        with patch.object(ui.platform, 'machine', return_value='x86_64'), patch.object(ui.os, 'cpu_count', return_value=1):
            self.assertFalse(window.backend_available(jellyfin))


class ApplySafety(Isolated):
    def test_schema5_dispatches_update_only_plan(self):
        runner = self.invoke({'schema': 5, 'updates': ['apt-refresh', 'apt-autoclean']})
        with patch.object(apply, 'LIB', ROOT / 'installer'):
            self.assertEqual(apply.main(), 0)
        self.assertEqual(len(runner.call_args_list), 1)
        command = runner.call_args.args[0]
        self.assertIn('shai-update-apply', command[1])
        self.assertEqual(command[-2:], ['--tasks', 'apt-refresh,apt-autoclean'])

    def test_unknown_update_rejected_before_commands(self):
        runner = self.invoke({'schema': 5, 'updates': ['run-arbitrary-command']})
        with patch.object(apply, 'LIB', ROOT / 'installer'):
            with self.assertRaisesRegex(apply.PlanRejected, 'unknown maintenance'):
                apply.main()
        runner.assert_not_called()

    def test_duplicate_updates_rejected(self):
        runner = self.invoke({'schema': 5, 'updates': ['apt-refresh', 'apt-refresh']})
        with self.assertRaisesRegex(apply.PlanRejected, 'duplicates'):
            apply.main()
        runner.assert_not_called()

    def test_backend_lock_blocks_duplicate_apply(self):
        apply.STATE.mkdir()
        with (apply.STATE / 'shapp-apply.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with patch.object(apply.os, 'geteuid', return_value=0), patch.object(apply, 'apply_plan') as operation:
                with self.assertRaisesRegex(apply.PlanRejected, 'still running'):
                    apply.main()
                operation.assert_not_called()

    def test_backend_lock_released_after_failure(self):
        with patch.object(apply.os, 'geteuid', return_value=0), patch.object(apply, 'apply_plan', side_effect=OSError('failed')):
            with self.assertRaises(OSError):
                apply.main()
        with patch.object(apply.os, 'geteuid', return_value=0), patch.object(apply, 'apply_plan', return_value=0):
            self.assertEqual(apply.main(), 0)

    def invoke(self, plan, simulation=''):
        account = SimpleNamespace(pw_uid=1000, pw_dir=str(self.tmp))
        info = SimpleNamespace(st_uid=1000)
        defaults = {'schema': 4, 'plan_id': 'abcdef0123456789', 'target_user': 'tester', 'architecture': 'direct-host',
                    'install': [], 'remove_apt': [], 'remove_snap': [], 'remove_container': [], 'remove_managed': []}
        defaults.update(plan)
        patches = [patch.object(apply.os, 'geteuid', return_value=0),
                   patch.object(sys, 'argv', ['apply', 'plan.json']),
                   patch.object(apply, 'read_secure_plan', return_value=(defaults, info)),
                   patch.object(apply.pwd, 'getpwnam', return_value=account),
                   patch.object(apply, 'CATALOG', CATALOG), patch.object(apply, 'STACK_CATALOG', STACK_CATALOG),
                   patch.object(apply, 'protected_patterns', return_value=[]),
                   patch.object(apply, 'visible_apt_packages', return_value={'kodi'}),
                   patch.object(apply, 'installed_snaps', return_value=set()),
                   patch.object(apply, 'audit'), patch.object(apply, 'write_result')]
        for item in patches:
            self.enterContext(item)
        def run(args, **kwargs):
            return subprocess.CompletedProcess(args, 0, stdout=simulation if '-s' in args else '')
        runner = self.enterContext(patch.object(apply, 'run', side_effect=run))
        return runner

    def test_rejects_unapproved_apt_dependency_removal(self):
        runner = self.invoke({'remove_apt': ['kodi']}, 'Remv kodi [1]\nRemv unrelated-editor [1]\n')
        with self.assertRaisesRegex(apply.PlanRejected, 'unapproved'):
            apply.main()
        self.assertFalse(any('-y' in call.args[0] for call in runner.call_args_list))

    def test_rejects_install_remove_overlap(self):
        runner = self.invoke({'install': ['kodi'], 'remove_apt': ['kodi']})
        with self.assertRaises(apply.PlanRejected):
            apply.main()
        runner.assert_not_called()

    def test_allows_explicit_apt_removal(self):
        runner = self.invoke({'remove_apt': ['kodi']}, 'Remv kodi [1]\n')
        self.assertEqual(apply.main(), 0)
        self.assertTrue(any('-y' in call.args[0] for call in runner.call_args_list))

    def test_rejects_managed_overlap(self):
        self.invoke({'install': ['wyoming'], 'remove_managed': ['wyoming']})
        with self.assertRaises(apply.PlanRejected):
            apply.main()


class HostSafety(Isolated):
    def test_voice_removal_requires_shapp_receipt(self):
        with patch.object(sys, 'argv', ['host', 'remove', 'wyoming', '--user', 'tester']), patch.object(host.os, 'geteuid', return_value=0), patch.object(host.pwd, 'getpwnam', return_value=SimpleNamespace(pw_uid=1000, pw_dir=str(self.tmp))), patch.object(host, 'STATE', self.tmp / 'receipts'), patch.object(host, 'run') as runner:
            with self.assertRaisesRegex(SystemExit, 'SHAPP-managed'):
                host.main()
        runner.assert_not_called()

    def test_source_architecture_rejected_before_prerequisites(self):
        with patch.object(sys, 'argv', ['source', 'install', 'veracrypt']), patch.object(source.os, 'geteuid', return_value=0), patch.object(Path, 'read_text', return_value='ID=ubuntu\nVERSION_ID="26.04"\n'), patch.object(Path, 'mkdir'), patch.object(source, 'run', return_value='arm64') as runner:
            with self.assertRaisesRegex(SystemExit, 'amd64'):
                source.main()
        self.assertEqual([call.args[0] for call in runner.call_args_list], [['dpkg', '--print-architecture']])


class StackSafety(Isolated):
    def test_remove_only_never_assesses_installs_or_downloads(self):
        data = self.tmp / 'data'
        data.mkdir()
        config = self.tmp / 'stack'
        config.mkdir()
        (config / 'compose.yaml').write_text('services: {}\n')
        catalog = json.loads(STACK_CATALOG.read_text())['services']
        with patch.object(sys, 'argv', ['stack', '--remove', 'jellyfin']), patch.object(stack.os, 'geteuid', return_value=0), patch.object(stack, 'installed', return_value={'jellyfin', 'mosquitto'}), patch.object(stack, 'load_catalog', return_value=catalog), patch.object(stack, 'DATA', data), patch.object(stack, 'STATE', data / 'installed.json'), patch.object(stack, 'STACK', config), patch.object(stack, 'REGISTRY', self.tmp / 'registry.json'), patch.object(stack, 'hardware_assessment', side_effect=AssertionError('removal must work under capacity')), patch.object(stack, 'install_engine', side_effect=AssertionError('removal must not install engine')), patch.object(stack, 'write_configuration', side_effect=AssertionError('removal must not pull images')), patch.object(stack, 'run', return_value='') as runner:
            self.assertEqual(stack.main(), 0)
        self.assertEqual(json.loads((data / 'installed.json').read_text())['services'], ['mosquitto'])
        self.assertTrue(any('rm' in call.args[0] and 'jellyfin' in call.args[0] for call in runner.call_args_list))
        self.assertFalse(any('up' in call.args[0] for call in runner.call_args_list))

    def test_cannot_remove_mqtt_while_retaining_zigbee(self):
        with patch.object(sys, 'argv', ['stack', '--remove', 'mosquitto']), patch.object(stack.os, 'geteuid', return_value=0), patch.object(stack, 'installed', return_value={'mosquitto', 'zigbee2mqtt'}):
            with self.assertRaisesRegex(SystemExit, 'Zigbee'):
                stack.main()


class RemovedUnitMarkers(unittest.TestCase):
    def test_insights_reset_is_scoped_to_absent_units(self):
        engine = (ROOT / 'installer/src/shai-installer').read_text()
        function = engine.split('clear_expected_removed_unit_failures() {', 1)[1].split('\n}\n', 1)[0]
        program = 'clear_expected_removed_unit_failures() {' + function + '\n}\n'
        for present in (False, True):
            mock = "dpkg-query() { return 1; }; systemctl() { :; }; run_as_user() { "
            mock += '[[ "$*" != *" cat "* ]] || return ' + ('0' if present else '1') + '; printf "%s\\n" "$*"; };\n'
            result = subprocess.run(['bash', '-c', program + mock + 'clear_expected_removed_unit_failures'], capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.count('reset-failed ubuntu-insights-'), 0 if present else 2)


if __name__ == '__main__':
    unittest.main()
