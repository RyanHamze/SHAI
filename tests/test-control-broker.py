#!/usr/bin/env python3
"""Isolated broker contract tests: no host services or real devices changed."""
import importlib.machinery
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "installer/src/shai-control-broker"
b = importlib.machinery.SourceFileLoader("broker_test", str(SOURCE)).load_module()

class BrokerContract(unittest.TestCase):
    def test_isolated_approval_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            b.PROPOSALS = root / "proposals.json"
            b.AUDIT = root
            b.WEBUI_TOKEN = root / "operator"
            b.APPROVAL_TOKEN = root / "approval"
            b.WEBUI_TOKEN.write_text("operator-test-only")
            b.APPROVAL_TOKEN.write_text("approval-test-only")
            called = []
            b.execute = lambda proposal: (called.append(proposal["id"]) is None, "isolated adapter receipt")
            server = b.ThreadingHTTPServer(("127.0.0.1", 0), b.Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}/v1"
            def post(path, payload, key):
                req = urllib.request.Request(base + path, data=json.dumps(payload).encode(), headers={"Authorization": "Bearer " + key}, method="POST")
                with urllib.request.urlopen(req, timeout=2) as response:
                    return json.load(response)
            try:
                proposal = post("/proposals", {"action": "systemd.restart", "arguments": {"unit": "shai-aia-model.service"}, "reason": "Isolated contract test"}, "operator-test-only")
                self.assertEqual(proposal["status"], "pending")
                self.assertFalse(called)
                with self.assertRaises(urllib.error.HTTPError) as denied:
                    post(f"/proposals/{proposal['id']}/approve", {}, "operator-test-only")
                self.assertEqual(denied.exception.code, 401)
                self.assertFalse(called)
                result = post(f"/proposals/{proposal['id']}/approve", {}, "approval-test-only")
                self.assertEqual(result["status"], "completed")
                self.assertEqual(len(called), 1)
                with self.assertRaises(urllib.error.HTTPError):
                    post(f"/proposals/{proposal['id']}/approve", {}, "approval-test-only")
                self.assertEqual(len(called), 1)
                self.assertFalse(b.validate_proposal({"action": "shell", "arguments": {}})[0])
                self.assertFalse(b.validate_proposal({"action": "systemd.restart", "arguments": {"unit": "ssh.service"}})[0])
            finally:
                server.shutdown()
                server.server_close()

if __name__ == "__main__": unittest.main()
