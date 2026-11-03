# SHAPP Executable Install Backends

## User Flow

Select apps -> persistent cart -> Apply -> visible terminal -> sudo authentication
-> protected plan validation -> download/install -> result and daily log. There
is no copy/paste step, no curl-to-shell installer, and no silent architecture
change. The plan chooses only fixed backend IDs; it cannot supply shell commands.

## Backend Commands

APT entries use `apt-get -o Acquire::ForceIPv4=true update`, protected removal
simulation, then `apt-get -o Acquire::ForceIPv4=true -y install -- PACKAGES`.

Host runtimes use:

```bash
sudo /usr/lib/shai-installer/shai-app-install install APP_ID --user USER
sudo /usr/lib/shai-installer/shai-app-install remove APP_ID --user USER
```

Host IDs: sniffnet, esphome, piper, whisper, openwakeword, wyoming. Voice engines
reuse AIA's managed runtime rather than create duplicate installations. ESPHome
uses an isolated desktop-user Python environment. Sniffnet uses an official
GitHub architecture-specific DEB and requires its published SHA-256 asset digest.
Runtime installation is not the same as selecting voices, enabling microphones,
training Speech-to-Phrase or configuring an automation dashboard.

Advanced container entries use:

```bash
sudo /usr/lib/shai-installer/shai-stack-apply --install SERVICE_ID
sudo /usr/lib/shai-installer/shai-stack-apply --remove SERVICE_ID
```

Container IDs: home-assistant, mosquitto, zigbee2mqtt, open-webui, esphome,
node-red, openhab, jellyfin, plex, emby, navidrome, zwavejs, adguard-home, pi-hole.
New entries expose loopback-only admin UIs, keep persistent per-app data and
bounded logs, validate Compose before startup, resolve image channels to immutable
digests, and reuse the recorded digest on later applies. Removal preserves data.
Existing stopped containers are not implicitly started by unrelated installs.

Plex permits outbound networking for its account-dependent workflow. Other new
services initially use the internal bridge; external integrations/metadata,
DNS uplinks and LAN access require explicit networking configuration. DNS tools
do not change host/router DNS, DHCP or firewall settings. Node-RED/HA APIs are
not exposed to the LAN. Radio apps require a reviewed serial-by-id device.

## Intentionally Gated

- Speech-to-Phrase: language, Home Assistant intent training and model selection.
- Matter/Thread: incompatible with strict IPv4-only policy without an exception.
- Emoncms: multi-service database/Redis/MQTT credentials and persistent storage.
- Zeek/ntopng: no package candidate on the target Ubuntu release, plus capture
  interface/privilege/retention and upstream-source review.

These entries remain visibly unavailable. No placeholder is labelled installed.
Direct-host mode does not use Docker as a hidden fallback for container-only apps.

## Verification

- Full package suite, backend mapping and isolated voice lifecycle tests passed.
- Live GTK test verified host/container selection, cart, schema-4 plan, and
  construction of automatic visible-terminal execution (installation suppressed).
- Real Wyoming download/install/dependency check/removal passed on the VM.
- Docker Compose accepted every one of the 14 service definitions without
  downloading or starting the heavy apps. Actual startup of all new services,
  radio behavior and media/DNS application setup remain unverified.
- No claim of full production acceptance, third-party signature verification,
  or complete installation coverage for the five gated entries is made.

## Upstream References

- https://esphome.io/install/
- https://nodered.org/docs/getting-started/docker
- https://jellyfin.org/docs/general/installation/container/
- https://www.openhab.org/docs/installation/docker
- https://www.navidrome.org/docs/installation/docker/
- https://docs.pi-hole.net/docker/configuration/
- https://github.com/GyulyVGC/sniffnet/releases
- https://github.com/emoncms/emoncms-docker
