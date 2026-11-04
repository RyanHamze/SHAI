#!/usr/bin/env python3
"""Read-only SHAI VM release audit; never prints configurations or credentials."""
import argparse
from collections import Counter
import json
from pathlib import Path
import pwd
import re
import subprocess

def run(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30, check=False)
        return result.stdout
    except (OSError, subprocess.TimeoutExpired):
        return args[0] + ': unavailable (not a clean-result claim)'

def clean(text):
    text = re.sub(r'(?i)(bearer\s+|(?:password|token|api[_-]?key)\s*[=:]\s*)\S+', r'\1[redacted]', text)
    text = re.sub(r'(?i)https?://\S+', '[endpoint]', text)
    return text[:360]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', default='shai')
    args = parser.parse_args()
    home = Path(pwd.getpwnam(args.user).pw_dir)
    logs = []
    folders = [home / '.local/state/shai', Path('/var/log/shai-installer'), Path('/var/log/shai'),
               Path('/var/log/mosquitto'), Path('/var/lib/shai-installer')]
    for directory in folders:
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob('*.log')):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                with path.open('rb') as stream:
                    stream.seek(max(0, path.stat().st_size - 4194304))
                    text = stream.read().decode('utf-8', errors='replace')
                errors = [clean(line) for line in text.splitlines() if re.search(r'Traceback|\bException\b|\bERROR\b|\bFAILED\b|^E:|error:', line, re.I)]
                logs.append({'path': str(path), 'bytes': path.stat().st_size, 'error_lines': len(errors), 'latest_errors': errors[-6:]})
            except OSError:
                logs.append({'path': str(path), 'unreadable': True})
    journal = run(['journalctl', '--no-pager', '-b', '-p', 'warning', '-o', 'json'])
    counts = Counter()
    samples = {}
    for line in journal.splitlines():
        try:
            row = json.loads(line)
            unit = row.get('_SYSTEMD_UNIT') or row.get('_COMM', 'unknown')
            counts[unit] += 1
            samples[unit] = clean(str(row.get('MESSAGE', '')))
        except ValueError:
            continue
    print(json.dumps({'logs': logs, 'journal_warnings': dict(counts), 'latest_warning_by_unit': samples,
                      'failed_system_units': run(['systemctl', '--failed', '--no-pager', '--plain']),
                      'crashes': run(['coredumpctl', 'list', '--no-pager'])[-4000:]}, indent=2))

if __name__ == '__main__':
    main()
