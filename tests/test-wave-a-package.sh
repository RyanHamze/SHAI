#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly ROOT
readonly PACKAGE="${1:-$ROOT/dist/shai-installer_0.3.2_amd64.deb}"
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
    "$ROOT/installer/src/shai-wave-a-shell" \
    "$ROOT/installer/src/shai-appearance" \
    "$ROOT/installer/src/shai-plan-validator"

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
    "$TEST_DIR/root/usr/bin/shai-wave-a-shell" \
    "$TEST_DIR/root/usr/bin/shai-appearance" \
    "$TEST_DIR/root/usr/lib/shai-installer/shai-plan-validator"

for path in \
    usr/bin/shai-installer \
    usr/bin/shai-setup \
    usr/bin/shai-wave-a-shell \
    usr/bin/shai-theme-apply \
    usr/bin/shai-theme-reset \
    usr/bin/shai-theme-default \
    usr/bin/shai-appearance \
    usr/lib/shai-installer/shai-plan-validator \
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

(cd "$(dirname "$PACKAGE")" && sha256sum -c "$(basename "$PACKAGE").sha256")
printf 'SHAI Setup Wave A package tests passed. Evidence: %s\n' "$TEST_DIR"
