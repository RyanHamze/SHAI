#!/usr/bin/env bash
set -Eeuo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly VERSION="0.1.2"
readonly PACKAGE="shai-installer_${VERSION}_amd64"
readonly BUILD_ROOT="$(mktemp -d "/tmp/shai-installer-build-${VERSION}.XXXXXX")"
readonly STAGE="$BUILD_ROOT/$PACKAGE"
readonly DIST="$ROOT/dist"
readonly SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git -C "$ROOT" log -1 --format=%ct 2>/dev/null || printf '0')}"
export SOURCE_DATE_EPOCH

if [[ -e "$DIST/$PACKAGE.deb" ]]; then
    printf 'Build output already exists. Move it aside before rebuilding:\n  %s\n' \
        "$DIST/$PACKAGE.deb" >&2
    exit 1
fi

install -d \
    "$STAGE/DEBIAN" \
    "$STAGE/usr/bin" \
    "$STAGE/usr/lib/shai-installer/catalog" \
    "$STAGE/usr/lib/shai-installer/assets" \
    "$STAGE/usr/share/doc/shai-installer" \
    "$DIST"

install -m 0644 "$ROOT/installer/debian/control" "$STAGE/DEBIAN/control"
install -m 0755 "$ROOT/installer/src/shai-installer" "$STAGE/usr/bin/shai-installer"
install -m 0755 "$ROOT/tools/collect_debloat_benchmark.sh" "$STAGE/usr/lib/shai-installer/collect-debloat-benchmark"
install -m 0755 "$ROOT/tools/configure_manual_updates.sh" "$STAGE/usr/lib/shai-installer/configure-manual-updates"
install -m 0755 "$ROOT/tools/restore_automatic_updates.sh" "$STAGE/usr/lib/shai-installer/restore-automatic-updates"
install -m 0644 "$ROOT/debloat/PROTECTED_PACKAGES.regex" "$STAGE/usr/lib/shai-installer/PROTECTED_PACKAGES.regex"

for file in \
    01-applications.list \
    02-print-scan-modem.list \
    02-print-scan-modem.allow-removals \
    03-domain-and-remote-desktop.list \
    04-reporting.list \
    05-non-us-dictionaries.list \
    06-filtered-orphans.list \
    07-help.list \
    09-extra-theme-packages.list \
    09-yaru-color-variant-paths.list \
    10-personal-utilities.list; do
    install -m 0644 "$ROOT/debloat/catalog/ubuntu-26.04/$file" "$STAGE/usr/lib/shai-installer/catalog/$file"
done

install -m 0755 "$ROOT/connectivity/bin/shai-web-connectivity-toggle" "$STAGE/usr/lib/shai-installer/assets/shai-web-connectivity-toggle"
install -m 0644 "$ROOT/connectivity/share/applications/shai-web-connectivity-toggle.desktop" "$STAGE/usr/lib/shai-installer/assets/shai-web-connectivity-toggle.desktop"
install -m 0644 "$ROOT/connectivity/etc/dconf/db/local.d/20-shai-web-offline" "$STAGE/usr/lib/shai-installer/assets/20-shai-web-offline"
install -m 0644 "$ROOT/connectivity/etc/dconf/profile/user" "$STAGE/usr/lib/shai-installer/assets/dconf-user-profile"
install -m 0644 "$ROOT/connectivity/etc/firefox/policies/policies.json" "$STAGE/usr/lib/shai-installer/assets/firefox-policies.json"
install -m 0644 "$ROOT/installer/README.md" "$STAGE/usr/share/doc/shai-installer/README.md"

find "$STAGE" -exec touch -h -d "@$SOURCE_DATE_EPOCH" {} +
dpkg-deb --root-owner-group --build "$STAGE" "$DIST/$PACKAGE.deb"
(cd "$DIST" && sha256sum "$PACKAGE.deb" > "$PACKAGE.deb.sha256")
dpkg-deb --info "$DIST/$PACKAGE.deb"
printf '\nBuilt:\n  %s\n  %s\n' "$DIST/$PACKAGE.deb" "$DIST/$PACKAGE.deb.sha256"
printf 'Temporary Linux staging root retained for inspection:\n  %s\n' "$STAGE"
