# Install and verify SHAI

Target: Ubuntu Desktop 26.04.x LTS, amd64. Public release **0.16.1** requires
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
- A signed release-validation attestation for `RyanHamze/SHAI`, its recorded
  validation workflow and exact commit, release tag and required checks,
  rejecting self-hosted runners. A mismatched signed policy also stops install.
- Package name, version and amd64 architecture.

The current workflow identity is
`RyanHamze/SHAI/.github/workflows/public-distribution.yml`, pinned to
`7ff54474718ea7d8ef7fb2b62f13a50b91d72a52` for this release. The custom predicate
is `https://aabeyllc.com/shai/release-validation/v1`. It confirms package
identity, checksum, inert install controls, application hashes and public
payload checks. It does not claim a public-source build or independent source
review. See
[GitHub's verification reference](https://cli.github.com/manual/gh_attestation_verify).
Offline bundle verification cannot detect later repository/owner name reuse;
the independent artifact and workflow-commit pins remain required.

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

- File: `shai-installer_0.16.1_amd64.deb`.
- SHA-256: `526f3fef3109259424481df4e21981a41b842b4f41a39a5095e09611333673d0`.
- Public attestation sidecar: `shai-installer_0.16.1_amd64.deb.intoto.jsonl`.
- [Release downloads](https://github.com/RyanHamze/SHAI/releases/tag/v0.16.1).

This is a test release, not a claim of universal hardware support or
publisher-GPG-signed APT metadata. See [Security](../SECURITY.md).
