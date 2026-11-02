#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly ROOT
readonly PACKAGE="${1:-$ROOT/dist/shai-installer_0.6.4_amd64.deb}"
TEST_DIR="$(mktemp -d /tmp/shai-wave-a-package-test.XXXXXX)"
readonly TEST_DIR
USER_NAME="$(id -un)"
readonly USER_NAME

[[ -f "$PACKAGE" ]] || { printf 'Package not found: %s\n' "$PACKAGE" >&2; exit 1; }

bash -n \
    "$ROOT/installer/build.sh" \
    "$ROOT/installer/src/shai-installer" \
    "$ROOT/installer/src/shai-theme-apply" \
    "$ROOT/installer/src/shai-theme-reset" \
    "$ROOT/installer/src/shai-theme-default"
python3 -m py_compile \
    "$ROOT/installer/src/shai-setup" \
    "$ROOT/installer/src/shai-shapp" \
    "$ROOT/installer/src/shai-shapp-apply" \
    "$ROOT/installer/src/shai-stack-apply" \
    "$ROOT/installer/src/shai-network-snapshot" \
    "$ROOT/installer/src/shai-shapp-log" \
    "$ROOT/installer/src/shai-health" \
    "$ROOT/installer/src/shai-wave-a-shell" \
    "$ROOT/installer/src/shai-appearance" \
    "$ROOT/installer/src/shai-plan-validator" \
    "$ROOT/installer/src/shai-system-summary"
python3 - "$ROOT/installer/catalog/shapp-apps.json" <<'PY'
import json
import pathlib
import sys

data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
apps = data["apps"]
ids = {item["id"] for item in apps}
assert data["schema"] == 2
assert len(apps) == 30
assert sum(item["category"] == "recommended" for item in apps) == 11
assert sum(item["category"] == "optional" for item in apps) == 19
assert len(ids) == len(apps)
assert {"sniffnet", "home-assistant", "mosquitto", "zigbee2mqtt", "whisper", "jellyfin",
        "keepassxc", "opensnitch", "suricata"} <= ids
assert all(item["packages"] for item in apps if item["available"])
assert all(not item["packages"] for item in apps if not item["available"])
PY

python3 - "$ROOT/installer/src/shai-installer" <<'PY'
import pathlib
import sys

lines = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
index = 0
count = 0
while index < len(lines):
    if "<<'PY'" not in lines[index]:
        index += 1
        continue
    start = index + 1
    end = start
    while end < len(lines) and lines[end] != "PY":
        end += 1
    if end == len(lines):
        raise SystemExit(f"Unterminated Python heredoc at line {index + 1}")
    compile("\n".join(lines[start:end]) + "\n", f"embedded-python-{index + 1}", "exec")
    count += 1
    index = end + 1
if count == 0:
    raise SystemExit("No embedded Python blocks were validated")
PY

umask 077
perl -MJSON::PP -e '
    $user = shift;
    print encode_json({
        schema => 1,
        plan_id => "01234567-89ab-cdef",
        target_user => $user,
        confirmed_debloat => JSON::PP::true,
        architecture => "managed-stack",
        smart_home => JSON::PP::true,
        local_ai => JSON::PP::false,
        offline_mode => JSON::PP::true,
        theme => "shai-brand-v2",
    }), "\n";
' "$USER_NAME" > "$TEST_DIR/valid.json"
"$ROOT/installer/src/shai-plan-validator" "$TEST_DIR/valid.json" \
    > "$TEST_DIR/normalized.json"
perl -MJSON::PP -0777 -e '
    $data = decode_json(<>);
    exit !(($data->{architecture} // "") eq "managed-stack"
        && $data->{confirmed_debloat} && !$data->{local_ai});
' "$TEST_DIR/normalized.json"

perl -MJSON::PP -0777 -e '
    $data = decode_json(<>);
    $data->{local_ai} = "yes";
    print encode_json($data), "\n";
' "$TEST_DIR/valid.json" > "$TEST_DIR/invalid.json"
chmod 0600 "$TEST_DIR/invalid.json"
if "$ROOT/installer/src/shai-plan-validator" "$TEST_DIR/invalid.json" \
    > "$TEST_DIR/invalid.out" 2> "$TEST_DIR/invalid.err"; then
    printf 'Invalid plan was incorrectly accepted.\n' >&2
    exit 1
fi

ln -s "$TEST_DIR/valid.json" "$TEST_DIR/symlink.json"
if "$ROOT/installer/src/shai-plan-validator" "$TEST_DIR/symlink.json" \
    > "$TEST_DIR/symlink.out" 2> "$TEST_DIR/symlink.err"; then
    printf 'Symbolic-link plan was incorrectly accepted.\n' >&2
    exit 1
fi

dpkg-deb --control "$PACKAGE" "$TEST_DIR/control"
mapfile -t control_files < <(
    find "$TEST_DIR/control" -mindepth 1 -maxdepth 1 -type f -printf '%f\n' | sort
)
[[ "${control_files[*]}" == control ]] || {
    printf 'Package must be inert; unexpected maintainer files: %s\n' \
        "${control_files[*]}" >&2
    exit 1
}

dpkg-deb --extract "$PACKAGE" "$TEST_DIR/root"
bash -n "$TEST_DIR/root/usr/bin/shai-installer"
python3 -m py_compile \
    "$TEST_DIR/root/usr/bin/shai-setup" \
    "$TEST_DIR/root/usr/bin/shai-shapp" \
    "$TEST_DIR/root/usr/bin/shai-shapp-apply" \
    "$TEST_DIR/root/usr/lib/shai-installer/shai-stack-apply" \
    "$TEST_DIR/root/usr/lib/shai-installer/shai-network-snapshot" \
    "$TEST_DIR/root/usr/lib/shai-installer/shai-shapp-log" \
    "$TEST_DIR/root/usr/bin/shai-health" \
    "$TEST_DIR/root/usr/bin/shai-wave-a-shell" \
    "$TEST_DIR/root/usr/bin/shai-appearance" \
    "$TEST_DIR/root/usr/lib/shai-installer/shai-plan-validator" \
    "$TEST_DIR/root/usr/lib/shai-installer/shai-system-summary"

mkdir -p "$TEST_DIR/log-home"
if [[ $EUID -eq 0 ]]; then
    chmod o+x "$TEST_DIR"
    chown nobody:nogroup "$TEST_DIR/log-home"
    runuser -u nobody -- env HOME="$TEST_DIR/log-home" \
        "$TEST_DIR/root/usr/lib/shai-installer/shai-shapp-log" \
        DISCOVERED apt test-package "Test application" \
        >/dev/null
else
    HOME="$TEST_DIR/log-home" \
        "$TEST_DIR/root/usr/lib/shai-installer/shai-shapp-log" \
        DISCOVERED apt test-package "Test application" \
        >/dev/null
fi
grep -Fq $'DISCOVERED\tapt\ttest-package\tTest application' \
    "$TEST_DIR/log-home/.local/state/shai/shapp/logs/$(date +%F).log"

for path in \
    usr/bin/shai-installer \
    usr/bin/shai-setup \
    usr/bin/shai-shapp \
    usr/bin/shai-shapp-apply \
    usr/lib/shai-installer/shai-stack-apply \
    usr/lib/shai-installer/shai-network-snapshot \
    usr/lib/shai-installer/catalog/shai-stack-services.json \
    usr/lib/systemd/system/shai-network-snapshot.service \
    usr/lib/systemd/system/shai-network-snapshot.timer \
    usr/lib/shai-installer/shai-shapp-log \
    usr/bin/shai-health \
    usr/bin/shai-wave-a-shell \
    usr/bin/shai-theme-apply \
    usr/bin/shai-theme-reset \
    usr/bin/shai-theme-default \
    usr/bin/shai-appearance \
    usr/lib/shai-installer/shai-plan-validator \
    usr/lib/shai-installer/shai-system-summary \
    usr/lib/shai-installer/catalog/shapp-apps.json \
    usr/lib/shai-installer/assets/30-shai-privacy \
    usr/lib/shai-installer/assets/gnome-wellbeing-panel.desktop \
    usr/lib/shai-installer/assets/shai.palette \
    usr/share/applications/shai-setup.desktop \
    usr/share/doc/shai-installer/SETUP_README.md \
    usr/share/shai/branding/shai-lockup-dark.svg \
    usr/share/shai/branding/shai-wallpaper-1920x1080.png \
    usr/share/themes/SHAI/gnome-shell/gnome-shell.css \
    usr/share/themes/SHAI/gtk-4.0/gtk.css \
    usr/share/icons/SHAI/index.theme \
    usr/share/icons/SHAI/scalable/apps/shai-dashboard.svg \
    usr/share/backgrounds/shai/shai-wallpaper-1920x1080.png \
    usr/share/backgrounds/shai/shai-wallpaper-2560x1440.png \
    usr/share/backgrounds/shai/shai-wallpaper-3840x2160.png; do
    [[ -e "$TEST_DIR/root/$path" ]] || {
        printf 'Required package path missing: %s\n' "$path" >&2
        exit 1
    }
done

python3 - "$TEST_DIR/root/usr/share/backgrounds/shai" <<'PY'
import pathlib
import struct
import sys

root = pathlib.Path(sys.argv[1])
expected = {
    "shai-wallpaper-1920x1080.png": (1920, 1080),
    "shai-wallpaper-2560x1440.png": (2560, 1440),
    "shai-wallpaper-3840x2160.png": (3840, 2160),
}
for name, dimensions in expected.items():
    data = (root / name).read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"Wallpaper is not PNG: {name}")
    actual = struct.unpack(">II", data[16:24])
    if actual != dimensions:
        raise SystemExit(f"Wallpaper dimensions for {name}: {actual} != {dimensions}")
PY

cmp -s \
    "$TEST_DIR/root/usr/share/shai/branding/shai-wallpaper-1920x1080.png" \
    "$TEST_DIR/root/usr/share/backgrounds/shai/shai-wallpaper-1920x1080.png" || {
    printf 'Branding and theme wallpaper copies differ.\n' >&2
    exit 1
}

bash -n \
    "$TEST_DIR/root/usr/bin/shai-theme-apply" \
    "$TEST_DIR/root/usr/bin/shai-theme-reset" \
    "$TEST_DIR/root/usr/bin/shai-theme-default"

for deferred in shai-home.desktop shai-shapp.desktop shai-health.desktop shai-aia.desktop shai-appearance.desktop; do
    [[ ! -e "$TEST_DIR/root/usr/share/applications/$deferred" ]] || {
        printf 'Deferred launcher was exposed before setup: %s\n' "$deferred" >&2
        exit 1
    }
    [[ -e "$TEST_DIR/root/usr/lib/shai-installer/assets/launchers/$deferred" ]] || {
        printf 'Deferred launcher source missing: %s\n' "$deferred" >&2
        exit 1
    }
done

grep -Fq "whitelisted-providers=['']" \
    "$TEST_DIR/root/usr/lib/shai-installer/assets/30-shai-privacy"
grep -Fq 'Foreground=#33EE33' \
    "$TEST_DIR/root/usr/lib/shai-installer/assets/shai.palette"
grep -Fq 'Background=#000000' \
    "$TEST_DIR/root/usr/lib/shai-installer/assets/shai.palette"
grep -Fq 'timedatectl set-ntp true' \
    "$TEST_DIR/root/usr/bin/shai-installer"
grep -Fq 'flatpak permission-remove location location' \
    "$TEST_DIR/root/usr/bin/shai-installer"
grep -Fq 'Automatic date and time' \
    "$TEST_DIR/root/usr/lib/shai-installer/shai-system-summary"
grep -Fq 'Exec=shai-shapp' \
    "$TEST_DIR/root/usr/lib/shai-installer/assets/launchers/shai-shapp.desktop"
grep -Fq 'CART_WIDTH = 320' \
    "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'MB runtime RAM' \
    "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'ram -= amount' \
    "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'window-close-symbolic' \
    "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'Open daily log folder' \
    "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'catalog item has no enabled installer backend' \
    "$TEST_DIR/root/usr/bin/shai-shapp-apply"
grep -Fq 'Capacity exceeded; remove a selection' \
    "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'Cannot fit:' \
    "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq '0 pending changes' \
    "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'snap-store.show-updates' \
    "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'Application architecture' \
    "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'LIVE AUTOSAVE' "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'Yes, change architecture' "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'Change application architecture?' "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'Exec=shai-health' \
    "$TEST_DIR/root/usr/lib/shai-installer/assets/launchers/shai-health.desktop"
grep -Fq 'CREATE TABLE IF NOT EXISTS hourly' "$TEST_DIR/root/usr/bin/shai-health"
grep -Fq 'Sniffnet: live network monitor' "$TEST_DIR/root/usr/bin/shai-health"
grep -Fq 'Active source → destination flows' "$TEST_DIR/root/usr/bin/shai-health"
grep -Fq 'Open listening ports and owners' "$TEST_DIR/root/usr/bin/shai-health"
grep -Fq '"schema": 3' "$TEST_DIR/root/usr/bin/shai-shapp"
grep -Fq 'remove_container' "$TEST_DIR/root/usr/bin/shai-shapp-apply"
grep -Fq 'home-assistant:2026.9.3' "$TEST_DIR/root/usr/lib/shai-installer/catalog/shai-stack-services.json"
grep -Fq 'Host Ubuntu Environment Summary' "$TEST_DIR/root/usr/bin/shai-health"
grep -Fq 'negative checks / total checks' "$TEST_DIR/root/usr/bin/shai-health"
grep -Fq 'Estimated energy usage · rolling 24 hours' "$TEST_DIR/root/usr/bin/shai-health"
grep -Fq 'Completed calendar days are exported' "$TEST_DIR/root/usr/bin/shai-health"
if grep -Eq 'chronyc|prepare_clock_for_online_install|timedatectl' \
    "$TEST_DIR/root/usr/bin/shai-shapp-apply"; then
    printf 'SHAPP apply must not alter or force system time synchronization.\n' >&2
    exit 1
fi

(cd "$(dirname "$PACKAGE")" && sha256sum -c "$(basename "$PACKAGE").sha256")
printf 'SHAI Setup package tests passed. Evidence: %s\n' "$TEST_DIR"
