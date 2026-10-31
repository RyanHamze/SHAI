#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

rm -f /etc/apt/apt.conf.d/99-shai-manual-updates

systemctl unmask \
  apt-daily.timer \
  apt-daily-upgrade.timer \
  update-notifier-download.timer \
  update-notifier-motd.timer \
  fwupd-refresh.timer \
  snapd.snap-repair.timer

systemctl enable --now \
  apt-daily.timer \
  apt-daily-upgrade.timer \
  update-notifier-download.timer \
  update-notifier-motd.timer \
  fwupd-refresh.timer \
  snapd.snap-repair.timer

snap refresh --unhold
echo "Ubuntu automatic update schedules restored."
