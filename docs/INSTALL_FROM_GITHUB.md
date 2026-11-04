# Install SHAI From GitHub

Target: fresh Ubuntu Desktop 26.04.x LTS, amd64, normal desktop terminal.
Create a recoverable VM checkpoint first. GitHub is private: sign in with an
account that has access; never put a token or password into a pasted command.

## One-Time Prerequisites

```bash
sudo apt update && sudo apt install -y gh git curl python3 ca-certificates
gh auth login --hostname github.com --web --git-protocol https
```

## Download And Open Setup

```bash
gh auth setup-git && gh repo clone RyanHamze/SHAI && bash SHAI/install.sh
```

Run from your home directory, where a `SHAI` folder does not already exist.
For a frozen test, check out the reviewed commit before running `install.sh`.
Clone/download completes before execution; no partial script is piped into Bash.
Do not run the installer as root. It requests sudo for package installation,
then launches SHAI Setup as the desktop user. Installing the package alone does
not debloat Ubuntu or apply appliance policies. Review and approve in Setup.

The entry point uses IPv4/HTTPS for the payload, checks an independently pinned
SHA-256 and DEB identity/version/architecture before privilege, and removes its
temporary authorization-header file. Cross-host redirects do not forward the
GitHub bearer token. APT may download missing dependencies over IPv4.

`bash install.sh --verify-only` downloads and verifies without installation or
launching Setup. It was tested against the actual private GitHub artifact.

## Development Channel Limits

The current entry point pins candidate 0.13.1 and its verified CI artifact.
This is not a signed production APT channel. The artifact expires on
2027-02-01 at 9:43 PM America/Chicago (2027-02-02 03:43 UTC). A later tested
release must update the pin; do not bypass hash checks if download expires.

An authentication/download failure makes no package changes. If no graphical
session is available, use the Ubuntu desktop terminal. Ubuntu clock, DNS and
internet/proxy settings must allow the explicitly requested initial download.
