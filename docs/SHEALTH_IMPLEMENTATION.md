# SHEALTH implementation

SHEALTH is the read-only SHAI health dashboard installed as `/usr/bin/shai-health`.
The current implementation follows `SHEALTH_OUTLINE.md` and incorporates the
earlier SHAI requirements for local system health, service failures, firewall
visibility, open listeners, offline status, Docker health, and energy estimates.

## Implemented

- GTK 4 interface retaining the existing `shai-health` heart icon.
- Health, Disk, Memory, CPU, Network, Services, Uptime, Energy, Events, and
  Settings tabs.
- Cached host sample every 60 seconds by default. UI refreshes read the cache.
- A root-owned, systemd-sandboxed snapshot collector runs every 30 seconds and
  writes sanitized socket ownership data to `/run/shai/network-snapshot.json`.
- Local SQLite raw samples, hourly rollups, threshold events, and retention.
- Disk/RAM/CPU thresholds, heartbeat display, seven-day hourly heatmap, and
  event banner.
- Compact clickable metric tiles, a rolling 24-hour heartbeat score graph, and
  a rolling 24-hour energy graph. Heartbeat is `100 × (1 - negative checks /
  total checks)`; over 95% is green, 80–95% amber, and below 80% red.
- The Health summary uses a single-width responsive layout, wraps metric/status
  groups, and permanently disables horizontal scrolling.
- Disk, RAM, and CPU pages render rolling 24-hour graphs from SHEALTH's local
  hourly history instead of displaying text-only cached sample rows.
- One local JSON health/energy summary per completed calendar day, exported on
  the first sample after midnight under `~/.local/state/shai/health/daily/`.
- Interface counters, every open listening socket, owning process/PID, likely
  registered purpose, active source-to-destination flows, container context,
  and container network/IP/gateway assignments. Purpose labels are hints and
  never claims about payload contents.
- Managed service status, CPU/memory/PID statistics, endpoints, private network
  addresses, and bounded lifecycle events through SHAI's permanent read-only
  observer. The desktop application never receives the raw engine socket.
- OS/service uptime, failed service signal, local firewall visibility, reboot
  marker, and SHAI web-connectivity mode.
- Offline energy model with configurable idle/max watts, currency, and price per
  kWh. All model-derived values are labelled as estimates.
- Sniffnet detection cached for ten minutes and a normal-user launch button.
  SHEALTH never installs Sniffnet or elevates its privileges.

## Safety boundary

SHEALTH does not install packages, change firewall/network settings, start or
stop containers, restart services, or perform online checks. Settings change
only SHEALTH collection, display, thresholds, retention, and estimates.

The observer image is pinned by digest, has no published port, drops all Linux
capabilities, uses a read-only filesystem, and permanently limits requests to
GET/HEAD for container status, events, info, ping, and version. Attribution and
Apache-2.0 notices are visible under SHEALTH Settings.

## Deferred integrations

GPU, backups, Home Assistant entities, smart-plug metering, VLAN/macvlan
configuration, and approved recovery actions remain separate future integrations.
Their absence is shown as unavailable rather than simulated.
