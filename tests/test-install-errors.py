#!/usr/bin/env python3
"""Exercise terminal-output capture and safe catalog constraints offline."""
import importlib.machinery
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
apply = importlib.machinery.SourceFileLoader('apply_errors', str(ROOT/'installer/src/shai-shapp-apply')).load_module()

class InstallationErrors(unittest.TestCase):
    def test_subprocess_output_survives_failure(self):
        with self.assertRaises(subprocess.CalledProcessError) as error:
            apply.run([sys.executable, '-c', 'import sys; print("Release file is not valid yet", flush=True); sys.exit(100)'])
        self.assertEqual(error.exception.returncode, 100)
        self.assertIn('not valid yet', error.exception.output)

    def test_optional_catalog_and_encryption(self):
        apps=json.loads((ROOT/'installer/catalog/shapp-apps.json').read_text())['apps']
        self.assertNotIn('xscreensaver', {entry['id'] for entry in apps})
        for entry in apps:
            if entry['category']=='optional':
                self.assertTrue(entry.get('available') or entry.get('host_backend') or entry.get('container_service'),entry['id'])
        crypt=next(entry for entry in apps if entry['id']=='luks-encryption')
        self.assertEqual(crypt['packages'],['cryptsetup'])
        source=(ROOT/'installer/src/shai-source-install').read_text()
        self.assertIn('Signed-By:',source)
        self.assertNotIn('trusted=yes',source)
        self.assertNotIn('luksFormat',source)

if __name__=='__main__': unittest.main()
