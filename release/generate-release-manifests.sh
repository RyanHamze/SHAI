#!/usr/bin/env bash
set -Eeuo pipefail
dist="${1:-dist}"
deb="$(find "$dist" -maxdepth 1 -type f -name 'shai-installer_*_amd64.deb' -print -quit)"
[[ -n "$deb" ]] || { echo "No SHAI amd64 DEB found" >&2; exit 1; }
(cd "$dist" && sha256sum "$(basename "$deb")" > SHA256SUMS)
python3 - "$deb" "$dist/SHAI-APP-CATALOG.json" <<'PY'
import hashlib, json, pathlib, subprocess, sys
deb = pathlib.Path(sys.argv[1])
version = subprocess.check_output(["dpkg-deb", "--field", str(deb), "Version"], text=True).strip()
catalog = {"schema": 1, "publisher": "Aabey LLC",
 "signing_identity": "SHAI App Catalog Signing <shai@aabeyllc.com>",
 "applications": [{"id": "com.aabey.shai.installer", "name": "SHAI Installer",
 "version": version, "architecture": "amd64", "artifact": deb.name,
 "sha256": hashlib.sha256(deb.read_bytes()).hexdigest(),
 "network_required_for_install": False, "privileged": True}]}
pathlib.Path(sys.argv[2]).write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n")
PY
