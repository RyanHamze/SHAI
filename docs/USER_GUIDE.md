# SHAI User Manual

For SHAI 0.16.0 test release on Ubuntu Desktop 26.04.x LTS, 64-bit amd64.
SHAI adds local smart-home and AI tools; Ubuntu remains your operating system.
This is test software. Back up before applying Setup or changing applications.

## Application And Service Choices

- Home Assistant is offered under SHAPP Architecture as a Docker installation.
  Native Home Assistant Core installation is not offered.
- Open WebUI has separate native and Docker routes. Do not install both on port
  3000. Existing data and containers are never automatically migrated.
- Native Gladys is experimental, core-only; Docker-managed integrations are not
  available in that route. Use Docker when those integrations are needed.
- Immich uses its own Compose project and requires at least 6 GB host RAM.
  It does not replace the existing SHAI containers or Portainer configuration.
- VPN clients require provider accounts, internet and explicit connection setup.
  Installing a VPN client does not establish protection. hide.me's client is
  staged without privileged route/DNS changes; activation requires review.
- Jellyfin, Navidrome and Calibre-Web need library and account configuration.
  Resource figures are planning estimates; media and databases need extra space.
- qBittorrent and Transmission are native Ubuntu torrent options. A maintained,
  verified Ubuntu 26 installer for legacy microTorrent is not provided.

SHEALTH Status shows the host services; Docker has container health, local links
and confirmed actions. The header refresh icon updates readings manually while
background sampling continues. Stop/Kill/Remove are not read-only operations.
Portainer's setup-key button is shown only when initial admin setup is required.
The web toggle controls proxy-aware browsing, not all network access or an air gap.
Browser shortcuts follow your default browser rather than forcing Firefox.

[Install SHAI](INSTALL_FROM_GITHUB.md) | [Security](../SECURITY.md) |
[Component credits](THIRD_PARTY_NOTICES.md) | [Home](../README.md)

## Start Here

1. Install the platform using the verified installer. Installation alone does
   not debloat or reconfigure Ubuntu.
2. In SHAI Setup, review cleanup and configuration choices. Approve only after
   making a recoverable backup and understanding the changes.
3. Use SHAPP to choose optional applications, AIA for local AI, and SHEALTH for
   monitoring and troubleshooting.

Apps remain in Ubuntu's application menu. Approved privileged operations open
a visible terminal and may request your normal administrator password.

## SHAI Setup

Setup repurposes an existing Ubuntu installation. It is not an Ubuntu installer,
replacement operating system or disk-encryption wizard.

Depending on what is installed, cleanup can purge selected office, games,
chat/media, printing, scanning, modem, domain-login, remote-desktop, help,
dictionary and theme packages. Purging can delete those packages' system
configuration files. Required Ubuntu desktop, login, networking, package-manager,
accessibility, kernel and boot components are protected from SHAI removal.

Setup applies approved theme, desktop, privacy and manual-update settings. This
can disable notifications, location/reporting controls, sharing and scheduled
update activity. Ubuntu still supplies OS, driver, firmware and security updates;
you must apply manual updates when automatic activity is disabled.

Personal documents and media are not cleanup targets. This does not replace a
backup. Removing SHAI later does not restore removed Ubuntu apps or undo every
changed setting. Review the on-screen cleanup scope before approval.

Choose the main architecture and smart-home/AI intent in Setup. Individual apps
are selected later in SHAPP. Apply opens a separate terminal for the approved
changes. Wait for its result; read the error and local log if it stops. Earlier
steps may have completed even when the overall operation failed.

After success, open SHAPP from the completion screen. Setup stays in the app
menu, but its completed desktop shortcut is removed. It does not open at every
login. Installing the platform or merely opening Setup does not approve cleanup.

## SHAPP: Apps And Updates

Recommended suggests apps. Optional lists additional tools. Currently Installed
discovers manageable installed applications. A detected package does not prove
its service or integration is configured correctly.

Check an app to stage installation. Uncheck a supported installed app to stage
removal. Pending Changes stays across tabs; its X cancels one pending action.
Nothing in the cart runs until Apply.

Review installations, removals and estimated resources first. Disk/RAM figures
are planning estimates, not guaranteed reservations. Dependencies/downloads can
need more space. Protected, unsupported or over-capacity choices are disabled.
Use Ubuntu's app manager for components outside SHAI's management boundary.

Apply opens a terminal and executes the approved commands. Ubuntu may ask for
sudo. Downloads require internet access. An error stops the operation, but
earlier changes can remain. Results link to the local daily-log folder; actions
are appended to a date-based log.

### Architecture

Direct Ubuntu installation is the simple default. Advanced Docker uses Docker
Engine/Compose with separate main-app containers and persistent storage.
Changing architecture affects future installation choices; it does not migrate
existing applications, credentials or data automatically.

Not every app supports both modes. This release's managed Home Assistant
installation uses Advanced Docker. It is Home Assistant Container, not Home
Assistant OS/Supervisor or its add-on store. Direct Ubuntu mode does not promise
a host-native installer for every catalog item. Read the app's availability.

Docker networks, coordinator devices, MQTT credentials and smart-home pairing
need separate configuration. Installation does not mean discovery or device
control is ready. Stable serial-device identifiers are used where supported.

### Update All

Maintenance checkboxes join the same cart. Refresh Ubuntu package lists before
upgrading installed packages. Other choices cover unused-dependency cleanup,
obsolete downloads, Snap updates, existing Flatpak updates, package-health
checks, firmware metadata and firmware installation.

The dependency-aware `apt dist-upgrade` task resolves package dependencies. It
does not upgrade the computer to a new Ubuntu release.

Firmware installation can change hardware firmware and may require AC power,
a backup and a later reboot. Some VMs/devices have no supported update; a skip
is not an error. Review the target and result before proceeding.

The Ubuntu App Store tab opens Ubuntu's separate store. Opening it does not
apply SHAPP's pending changes.

### Monitoring Tools

PowerJoular monitors supported CPU/process power counters or estimates. nvtop
shows supported GPU utilization and power sensors. Neither guarantees a complete
whole-PC measurement, particularly inside a VM. btop and Glances provide wider
resource views; MangoHud is an optional graphics-workload overlay.

System Bridge and Go Hass Agent can expose host sensors to Home Assistant.
Go Hass Agent is an independent Linux alternative, not Windows HASS.Agent.
NUT supports compatible UPS battery backups. Pairing, listeners, permissions,
UPS drivers and shutdown behavior need separate configuration. Installing these
tools does not automatically configure a home energy system.

## SHEALTH: Local Monitoring

Health shows high-level CPU, memory and storage checks, including configured
volumes, inodes and read-only/unavailable states. Open Resources launches the
installed Ubuntu-compatible resource monitor for detailed graphs/processes.

Network shows interfaces, listeners and observed connections. Network Inspection
groups known connections by app and scope, including local, internet, loopback
and Docker. Details show available endpoints/owners; private history records
previous observations. Counters are known socket counters where available,
not a complete packet audit or guaranteed bandwidth attribution. Missing data
is not zero traffic. The Sniffnet panel launches advanced monitoring or opens
SHAPP with an online-install warning if it is missing.

Status shows host boot time, uptime, firewall status, detected services and
available active durations. SSH, HA, MQTT, Docker and supported services appear
where detected. Container details and confirmed actions live in Docker. No matching unit
does not prove an app is absent: manual processes, remote installations and
inaccessible status may not be assessed.

### Energy

The summary shows estimated power, monitored energy since this boot, recent
usage and estimated cost. It does not invent consumption during unobserved
periods. The rolling 24-hour chart uses 15-minute bars and half-hour local-time
labels, including partial end intervals. Point at a bar for exact time, Wh,
average power and observation coverage. Gray means unobserved, not zero usage.

Choose currency and your actual price per kWh in Settings. The list is offline.
Changing currency does not convert the price or historical costs: enter the
correct local rate yourself. The CPU-utilization model is an estimate, not a
physical meter or complete carbon-footprint calculation.

Energy recommends going to the shop and installing PowerJoular and nvtop there.
For home devices, use Home Assistant's Energy Dashboard with compatible energy
sensors. When a local HA service/container is detected, its local Energy link
appears. Detection does not prove the service is running or energy sources are
configured. The separate documentation link requires internet access.

The energy-log link opens local daily exports. These and the chart cover
observed periods, not a billing-grade usage record.

### Events And Settings

Events distinguishes Active, Recovered and Recorded historical failures.
Available details include values/thresholds, service exit results, restart
counts, container failures and safe summaries of app/journal errors. Historical
errors do not establish a current fault. Coverage is not universal: unlogged
crashes, missing sensors and SMART diagnostics are not fully assessed. Inspect
original local logs when the precise cause is unavailable.

Refresh preserves scroll position where remaining content allows it. Settings
controls SHEALTH thresholds, sampling, retention, history, notifications and
energy assumptions. Save locally; reopen SHEALTH for changed sampling intervals
to take full effect.

Reset settings to defaults asks for confirmation and affects SHEALTH only. It
does not immediately erase history/logs; restored retention rules apply to future
collection. It does not reset Ubuntu or other SHAI apps.

## AIA: Local AI Center

Chat uses the selected active local model after its runtime/model are installed
and running. A displayed name alone is not proof of successful inference. Read
service/model errors. Small models have limited reasoning and tool-use ability;
no cloud fallback or unrestricted control is promised.

Models manages supported downloads, local imports, removal and the active
default. The active highlight identifies the selected model, not just the
recommendation. Capacity checks may disable unsupported choices. Enable Allow
approved online installs in Settings before online model/tool downloads.
Chat-history saving is separate and optional. Downloads need approval and run
visibly; Ubuntu may request sudo. Importing a local model is not an online
download. Formats, runtimes, storage, model activation and context size matter.

Hardware reports detected CPU, RAM, GPU/VRAM and storage information and model
guidance for a shared computer. Recommendations are estimates, not benchmarks or
guarantees that every model fits every context size.

Voice & TTS manages supported recognition, wake-word and speech-synthesis tools.
Use available test/use controls for installed tools. Engines may still require
model files, audio devices and permissions. Installation does not imply
continuous microphone listening.

Integrations separates installation, configuration and connection-test status.
Read each test result: an open port, executable or folder is not a full API
test. Use credential fields, not notes, for tokens/passwords. Custom integrations
support user-defined fields and approved terminal test scripts. Scripts can
affect the machine; inspect them first. Their terminal logs are not a permanent
automatic integration pass/fail monitor.

Settings controls online installs, chat history and saved reference notes.
The latest 100 notes persist locally. Shared non-sensitive context helps
compatible local AI sessions read system/app/integration summaries. This is
reference information, not model training or permission to execute instructions
embedded in data. Secrets and raw chat/log text are not intended for shared
context. Keep credentials out of notes and public reports.

Activity shows local audit logs. Control Center, at the menu's bottom, offers
supported broker-mediated actions and approval requests. It is not an
unrestricted root terminal. Review each requested action; unsupported actions
or missing integrations cannot be assumed to work.

Open WebUI is an optional separate frontend in SHAPP. Connections, shared context
and control permissions require appropriate local configuration. Installing a
UI does not grant models access to every file, credential, command or device.

## Metadata, Connectivity And Removal

Metadata Cleaner uses ExifTool. Review file selection, folder contents,
recursive subfolders and backup options before approval. Original backups can
retain sensitive metadata. Some formats/fields cannot be fully rewritten;
keep backups and inspect the results.

The desktop web/internet toggle changes proxy behavior for compatible clients.
It is not a host-wide firewall, guaranteed network isolation or physical air gap.
Optional apps may have their own networking. Normal local operations require no
cloud login; approved downloads, verification and online docs require internet.
Keep the clock accurate for TLS and signatures.

Use SHAPP for supported optional-app removal. Use Ubuntu's package manager for
the platform, for example `sudo apt remove shai-installer`. Removal does not
restore purged Ubuntu apps, reverse all settings or necessarily remove
third-party software/data. Use your backup for full rollback.

Inspect local logs before sharing a redacted support report. Never upload
credentials, complete configuration dumps or personal data to a public issue.
See [Security](../SECURITY.md).
