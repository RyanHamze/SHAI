# SHAI checkpoint-test installer

This directory builds the first test-only SHAI installer package. It targets a
fresh, fully installed Ubuntu Desktop 26.04 system on `amd64` and reproduces
only configuration already validated on the disposable SHAI VM.

Installing the package does not debloat or reconfigure Ubuntu. It installs the
`shai-installer` command and its read-only catalogs. The transformation starts
only when the user runs:

```bash
sudo shai-installer
```

The command inventories the host, simulates every exact APT removal wave,
rejects simulations that install packages or remove protected components,
shows the proposal, and requires the user to type `APPLY`. It never runs
`apt update`, downloads packages, or performs a broad `autoremove`.

This is not the finished SHAI product. It does not include Home Assistant,
containers, local AI, the SHAI dashboard, branding, firewall enforcement, or
the proposed post-audit Wave 11 removals.

## Build

```bash
./installer/build.sh
```

The package and checksum are written to `dist/`. Build from the SHAI project
root. The build is local and does not contact an online source.

## Test workflow

1. Revert the Hyper-V VM to the fresh, fully updated Ubuntu checkpoint.
2. Copy the `.deb` to the VM.
3. Install it with `sudo apt install ./shai-installer_0.1.2_amd64.deb`.
4. Run `sudo shai-installer --assess` for a preview without changes.
5. Run `sudo shai-installer --checkpoint "CHECKPOINT NAME"`, review the
   simulation, then type `APPLY`.
6. Reboot and inspect the desktop before accepting the checkpoint test.

The installer records the supplied checkpoint name and backs up policy files
and user settings before changing them. The VM checkpoint remains the only
complete rollback mechanism for this initial test. Removing
the `.deb` cannot reinstall applications that the user approved for removal.
