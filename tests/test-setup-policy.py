#!/usr/bin/env python3
"""Privacy policy compilation and offline/Ready UI regressions."""
import ast
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Policy(unittest.TestCase):
    def test_offline_is_selected_by_default(self):
        tree = ast.parse((ROOT / 'installer/src/shai-setup').read_text())
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute) and node.func.attr == 'purpose_row'
                 and node.args and isinstance(node.args[0], ast.Constant)
                 and node.args[0].value == 'Operate the environment offline by default']
        self.assertEqual(len(calls), 1)
        self.assertIs(calls[0].args[2].value, True)

    def test_ready_has_green_markup(self):
        self.assertIn('<span foreground="#33EE33" weight="bold">Ready</span>',
                      (ROOT / 'installer/src/shai-setup').read_text())

    def test_preflight_precedes_changes(self):
        source = (ROOT / 'installer/src/shai-installer').read_text()
        self.assertLess(source.index('\nvalidate_policy_assets\n'),
                        source.index('\ncapture_prechange_state\n'))
        self.assertIn('dconf compile "$RUN_DIR/policy-preflight"', source)

    @unittest.skipUnless(shutil.which('dconf'), 'run on Ubuntu with dconf installed')
    def test_real_dconf_compiler_and_negative_control(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder) / 'source'
            directory.mkdir()
            for name in ('20-shai-web-offline', '30-shai-privacy'):
                origin = ROOT / 'installer/assets' / name
                if not origin.exists():
                    origin = ROOT / 'connectivity/etc/dconf/db/local.d' / name
                shutil.copyfile(origin, directory / name)
            target = Path(folder) / 'local'
            subprocess.run(['dconf', 'compile', str(target), str(directory)], check=True,
                           capture_output=True)
            privacy = directory / '30-shai-privacy'
            privacy.write_text(privacy.read_text().replace('@as []', '[]'))
            result = subprocess.run(['dconf', 'compile', str(target), str(directory)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('unable to infer type', result.stderr)

if __name__ == '__main__':
    unittest.main()
