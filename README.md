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

Version `0.14.0` targets Ubuntu Desktop 26.04 on `amd64`. Installing the DEB is
inert: no debloat, theme, policy, or application change occurs until the normal
desktop user launches SHAI Setup, reviews the plan, and approves execution in a
visible Ubuntu terminal with normal sudo authentication.

```bash
sudo apt install ./shai-installer_0.14.0_amd64.deb
shai-setup
```

The current package provides:

- a protected, exact-package Ubuntu debloat workflow;
- SHAI Setup with architecture, smart-home, AI, and offline choices;
- a reversible SHAI desktop theme with corrected SHAI wordmark wallpapers;
- the proxy-based Web Offline toggle;
- SHAPP, SHEALTH and AIA with local backends and approved terminal execution;
- local evidence, before/after benchmarks, logs, and final health checks.
- private shared AIA/Open WebUI context and explicit local memory notes.

Optional applications, Docker services, Home Assistant, AI runtimes, and model
weights are not silently installed by the base package. SHAPP manages approved
app changes and checkbox-based maintenance tasks. Setup stays in the app menu
after completion, without a desktop shortcut or login autostart.

## Install From Public GitHub

Run these commands in a fresh Ubuntu desktop terminal as your normal user:

```bash
sudo apt install curl python3 ca-certificates
curl -fL https://raw.githubusercontent.com/RyanHamze/SHAI/main/install.sh -o shai-install.sh
bash shai-install.sh
```

No GitHub account is required. The entry point verifies the fixed release's
pinned hash, signed GitHub workflow provenance, source commit and DEB identity
before sudo. Nothing is debloated until you approve it in Setup. This is a public
test candidate, not a publisher-GPG-signed APT release. See
[the install guide](docs/INSTALL_FROM_GITHUB.md) for the initial bootstrap trust
boundary, verification details and verify-only mode.

## Build and test

```bash
./installer/build.sh
./tests/test-wave-a-package.sh
```

GitHub Actions builds, tests and hashes the DEB. The existing attestation step
runs only for a public repository. Production APT
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
