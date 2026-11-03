#!/usr/bin/env python3
"""Static UI callback and syntax checks; does not claim runtime button coverage."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'installer/src'

class Wiring(unittest.TestCase):
    def test_entrypoint_syntax(self):
        for path in ROOT.iterdir():
            if path.is_file() and path.read_bytes().startswith(b'#!/usr/bin/env python3'):
                with self.subTest(script=path.name):
                    ast.parse(path.read_text(), filename=str(path))

    def test_self_signal_handlers_exist(self):
        for name in ('shai-setup', 'shai-shapp', 'shai-aia', 'shai-health'):
            tree = ast.parse((ROOT / name).read_text())
            count = 0
            for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
                methods = {node.name for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
                for node in ast.walk(cls):
                    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                            and node.func.attr == 'connect' and len(node.args) >= 2):
                        continue
                    handler = node.args[1]
                    if isinstance(handler, ast.Attribute) and isinstance(handler.value, ast.Name) and handler.value.id == 'self':
                        count += 1
                        with self.subTest(app=name, handler=handler.attr):
                            self.assertIn(handler.attr, methods)
            self.assertGreater(count, 0, name)

if __name__ == '__main__':
    unittest.main()
