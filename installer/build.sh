#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly ROOT
readonly VERSION="0.8.3"
readonly PACKAGE="shai-installer_${VERSION}_amd64"
BUILD_ROOT="$(mktemp -d "/tmp/shai-installer-build-${VERSION}.XXXXXX")"
readonly BUILD_ROOT
readonly STAGE="$BUILD_ROOT/$PACKAGE"
readonly DIST="$ROOT/dist"
readonly SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(<"$ROOT/installer/SOURCE_DATE_EPOCH")}"
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
    "$STAGE/usr/lib/shai-installer/assets/launchers" \
    "$STAGE/usr/lib/systemd/system" \
    "$STAGE/usr/lib/systemd/user" \
    "$STAGE/usr/share/applications" \
    "$STAGE/usr/share/doc/shai-installer" \
    "$STAGE/usr/share/icons/hicolor/scalable/apps" \
    "$STAGE/usr/share/icons/SHAI/scalable/apps" \
    "$STAGE/usr/share/themes/SHAI/gnome-shell" \
    "$STAGE/usr/share/themes/SHAI/gtk-4.0" \
    "$STAGE/usr/share/backgrounds/shai" \
    "$STAGE/usr/share/shai/branding" \
    "$DIST"

install -m 0644 "$ROOT/installer/debian/control" "$STAGE/DEBIAN/control"
install -m 0755 "$ROOT/installer/src/shai-installer" "$STAGE/usr/bin/shai-installer"
install -m 0755 "$ROOT/installer/src/shai-setup" "$STAGE/usr/bin/shai-setup"
install -m 0755 "$ROOT/installer/src/shai-shapp" "$STAGE/usr/bin/shai-shapp"
install -m 0755 "$ROOT/installer/src/shai-shapp-apply" "$STAGE/usr/bin/shai-shapp-apply"
install -m 0755 "$ROOT/installer/src/shai-stack-apply" "$STAGE/usr/lib/shai-installer/shai-stack-apply"
install -m 0755 "$ROOT/installer/src/shai-network-snapshot" "$STAGE/usr/lib/shai-installer/shai-network-snapshot"
install -m 0755 "$ROOT/installer/src/shai-shapp-log" "$STAGE/usr/lib/shai-installer/shai-shapp-log"
install -m 0755 "$ROOT/installer/src/shai-health" "$STAGE/usr/bin/shai-health"
install -m 0755 "$ROOT/installer/src/shai-aia" "$STAGE/usr/bin/shai-aia"
install -m 0755 "$ROOT/installer/src/shai-aia-server" "$STAGE/usr/bin/shai-aia-server"
install -m 0755 "$ROOT/installer/src/shai-wave-a-shell" "$STAGE/usr/bin/shai-wave-a-shell"
install -m 0755 "$ROOT/installer/src/shai-theme-apply" "$STAGE/usr/bin/shai-theme-apply"
install -m 0755 "$ROOT/installer/src/shai-theme-reset" "$STAGE/usr/bin/shai-theme-reset"
install -m 0755 "$ROOT/installer/src/shai-theme-default" "$STAGE/usr/bin/shai-theme-default"
install -m 0755 "$ROOT/installer/src/shai-terminal-theme-apply" "$STAGE/usr/bin/shai-terminal-theme-apply"
install -m 0755 "$ROOT/installer/src/shai-appearance" "$STAGE/usr/bin/shai-appearance"
install -m 0755 "$ROOT/installer/src/shai-plan-validator" "$STAGE/usr/lib/shai-installer/shai-plan-validator"
install -m 0755 "$ROOT/installer/src/shai-system-summary" "$STAGE/usr/lib/shai-installer/shai-system-summary"
install -m 0755 "$ROOT/tools/collect_debloat_benchmark.sh" "$STAGE/usr/lib/shai-installer/collect-debloat-benchmark"
install -m 0755 "$ROOT/tools/configure_manual_updates.sh" "$STAGE/usr/lib/shai-installer/configure-manual-updates"
install -m 0755 "$ROOT/tools/restore_automatic_updates.sh" "$STAGE/usr/lib/shai-installer/restore-automatic-updates"
install -m 0644 "$ROOT/debloat/PROTECTED_PACKAGES.regex" "$STAGE/usr/lib/shai-installer/PROTECTED_PACKAGES.regex"
install -m 0644 "$ROOT/installer/catalog/shapp-apps.json" "$STAGE/usr/lib/shai-installer/catalog/shapp-apps.json"
install -m 0644 "$ROOT/installer/catalog/shai-stack-services.json" "$STAGE/usr/lib/shai-installer/catalog/shai-stack-services.json"
install -m 0644 "$ROOT/installer/systemd/shai-network-snapshot.service" "$STAGE/usr/lib/systemd/system/shai-network-snapshot.service"
install -m 0644 "$ROOT/installer/systemd/shai-network-snapshot.timer" "$STAGE/usr/lib/systemd/system/shai-network-snapshot.timer"
install -m 0644 "$ROOT/installer/systemd/shai-aia-model.service" "$STAGE/usr/lib/systemd/user/shai-aia-model.service"

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
install -m 0644 "$ROOT/installer/assets/30-shai-privacy" "$STAGE/usr/lib/shai-installer/assets/30-shai-privacy"
install -m 0644 "$ROOT/installer/assets/gnome-wellbeing-panel.desktop" "$STAGE/usr/lib/shai-installer/assets/gnome-wellbeing-panel.desktop"
install -m 0644 "$ROOT/installer/assets/shai.palette" "$STAGE/usr/lib/shai-installer/assets/shai.palette"
install -m 0644 "$ROOT/installer/README.md" "$STAGE/usr/share/doc/shai-installer/README.md"
install -m 0644 "$ROOT/installer/SETUP_README.md" "$STAGE/usr/share/doc/shai-installer/SETUP_README.md"
install -m 0644 "$ROOT/docs/THIRD_PARTY_NOTICES.md" "$STAGE/usr/share/doc/shai-installer/THIRD_PARTY_NOTICES.md"
install -m 0644 "$ROOT/installer/share/applications/shai-setup.desktop" "$STAGE/usr/share/applications/shai-setup.desktop"
for launcher in shai-home.desktop shai-shapp.desktop shai-health.desktop shai-aia.desktop shai-appearance.desktop; do
    install -m 0644 "$ROOT/installer/share/applications/$launcher" "$STAGE/usr/lib/shai-installer/assets/launchers/$launcher"
done
install -m 0644 "$ROOT/branding/SHAI_Brand_v2/shai-lockup-dark.svg" "$STAGE/usr/share/shai/branding/shai-lockup-dark.svg"
install -m 0644 "$ROOT/branding/SHAI_Brand_v2/shai-wordmark-dark.svg" "$STAGE/usr/share/shai/branding/shai-wordmark-dark.svg"
install -m 0644 "$ROOT/branding/SHAI_Brand_v2/shai-welcome-1200x630.png" "$STAGE/usr/share/shai/branding/shai-welcome-1200x630.png"
install -m 0644 "$ROOT/branding/theme/share/backgrounds/shai/shai-wallpaper-1920x1080.png" "$STAGE/usr/share/shai/branding/shai-wallpaper-1920x1080.png"
install -m 0644 "$ROOT/branding/SHAI_Brand_v2/shai-lockup-dark.svg" "$STAGE/usr/share/icons/hicolor/scalable/apps/shai.svg"
install -m 0644 "$ROOT/branding/theme/share/icons/SHAI/scalable/apps/shai-health.svg" "$STAGE/usr/share/icons/hicolor/scalable/apps/shai-health.svg"
install -m 0644 "$ROOT/branding/theme/share/icons/SHAI/scalable/apps/shai-ai-advisor.svg" "$STAGE/usr/share/icons/hicolor/scalable/apps/shai-ai-advisor.svg"
install -m 0644 "$ROOT/branding/theme/share/themes/SHAI/index.theme" "$STAGE/usr/share/themes/SHAI/index.theme"
install -m 0644 "$ROOT/branding/theme/share/themes/SHAI/gnome-shell/gnome-shell.css" "$STAGE/usr/share/themes/SHAI/gnome-shell/gnome-shell.css"
install -m 0644 "$ROOT/branding/theme/share/themes/SHAI/gtk-4.0/gtk.css" "$STAGE/usr/share/themes/SHAI/gtk-4.0/gtk.css"
install -m 0644 "$ROOT/branding/theme/share/icons/SHAI/index.theme" "$STAGE/usr/share/icons/SHAI/index.theme"
install -m 0644 "$ROOT/branding/theme/share/icons/SHAI/scalable/apps/"*.svg "$STAGE/usr/share/icons/SHAI/scalable/apps/"
install -m 0644 "$ROOT/branding/theme/share/backgrounds/shai/"*.png "$STAGE/usr/share/backgrounds/shai/"

dpkg-deb --root-owner-group --build "$STAGE" "$DIST/$PACKAGE.deb"
(cd "$DIST" && sha256sum "$PACKAGE.deb" > "$PACKAGE.deb.sha256")
dpkg-deb --info "$DIST/$PACKAGE.deb"
printf '\nBuilt:\n  %s\n  %s\n' "$DIST/$PACKAGE.deb" "$DIST/$PACKAGE.deb.sha256"
printf 'Temporary Linux staging root retained for inspection:\n  %s\n' "$STAGE"
