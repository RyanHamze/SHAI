# SHAI

**Smart Home Automation and AI** for an existing Ubuntu Desktop installation.
Ubuntu remains your operating system. SHAI is not an OS, distribution, ISO or
replacement shell. SHAI and Aabey LLC are not affiliated with or endorsed by
Canonical. Ubuntu is a trademark of Canonical Ltd.

## Install

Current public test release: **0.14.0**, Ubuntu Desktop 26.04, amd64.
Back up your system before using Setup. In your normal desktop terminal:

```bash
sudo apt install curl python3 ca-certificates
curl -fL https://raw.githubusercontent.com/RyanHamze/SHAI/main/install.sh -o shai-install.sh
bash shai-install.sh
```

Inspect the downloaded script before running it. Do not run it with sudo or
pipe a download into Bash. It verifies the pinned release before asking for
administrator authentication. Installing the package does not debloat Ubuntu;
Setup explains and requests approval for those changes separately.

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
