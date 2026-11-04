# SHAI

SHAI means **Smart Home Automation and AI**. It is an explicit, guided
installer that configures an existing supported Ubuntu Desktop installation as
a local-first home appliance. Ubuntu remains the operating system and retains
ownership of its kernel, repositories, drivers, firmware, terminal, package
manager, and OS security updates.

SHAI is not an operating system, Ubuntu distribution, ISO, or replacement
shell. It is not affiliated with or endorsed by Canonical. Ubuntu is a
trademark of Canonical Ltd.

## Current package

Version `0.13.1` targets Ubuntu Desktop 26.04 on `amd64`. Installing the DEB is
inert: no debloat, theme, policy, or application change occurs until the normal
desktop user launches SHAI Setup, reviews the plan, and approves execution in a
visible Ubuntu terminal with normal sudo authentication.

```bash
sudo apt install ./shai-installer_0.13.1_amd64.deb
shai-setup
```

The current package provides:

- a protected, exact-package Ubuntu debloat workflow;
- SHAI Setup with architecture, smart-home, AI, and offline choices;
- a reversible SHAI desktop theme with corrected SHAI wordmark wallpapers;
- the proxy-based Web Offline toggle;
- SHAPP, SHEALTH and AIA with local backends and approved terminal execution;
- local evidence, before/after benchmarks, logs, and final health checks.

Optional applications, Docker services, Home Assistant, AI runtimes, and model
weights are not silently installed by the base package. SHAPP manages approved
app changes and checkbox-based maintenance tasks. Setup stays in the app menu
after completion, without a desktop shortcut or login autostart.

## Install From Private GitHub

Run these commands in a fresh Ubuntu desktop terminal as your normal user:

```bash
sudo apt -o Acquire::ForceIPv4=true update
sudo apt -o Acquire::ForceIPv4=true install -y gh git curl python3 ca-certificates
gh auth login --hostname github.com --web --git-protocol https
gh auth setup-git && gh repo clone RyanHamze/SHAI -- --ipv4 --depth 1 && bash SHAI/install.sh
```

The private repository requires GitHub access. The downloaded entry point
verifies the fixed candidate's pinned checksum before asking for sudo and
opening Setup. Nothing is debloated until you approve it in Setup. This test
channel is not a publisher-signed APT release. For artifact expiry, frozen
commit instructions and verify-only mode, see [the install guide](docs/INSTALL_FROM_GITHUB.md).

## Build and test

```bash
./installer/build.sh
./tests/test-wave-a-package.sh
```

GitHub Actions builds, tests and hashes the DEB. The existing attestation step
runs only for a public repository; this repository remains private. Production APT
metadata additionally requires the offline SHAI archive signature. Private
keys, passphrases, and hardware-token PINs are never stored in this repository
or GitHub Actions.

Start with [START_HERE.md](START_HERE.md), then review
[the Setup specification](docs/WAVE_A_SETUP_SPEC.md),
[the application catalog](docs/SHAI_APP_APPROVAL_CATALOG.md), and
[SECURITY.md](SECURITY.md).

No project-wide open-source license has been selected. Copyright Aabey LLC; no
license is granted beyond GitHub's applicable terms until a LICENSE file is
published. Bundled third-party-derived theme material retains its own license
notice under `branding/theme/`.
