#!/usr/bin/env python3
"""Offline backend coverage and generated Compose contract checks."""
import importlib.machinery
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
stack = importlib.machinery.SourceFileLoader('stack_contract', str(ROOT / 'installer/src/shai-stack-apply')).load_module()
host = importlib.machinery.SourceFileLoader('host_contract', str(ROOT / 'installer/src/shai-app-install')).load_module()
catalog = json.loads((ROOT / 'installer/catalog/shapp-apps.json').read_text())['apps']
services = json.loads((ROOT / 'installer/catalog/shai-stack-services.json').read_text())

class Contracts(unittest.TestCase):
    def test_catalog_backends(self):
        for app in catalog:
            if app.get('host_backend'):
                self.assertIn(app['id'], host.SUPPORTED)
            if app.get('container_service'):
                self.assertIn(app['container_service'], stack.SUPPORTED)
                self.assertIn(app['container_service'], services['services'])

    def test_all_generated_services(self):
        stack.serial_device = lambda: '/dev/serial/by-id/test-controller'
        for key, entry in services['services'].items():
            output = stack.compose_text({key}, services['services'], '/dev/serial/by-id/test-controller', services['infrastructure']['engine-observer']['image'])
            self.assertIn('shai-' + key, output)
            self.assertNotIn('privileged: true', output)
            if entry.get('generic'):
                self.assertIn('127.0.0.1:', output)
                self.assertIn('max-size', output)
                self.assertNotIn('network_mode: host', output)
                self.assertNotIn('/var/run/docker.sock:', output.split('  '+key+':')[1].split('networks:\n')[0])

if __name__ == '__main__': unittest.main()
