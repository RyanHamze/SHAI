#!/usr/bin/env bash

# Read-only Ubuntu baseline collector. Run as root after an approved update.
# It inventories system state without copying credential stores or private keys.

set -u
umask 077

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="${1:-/tmp/shai-vm-inventory-${STAMP}}"
TARGET_USER="${SUDO_USER:-shai}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
export TARGET_USER TARGET_HOME

mkdir -p "$OUT"/{apps,config,hardware,network,services,security,storage,user}

capture() {
    local relative="$1"
    shift
    {
        printf '$'
        printf ' %q' "$@"
        printf '\n\n'
        "$@"
    } >"$OUT/$relative" 2>&1 || true
}

capture_shell() {
    local relative="$1"
    local command="$2"
    {
        printf '$ %s\n\n' "$command"
        bash -o pipefail -c "$command"
    } >"$OUT/$relative" 2>&1 || true
}

capture config/identity.txt hostnamectl
capture config/os-release.txt cat /etc/os-release
capture config/kernel-command-line.txt cat /proc/cmdline
capture config/time.txt timedatectl
capture config/locale.txt localectl
capture config/environment.txt sh -c 'printf "LANG=%s\nDESKTOP=%s\n" "${LANG:-}" "${XDG_CURRENT_DESKTOP:-}"'
capture config/alternatives.txt update-alternatives --get-selections
capture config/sysctl-effective.txt sysctl -a
capture_shell config/sysctl-files.txt 'for f in /etc/sysctl.conf /etc/sysctl.d/*.conf; do [ -f "$f" ] || continue; printf "\n### %s\n" "$f"; cat "$f"; done'
capture_shell config/system-environment-files.txt 'for f in /etc/environment /etc/default/locale /etc/profile /etc/bash.bashrc; do [ -f "$f" ] || continue; printf "\n### %s\n" "$f"; cat "$f"; done'
capture_shell config/cron-file-manifest.txt 'find /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.monthly /etc/cron.weekly /var/spool/cron -xdev -printf "%M\t%u\t%g\t%s\t%p\n" 2>/dev/null | sort'
capture config/etc-file-manifest.txt find /etc -xdev -type f -printf '%M\t%u\t%g\t%s\t%TY-%Tm-%Td %TH:%TM\t%p\n'
capture_shell config/apt-sources.txt 'for f in /etc/apt/sources.list /etc/apt/sources.list.d/*.list /etc/apt/sources.list.d/*.sources; do [ -f "$f" ] || continue; printf "\n### %s\n" "$f"; sed -E "s#(https?://)[^/@[:space:]]+:[^/@[:space:]]+@#\1[credentials-redacted]@#g" "$f"; done'
capture config/apt-policy.txt apt-cache policy
capture_shell config/automatic-update-settings.txt 'grep -RhsE "^[[:space:]]*[^/#].*" /etc/apt/apt.conf.d/10periodic /etc/apt/apt.conf.d/20auto-upgrades /etc/apt/apt.conf.d/50unattended-upgrades 2>/dev/null'
capture_shell config/boot-files.txt 'for f in /etc/default/grub /etc/fstab /etc/crypttab; do [ -f "$f" ] || continue; printf "\n### %s\n" "$f"; cat "$f"; done'

capture apps/dpkg-packages.tsv dpkg-query -W -f '${binary:Package}\t${Version}\t${Architecture}\t${db:Status-Abbrev}\t${Installed-Size}\t${binary:Summary}\n'
capture apps/apt-manual.txt apt-mark showmanual
capture apps/apt-holds.txt apt-mark showhold
capture apps/apt-upgradable-from-current-cache.txt apt list --upgradable
capture apps/snaps.txt snap list --all
capture_shell apps/flatpaks.txt 'command -v flatpak >/dev/null && flatpak list --columns=application,ref,version,installation || echo "Flatpak is not installed"'
capture_shell apps/desktop-applications.tsv 'find /usr/share/applications "${TARGET_HOME:-/nonexistent}/.local/share/applications" -maxdepth 1 -type f -name "*.desktop" -printf "%p\n" 2>/dev/null | sort'
capture_shell apps/appimages.txt 'find /opt /usr/local "${TARGET_HOME:-/nonexistent}" -xdev -type f \( -iname "*.AppImage" -o -iname "*.appimage" \) -printf "%p\t%s bytes\n" 2>/dev/null | sort'
capture_shell apps/python-packages.txt 'python3 -m pip list 2>/dev/null || echo "No system pip inventory available"'
capture_shell apps/pipx.txt 'command -v pipx >/dev/null && sudo -H -u '"$TARGET_USER"' pipx list || echo "pipx is not installed"'
capture_shell apps/npm-global.txt 'command -v npm >/dev/null && npm --global list --depth=0 || echo "npm is not installed"'
capture_shell apps/container-tools.txt 'for c in docker podman incus lxc virsh; do command -v "$c" 2>/dev/null || true; done'
capture_shell apps/docker-state.txt 'if command -v docker >/dev/null; then docker version; docker ps -a; docker image ls; docker volume ls; docker network ls; else echo "Docker is not installed"; fi'

capture hardware/cpu.txt lscpu
capture hardware/proc-cpuinfo.txt cat /proc/cpuinfo
capture hardware/memory.txt free -h
capture hardware/proc-meminfo.txt cat /proc/meminfo
capture hardware/dmi.txt dmidecode
capture hardware/pci.txt lspci -nnk
capture hardware/usb.txt lsusb -v
capture hardware/kernel-modules.txt lsmod
capture hardware/firmware-devices.txt fwupdmgr get-devices
capture_shell hardware/gpu.txt 'lspci -nnk | grep -A4 -Ei "VGA|3D|Display"; command -v nvidia-smi >/dev/null && nvidia-smi || true'
capture_shell hardware/lshw-sanitized.txt 'command -v lshw >/dev/null && lshw -sanitize || echo "lshw is not installed"'
capture hardware/udev-database.txt udevadm info --export-db
capture hardware/kernel-log.txt journalctl -k -b --no-pager
capture_shell hardware/driver-recommendations.txt 'command -v ubuntu-drivers >/dev/null && ubuntu-drivers devices || echo "ubuntu-drivers is not installed"'
capture_shell hardware/power.txt 'command -v powerprofilesctl >/dev/null && powerprofilesctl; for b in /sys/class/power_supply/*; do [ -e "$b" ] || continue; printf "\n### %s\n" "$b"; grep -Hs . "$b"/{type,status,capacity,technology,manufacturer,model_name} 2>/dev/null; done'

capture storage/block-devices.txt lsblk -e7 -o NAME,PATH,SIZE,TYPE,FSTYPE,FSVER,LABEL,UUID,FSAVAIL,FSUSE%,MOUNTPOINTS
capture storage/filesystems.txt df -hT
capture storage/mounts.txt findmnt --real
capture storage/swap.txt swapon --show --output NAME,TYPE,SIZE,USED,PRIO

capture network/addresses.txt ip -details address
capture network/link-statistics.txt ip -s -details link
capture network/routes.txt ip route show table all
capture network/rules.txt ip rule show
capture network/neighbors.txt ip neigh show nud all
capture network/multicast-membership.txt ip maddress show
capture network/resolver.txt resolvectl status
capture network/network-manager.txt nmcli -f NAME,UUID,TYPE,DEVICE,AUTOCONNECT connection show
capture network/network-manager-general.txt nmcli general status
capture network/network-manager-devices.txt nmcli -f GENERAL,IP4,IP6 device show
capture_shell network/netplan-sanitized.txt 'if command -v netplan >/dev/null; then netplan get 2>/dev/null | sed -E "s/^([[:space:]]*(password|psk|private-key-password|token)[[:space:]]*:).*/\1 [redacted]/I"; else echo "netplan is unavailable"; fi'
capture_shell network/name-service-files.txt 'for f in /etc/hosts /etc/hostname /etc/nsswitch.conf /etc/resolv.conf; do [ -e "$f" ] || continue; printf "\n### %s\n" "$f"; cat "$f"; done'
capture_shell network/ethernet-details.txt 'for dev in /sys/class/net/*; do name="${dev##*/}"; [ "$name" = lo ] && continue; printf "\n### %s\n" "$name"; command -v ethtool >/dev/null && ethtool "$name" 2>&1 || echo "ethtool is not installed"; done'
capture network/listening-ports.txt ss -H -lntup
capture network/interfaces.txt networkctl list

capture services/unit-files.txt systemctl list-unit-files --no-pager
capture services/all-services.txt systemctl list-units --type=service --all --no-pager
capture services/running-services.txt systemctl list-units --type=service --state=running --no-pager
capture services/failed-units.txt systemctl --failed --no-pager
capture services/timers.txt systemctl list-timers --all --no-pager
capture services/sockets.txt systemctl list-sockets --all --no-pager
capture services/default-target.txt systemctl get-default
capture services/boot-time.txt systemd-analyze
capture services/boot-blame.txt systemd-analyze blame
capture services/boot-critical-chain.txt systemd-analyze critical-chain
capture services/user-unit-files.txt systemctl --user --global list-unit-files --no-pager
capture_shell services/reboot-required.txt 'if [ -f /var/run/reboot-required ]; then cat /var/run/reboot-required; cat /var/run/reboot-required.pkgs 2>/dev/null; else echo "No reboot-required marker"; fi'

capture security/ufw.txt ufw status verbose
capture security/nftables.txt nft list ruleset
capture security/iptables-v4.txt iptables-save
capture security/iptables-v6.txt ip6tables-save
capture security/apparmor.txt aa-status
capture security/secure-boot.txt mokutil --sb-state
capture security/ssh-effective-config.txt sshd -T
capture_shell security/sudoers-file-list.txt 'find /etc/sudoers.d -maxdepth 1 -type f -printf "%M\t%u\t%g\t%p\n" 2>/dev/null | sort'
capture security/sudo-access.txt sudo -l -U "$TARGET_USER"
capture security/login-defs-active.txt sh -c "grep -Ev '^[[:space:]]*(#|$)' /etc/login.defs"
capture security/account-password-status.txt passwd -Sa
capture_shell security/pam-file-manifest.txt 'find /etc/pam.d -maxdepth 1 -type f -printf "%M\t%u\t%g\t%s\t%p\n" | sort'
capture_shell security/security-services.txt 'for unit in apparmor auditd fail2ban ufw unattended-upgrades; do printf "\n### %s\n" "$unit"; systemctl is-enabled "$unit" 2>&1 || true; systemctl is-active "$unit" 2>&1 || true; done'
capture_shell security/file-capabilities.txt 'command -v getcap >/dev/null && getcap -r /usr /opt 2>/dev/null || echo "getcap is unavailable"'
capture security/setuid-setgid-files.txt find / -xdev -type f -perm /6000 -printf '%M\t%u\t%g\t%s\t%p\n'
capture security/world-writable-directories.txt find / -xdev -type d -perm -0002 -printf '%M\t%u\t%g\t%p\n'
capture_shell security/auth-log-summary.txt 'journalctl -b -u ssh --no-pager --output=short-iso | tail -n 250'

capture user/accounts.txt getent passwd
capture user/groups.txt getent group
capture user/logged-in.txt loginctl list-users
capture user/account-status.txt passwd -Sa
capture user/lastlog.txt lastlog
capture user/recent-logins.txt last -a -n 100
capture_shell user/identity-details.txt 'while IFS=: read -r name _ uid gid gecos home shell; do printf "\n### %s\nuid=%s gid=%s gecos=%s home=%s shell=%s\n" "$name" "$uid" "$gid" "$gecos" "$home" "$shell"; id "$name" 2>/dev/null || true; done </etc/passwd'
capture_shell user/home-directory-metadata.txt 'find /home -mindepth 1 -maxdepth 2 -printf "%M\t%u\t%g\t%s\t%p\n" 2>/dev/null | sort'
capture_shell user/autostart-files.txt 'find /etc/xdg/autostart "${TARGET_HOME:-/nonexistent}/.config/autostart" -maxdepth 1 -type f -name "*.desktop" -printf "%p\n" 2>/dev/null | sort'
capture_shell user/gnome-extensions.txt 'command -v gnome-extensions >/dev/null && sudo -H -u '"$TARGET_USER"' gnome-extensions list --enabled || echo "GNOME extension tool is unavailable"'
capture_shell user/dconf.ini 'if command -v dconf >/dev/null; then sudo -H -u '"$TARGET_USER"' dconf dump /; else echo "dconf is unavailable"; fi'

{
    printf 'SHAI Ubuntu VM inventory\n'
    printf 'Collected: %s\n' "$(date --iso-8601=seconds)"
    printf 'Host: %s\n' "$(hostname)"
    printf 'Target user: %s\n' "$TARGET_USER"
    printf 'Collector: %s\n' "$0"
    printf 'Scope: installed software and operational configuration; credential stores, private keys, tokens, browser profiles, and saved network secrets excluded.\n'
} >"$OUT/README.txt"

(cd "$OUT" && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum >SHA256SUMS)
chmod -R go-rwx "$OUT"
printf '%s\n' "$OUT"
