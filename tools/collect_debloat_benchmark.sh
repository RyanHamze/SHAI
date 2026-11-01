#!/usr/bin/env bash
# shellcheck disable=SC1091,SC2016

# Standardized, read-only checkpoint collected before and after each debloat wave.

set -u

LABEL="${1:?usage: collect_debloat_benchmark.sh LABEL}"
STAMP="$(date +%Y%m%d-%H%M%S)"

printf '# SHAI debloat benchmark: %s\n\n' "$LABEL"
printf -- '- Collected: `%s`\n' "$(date --iso-8601=seconds)"
printf -- '- Host: `%s`\n' "$(hostname)"
printf -- '- OS: `%s`\n' "$(. /etc/os-release && printf '%s' "$PRETTY_NAME")"
printf -- '- Kernel: `%s`\n' "$(uname -r)"
printf -- '- Boot ID: `%s`\n' "$(cat /proc/sys/kernel/random/boot_id)"
printf -- '- Uptime seconds: `%s`\n' "$(cut -d. -f1 /proc/uptime)"
printf -- '- DPKG packages: `%s`\n' "$(dpkg-query -W -f='${binary:Package}\n' | wc -l)"
printf -- '- Manually marked APT packages: `%s`\n' "$(apt-mark showmanual | wc -l)"
printf -- '- Active Snap names: `%s`\n' "$(snap list 2>/dev/null | awk 'NR>1 {count++} END {print count+0}')"
printf -- '- Running services: `%s`\n' "$(systemctl list-units --type=service --state=running --no-legend --no-pager | wc -l)"
printf -- '- Failed units: `%s`\n' "$(systemctl --failed --no-legend --no-pager | wc -l)"
printf -- '- Listening sockets: `%s`\n' "$(ss -H -lntup | wc -l)"
printf -- '- Load average: `%s`\n' "$(cat /proc/loadavg)"
printf -- '- Processes: `%s`\n' "$(ps -e --no-headers | wc -l)"
printf -- '- Root filesystem: `%s`\n' "$(df -h --output=size,used,avail,pcent / | tail -n1 | xargs)"
printf -- '- Memory: `%s`\n' "$(free -h | awk '/^Mem:/ {printf "total=%s used=%s available=%s",$2,$3,$7}')"
printf -- '- Swap: `%s`\n' "$(free -h | awk '/^Swap:/ {printf "total=%s used=%s free=%s",$2,$3,$4}')"
printf -- '- UFW configured enabled: `%s`\n' "$(awk -F= '/^ENABLED=/{print $2}' /etc/ufw/ufw.conf 2>/dev/null || printf unknown)"
printf -- '- Reboot required: `%s`\n' "$([ -e /var/run/reboot-required ] && printf yes || printf no)"
printf -- '- Collector stamp: `%s`\n\n' "$STAMP"

printf '## Hardware identity\n\n```text\n'
lscpu | grep -E '^(Architecture|CPU\(s\)|Model name|Virtualization):'
free -h
lsblk -e7 -o NAME,SIZE,TYPE,FSTYPE,FSAVAIL,FSUSE%,MOUNTPOINTS
printf '```\n\n## Failed units\n\n```text\n'
systemctl --failed --no-pager
printf '```\n\n## Listening sockets\n\n```text\n'
ss -H -lntup
printf '```\n\n## Package audit\n\n```text\n'
dpkg --audit
printf '```\n'
