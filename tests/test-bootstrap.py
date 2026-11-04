#!/usr/bin/env python3
"""Bootstrap safety checks. No network access, sudo or installation in tests."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'install.sh'

class Bootstrap(unittest.TestCase):
    def test_help_and_shell_syntax(self):
        subprocess.run(['bash', '-n', str(SCRIPT)], check=True)
        result = subprocess.run(['bash', str(SCRIPT), '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('--verify-only', result.stdout)

    def test_fixed_identity_and_safe_download(self):
        source = SCRIPT.read_text()
        self.assertIn('4535b5ee0a0d507f3969913e064cacfe7d1d902900566fad082625388a6e4c7a', source)
        self.assertIn('curl -q -4 --fail', source)
        self.assertIn('--proto-redir', source)
        self.assertNotIn('--location-trusted --', source)
        self.assertIn('rm -f -- "$work/headers"', source)
        self.assertLess(source.index('sha256sum --check'), source.index('sudo apt-get'))
        self.assertNotIn('--apply-plan', source)

    @unittest.skipIf(os.geteuid() == 0, 'runtime bootstrap rejects root by design; exercised as normal desktop user')
    def test_tampered_package_rejected_without_privilege(self):
        if 'VERSION_ID="26.04"' not in Path('/etc/os-release').read_text():
            self.skipTest('runtime candidate targets Ubuntu 26.04')
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            binary = directory / 'bin'
            binary.mkdir()
            bundle = directory / 'fixture.zip'
            with zipfile.ZipFile(bundle, 'w') as archive:
                archive.writestr('shai-installer_0.13.1_amd64.deb', 'corrupted')
                archive.writestr('SHA256SUMS', '')
                archive.writestr('SHAI-APP-CATALOG.json', '{}')
            scripts = {
                'gh': '#!/bin/sh\nprintf "test-only-token\\n"\n',
                'curl': '#!/bin/sh\nwhile [ "$#" -gt 0 ]; do if [ "$1" = -o ]; then shift; cp "$FIXTURE" "$1"; exit; fi; shift; done\nexit 1\n',
                'sudo': '#!/bin/sh\ntouch "$PRIVILEGE_MARKER"\nexit 99\n',
            }
            for name, content in scripts.items():
                path = binary / name
                path.write_text(content)
                path.chmod(0o755)
            marker = directory / 'privilege-called'
            result = subprocess.run(['bash', str(SCRIPT), '--verify-only'], text=True, capture_output=True,
                                    env={**os.environ, 'PATH': str(binary) + ':' + os.environ['PATH'],
                                         'FIXTURE': str(bundle), 'PRIVILEGE_MARKER': str(marker)})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FAILED', result.stdout)
            self.assertFalse(marker.exists())
            self.assertNotIn('test-only-token', result.stdout + result.stderr)

if __name__ == '__main__':
    unittest.main()
