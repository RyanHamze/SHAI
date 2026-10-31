# SHAI

SHAI means Smart Home Automation and AI. It configures an existing supported
Ubuntu Desktop installation as a local-first home appliance. Ubuntu remains the
operating system and owns its kernel, repositories, updates, firmware, terminal,
and desktop base. SHAI is not an Ubuntu distribution and is not affiliated with
or endorsed by Canonical. Ubuntu is a trademark of Canonical Ltd.

Version 0.1.2 is a checkpoint-tested development release for Ubuntu 26.04
`amd64`. Installing the `.deb` is inert. Changes begin only after the user runs
`sudo shai-installer --checkpoint "CHECKPOINT NAME"`, reviews the complete APT
simulation, and explicitly enters `APPLY`.

GitHub Actions builds, tests, hashes, and attests packages. Production APT
metadata must additionally be signed by the offline SHAI archive key. Optional
SHAI applications must be listed by digest in a separately signed app catalog.
Private keys, passphrases, and hardware-token PINs are never stored in this
repository or GitHub Actions. Until offline signatures are attached and
verified, releases remain drafts and are not production-trusted.

See [SECURITY.md](SECURITY.md), [release/KEY_CEREMONY.md](release/KEY_CEREMONY.md),
and [release/RELEASE_PROCESS.md](release/RELEASE_PROCESS.md).

No open-source license has been selected. Copyright Aabey LLC; no license is
granted beyond GitHub's applicable terms until a LICENSE file is published.
