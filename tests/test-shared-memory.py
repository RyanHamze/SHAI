#!/usr/bin/env python3
"""Private memory and real loopback HTTP contract tests; no model or VM changes."""
from contextlib import ExitStack
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import http.client
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    loader = importlib.machinery.SourceFileLoader(name.replace('-', '_'), str(ROOT / 'installer/src' / name))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
    loader.exec_module(module)
    return module

memory = load('shai-context')
gateway = load('shai-context-gateway')
stack = load('shai-stack-apply')

class Memory(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.store = self.home / '.local/share/shai/memory'
        self.config = self.home / '.config/shai/aia.json'
        self.config.parent.mkdir(parents=True)
        self.config.write_text(json.dumps({'active_model': 'test-model', 'integrations': {}}))
        self.patches = ExitStack()
        self.addCleanup(self.patches.close)
        self.patches.enter_context(patch.multiple(memory, HOME=self.home, MEMORY=self.store,
                                                LIB=self.home / 'lib', STATE=self.home / 'setup', NETWORK=self.home / 'network.json'))
        self.patches.enter_context(patch.object(memory, 'command', return_value='example\t1.0\tii \n'))
        self.patches.enter_context(patch.object(memory, 'health_sample', return_value={'ts': 123, 'cpu': 4}))

    def test_private_store_and_real_configuration_snapshot(self):
        snapshot = memory.refresh()
        self.assertEqual(snapshot['aia']['configuration']['active_model'], 'test-model')
        self.assertEqual(snapshot['shapp']['installed_packages'], {'example': '1.0'})
        self.assertEqual(snapshot['shealth']['latest_sample']['cpu'], 4)
        self.assertEqual(self.store.stat().st_mode & 0o777, 0o700)
        for name in ('context.json', 'context.md'):
            self.assertEqual((self.store / name).stat().st_mode & 0o777, 0o600)
        event = next((self.store / 'events').glob('*.jsonl'))
        self.assertEqual(event.stat().st_mode & 0o777, 0o600)

    def test_secrets_and_url_credentials_not_exported(self):
        self.config.write_text(json.dumps({
            'integrations': {'mqtt': {'password': 'CANARY_SECRET_42', 'note': 'copied CANARY_SECRET_42',
                                       'url': 'HTTP://alice:embedded-pass@localhost:8123/api?auth=hidden#fragment'},
                             'custom': {'door_code': 'CANARY_CUSTOM_99'}},
            'custom_integrations': [{'fields': [{'key': 'door_code', 'secret': True},
                                                 {'key': 'extra', 'secret': True, 'value': 'CANARY_SCHEMA_01'}]}],
            'chat_history': ['CANARY_CHAT_33'],
        }))
        key = self.home / '.local/state/shai/aia/server-api-key'
        key.parent.mkdir(parents=True)
        key.write_text('CANARY_API_KEY_66')
        self.config.write_text(self.config.read_text().replace('copied ', 'CANARY_API_KEY_66 copied '))
        snapshot = memory.refresh()
        dumped = json.dumps(snapshot)
        for canary in ('CANARY_SECRET_42', 'CANARY_CUSTOM_99', 'CANARY_SCHEMA_01', 'CANARY_CHAT_33',
                       'CANARY_API_KEY_66', 'embedded-pass', 'alice:', 'auth=hidden', '#fragment'):
            self.assertNotIn(canary, dumped)
        self.assertEqual(snapshot['aia']['configuration']['integrations']['mqtt']['password'], {'configured': True})

    def test_null_custom_schema_does_not_break_export(self):
        for custom in (None, [{'fields': None}], [{'fields': 'invalid'}]):
            self.config.write_text(json.dumps({'custom_integrations': custom}))
            self.assertIsInstance(memory.refresh(True), dict)

    def test_new_settings_invalidate_recent_cache(self):
        first = memory.refresh()
        self.config.write_text(json.dumps({'active_model': 'new-model', 'token': 'new-secret'}))
        second = memory.refresh()
        self.assertNotEqual(first['source_revision'], second['source_revision'])
        self.assertEqual(second['aia']['configuration']['active_model'], 'new-model')
        self.assertNotIn('new-secret', (self.store / 'context.md').read_text())

    def test_symlinked_memory_directory_rejected(self):
        outside = self.home / 'elsewhere'
        outside.mkdir()
        self.store.parent.mkdir(parents=True)
        self.store.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            memory.refresh()
        self.assertEqual(list(outside.iterdir()), [])

    def test_notes_preserved_and_credentials_rejected(self):
        memory.remember('The living room switch is called Lounge')
        memory.remember('The garage sensor uses the local bridge')
        notes = json.loads((self.store / 'notes.json').read_text())
        self.assertEqual(len(notes), 2)
        with self.assertRaises(ValueError):
            memory.remember('password=do-not-store-this')
        self.assertEqual(json.loads((self.store / 'notes.json').read_text()), notes)

    def test_only_event_names_exported_never_raw_log_details(self):
        logs = self.home / '.local/state/shai/aia/logs'
        logs.mkdir(parents=True)
        (logs / '2026-11-03.log').write_text('date | model-selected | CANARY_RAW_TOKEN and private prompt\n')
        output = memory.refresh()
        self.assertEqual(output['aia']['events']['events'], {'model-selected': 1})
        self.assertNotIn('CANARY_RAW_TOKEN', json.dumps(output))

    def test_summary_keeps_newest_notes_with_large_configuration(self):
        self.config.write_text(json.dumps({'huge': 'x' * 10000}))
        data = memory.refresh()
        data['notes'] = [{'text': 'older ' * 300}, {'text': 'NEWEST NOTE survives'}]
        prompt = memory.prompt_summary(data)
        self.assertIn('NEWEST NOTE survives', prompt)
        self.assertLess(len(prompt), 4000)

    def test_context_injected_once_without_mutating_original(self):
        original = [{'role': 'system', 'content': 'Original policy'}, {'role': 'user', 'content': 'configuration?'}]
        data = memory.refresh()
        first = memory.inject(original, data)
        second = memory.inject(first, data)
        self.assertEqual(second[0]['content'].count(memory.START), 1)
        self.assertEqual(original[0]['content'], 'Original policy')
        self.assertIn('test-model', second[0]['content'])

    def test_prompt_budget_includes_escaped_notes_and_package_matches(self):
        data = memory.refresh()
        data['notes'] = [{'text': '\u2603\\"' * 500} for _ in range(3)]
        data['aia']['configuration']['active_model'] = 'm' * 5000
        data['shapp']['installed_packages'] = {'package' + str(index): 'v' * 3000 for index in range(12)}
        question = ' '.join(data['shapp']['installed_packages'])
        self.assertLessEqual(len(memory.prompt_summary(data, question=question)), 3500)

    def test_cli_note_uses_stdin_not_arguments(self):
        with patch.object(memory.os, 'geteuid', return_value=1000), patch.object(sys, 'argv', ['shai-context', '--remember-stdin']), patch.object(sys, 'stdin', io.StringIO('A new local preference')), patch.object(memory, 'remember', return_value={}) as remember:
            memory.main()
        remember.assert_called_once_with('A new local preference')

class HTTPContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        key = Path(self.temp.name) / 'key'
        key.write_text('test-only-bearer-key')
        key.chmod(0o600)
        self.key = key
        self.records = []
        records = self.records
        class Backend(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass
            def do_GET(self):
                records.append((self.path, self.headers.get('Authorization'), None))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            def do_POST(self):
                data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                records.append((self.path, self.headers.get('Authorization'), data))
                self.send_response(200)
                if data.get('stream'):
                    self.send_header('Content-Type', 'text/event-stream')
                    self.end_headers()
                    self.wfile.write(b'data: {"choices":[]}\n\ndata: [DONE]\n\n')
                else:
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'choices': [{'message': {'content': data['messages'][-1]['content']}}]}).encode())
        self.backend = ThreadingHTTPServer(('127.0.0.1', 0), Backend)
        self.backend.daemon_threads = True
        self.http = gateway.LocalServer(('127.0.0.1', 0), gateway.Handler)
        self.fixture = {'generated_at': 'test-timestamp', 'storage': str(Path(self.temp.name) / 'memory'),
                        'aia': {'configuration': {'active_model': 'SELECTED_MODEL'}},
                        'notes': [{'text': 'SHARED_NOTE_42'}]}
        self.patches = ExitStack()
        self.patches.enter_context(patch.multiple(gateway, KEY=key, BACKEND_PORT=self.backend.server_port,
                                                context=SimpleNamespace(refresh=lambda: self.fixture, inject=memory.inject)))
        self.patches.enter_context(patch.object(gateway.subprocess, 'run', return_value=SimpleNamespace(
            returncode=0, stdout=f'MainPID={os.getpid()}\nActiveState=active\n')))
        self.threads = [threading.Thread(target=server.serve_forever, daemon=True) for server in (self.backend, self.http)]
        for thread in self.threads:
            thread.start()
        self.addCleanup(self.cleanup_servers)

    def cleanup_servers(self):
        for server in (self.http, self.backend):
            server.shutdown()
            server.server_close()
        for thread in self.threads:
            thread.join(timeout=2)
        self.patches.close()

    def request(self, method, path, value=None, authorized=True):
        client = http.client.HTTPConnection('127.0.0.1', self.http.server_port, timeout=4)
        try:
            headers = {'Authorization': 'Bearer test-only-bearer-key'} if authorized else {}
            client.request(method, path, json.dumps(value) if value is not None else None, headers)
            response = client.getresponse()
            return response.status, response.read(), response.getheader('Content-Type')
        finally:
            client.close()

    def test_context_and_notes_require_authentication(self):
        for path in ('/v1/shai/context', '/v1/shai/memory'):
            self.assertEqual(self.request('GET', path, authorized=False)[0], 401)
            status, body, _ = self.request('GET', path)
            self.assertEqual(status, 200)
            self.assertIn('SHARED_NOTE_42', body.decode())

    def test_no_arbitrary_paths_or_config_writes(self):
        for method, path in (('GET', '/etc/passwd'), ('POST', '/v1/shai/config'), ('POST', '/v1/shai/memory')):
            self.assertEqual(self.request(method, path, {})[0], 404)
        self.assertEqual(self.records, [])

    def test_frontends_receive_same_context_and_real_forwarded_replies(self):
        for prompt in ('AIA question one', 'Open WebUI question two'):
            status, body, _ = self.request('POST', '/v1/chat/completions', {
                'model': 'local', 'messages': [{'role': 'user', 'content': prompt}], 'stream': False})
            self.assertEqual(status, 200, body)
            self.assertEqual(json.loads(body)['choices'][0]['message']['content'], prompt)
            path, auth, payload = self.records[-1]
            self.assertEqual(path, '/v1/chat/completions')
            self.assertEqual(auth, 'Bearer test-only-bearer-key')
            self.assertIn('SHARED_NOTE_42', payload['messages'][0]['content'])
            self.assertIn('SELECTED_MODEL', payload['messages'][0]['content'])

    def test_sse_stream_passed_through(self):
        status, body, kind = self.request('POST', '/v1/chat/completions', {
            'messages': [{'role': 'user', 'content': 'stream'}], 'stream': True})
        self.assertEqual(status, 200, body)
        self.assertEqual(kind, 'text/event-stream')
        self.assertIn(b'data: [DONE]', body)

    def test_transient_socket_owner_retried_before_payload(self):
        original = Path.read_text
        reads = []
        def initializing_owner(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if str(path) == '/proc/self/net/tcp':
                reads.append(True)
                if len(reads) == 1:
                    self.assertEqual(self.records, [])
                    lines = text.splitlines()
                    for index in range(1, len(lines)):
                        row = lines[index].split()
                        if len(row) >= 10:
                            row[7] = str(os.getuid() + 1)
                            lines[index] = ' '.join(row)
                    return '\n'.join(lines)
            return text
        with patch.object(Path, 'read_text', new=initializing_owner):
            status, body, _ = self.request('POST', '/v1/chat/completions', {
                'messages': [{'role': 'user', 'content': 'wait for ownership'}]})
        self.assertEqual(status, 200, body)
        self.assertGreaterEqual(len(reads), 2)

    def test_invalid_payload_never_reaches_backend(self):
        for value in ({}, {'messages': []}, {'messages': [{'role': 'root', 'content': 'bad'}]}):
            self.assertEqual(self.request('POST', '/v1/chat/completions', value)[0], 400)
        self.assertEqual(self.records, [])

    def test_persistently_wrong_socket_owner_gets_no_payload(self):
        original = Path.read_text
        def wrong_owner(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if str(path) == '/proc/self/net/tcp':
                lines = text.splitlines()
                for index in range(1, len(lines)):
                    row = lines[index].split()
                    if len(row) >= 10:
                        row[7] = str(os.getuid() + 1)
                        lines[index] = ' '.join(row)
                return '\n'.join(lines)
            return text
        with patch.object(Path, 'read_text', new=wrong_owner):
            status, _, _ = self.request('POST', '/v1/chat/completions', {
                'messages': [{'role': 'user', 'content': 'must stay private'}]})
        self.assertEqual(status, 502)
        self.assertEqual(self.records, [])

    def test_untrusted_backend_gets_no_key_or_context(self):
        with patch.object(gateway.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='MainPID=0\nActiveState=inactive')):
            status, _, _ = self.request('POST', '/v1/chat/completions', {'messages': [{'role': 'user', 'content': 'private'}]})
        self.assertEqual(status, 502)
        self.assertEqual(self.records, [])

    def test_openapi_paths_match_authenticated_routes(self):
        status, body, _ = self.request('GET', '/openapi.json', authorized=False)
        self.assertEqual(status, 200)
        spec = json.loads(body)
        self.assertEqual(spec['security'], [{'BearerAuth': []}])
        for path in spec['paths']:
            self.assertEqual(self.request('GET', path)[0], 200)

    def test_private_key_permissions_enforced(self):
        self.key.chmod(0o644)
        self.assertEqual(self.request('GET', '/v1/shai/context')[0], 503)

    def test_bounded_handlers_close_excess_idle_connections(self):
        clients = []
        try:
            for _ in range(5):
                clients.append(socket.create_connection(('127.0.0.1', self.http.server_port), timeout=2))
            clients[-1].settimeout(2)
            self.assertEqual(clients[-1].recv(1), b'')
        finally:
            for client in clients:
                client.close()

class Wiring(unittest.TestCase):
    def test_build_contains_all_memory_helpers_and_units(self):
        build = (ROOT / 'installer/build.sh').read_text()
        for name in ('shai-context', 'shai-context-gateway', 'shai-context.service', 'shai-context.timer', 'shai-context-gateway.service'):
            self.assertIn(name, build)
        aia = (ROOT / 'installer/src/shai-aia').read_text()
        self.assertIn('SERVER_URL = "http://127.0.0.1:11437"', aia)
        self.assertIn('--remember-stdin', aia)

    def test_gateway_sandbox_preserves_proc_peer_identity_checks(self):
        unit = (ROOT / 'installer/systemd/shai-context-gateway.service').read_text()
        self.assertIn('NoNewPrivileges=true', unit)
        self.assertIn('IPAddressAllow=127.0.0.1/32', unit)
        for incompatible in ('ProtectHome=', 'ProtectSystem=', 'PrivateTmp='):
            self.assertNotIn(incompatible, unit)

    def test_compose_uses_gateway_and_authenticated_memory_tools(self):
        catalog = json.loads((ROOT / 'installer/catalog/shai-stack-services.json').read_text())['services']
        compose = stack.compose_text({'open-webui'}, catalog, None, 'observer:test')
        self.assertIn('OPENAI_API_BASE_URL: http://127.0.0.1:11437/v1', compose)
        self.assertIn('shai-local-memory', compose)
        self.assertNotIn('/home/', compose)
        self.assertNotIn('/:/', compose)

if __name__ == '__main__':
    unittest.main()
