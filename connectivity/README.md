# SHAI web connectivity prototype

This prototype makes proxy-aware applications web-offline by default while preserving common private-LAN and `.local` destinations for Home Assistant. Firefox is forced to follow the GNOME system proxy through its supported enterprise policy.

Install paths:

- `bin/shai-web-connectivity-toggle` -> `/usr/local/bin/`
- `share/applications/shai-web-connectivity-toggle.desktop` -> `/usr/share/applications/` and the user's Desktop
- `etc/dconf/db/local.d/20-shai-web-offline` -> `/etc/dconf/db/local.d/`, followed by `dconf update`
- `etc/dconf/profile/user` -> `/etc/dconf/profile/user`, so current and future users read the SHAI system database
- `etc/firefox/policies/policies.json` -> `/etc/firefox/policies/policies.json`

The toggle does not require root. Offline mode points HTTP, HTTPS, FTP and SOCKS proxy settings at closed loopback port 1. Online mode sets GNOME proxy mode to `none`.

This is not firewall enforcement. Software that ignores the GNOME proxy can still reach the internet. Do not describe this control as air-gapped or as a complete host internet block. SHAI still needs a separately tested firewall-backed LAN-only mode covering host processes, containers, DNS, IPv4 and IPv6.
