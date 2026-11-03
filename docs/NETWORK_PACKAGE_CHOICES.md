# Network Packages: Ubuntu And Upstream Sources

2026-11-03: vnStat and NetHogs added as optional Ubuntu APT installations.
OpenSnitch continues using the Ubuntu package. No firewall change or monitoring
daemon installation was applied to the VM as part of the catalog update.

Commands generated after the user's SHAPP selection and approval include:

```bash
sudo apt-get -o Acquire::ForceIPv4=true install vnstat nethogs
```

The SHAPP backend installs only the actual selected packages. OpenSnitch is a
separate opt-in firewall choice, not a side effect of installing monitoring tools.
RAM/disk figures in the catalog are planning estimates, not measured benchmarks.

## Zeek Correction

No candidate in configured Ubuntu repositories does NOT imply no compatible
upstream binary. Zeek's official OBS repository currently publishes
`xUbuntu_26.04`, including amd64/arm64 package indexes. Its binary-package guide
explicitly lists Ubuntu 26.04. It can be installed through APT after enrolling
that upstream repository, but it is not thereby a Canonical-maintained package.

Future SHAPP enrollment must use a dedicated keyring under /etc/apt/keyrings,
a verified signing-key fingerprint, a deb822 Signed-By restriction, and the exact
supported Ubuntu release. Do not use apt-key, trusted=yes, global trusted.gpg.d
keys, or a repository for an older Ubuntu release. Inspect package candidates
and simulate dependency changes before installation. Starting capture requires
separate interface and privilege approval. None of this trust enrollment was
performed during this catalog update.

References:
- https://zeek.org/get-zeek/
- https://github.com/zeek/zeek/wiki/Binary-Packages
- https://download.opensuse.org/repositories/security:/zeek/xUbuntu_26.04/Release
