# SHAPP 0.11.1 Optional Installers And Failure Diagnosis

## Catalog

Removed XScreenSaver from the catalog. Added Ubuntu cryptsetup/LUKS tools and
the official Ubuntu-release-matched VeraCrypt GUI package. No formatting,
partitioning, encryption or password operations occur during tool installation.
The existing Ubuntu Disks app remains the graphical Ubuntu volume manager.

All optional entries have a backend for the appropriate architecture. Host mode
does not silently use Docker; container-only apps require Advanced mode. Matter
is explicitly runtime staging only until an IPv6 exception is approved. It does
not become an operational Matter installation under an IPv4-only policy.
Speech-to-Phrase remains a recommended (not optional) entry requiring training.

Added Zeek 9.0 LTS and stable ntopng upstream repository installers. Publisher
keys are fingerprint-pinned and restricted with deb822 Signed-By keyrings.
VeraCrypt 1.26.30 uses its official Ubuntu DEB, detached PGP signature and pinned
publisher key. No signature checks or APT date checks are bypassed. ntopng's
capture daemon is not auto-enabled, and running external installations are not
silently reconfigured.

Emoncms has a private web/MariaDB/Redis recipe, generated root-owned credentials,
persistent feeds, loopback web UI and MQTT initially disabled. Matter uses the
current Matter.js image, not the archived Python server. Its runtime image is
downloaded but deliberately not started.

## Actual Failure

The user's failed plan was 2387f147-495c-4f62-9226-625cbc4d0d72. APT update
returned 100 before package installation/removal. Reproduced errors explicitly
said repository Release files were "not valid yet", by up to about 16 hours.
The VM system clock was behind its hardware RTC; NTP was active but reported
unsynchronized. A one-time correction from the VM RTC restored successful APT
update with all date/signature checks left enabled. No time adjustment was added
to SHAPP Apply, and no failed plan was replayed automatically.

The old plan also requested removal of Image Viewer, Software Updater, Mosquitto
and its clients. Those selections were not replayed. Review them before applying
a new plan. Desktop log1.txt was historical AIA model output, not this APT failure.

## Logging

SHAPP now streams subprocess output to the visible terminal, captures errors in
the daily private log, and includes the actual error tail in the result. Date
validation failures add an actionable clock/NTP hint without altering the clock
or weakening APT verification.

## Verification

- Full package tests and offline backend contracts passed.
- Live GTK selection/cart/terminal-plan test passed.
- All 16 Compose definitions validated without pulling/starting heavy apps.
- Zeek/ntop repository InRelease signatures verified using the pinned keys.
- VeraCrypt Ubuntu 26.04 DEB signature verified against its official fingerprint.
- Ubuntu LUKS tools installed on the VM; no disk encryption performed.
- VeraCrypt 1.26.30 installed on the VM after successful publisher-signature
  verification. cryptsetup is 2.8.4; the root filesystem remains ext4, not LUKS.
- Built and deployed shai-installer 0.11.1; package checksum matched on the VM.
- Heavy optional runtime startup and real networking/radio behavior remain
  separate acceptance tests; a valid recipe is not a claim of universal success.

References:
- https://github.com/zeek/zeek/wiki/Binary-Packages
- https://packages.ntop.org/apt-stable/
- https://veracrypt.io/en/Downloads.html
- https://github.com/matter-js/matterjs-server/blob/main/docs/docker.md
- https://github.com/emoncms/emoncms-docker
