# Current decisions

Updated 2026-11-01; these supersede conflicting October 24 plan details.

- Claude involvement is stopped at Ryan's request after hitting its usage limit. Rebranding is deferred. Preserve received research/reference assets, but do not assign further Claude work or require artwork completion before installer work.

- Strict offline policy: no online checks, probes or downloads unless specifically authorized. Label operations by online source and scope permission to the action; scheduled online checks/downloads/installs default off. See NETWORK_POLICY.md. LAN-only access requires approved local integrations; true air-gapped mode also blocks LAN. This policy is recorded, not yet implemented or tested.

- Name is SHAI, Smart Home Automation and AI; not an OS or shell.
- Target test installation: full Ubuntu 26.04.1 LTS 64-bit VM at `shai-vm`. Continue verifying actual release/architecture before claiming support.
- Ubuntu owns OS identity, terminal, kernel, repositories, drivers and security/package update mechanisms. SHAI maintains its software, configurations, containers and AI.
- Keep Ubuntu automatic date and time synchronization enabled. Setup may perform the one-time correction, but normal SHAPP Apply operations must not force synchronization or change time settings. This is separate from the manual software-update policy.
- Installer locally inspects hardware/software, explains recommendations, offers default/recommended/optional choices and previews changes for approval before visible execution.
- User requests suppressing routine notifications and disabling automatic update installation in the approved appliance configuration. Present package/security/firmware updates and app/container/runtime updates in SHAI, distinguish checking from installing, and preserve critical alerts. This supersedes the plan's older recommendation to preserve automatic-update settings by default.
- AI selector and runtime run on Ubuntu host; offer No AI and reserve automation resources.
- Application dashboard includes installed/available/install/remove/update views.
- SHAPP includes an Architecture tab. Setup seeds `direct-host` or `managed-stack`; changing it is an immediate live-autosave setting, requires an explicit warning confirmation, and restarts SHAPP to rebuild the catalog. It affects future installs only and never silently installs Docker or migrates existing services. An app is selectable only when the active architecture has a validated install and uninstall backend.
- SHEALTH is a normal-user, read-only GTK 4 monitor. It samples host health every 60 seconds by default, stores local SQLite raw/hourly history, and performs detailed socket or Docker reads only while their tabs are open. It never remediates, installs, elevates, or contacts an online service.
- Direct Ubuntu installation is the default architecture. Advanced mode uses Docker Engine plus Compose, one main service per container, persistent per-service storage, stable `/dev/serial/by-id` Zigbee mapping, an internal `shai-automation` bridge, and a separate Home Assistant outbound bridge. SHAI enables no Home Assistant discovery and publishes no Docker web interface beyond loopback by default.
- SHEALTH Network reads a sanitized root-owned snapshot every 30 seconds and shows open ports, process/PID ownership, likely purpose, source/destination flows, and container network addresses. The collector observes metadata only and never payload contents.
- Debloat after inspecting the full installation and dependency impacts. Preserve working login, desktop, networking, terminal, security and recovery.
- User wants simple Home Assistant deployment. The settled Advanced design is one managed Compose project with separate service containers and persistent storage; direct-host Ubuntu remains the default.
- No shared shai/shai credentials or silent conversion of the development host.
- New branding goes under branding/assets. Original reference art stays unchanged.
