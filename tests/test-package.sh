#!/usr/bin/env bash
set -Eeuo pipefail
bash -n \
    installer/build.sh \
    installer/src/shai-installer \
    installer/src/shai-theme-apply \
    installer/src/shai-theme-default \
    installer/src/shai-theme-reset \
    release/*.sh \
    tools/*.sh \
    connectivity/bin/*
python3 -m py_compile \
    installer/src/shai-appearance \
    installer/src/shai-plan-validator \
    installer/src/shai-setup \
    installer/src/shai-wave-a-shell
./installer/build.sh
deb="$(find dist -maxdepth 1 -name 'shai-installer_*_amd64.deb' -print -quit)"
tests/test-wave-a-package.sh "$deb"
python3 tests/test-shapp-backends.py
python3 tests/test-install-errors.py
python3 tests/test-control-broker.py
python3 tests/test-voice-manage.py
python3 tests/test-setup-shapp-audit.py
python3 tests/test-aia-health-regressions.py
python3 tests/test-ui-wiring.py
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
