#!/usr/bin/env python3
"""Offline lifecycle tests with isolated storage and no package/system changes."""
import importlib.machinery
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "installer/src/shai-voice-manage"
voice = importlib.machinery.SourceFileLoader("voice_test", str(SOURCE)).load_module()

class VoiceLifecycle(unittest.TestCase):
    def test_managed_python_lifecycle(self):
        with tempfile.TemporaryDirectory() as folder:
            voice.ROOT = Path(folder)
            commands = []
            def fake_run(args):
                commands.append(args)
                if args[1:3] == ["-m", "venv"]:
                    (voice.ROOT / "wyoming/venv").mkdir(parents=True, exist_ok=True)
            with patch.object(voice, "run", fake_run), patch.object(voice.subprocess, "run") as subprocess_run:
                subprocess_run.return_value.returncode = 0
                with patch.object(sys, "argv", ["voice", "install", "wyoming"]):
                    voice.main()
                self.assertTrue((voice.ROOT / "wyoming/installed.json").is_file())
                pip_install = next(x for x in commands if "--only-binary=:all:" in x)
                self.assertIn(voice.IPV4_PIP, pip_install)
                self.assertIn("wyoming==1.11.0", pip_install)
                with patch.object(sys, "argv", ["voice", "remove", "wyoming"]):
                    voice.main()
                self.assertFalse((voice.ROOT / "wyoming/installed.json").exists())
                with patch.object(sys, "argv", ["voice", "remove", "piper"]):
                    with self.assertRaises(SystemExit):
                        voice.main()

if __name__ == "__main__": unittest.main()
