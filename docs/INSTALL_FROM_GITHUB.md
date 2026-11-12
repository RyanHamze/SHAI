# Install and verify SHAI

Target: Ubuntu Desktop 26.04.x LTS, amd64. Public release **0.14.0** requires
no GitHub account, token or Git checkout. Back up your system first.

## Open Setup

Run separately as your normal desktop user:

```bash
sudo apt install curl python3 ca-certificates
curl -q --fail --show-error --location --proto '=https' --proto-redir '=https' --max-filesize 1048576 https://raw.githubusercontent.com/RyanHamze/SHAI/main/install.sh --output shai-install.sh
bash shai-install.sh
```

Inspect the script before running it. Do not run it with sudo or pipe a
download into Bash. Trusting this entry point is the initial trust decision:
its embedded pins do not independently authenticate the entry point itself.

To verify without installation or opening Setup:

```bash
bash shai-install.sh --verify-only
```

## What is verified

The entry point downloads a fixed release DEB and its attestation bundle over
HTTPS, then verifies:

- The exact pinned package SHA-256.
- Signed GitHub provenance for `RyanHamze/SHAI`, the recorded release-build
  workflow, release tag and exact source digest, rejecting self-hosted runners.
- Package name, version and amd64 architecture.

The current workflow identity is
`RyanHamze/SHAI/.github/workflows/build-attest-release.yml`; it identifies the
historical signed release build, not a requirement that development files
remain in the current public tree. See
[GitHub's verification reference](https://cli.github.com/manual/gh_attestation_verify).
Offline bundle verification cannot detect later repository/owner name reuse;
the independent artifact/source pins remain required.

If the installed GitHub CLI cannot verify the bundle, the script downloads a
fixed official portable CLI, verifies its pinned hash and uses it temporarily.
Downloads, temporary tooling and trust caches are cleaned up afterward. No
GitHub login is needed. Verification/downloads require internet access, working
DNS/TLS and a correct system clock; this is not an offline installation path.

Only after verification does Ubuntu request sudo authentication to install
the package and any missing dependencies. Setup then opens as your desktop
user. Debloat and configuration require separate approval inside Setup.

Missing assets, signature/hash mismatches or wrong package identity stop the
process. Do not disable the checks or substitute an unpinned package.

## Current public artifact

- File: `shai-installer_0.14.0_amd64.deb`.
- SHA-256: `3a9fa6c11ff5598cf53b0574ef83e19383b9cb5977d01813dd905efe70f784d9`.
- Public attestation sidecar: `shai-installer_0.14.0_amd64.deb.intoto.jsonl`.
- [Release downloads](https://github.com/RyanHamze/SHAI/releases/tag/v0.14.0).

This is a test release, not a claim of universal hardware support or
publisher-GPG-signed APT metadata. See [Security](../SECURITY.md).
