#!/usr/bin/env python3
"""Validate every service with Docker Compose without pulling or starting it."""
import importlib.machinery
import json
from pathlib import Path
import subprocess
import tempfile

module = importlib.machinery.SourceFileLoader('stack_preview', '/usr/lib/shai-installer/shai-stack-apply').load_module()
module.serial_device = lambda: '/dev/serial/by-id/validation-only'
data = json.loads(Path('/usr/lib/shai-installer/catalog/shai-stack-services.json').read_text())
with tempfile.TemporaryDirectory(prefix='shai-compose-contract-') as directory:
    path = Path(directory) / 'compose.yaml'
    for service in sorted(data['services']):
        path.write_text(module.compose_text({service}, data['services'], '/dev/serial/by-id/validation-only', data['infrastructure']['engine-observer']['image']))
        subprocess.run(['docker', 'compose', '-f', str(path), 'config', '--quiet'], check=True,
                       env={**__import__('os').environ, 'AIA_API_KEY':'validation-only','OPEN_WEBUI_SECRET':'validation-only','SHAI_CONTROL_TOKEN':'validation-only','PIHOLE_PASSWORD':'validation-only','EMONCMS_PASSWORD':'validation-only','EMONCMS_ROOT_PASSWORD':'validation-only','TZ':'UTC'})
        print('PASS Compose schema', service)
