# SHAI

**Smart Home Automation and AI**

SHAI is an installer add-on for a computer that already runs Ubuntu Desktop.
It helps repurpose that computer as a local smart-home and AI hub: choose your
apps, manage local AI and monitor the computer from SHAI's desktop tools.
It does not install or replace Ubuntu. Ubuntu remains your operating system.

### Individual Apps

You can install AIA, SHEALTH, SHAPP or Metadata Cleaner without applying Setup,
debloating Ubuntu or changing your theme. Download the same installer, then use
`bash install.sh --app aia`, `--app health`, `--app shapp` or `--app metadata`.
The installer verifies the published release first and asks for sudo when needed.
`--app setup` installs Setup alone; no changes are applied until you approve them.

After installation, the desktop SHAI folder contains your app launchers. Missing
apps have an Install entry. Removing AIA preserves shared model files, security
keys, integrations and Open WebUI. Its optional app-only cleanup clears chat and
resets UI preferences, not shared configuration.

## Read Before Installing

**Back up first. After you approve Setup, it can purge selected Ubuntu apps
and their system configuration, change desktop/privacy/sharing settings, and
switch scheduled updates to manual operation.** Review the displayed removal
scope. Setup does not target your personal documents or media, but a backup is
still essential. Uninstalling SHAI does not put removed apps or all settings back.

Current public test release: **0.16.0**. You need **Ubuntu Desktop 26.04.x LTS
on a 64-bit Intel/AMD PC (amd64)**. This package is not for ARM/Raspberry Pi or
32-bit Ubuntu. Optional apps and AI models need additional resources and setup.

## Install In Ubuntu Terminal

Open Terminal on your Ubuntu desktop. Copy and run these lines in order:

```bash
sudo apt install curl python3 ca-certificates
curl -fL https://raw.githubusercontent.com/RyanHamze/SHAI/main/install.sh -o shai-install.sh
bash shai-install.sh
```

`sudo` asks for your Ubuntu administrator password. Type it and press Enter;
password characters normally do not appear. The first line installs download
tools and may ask you to confirm. The next lines download and run SHAI's installer.

Internet is needed for this download, verification and any missing dependencies.
No GitHub account is needed. You can inspect `shai-install.sh` before running it.
Run it as your normal desktop user, not with `sudo bash`; it asks for administrator
permission when required. Do not pipe a download straight into Bash.

The installer verifies the pinned package and signed release-validation
attestation, installs the platform, then opens SHAI Setup. **Installing alone
does not approve cleanup.** Read Setup's choices and approve only when ready.
If verification fails, stop; do not bypass it. Individual smart-home apps and
models are selected later in SHAPP or AIA, not all preinstalled.

[Installation and verification](docs/INSTALL_FROM_GITHUB.md) |
[Using SHAI](docs/USER_GUIDE.md) |
[Downloads](https://github.com/RyanHamze/SHAI/releases) |
[Security](SECURITY.md) |
[Third-party credits and licenses](docs/THIRD_PARTY_NOTICES.md)

## Applications

- **SHAI Setup:** review and approve initial configuration.
- **SHAPP:** select optional applications and maintenance tasks.
- **SHEALTH:** view local resource, service and network information.
- **AIA:** manage local AI models, integrations and supported voice tools.
- **Metadata Cleaner:** approved local ExifTool operations.

Features vary with the installed release, hardware and optional software.
Normal local operation is designed not to require cloud services; explicitly
requested downloads and update verification require internet access. The
browser proxy toggle is not a host-wide firewall or physical air gap.
When scheduled updates are disabled, you must check and apply security updates
manually using SHAPP or Ubuntu's tools.

SHAI and Aabey LLC are not affiliated with or endorsed by Canonical. Ubuntu is
a trademark of Canonical Ltd. SHAI is not an OS, distribution, ISO or replacement
shell. For detailed app instructions and limitations, read the
[SHAI User Manual](docs/USER_GUIDE.md).

## Distribution Repository

This repository contains the public installer entry point, user documentation,
credits, required third-party source/license material and release downloads.
Application development, tests, build/signing operations and internal records
are maintained separately and are not accepted into this public tree.

SHAI application code is not offered under a project-wide open-source license.
Copyright Aabey LLC; no additional license is granted by this repository beyond
applicable distribution/platform terms. Third-party material retains its own
licenses and rights. Distributed packages contain the executable code needed
to run the product; this policy does not claim that code is technically secret.
