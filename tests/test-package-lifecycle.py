#!/usr/bin/env python3
"""Execute prerm with isolated fake tools, never host services or real runuser."""
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRERM = ROOT / 'installer/debian/prerm'
USER_UNITS = (
    'shai-context.timer', 'shai-context.service',
    'shai-context-gateway.service', 'shai-aia-model.service',
)
SYSTEM_UNITS = (
    'shai-network-snapshot.timer', 'shai-network-snapshot.service',
    'shai-control-broker.service',
)

# No fake command launches another executable. In particular, runuser only logs
# and interprets its argv; its clean env is checked without crossing privileges.
FAKE_TOOL = r'''
import json
import os
from pathlib import Path
import sys

data = json.loads(Path(os.environ['LIFECYCLE_FIXTURE']).read_text())
tool = Path(sys.argv[0]).name
args = sys.argv[1:]
with Path(os.environ['LIFECYCLE_LOG']).open('a') as log:
    log.write(json.dumps([tool, *args]) + '\n')

def mock_error(kind, value, traceback):
    with Path(os.environ['LIFECYCLE_LOG']).open('a') as log:
        log.write(json.dumps(['MOCK_ERROR', str(value)]) + '\n')
sys.excepthook = mock_error

scope = 'system'
if tool == 'runuser':
    assert args[0] == '-u' and args[2:6] == ['--', 'env', '-i', 'PATH=/usr/sbin:/usr/bin:/sbin:/bin']
    scope = args[1]
    account = next(record.split(':') for record in data['accounts'].values()
                   if isinstance(record, str) and record.split(':')[0] == scope)
    uid, home = account[2], account[5]
    assert args[6:11] == [f'HOME={home}', f'USER={scope}', f'LOGNAME={scope}',
                          f'XDG_RUNTIME_DIR=/run/user/{uid}',
                          f'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus']
    assert args[11:13] == ['systemctl', '--user']
    tool, args = 'systemctl', args[13:]

if tool == 'loginctl':
    assert args == ['list-users', '--no-legend', '--no-pager']
    print(data['users'])
    sys.exit(data.get('loginctl_rc', 0))
if tool == 'getent':
    assert args[0] == 'passwd' and len(args) == 2
    record = data['accounts'].get(args[1])
    if record is None:
        sys.exit(2)
    print(record)
    sys.exit(0)
if tool == 'dpkg-query':
    assert args[:2] == ['--search', '--'] and len(args) == 3
    owner = data['owners'].get(args[2])
    if owner is None:
        sys.exit(1)
    print(owner)
    sys.exit(0)
if tool == 'systemctl':
    if args[:4] == ['show', '--property=ActiveState', '--value', '--']:
        assert scope == 'system' and args[-1].startswith('user@') and args[-1].endswith('.service')
        uid = args[-1].removeprefix('user@').removesuffix('.service')
        if uid in data.get('manager_failures', []):
            sys.exit(1)
        print('active' if uid in data['active_managers'] else 'inactive')
        sys.exit(0)
    assert args[0] in ('show', 'stop', 'disable', 'cat')
    unit = args[-1]
    if [scope, args[0], unit] in data.get('failures', []):
        sys.exit(1)
    if args[0] == 'cat':
        assert args[1:-1] == ['--no-pager', '--']
        print(data.get('contents', {}).get(scope, {}).get(unit, ''))
    elif args[0] == 'show':
        assert args[1:-1] == ['--property=FragmentPath', '--property=DropInPaths', '--']
        custom = data.get('properties', {}).get(scope, {}).get(unit)
        if custom is not None:
            print(custom)
        else:
            fragment = data['fragments'].get(scope, {}).get(unit, '')
            dropins = data.get('dropins', {}).get(scope, {}).get(unit, '')
            print(f'FragmentPath={fragment}\nDropInPaths={dropins}')
    else:
        assert args[1:-1] == ['--']
    sys.exit(0)
raise AssertionError(f'unexpected tool: {tool}')
'''


def fixture():
    fragments = {
        'system': {unit: f'/usr/lib/systemd/system/{unit}' for unit in SYSTEM_UNITS},
        'alice': {unit: f'/usr/lib/systemd/user/{unit}' for unit in USER_UNITS},
        'bob': {unit: f'/usr/lib/systemd/user/{unit}' for unit in USER_UNITS},
    }
    return {
        'users': '1000 alice\n1001 bob',
        'accounts': {
            '1000': 'alice:x:1000:1000:Alice:/home/alice:/bin/bash',
            '1001': 'bob:x:1001:1001:Bob:/home/bob:/bin/bash',
        },
        'active_managers': ['1000', '1001'],
        'fragments': fragments,
        'owners': {path: f'shai-installer: {path}'
                   for units in fragments.values() for path in units.values()},
    }


class PackageLifecycle(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.bin = self.directory / 'bin'
        self.bin.mkdir()
        mock = self.bin / 'mock-tool'
        mock.write_text(f'#!{sys.executable}\n{FAKE_TOOL}')
        mock.chmod(0o755)
        for tool in ('systemctl', 'runuser', 'loginctl', 'getent', 'dpkg-query'):
            (self.bin / tool).symlink_to(mock)
        self.data = fixture()

    def run_prerm(self, *args):
        config = self.directory / 'fixture.json'
        config.write_text(json.dumps(self.data))
        log = self.directory / 'commands.jsonl'
        log.write_text('')
        env = {
            'PATH': str(self.bin), 'LC_ALL': 'C',
            'LIFECYCLE_FIXTURE': str(config), 'LIFECYCLE_LOG': str(log),
            'HOME': str(self.directory),
            'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/do-not-use',
            'XDG_RUNTIME_DIR': '/do-not-use', 'PYTHONPATH': '/do-not-use',
        }
        result = subprocess.run(['/bin/bash', str(PRERM), *args], env=env,
                                text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        calls = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertFalse(any(call[0] == 'MOCK_ERROR' for call in calls), calls)
        return calls

    def actions(self, calls):
        actions = []
        for call in calls:
            if call[0] == 'systemctl' and call[1] in ('stop', 'disable'):
                actions.append(('system', call[1], call[-1]))
            elif call[0] == 'runuser':
                args = call[call.index('--user') + 1:]
                if args[0] in ('stop', 'disable'):
                    actions.append((call[2], args[0], args[-1]))
        return actions

    def expected_actions(self):
        return [(scope, verb, unit)
                for scope, units in (('system', SYSTEM_UNITS),
                                     ('alice', USER_UNITS), ('bob', USER_UNITS))
                for unit in units for verb in ('stop', 'disable')]

    def test_remove_cleans_exact_packaged_units_for_all_managers(self):
        calls = self.run_prerm('remove')
        self.assertEqual(self.actions(calls), self.expected_actions())
        queries = [call[-1] for call in calls if call[0] == 'dpkg-query']
        self.assertEqual(len(queries), 11)

    def test_deconfigure_cleans_units(self):
        self.assertEqual(self.actions(self.run_prerm('deconfigure', 'in-favour', 'replacement', '1')),
                         self.expected_actions())

    def test_upgrade_failure_recovery_and_unknown_actions_are_noops(self):
        for args in ((), ('upgrade', '99'), ('failed-upgrade', '99'),
                     ('abort-upgrade',), ('purge',), ('configure',), ('anything',)):
            with self.subTest(args=args):
                self.assertEqual(self.run_prerm(*args), [])

    def test_local_replacements_masks_aliases_and_foreign_units_are_skipped(self):
        unit = USER_UNITS[-1]
        for fragment in (f'/home/alice/.config/systemd/user/{unit}',
                         f'/etc/systemd/user/{unit}', f'/run/systemd/user/{unit}',
                         '/dev/null', '', '/usr/lib/systemd/user/other.service',
                         f'/usr/lib/systemd/user/../user/{unit}'):
            with self.subTest(fragment=fragment):
                self.data['fragments']['alice'][unit] = fragment
                actions = self.actions(self.run_prerm('remove'))
                self.assertNotIn(('alice', 'stop', unit), actions)
                self.assertIn(('bob', 'stop', unit), actions)

    def test_system_replacement_is_skipped(self):
        unit = SYSTEM_UNITS[-1]
        self.data['fragments']['system'][unit] = f'/etc/systemd/system/{unit}'
        self.assertNotIn(('system', 'stop', unit), self.actions(self.run_prerm('remove')))

    def test_dropins_in_either_scope_are_preserved(self):
        for scope, unit in (('system', SYSTEM_UNITS[-1]), ('alice', USER_UNITS[0])):
            with self.subTest(scope=scope):
                self.data['dropins'] = {scope: {unit: '/etc/systemd/override.conf'}}
                actions = self.actions(self.run_prerm('remove'))
                self.assertNotIn((scope, 'stop', unit), actions)
                self.assertNotIn((scope, 'disable', unit), actions)

    def model_limits(self, contents=None, names=('CPUQuota', 'MemoryHighScale', 'MemoryMaxScale')):
        unit = USER_UNITS[-1]
        directory = f'/run/user/1000/systemd/user.control/{unit}.d'
        paths = [f'{directory}/50-{name}.conf' for name in names]
        self.data['dropins'] = {'alice': {unit: ' '.join(paths)}}
        body = f'# /usr/lib/systemd/user/{unit}\n[Service]\nExecStart=/usr/bin/shai-aia-server\n'
        for path, directive in zip(paths, ('CPUQuota=1200%', 'MemoryHigh=20%', 'MemoryMax=25%')):
            body += f'\n# {path}\n# Automatically generated\n[Service]\n{directive}\n'
        self.data['contents'] = {'alice': {unit: body if contents is None else contents}}
        return body

    def test_aia_generated_runtime_resource_limits_do_not_prevent_cleanup(self):
        for names in (('CPUQuota', 'MemoryHighScale', 'MemoryMaxScale'),
                      ('CPUQuotaPerSecUSec', 'MemoryHigh', 'MemoryMax')):
            with self.subTest(names=names):
                self.model_limits(names=names)
                self.assertEqual(self.actions(self.run_prerm('remove')), self.expected_actions())

    def test_runtime_limits_with_custom_behavior_or_unsafe_paths_are_skipped(self):
        for addition in ('ExecStart=/home/alice/personal', 'ExecStop=/home/alice/personal',
                         '[Unit]\nRequires=personal.service', 'Environment=PERSONAL=1',
                         'CPUQuota=20%\\', '# comment\\'):
            with self.subTest(addition=addition):
                body = self.model_limits()
                self.data['contents']['alice'][USER_UNITS[-1]] = body + addition
                self.assertNotIn(('alice', 'stop', USER_UNITS[-1]), self.actions(self.run_prerm('remove')))
        for path in ('/run/user/1001/systemd/user.control/shai-aia-model.service.d/50-MemoryMax.conf',
                     '/run/user/1000/systemd/user.control/shai-aia-model.service.d/../50-MemoryMax.conf',
                     '/run/user/1000/systemd/user.control/shai-aia-model.service.d/50-ExecStart.conf'):
            with self.subTest(path=path):
                self.model_limits()
                self.data['dropins']['alice'][USER_UNITS[-1]] = path
                self.data['contents']['alice'][USER_UNITS[-1]] = f'# {path}\n[Service]\nMemoryMax=25%\n'
                self.assertNotIn(('alice', 'stop', USER_UNITS[-1]), self.actions(self.run_prerm('remove')))
        self.model_limits('')
        self.assertNotIn(('alice', 'stop', USER_UNITS[-1]), self.actions(self.run_prerm('remove')))
        self.model_limits()
        self.data['failures'] = [['alice', 'cat', USER_UNITS[-1]]]
        self.assertNotIn(('alice', 'stop', USER_UNITS[-1]), self.actions(self.run_prerm('remove')))

    def test_package_ownership_must_match_exactly(self):
        unit = USER_UNITS[0]
        path = self.data['fragments']['alice'][unit]
        for owner in (None, f'other-package: {path}', f'not-shai-installer: {path}',
                      f'shai-installer: {path}\nother-package: {path}',
                      f'local diversion from: {path}\nshai-installer: {path}'):
            with self.subTest(owner=owner):
                self.data['owners'][path] = owner
                actions = self.actions(self.run_prerm('remove'))
                self.assertNotIn(('alice', 'stop', unit), actions)
                self.assertNotIn(('bob', 'disable', unit), actions)

    def test_merged_usr_and_arch_qualified_ownership(self):
        for scope, units in self.data['fragments'].items():
            for unit, path in units.items():
                units[unit] = path.removeprefix('/usr')
                self.data['owners'][path] = f'shai-installer:amd64: {path}'
        self.assertEqual(self.actions(self.run_prerm('remove')), self.expected_actions())

    def test_missing_package_ownership_prevents_all_stop_and_disable_actions(self):
        self.data['owners'] = {}
        self.assertEqual(self.actions(self.run_prerm('remove')), [])

    def test_missing_malformed_or_repeated_properties_fail_closed(self):
        unit = USER_UNITS[0]
        path = self.data['fragments']['alice'][unit]
        for properties in ('', f'FragmentPath={path}', 'DropInPaths=',
                           f'FragmentPath={path}\nDropInPaths=\nFragmentPath={path}',
                           f'FragmentPath={path}\nDropInPaths=\nDropInPaths=',
                           f'FragmentPath={path}\nDropInPaths=\nUnknown=1'):
            with self.subTest(properties=properties):
                self.data['properties'] = {'alice': {unit: properties}}
                self.assertNotIn(('alice', 'stop', unit), self.actions(self.run_prerm('remove')))

    def test_inactive_and_disappeared_managers_are_not_started(self):
        self.data['active_managers'] = ['1001']
        calls = self.run_prerm('remove')
        self.assertFalse(any(call[:3] == ['runuser', '-u', 'alice'] for call in calls))
        self.assertIn(('bob', 'stop', USER_UNITS[0]), self.actions(calls))
        self.data['active_managers'] = ['1000', '1001']
        self.data['manager_failures'] = ['1000']
        self.assertFalse(any(call[:3] == ['runuser', '-u', 'alice']
                             for call in self.run_prerm('remove')))
        self.data['manager_failures'] = []
        self.data['failures'] = [['alice', 'show', unit] for unit in USER_UNITS]
        self.assertFalse(any(scope == 'alice' for scope, _, _ in self.actions(self.run_prerm('remove'))))

    def test_logind_unavailable_or_empty_is_best_effort(self):
        for users, rc in (('', 0), ('1000 alice', 1)):
            with self.subTest(users=users, rc=rc):
                self.data.update(users=users, loginctl_rc=rc)
                calls = self.run_prerm('remove')
                self.assertEqual(self.actions(calls), self.expected_actions()[:6])
                self.assertFalse(any(call[0] == 'runuser' for call in calls))

    def test_invalid_uid_and_name_records_never_reach_account_or_user_commands(self):
        for record in ('-1 alice', '+1000 alice', '01000 alice', '1e3 alice',
                       '4294967295 alice', '999999999999999999999 alice',
                       '1000 -alice', '1000 alice;id', '1000 alice@host', '1000',
                       '1000 alice/root', 'bad alice'):
            with self.subTest(record=record):
                self.data['users'] = record
                calls = self.run_prerm('remove')
                self.assertFalse(any(call[0] in ('getent', 'runuser') for call in calls))

    def test_nss_identity_mismatch_or_unsafe_home_is_skipped(self):
        for record in (None, 'mallory:x:1000:1000::/home/alice:/bin/bash',
                       'alice:x:1001:1000::/home/alice:/bin/bash',
                       'alice:x:1000:1000::relative:/bin/bash',
                       'alice:x:1000:1000::/home/alice:/bin/bash:extra',
                       'alice:x:1000:1000::/home/alice:/bin/bash\ninjected'):
            with self.subTest(record=record):
                self.data['accounts']['1000'] = record
                calls = self.run_prerm('remove')
                self.assertFalse(any(call[:3] == ['runuser', '-u', 'alice'] for call in calls))
                self.assertIn(('bob', 'stop', USER_UNITS[0]), self.actions(calls))

    def test_duplicate_users_and_optional_logind_columns(self):
        self.data['users'] = '1000 alice yes active\n1000 alice\n1001 bob no active'
        self.assertEqual(self.actions(self.run_prerm('remove')), self.expected_actions())

    def test_root_user_manager_has_same_identity_checks(self):
        self.data['users'] = '0 root'
        self.data['accounts']['0'] = 'root:x:0:0:root:/root:/bin/bash'
        self.data['active_managers'] = ['0']
        self.data['fragments']['root'] = copy.deepcopy(self.data['fragments']['alice'])
        calls = self.run_prerm('remove')
        self.assertEqual(self.actions(calls)[6:],
                         [('root', verb, unit) for unit in USER_UNITS for verb in ('stop', 'disable')])

    def test_individual_stop_disable_and_query_failures_do_not_abort_other_units(self):
        for scope, verb, unit in (('system', 'stop', SYSTEM_UNITS[0]),
                                  ('alice', 'disable', USER_UNITS[0]),
                                  ('alice', 'show', USER_UNITS[0])):
            with self.subTest(scope=scope, verb=verb):
                self.data['failures'] = [[scope, verb, unit]]
                actions = self.actions(self.run_prerm('remove'))
                self.assertIn(('bob', 'disable', USER_UNITS[-1]), actions)
                if verb != 'show':
                    self.assertEqual(actions, self.expected_actions())
                else:
                    self.assertNotIn((scope, 'stop', unit), actions)

    def test_missing_tools_cannot_fall_through_to_host_path(self):
        for tool in ('systemctl', 'loginctl', 'getent', 'runuser', 'dpkg-query'):
            with self.subTest(tool=tool):
                path = self.bin / tool
                path.unlink()
                try:
                    self.run_prerm('remove')
                finally:
                    path.symlink_to(self.bin / 'mock-tool')

    def test_personal_configuration_models_memory_and_units_are_unchanged(self):
        self.data['accounts']['1000'] = f'alice:x:1000:1000:Alice:{self.directory}:/bin/bash'
        paths = ('.config/shai/aia.json', '.local/share/shai/models/model.gguf',
                 '.local/share/shai/memory/notes.json', '.local/state/shai/aia/server-api-key',
                 '.config/systemd/user/shai-aia-model.service')
        for relative in paths:
            path = self.directory / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('personal data, preserve exactly\n')
        before = {path: (path.read_bytes(), path.stat().st_mode, path.stat().st_mtime_ns)
                  for path in (self.directory / relative for relative in paths)}
        self.run_prerm('remove')
        self.assertEqual(before, {path: (path.read_bytes(), path.stat().st_mode, path.stat().st_mtime_ns)
                                  for path in before})
        body = PRERM.read_text()
        self.assertIsNone(re.search(r'\b(rm|unlink|kill|killall|pkill|find|eval)\b', body))
        self.assertNotIn('--global', body)
        self.assertNotIn('dbus-run-session', body)

    def test_build_installs_executable_prerm_and_shell_syntax_is_valid(self):
        line = 'install -m 0755 "$ROOT/installer/debian/prerm" "$STAGE/DEBIAN/prerm"'
        self.assertEqual((ROOT / 'installer/build.sh').read_text().splitlines().count(line), 1)
        subprocess.run(['/bin/bash', '-n', str(PRERM)], check=True, timeout=5)


if __name__ == '__main__':
    unittest.main()
