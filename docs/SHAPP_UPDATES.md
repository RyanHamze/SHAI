# SHAPP Update All

Update All stages maintenance tasks in the same cart as app installations and
removals. Nothing is checked or executed automatically. Each row shows its
command, purpose and online/local label. Apply opens a visible sudo terminal;
it does not enable automatic updates or bypass proxy/firewall settings.

APT metadata, safe installed-package upgrades, dependency-aware package
upgrades, Snap, optional Flatpak, firmware metadata/updates, guarded orphan
cleanup, package-cache cleanup and a local package-health check are available.
Missing optional tools are unavailable rather than silently installed.

`apt dist-upgrade` is not an upgrade to a new Ubuntu release. Ubuntu's release
upgrade command is `do-release-upgrade`, which is deliberately not included.
Package upgrades in this interface cannot remove Ubuntu components. Orphan
cleanup simulates first and excludes kernels/protected components rather than
blindly executing broad autoremove. Read the displayed guarded command.
[Ubuntu package-management documentation](https://ubuntu.com/server/docs/tutorial/managing-software/).

Firmware updating is a separate deliberate selection. It may need AC power,
supported hardware and a later reboot; it does not automatically reboot here.
Firmware uses Ubuntu's fwupd transport, not an invented IPv4-only guarantee.
[Upstream firmware update workflow](https://github.com/fwupd/fwupd/blob/main/src/fwupdmgr.md).

App cart RAM/disk estimates do not predict update downloads or firmware sizes.
The underlying package/firmware manager performs its own checks. Existing daily
logs capture visible terminal output and errors. Failed tasks do not roll back
already-completed operations.

Setup's final action is named "Close SHAI Setup and open SHAPP". SHAPP launches
in an independent user service, and Setup checks startup before closing. An
already-running registered SHAPP window is also accepted after activation.
