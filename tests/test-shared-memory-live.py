#!/usr/bin/env python3
"""Run as the VM desktop user. A temporary test note is removed in finally."""
import importlib.machinery
import json
from pathlib import Path
import secrets
import urllib.error
import urllib.request

memory = importlib.machinery.SourceFileLoader('live_local_memory', '/usr/lib/shai-installer/shai-context').load_module()
key = (Path.home() / '.local/state/shai/aia/server-api-key').read_text().strip()
http = urllib.request.build_opener(urllib.request.ProxyHandler({}))
def request(path, body=None, auth=True):
    headers = {'Content-Type': 'application/json'}
    if auth:
        headers['Authorization'] = 'Bearer ' + key
    req = urllib.request.Request('http://127.0.0.1:11437' + path,
                                 data=None if body is None else json.dumps(body).encode(), headers=headers)
    with http.open(req, timeout=180) as response:
        return json.load(response)

try:
    request('/v1/shai/context', auth=False)
    raise AssertionError('Unauthenticated context exposed')
except urllib.error.HTTPError as error:
    assert error.code == 401
data = request('/v1/shai/context')
assert data['aia']['configuration']['active_model']
assert key not in json.dumps(data)
assert data['shapp']['installed_packages'].get('shai-installer') == '0.14.0'
assert memory.MEMORY.stat().st_mode & 0o777 == 0o700
assert (memory.MEMORY / 'context.json').stat().st_mode & 0o777 == 0o600
print('PASS live authenticated context, installed package, key exclusion and private modes', flush=True)
marker = 'TA3 memory verification ' + secrets.token_hex(6)
notes_path = memory.MEMORY / 'notes.json'
existed = notes_path.exists()
try:
    memory.remember(marker)
    assert any(note['text'] == marker for note in request('/v1/shai/memory')['notes'])
    print('PASS explicit local note is visible immediately through shared memory API', flush=True)
finally:
    with memory.locked('.notes-lock'):
        notes = [note for note in memory.read_json(notes_path, []) if note.get('text') != marker]
        if notes or existed:
            memory.write_private(notes_path, json.dumps(notes, indent=2) + '\n')
        else:
            notes_path.unlink(missing_ok=True)
    memory.refresh(True)
