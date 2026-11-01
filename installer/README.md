# SHAI Setup Wave A installer

This directory builds `shai-installer` 0.3.2 for a fresh, fully installed
Ubuntu Desktop 26.04 system on `amd64`.

Installing the DEB is inert. It installs the SHAI Setup GUI, exact debloat
catalogs, protected execution engine, SHAI desktop theme assets, documentation, and
Wave A application shells. It does not debloat Ubuntu or change desktop
settings during package installation.

Launch setup as the normal desktop user:

```bash
shai-setup
```

The graphical sequence is:

1. Review and explicitly approve the tested debloat scope.
2. Choose one managed Docker stack or compatible direct Ubuntu installs.
3. Choose smart-home intent and local-AI intent.
4. Review the exact Wave A plan.
5. Apply in a separate visible Ubuntu terminal using normal sudo authentication.
6. Run health checks, apply the reversible SHAI desktop theme, save the architecture, then open
   SHAI Home and SHAPP.

Wave A does not install Docker, Home Assistant, MQTT, Zigbee, Z-Wave, ESPHome,
Matter, Node-RED, media servers, voice tools, AI runtimes, or model weights.
Those are selected later in SHAPP. The Wave A Home, SHAPP, Health, and AIA
windows are honest handoff shells and do not pretend their later backends exist.

The existing terminal assessment path remains available:

```bash
sudo shai-installer --assess --user "$USER"
```

The legacy checkpoint-test apply path remains for development VM regression
tests. Normal Wave A application uses a strict user-owned JSON plan generated
by `shai-setup` and validated again after sudo elevation.

## Build

```bash
./installer/build.sh
```

The package and checksum are written to `dist/`. The build is local and does
not contact an online source.

## Safety properties

- no changes when the package is merely installed or Setup is merely opened;
- no online checks or downloads in Wave A;
- no broad package purge, broad autoremove, kernel removal, or disk operation;
- authoritative APT simulation before each exact removal wave;
- protected-package gate and no-install gate;
- user-owned, mode-0600, strict-schema setup plan;
- visible terminal execution and sudo prompt;
- personal files and media are outside the operation target set;
- final APT, DPKG, protected-package, and systemd health checks;
- local evidence, logs, before/after manifests, and setup result record.

The VM checkpoint remains the only complete rollback mechanism during current
development testing. Removing the DEB cannot reinstall applications removed
with approval.
