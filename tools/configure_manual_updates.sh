#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

cat >/etc/apt/apt.conf.d/99-shai-manual-updates <<'EOF'
// SHAI offline-first policy: retain Ubuntu update tools, disable scheduled checks.
APT::Periodic::Enable "0";
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Download-Upgradeable-Packages "0";
APT::Periodic::Unattended-Upgrade "0";
APT::Periodic::AutocleanInterval "0";
EOF

units=(
  apt-daily.timer
  apt-daily-upgrade.timer
  update-notifier-download.timer
  update-notifier-motd.timer
  fwupd-refresh.timer
  snapd.snap-repair.timer
)

for unit in "${units[@]}"; do
  if systemctl cat "$unit" >/dev/null 2>&1; then
    systemctl disable --now "$unit" >/dev/null 2>&1 || true
    systemctl mask "$unit"
  else
    printf 'Not present, skipped: %s\n' "$unit"
  fi
done

# A system-wide hold prevents automatic Snap refreshes. Explicit `snap refresh`
# remains available for a user-approved update session.
snap refresh --hold=forever

echo "SHAI manual-update policy applied."
echo "Manual commands remain available:"
echo "  sudo apt update && sudo apt upgrade"
echo "  sudo snap refresh"
echo "  sudo fwupdmgr refresh && sudo fwupdmgr get-updates"
