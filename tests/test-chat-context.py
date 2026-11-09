#!/usr/bin/env python3
"""Source-only chat scrolling, ExifTool grounding and dock identity tests."""
import importlib.machinery
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
base = importlib.machinery.SourceFileLoader('chat_regression_loader', str(ROOT / 'tests/test-aia-health-regressions.py')).load_module()
aia = base.aia

class Chat(unittest.TestCase):
    def test_scroll_targets_bottom_after_layout(self):
        window = object.__new__(aia.AIAWindow)
        adjustment = Mock()
        adjustment.get_lower.return_value = 0
        adjustment.get_upper.return_value = 1200
        adjustment.get_page_size.return_value = 300
        window.chat_scroll = Mock()
        window.chat_scroll.get_vadjustment.return_value = adjustment
        self.assertFalse(window.scroll_chat_to_bottom())
        adjustment.set_value.assert_called_once_with(900)

    def test_render_schedules_scroll_after_new_text(self):
        window = object.__new__(aia.AIAWindow)
        window.chat_messages = [('You', 'question'), ('AIA', 'answer')]
        window.chat_view = Mock()
        with patch.object(aia.GLib, 'idle_add') as idle:
            window.render_chat()
        window.chat_view.get_buffer().set_text.assert_called_once_with('You: question\n\nAIA: answer')
        idle.assert_called_once_with(window.scroll_chat_to_bottom)

    def test_local_guide_and_safe_recipes_are_context_not_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            guide = Path(folder)
            manifest = json.loads((ROOT / 'installer/assets/exiftool/commands.json').read_text())
            manifest['recipes']['injected'] = {'argv': ['sudo', 'unsafe-command']}
            (guide / 'commands.json').write_text(json.dumps(manifest))
            with patch.object(aia, 'EXIFTOOL_GUIDE', guide), patch.object(aia.shutil, 'which', return_value='/usr/bin/exiftool'):
                context = aia.exiftool_context()
            self.assertIn(str(guide / 'README.md'), context)
            self.assertIn('remove_folder_metadata_recursive', context)
            self.assertIn('Chat currently cannot execute metadata writes', context)
            self.assertNotIn('unsafe-command', context)

    def test_missing_guide_does_not_claim_it_was_read(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(aia, 'EXIFTOOL_GUIDE', Path(folder)):
            self.assertIn('not found or invalid', aia.exiftool_context())

    def test_context_is_fed_to_actual_model_prompt(self):
        window = object.__new__(aia.AIAWindow)
        window.active_model = Mock(return_value=None)
        window.service_status = Mock(return_value=('ready', 'test'))
        window.config = {}
        with patch.object(aia, 'exiftool_context', return_value='TEST_LOCAL_GUIDE'):
            self.assertIn('TEST_LOCAL_GUIDE', window.system_prompt())

    def test_canonical_shapp_desktop_identity_and_icon(self):
        source = (ROOT / 'installer/src/shai-shapp').read_text()
        build = (ROOT / 'installer/build.sh').read_text()
        self.assertIn('APP_ID = "com.aabey.shai.Shapp"', source)
        self.assertIn("self.set_icon_name('shai-deploy')", source)
        self.assertIn('GLib.set_prgname(APP_ID)', source)
        self.assertIn('com.aabey.shai.Shapp.desktop', build)
        self.assertIn('Icon=shai-deploy', (ROOT / 'installer/share/applications/shai-shapp.desktop').read_text())

if __name__ == '__main__':
    unittest.main()
