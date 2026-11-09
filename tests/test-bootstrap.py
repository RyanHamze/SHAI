#!/usr/bin/env python3
"""Rootless bootstrap tests: mocked downloads, gh, sudo and package tools."""
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'install.sh'
SOURCE = SCRIPT.read_text()
VERSION = re.search(r'^readonly SHAI_VERSION=(\S+)$', SOURCE, re.M).group(1)
PACKAGE = f'shai-installer_{VERSION}_amd64.deb'
CLI_PREFIX = 'gh_2.103.3_linux_amd64'
BASH = shutil.which('bash')
FLAGS = '--bundle --repo --signer-workflow --source-ref --source-digest --hostname'
MOCK = r'''
import json
import os
from pathlib import Path
import shutil
import signal
import sys
name, args = Path(sys.argv[0]).name, sys.argv[1:]
portable = name == 'gh' and Path(sys.argv[0]).parent != Path(os.environ['MOCK_BIN'])
event = {'command': name, 'args': args, 'uid': os.geteuid(), 'portable': portable}
if name == 'curl':
    output = Path(args[args.index('--output') + 1])
    event['work_mode'] = output.parent.stat().st_mode & 0o777
if name == 'gh':
    for key in ('HOME', 'GH_CONFIG_DIR', 'XDG_CACHE_HOME', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'TMPDIR'):
        event[key] = os.environ[key]
    event['credentials'] = any(os.environ.get(key) for key in (
        'GH_TOKEN', 'GITHUB_TOKEN', 'GH_ENTERPRISE_TOKEN', 'GITHUB_ENTERPRISE_TOKEN'))
    if portable:
        event['binary_mode'] = Path(sys.argv[0]).stat().st_mode & 0o777
        event['extra_extracted'] = (Path(sys.argv[0]).parent / 'LICENSE').exists()
with open(os.environ['MOCK_LOG'], 'a') as log:
    log.write(json.dumps(event) + '\n')
if name == 'curl':
    url = args[-1]
    kind = 'cli' if url.endswith('.tar.gz') else 'bundle' if url.endswith('.jsonl') else 'package'
    source = Path(os.environ['MOCK_' + kind.upper()])
    if kind == 'package' and os.environ.get('MOCK_SHAPE') == 'symlink':
        output.symlink_to(source)
    else:
        shutil.copyfile(source, output)
    if kind == 'package' and os.environ.get('MOCK_SHAPE') in ('empty', 'oversize'):
        with output.open('wb') as stream:
            stream.truncate(67108865 if os.environ['MOCK_SHAPE'] == 'oversize' else 0)
    if os.environ.get('MOCK_INTERRUPT') == kind:
        os.kill(os.getppid(), signal.SIGTERM)
    sys.exit(22 if os.environ.get('MOCK_DOWNLOAD_FAIL') == kind else 0)
if name == 'gh':
    if args == ['attestation', 'verify', '--help']:
        if not portable and os.environ.get('MOCK_OLD_GH'):
            sys.exit(1)
        print(os.environ['MOCK_FLAGS'])
        sys.exit(0)
    if args[:2] != ['attestation', 'verify'] or '--bundle' not in args:
        sys.exit(95)
    cache = Path(os.environ['HOME']) / '.sigstore'
    cache.mkdir(exist_ok=True)
    (cache / 'temporary-trust-cache').write_text('fixture')
    sys.exit(1 if os.environ.get('MOCK_ATTEST_FAIL') else 0)
if name == 'dpkg':
    print(os.environ.get('MOCK_HOST_ARCH', 'amd64'))
    sys.exit(0)
if name == 'dpkg-deb':
    if os.environ.get('MOCK_DEB_FAIL'):
        sys.exit(2)
    field = args[-1]
    print(os.environ.get('MOCK_DEB_' + field.upper(), {
        'Package': 'shai-installer', 'Version': os.environ['MOCK_VERSION'], 'Architecture': 'amd64'}[field]))
    sys.exit(0)
if name == 'sudo':
    Path(os.environ['MOCK_PRIVILEGE']).touch()
    sys.exit(1 if os.environ.get('MOCK_SUDO_FAIL') else 0)
if name == 'shai-setup':
    sys.exit(0)
sys.exit(96)
'''


class BootstrapShape(unittest.TestCase):
    def test_help_and_shell_syntax(self):
        subprocess.run([BASH, '-n', str(SCRIPT)], check=True)
        result = subprocess.run([BASH, str(SCRIPT), '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('--verify-only', result.stdout)

    def test_unknown_options_rejected(self):
        for args in (['--unknown'], ['--verify-only', 'extra']):
            self.assertNotEqual(subprocess.run([BASH, str(SCRIPT), *args], capture_output=True).returncode, 0)

    def test_safe_shape(self):
        self.assertEqual(VERSION, '0.14.0')
        self.assertIn('https://github.com/RyanHamze/SHAI/releases/download/v', SOURCE)
        self.assertIn('readonly GH_VERSION=2.103.3', SOURCE)
        self.assertIn('readonly GH_SHA256=4c806978ffce1cec70853302a56d70ac6da4f19bae7adca4e1a8ab00633dd91d', SOURCE)
        self.assertIn("curl -q --fail", SOURCE)
        self.assertIn("--proto '=https' --proto-redir '=https'", SOURCE)
        self.assertIn('--max-filesize', SOURCE)
        self.assertIn('chmod 0700 -- "$work"', SOURCE)
        self.assertIn('target.chmod(0o700)', SOURCE)
        for forbidden in ('extractall', ' -4 ', 'ForceIPv4', 'gh auth', 'actions/artifacts',
                          '--location-trusted', '--apply-plan'):
            self.assertNotIn(forbidden, SOURCE)
        for gate in ('sha256sum --check', 'if ! run_gh attestation verify', 'dpkg-deb --field'):
            self.assertLess(SOURCE.index(gate), SOURCE.index('sudo apt-get'))
        self.assertIn('sudo apt-get --no-remove --no-install-recommends', SOURCE)
        self.assertTrue(SOURCE.rstrip().endswith('/usr/bin/shai-setup'))


@unittest.skipIf(os.geteuid() == 0, 'Bootstrap deliberately refuses root')
class BootstrapRuntime(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix='shai bootstrap ')
        self.addCleanup(folder.cleanup)
        self.directory = Path(folder.name)
        self.binary = self.directory / 'bin'
        self.binary.mkdir()
        self.scratch = self.directory / 'temporary'
        self.scratch.mkdir()
        (self.scratch / 'keep-me').write_text('keep')
        self.home = self.directory / 'original-home'
        self.home.mkdir()
        (self.home / 'keep-me').write_text('keep')
        self.log = self.directory / 'calls.jsonl'
        self.marker = self.directory / 'privilege-called'
        self.payload = self.directory / 'fixture.deb'
        self.payload.write_bytes(b'fixture payload; not an installable package\n')
        self.bundle = self.directory / 'fixture.intoto.jsonl'
        self.bundle.write_text('{"fixture": true}\n')
        self.archive = self.directory / 'fixture.tar.gz'
        self.mock = ('#!' + sys.executable + '\n' + MOCK).encode()
        for name in ('curl', 'gh', 'sudo', 'apt-get', 'dpkg', 'dpkg-deb', 'shai-setup'):
            path = self.binary / name
            path.write_bytes(self.mock)
            path.chmod(0o755)
        # Closed PATH prevents accidentally invoking real network or package tools.
        for name in ('python3', 'sha256sum', 'mktemp', 'chmod', 'mkdir', 'stat', 'rm'):
            (self.binary / name).symlink_to(shutil.which(name))
        self.os_release = self.directory / 'os-release'
        self.os_release.write_text('ID=ubuntu\nVERSION_ID=26.04\n')
        self.script = self.directory / 'install.sh'
        self.make_archive()
        self.write_script()
        self.env = {k: v for k, v in os.environ.items()
                    if k not in ('DISPLAY', 'WAYLAND_DISPLAY', 'BASH_ENV', 'ENV', 'SHELLOPTS', 'BASHOPTS')}
        self.env.update({
            'PATH': str(self.binary), 'HOME': str(self.home), 'TMPDIR': str(self.scratch),
            'MOCK_BIN': str(self.binary), 'MOCK_LOG': str(self.log),
            'MOCK_PRIVILEGE': str(self.marker), 'MOCK_PACKAGE': str(self.payload),
            'MOCK_CLI': str(self.archive), 'MOCK_BUNDLE': str(self.bundle),
            'MOCK_VERSION': VERSION, 'MOCK_FLAGS': FLAGS,
        })

    def make_archive(self, members=None):
        if members is None:
            members = [(CLI_PREFIX + '/LICENSE', b'ignored', None),
                       (CLI_PREFIX + '/bin/gh', self.mock, None)]
        with tarfile.open(self.archive, 'w:gz') as archive:
            for name, data, kind in members:
                item = tarfile.TarInfo(name)
                if kind is None:
                    item.size = len(data)
                else:
                    item.type, item.linkname = kind, 'outside'
                archive.addfile(item, io.BytesIO(data) if kind is None else None)

    def write_script(self, package_hash=None, cli_hash=None, commit='1' * 40):
        # Fixture-only pins/platform/launcher. Production has no pin override.
        source = re.sub(r'^readonly SHA256=.*$', 'readonly SHA256=' + (
            package_hash or hashlib.sha256(self.payload.read_bytes()).hexdigest()), SOURCE, flags=re.M)
        source = re.sub(r'^readonly GH_SHA256=.*$', 'readonly GH_SHA256=' + (
            cli_hash or hashlib.sha256(self.archive.read_bytes()).hexdigest()), source, flags=re.M)
        source = re.sub(r'^readonly SOURCE_COMMIT=.*$', 'readonly SOURCE_COMMIT=' + commit, source, flags=re.M)
        source = source.replace('source /etc/os-release', 'source ' + shlex.quote(str(self.os_release)))
        source = source.replace('/usr/bin/shai-setup', shlex.quote(str(self.binary / 'shai-setup')))
        self.script.write_text(source)

    def run_bootstrap(self, verify_only=True, **environment):
        self.log.unlink(missing_ok=True)
        self.marker.unlink(missing_ok=True)
        result = subprocess.run([BASH, str(self.script), *(['--verify-only'] if verify_only else [])],
                                capture_output=True, text=True, timeout=15, env={**self.env, **environment})
        self.events = [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []
        for folder in (self.scratch, self.home):
            self.assertEqual(sorted(p.name for p in folder.iterdir()), ['keep-me'])
            self.assertEqual((folder / 'keep-me').read_text(), 'keep')
        for event in self.events:
            self.assertEqual(event['uid'], os.geteuid())
            if event['command'] == 'curl':
                self.assertEqual(event['work_mode'], 0o700)
                args = event['args']
                self.assertEqual(args[0], '-q')
                for flag in ('--proto', '--proto-redir'):
                    self.assertEqual(args[args.index(flag) + 1], '=https')
                self.assertIn('--max-filesize', args)
                self.assertNotIn('-4', args)
            if event['command'] == 'gh':
                self.assertFalse(event['credentials'])
                for key in ('HOME', 'GH_CONFIG_DIR', 'XDG_CACHE_HOME', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'TMPDIR'):
                    self.assertTrue(Path(event[key]).is_relative_to(self.scratch), event)
                if event['portable']:
                    self.assertEqual(event['binary_mode'], 0o700)
                    self.assertFalse(event['extra_extracted'])
        return result

    def assert_no_privilege(self):
        self.assertFalse(self.marker.exists())
        self.assertFalse(any(e['command'] in ('sudo', 'apt-get', 'shai-setup') for e in self.events))

    def assert_policy(self):
        verified = [e for e in self.events if e['command'] == 'gh' and '--help' not in e['args']]
        self.assertEqual(len(verified), 1)
        args = verified[0]['args']
        for flag, value in (
            ('--repo', 'RyanHamze/SHAI'),
            ('--signer-workflow', 'RyanHamze/SHAI/.github/workflows/build-attest-release.yml'),
            ('--source-ref', 'refs/tags/v' + VERSION), ('--source-digest', '1' * 40),
            ('--hostname', 'github.com')):
            self.assertEqual(args[args.index(flag) + 1], value)
        self.assertTrue(args[args.index('--bundle') + 1].endswith(PACKAGE + '.intoto.jsonl'))

    def test_verify_only_existing_cli(self):
        for name in ('sudo', 'apt-get', 'shai-setup'):
            (self.binary / name).unlink()
        result = self.run_bootstrap()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Verification complete', result.stdout)
        self.assert_no_privilege()
        self.assert_policy()
        urls = [e['args'][-1] for e in self.events if e['command'] == 'curl']
        base = f'https://github.com/RyanHamze/SHAI/releases/download/v{VERSION}/{PACKAGE}'
        self.assertEqual(urls, [base, base + '.intoto.jsonl'])

    def test_portable_cli_missing_old_or_incomplete(self):
        for mode in ('missing', 'old', 'incomplete'):
            with self.subTest(mode=mode):
                gh = self.binary / 'gh'
                gh.unlink(missing_ok=True)
                if mode != 'missing':
                    gh.write_bytes(self.mock)
                    gh.chmod(0o755)
                if mode == 'incomplete':
                    gh.write_bytes(self.mock.replace(b"print(os.environ['MOCK_FLAGS'])",
                        b"print(os.environ['MOCK_FLAGS'].replace('--source-ref', '--unsupported'))"))
                result = self.run_bootstrap(**({'MOCK_OLD_GH': '1'} if mode == 'old' else {}))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assert_no_privilege()
                self.assert_policy()
                self.assertTrue(any(e['portable'] for e in self.events))
                self.assertIn('https://github.com/cli/cli/releases/download/v2.103.3/' + CLI_PREFIX + '.tar.gz',
                              [e['args'][-1] for e in self.events if e['command'] == 'curl'])

    def test_corrupt_payload_no_sudo(self):
        self.payload.write_bytes(b'corrupted payload')
        result = self.run_bootstrap(False, DISPLAY=':fixture')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('FAILED', result.stdout)
        self.assert_no_privilege()
        self.assertFalse(any(e['command'] == 'gh' for e in self.events))

    def test_corrupt_cli_never_executed(self):
        self.archive.write_bytes(b'corrupt archive')
        result = self.run_bootstrap(MOCK_OLD_GH='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('FAILED', result.stdout)
        self.assert_no_privilege()
        self.assertFalse(any(e['portable'] for e in self.events))

    def test_attestation_failure_no_identity_or_privilege(self):
        result = self.run_bootstrap(False, DISPLAY=':fixture', MOCK_ATTEST_FAIL='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Attestation verification failed', result.stderr)
        self.assert_no_privilege()
        self.assertFalse(any(e['command'] == 'dpkg-deb' for e in self.events))

    def test_wrong_deb_identity_no_privilege(self):
        for env in ({'MOCK_DEB_PACKAGE': 'wrong'}, {'MOCK_DEB_VERSION': '0.13.1'},
                    {'MOCK_DEB_ARCHITECTURE': 'all'}, {'MOCK_DEB_PACKAGE': 'shai-installer\nextra'},
                    {'MOCK_DEB_FAIL': '1'}):
            with self.subTest(env=env):
                result = self.run_bootstrap(False, DISPLAY=':fixture', **env)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('DEB package identity', result.stderr)
                self.assert_no_privilege()

    def test_download_failures_clean_up(self):
        for kind in ('package', 'cli', 'bundle'):
            with self.subTest(kind=kind):
                result = self.run_bootstrap(MOCK_OLD_GH='1', MOCK_DOWNLOAD_FAIL=kind)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Download failed', result.stderr)
                self.assert_no_privilege()

    def test_download_shape_and_size(self):
        for shape in ('empty', 'symlink', 'oversize'):
            with self.subTest(shape=shape):
                result = self.run_bootstrap(MOCK_SHAPE=shape)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Unexpected download type or size', result.stderr)
                self.assert_no_privilege()

    def test_unsafe_cli_archive_shape(self):
        binary = (CLI_PREFIX + '/bin/gh', self.mock, None)
        cases = [[('../escape', b'x', None), binary], [('/absolute', b'x', None), binary],
                 [binary, binary], [(CLI_PREFIX + '/LICENSE', b'missing binary', None)],
                 [(CLI_PREFIX + '/bin/gh', b'', None)],
                 [(CLI_PREFIX + '/../escape', b'x', None), binary]]
        for kind in (tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.DIRTYPE, tarfile.FIFOTYPE):
            cases.append([(CLI_PREFIX + '/bin/gh', b'', kind)])
        for members in cases:
            with self.subTest(members=[m[0] for m in members]):
                self.make_archive(members)
                self.write_script()
                result = self.run_bootstrap(MOCK_OLD_GH='1')
                self.assertNotEqual(result.returncode, 0)
                self.assert_no_privilege()
                self.assertFalse(any(e['portable'] for e in self.events))

    def test_unfinalized_pins_stop_before_download(self):
        for kwargs in ({'package_hash': '0' * 64}, {'commit': '0' * 40}):
            with self.subTest(kwargs=kwargs):
                self.write_script(**kwargs)
                result = self.run_bootstrap()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Release pins are not finalized', result.stderr)
                self.assert_no_privilege()
                self.assertFalse(any(e['command'] == 'curl' for e in self.events))

    def test_cli_archive_size_and_entry_caps(self):
        item = tarfile.TarInfo(CLI_PREFIX + '/bin/gh')
        item.size = 67108865
        self.archive.write_bytes(gzip.compress(item.tobuf() + b'\0' * 1024))
        self.write_script()
        result = self.run_bootstrap(MOCK_OLD_GH='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Unsafe GitHub CLI archive shape', result.stderr)
        self.assert_no_privilege()
        self.assertFalse(any(e['portable'] for e in self.events))
        self.make_archive([(CLI_PREFIX + f'/entry-{index}', b'', None) for index in range(1025)])
        self.write_script()
        result = self.run_bootstrap(MOCK_OLD_GH='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Unsafe GitHub CLI archive shape', result.stderr)
        self.assert_no_privilege()

    def test_portable_cli_missing_required_flags_rejected(self):
        result = self.run_bootstrap(MOCK_FLAGS='--bundle --repo')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('lacks the required attestation verification flags', result.stderr)
        self.assert_no_privilege()
        self.assertFalse(any(e['command'] == 'dpkg-deb' for e in self.events))

    def test_install_then_rootless_setup(self):
        result = self.run_bootstrap(False, DISPLAY=':fixture')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.marker.exists())
        self.assert_policy()
        names = [e['command'] for e in self.events]
        sudo = names.index('sudo')
        self.assertGreater(sudo, max(i for i, name in enumerate(names) if name == 'dpkg-deb'))
        self.assertEqual(names[-2:], ['sudo', 'shai-setup'])
        self.assertEqual(self.events[sudo]['args'][:5],
                         ['apt-get', '--no-remove', '--no-install-recommends', '-y', 'install'])
        self.assertTrue(self.events[sudo]['args'][-1].endswith('/' + PACKAGE))

    def test_apt_failure_does_not_launch_setup(self):
        result = self.run_bootstrap(False, DISPLAY=':fixture', MOCK_SUDO_FAIL='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(e['command'] == 'shai-setup' for e in self.events))

    def test_signal_cleanup(self):
        result = self.run_bootstrap(MOCK_INTERRUPT='package')
        self.assertEqual(result.returncode, 143)
        self.assert_no_privilege()

    def test_credentials_unused(self):
        # Synthetic markers only, never actual secret material.
        result = self.run_bootstrap(GH_TOKEN='fixture-only', GITHUB_TOKEN='fixture-only',
                                    GH_ENTERPRISE_TOKEN='fixture-only', GITHUB_ENTERPRISE_TOKEN='fixture-only')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('fixture-only', result.stdout + result.stderr)
        self.assert_no_privilege()

    def test_wrong_arch_and_no_desktop_stop_before_download(self):
        for env in ({'MOCK_HOST_ARCH': 'arm64'}, {}):
            result = self.run_bootstrap(False, **env)
            self.assertNotEqual(result.returncode, 0)
            self.assert_no_privilege()
            self.assertFalse(any(e['command'] == 'curl' for e in self.events))


if __name__ == '__main__':
    unittest.main()
