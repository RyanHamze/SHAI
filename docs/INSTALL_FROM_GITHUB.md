# Install SHAI From GitHub

Target: Ubuntu Desktop 26.04.x LTS, amd64, in your normal desktop terminal.
The public v0.14.0 release needs no GitHub account, token, Git clone or login.
Create a recoverable checkpoint before installing.

## Download And Open Setup

Run these three commands separately from a directory you own. The first installs
prerequisites from your configured Ubuntu APT repositories. The second downloads
the complete bootstrap; run the third only if that download succeeds.

```bash
sudo apt install curl python3 ca-certificates
curl -q --fail --show-error --location --proto '=https' --proto-redir '=https' --max-filesize 1048576 https://raw.githubusercontent.com/RyanHamze/SHAI/main/install.sh --output shai-install.sh
bash shai-install.sh
```

Do not run the script with sudo or pipe a download into Bash. Inspect the script
before running it. Trust in this downloaded bootstrap is the initial trust
boundary; its pins do not independently authenticate the bootstrap itself. The
`main` URL supplies the finalized bootstrap, which pins the release's earlier
build commit; the release tag's build input can still contain placeholder pins.
For a frozen bootstrap, replace `main` with its independently reviewed commit.

The bootstrap downloads the fixed v0.14.0 release DEB and its public
`shai-installer_0.14.0_amd64.deb.intoto.jsonl` attestation sidecar, plus the
portable GitHub CLI described below when needed. HTTPS is required for downloads
and redirects, curl configuration files are disabled, and download sizes are
bounded. It does not force IPv4 or change network settings.

Before any package sudo/APT action, it verifies the independently pinned package
SHA-256, attestation signatures with `gh attestation verify`, and the DEB's
package name (`shai-installer`), version (`0.14.0`) and architecture (`amd64`).
Attestation policy requires repository `RyanHamze/SHAI`, signer workflow
`RyanHamze/SHAI/.github/workflows/build-attest-release.yml`, source ref
`refs/tags/v0.14.0`, and the source commit pinned in the script.
The [GitHub CLI verification reference](https://cli.github.com/manual/gh_attestation_verify)
explains the exact policy flags and bundle verification.

The public bundle is fetched over HTTPS and verified cryptographically; no
GitHub authentication/API lookup is needed. With `--bundle`, repository/owner
names are checked against the signed certificate as issued, not against current
GitHub repository IDs. This cannot detect a later repository/owner rename or
name reuse. The independent package hash and source commit pins remain mandatory.

## Temporary Verification Tool

An existing `gh` is used only if its attestation help supports all required flags.
Ubuntu's older CLI need not be installed or upgraded. Otherwise the bootstrap
fetches the official portable GitHub CLI **2.103.3** Linux amd64 archive from
`cli/cli`'s fixed release URL and checks its source-pinned SHA-256:

```text
4c806978ffce1cec70853302a56d70ac6da4f19bae7adca4e1a8ab00633dd91d
```

This pin comes from the official release's
[checksum file](https://github.com/cli/cli/releases/download/v2.103.3/gh_2.103.3_checksums.txt).
No live checksum file is trusted at installation time. A bounded structured TAR
reader accepts only safe regular-file/directory entries and copies only the
expected `gh_2.103.3_linux_amd64/bin/gh`, never bulk-extracting the archive.
The temporary binary is mode 0700. No system CLI installation occurs.

All downloads, extracted tooling, CLI configuration and signature trust caches
stay inside a rootless mode-0700 temporary directory and are removed on exit or
interruption. GitHub credentials are neither required nor read by the isolated
verification command. Signature verification may contact GitHub/Sigstore trust
services; verification is not an offline operation.

## Verification And Installation

`bash shai-install.sh --verify-only` performs the same verification, including
portable CLI preparation if needed, without package installation, Setup launch,
or persistent software/configuration writes. Its only writes are temporary.

Normal installation requests sudo only after every verification passes, runs
APT with `--no-remove --no-install-recommends`, then opens SHAI Setup as your
desktop user. APT may download missing dependencies from configured Ubuntu
repositories. Installing the package alone does not debloat Ubuntu or apply
appliance policies; review and approve those separately inside Setup.

Missing assets, bad checksums, invalid/missing signatures, wrong workflow/tag/
commit, malformed archives or wrong DEB identity stop installation. Do not bypass
checks or substitute `latest` downloads. Clock, DNS, TLS, internet and proxy
settings must permit the explicitly requested downloads and trust verification.

## Release Preparation

The development bootstrap intentionally contains all-zero package SHA-256 and
source commit placeholders and refuses downloads until release engineering fills
both. Freeze build commit A, tag it `v0.14.0`, and build/attest that exact source.
Attach the exact DEB and its Sigstore bundle named
`shai-installer_0.14.0_amd64.deb.intoto.jsonl` to the public release. Finalize the
bootstrap in later commit B with the verified DEB hash and source commit A; do
not move the release tag to B. The three-line instructions fetch the finalized
bootstrap from main. The bootstrap never substitutes a downloaded DEB checksum
file for its source pin.
