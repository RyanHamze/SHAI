# Held packages and capabilities

These are intentionally excluded from the approved debloat waves.

- `cloud-init`: provisions users, hostnames, networking, and metadata during first boot. Hold until its completed state and datasource are verified.
- `packagekit`: supports graphical software and update operations. Hold until SHAI provides a tested replacement update portal.
- `brltty`: braille-display support. It can interfere with some USB serial adapters, but removal requires an explicit accessibility decision.
- `orca`: GNOME screen reader. Removal requires an explicit accessibility decision.
- `snapd`: Canonical's sandboxed application/runtime system. Ubuntu desktop components still use it.
- `firefox`: retained until SHAI has a working local dashboard/administration experience.
- `avahi-daemon`: retained for local-device and Home Assistant discovery.
- `openssh-server`: retained for approved local administration and current development access.
- All kernel, kernel module, kernel header, bootloader, firmware, driver, GNOME login, networking, APT, audio, authorization, and recovery packages are protected.

Future work remains pinned: Ryan will later provide requirements for discovering and removing unwanted software on unfamiliar Ubuntu installations rather than relying only on a known baseline.

Later decision recorded: Firefox and Snap remain because Firefox will be used to access Home Assistant. SHAI will later provide an explicit connectivity switch instead of removing the browser.
