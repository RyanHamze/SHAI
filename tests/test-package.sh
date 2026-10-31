#!/usr/bin/env bash
set -Eeuo pipefail
bash -n installer/src/shai-installer installer/build.sh release/*.sh tools/*.sh connectivity/bin/*
./installer/build.sh
deb="$(find dist -maxdepth 1 -name 'shai-installer_*_amd64.deb' -print -quit)"
[[ "$(dpkg-deb --field "$deb" Architecture)" == amd64 ]]
[[ "$(dpkg-deb --field "$deb" Package)" == shai-installer ]]
control_listing="$(dpkg-deb --ctrl-tarfile "$deb" | tar -tf -)"
[[ "$control_listing" == *"./control"* && "$control_listing" != *"postinst"* ]]
extract="$(mktemp -d)"; dpkg-deb --extract "$deb" "$extract"
bash -n "$extract/usr/bin/shai-installer"
grep -q '^\^linux-' debloat/PROTECTED_PACKAGES.regex
grep -q 'gdm3' debloat/PROTECTED_PACKAGES.regex
grep -q 'network-manager' debloat/PROTECTED_PACKAGES.regex
release/generate-release-manifests.sh dist
(cd dist && sha256sum --check SHA256SUMS)
python3 -m json.tool dist/SHAI-APP-CATALOG.json >/dev/null
echo "SHAI package tests passed"
