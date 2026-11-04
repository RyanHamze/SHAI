#!/usr/bin/env bash
set -Eeuo pipefail
dist="${1:-dist}"
deb="$(find "$dist" -maxdepth 1 -type f -name 'shai-installer_*_amd64.deb' -print -quit)"
[[ -n "$deb" ]] || { echo "No SHAI amd64 DEB found" >&2; exit 1; }
python3 - "$deb" "$dist/SHAI-APP-CATALOG.json" <<'PY'
import hashlib, io, json, pathlib, subprocess, sys, tarfile
deb = pathlib.Path(sys.argv[1])
version = subprocess.check_output(["dpkg-deb", "--field", str(deb), "Version"], text=True).strip()
catalog = {"schema": 2, "publisher": "Aabey LLC", "publisher_contact": "shai@aabeyllc.com",
 "signature_policy": "Public test candidate: verify GitHub workflow provenance. Offline publisher APT signatures are separate.",
 "applications": [{"id": "com.aabey.shai.installer", "name": "SHAI Installer",
 "version": version, "architecture": "amd64", "artifact": deb.name,
 "sha256": hashlib.sha256(deb.read_bytes()).hexdigest(),
 "network_required_for_install": False, "privileged": True}]}
names = {'shai-setup': 'SHAI Setup', 'shai-shapp': 'SHAPP', 'shai-health': 'SHEALTH',
         'shai-aia': 'AIA AI Assistant', 'shai-metadata': 'SHAI Metadata Cleaner'}
payload = subprocess.check_output(['dpkg-deb', '--fsys-tarfile', str(deb)])
with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
    for name, title in names.items():
        member = archive.getmember('./usr/bin/' + name)
        if not member.isfile():
            raise SystemExit('Expected regular packaged application: ' + name)
        contents = archive.extractfile(member).read()
        catalog['applications'].append({'id': name, 'name': title, 'version': version,
                                       'package_path': '/usr/bin/' + name,
                                       'sha256': hashlib.sha256(contents).hexdigest(),
                                       'authentication': 'Covered by attested DEB and app catalog; no separate executable signature claim'})
pathlib.Path(sys.argv[2]).write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n")
PY
(cd "$dist" && sha256sum "$(basename "$deb")" SHAI-APP-CATALOG.json > SHA256SUMS)
