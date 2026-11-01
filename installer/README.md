# SHAI Setup Wave A installer

This directory builds `shai-installer` 0.4.0 for a fresh, fully installed
Ubuntu Desktop 26.04 system on `amd64`.

Installing the DEB is inert. It installs the SHAI Setup GUI, exact debloat
catalogs, protected execution engine, SHAI desktop theme assets, documentation, and
initial application shells. It does not debloat Ubuntu or change desktop
settings during package installation.

Launch setup as the normal desktop user:

```bash
shai-setup
```

The graphical sequence is:

1. Review and explicitly approve the tested debloat scope.
2. Choose one managed Docker stack or compatible direct Ubuntu installs.
3. Choose smart-home intent and local-AI intent.
4. Review the exact Setup plan.
5. Apply in a separate visible Ubuntu terminal using normal sudo authentication.
6. Run health checks, apply the reversible SHAI desktop theme, save the architecture, then open
   SHAI Home and SHAPP.

Setup does not install Docker, Home Assistant, MQTT, Zigbee, Z-Wave, ESPHome,
Matter, Node-RED, media servers, voice tools, AI runtimes, or model weights.
Those are selected later in SHAPP. The initial Home, SHAPP, Health, and AIA
windows are honest handoff shells and do not pretend their later backends exist.

The existing terminal assessment path remains available:

```bash
sudo shai-installer --assess --user "$USER"
```

The legacy checkpoint-test apply path remains for development VM regression
tests. Normal Setup application uses a strict user-owned JSON plan generated
by `shai-setup` and validated again after sudo elevation.

## Build

```bash
./installer/build.sh
```

The package and checksum are written to `dist/`. The build is local and does
not contact an online source. `installer/SOURCE_DATE_EPOCH` fixes archive
timestamps so the same source produces the same DEB locally and in GitHub CI.

## Safety properties

- no changes when the package is merely installed or Setup is merely opened;
- no online checks or downloads in base Setup;
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

## SHAPP functional draft

Version 0.4.0 replaces the SHAPP handoff shell with a functional GTK draft.
Recommended and Optional tabs contain two audited catalog entries each. The
Currently Installed tab discovers user-facing APT, Snap, and local desktop
applications; protected Ubuntu/GNOME components are visible but locked.

Checkboxes stage a cumulative desired state in the persistent right-hand cart.
Apply writes a mode-0600 plan and opens a visible terminal. The privileged
helper revalidates catalog IDs, plan ownership, visible installed applications,
and protected-package simulations before one exact APT transaction and any
approved Snap removals. It never runs broad autoremove. Ubuntu App Store only
launches Ubuntu's existing store in another window.
