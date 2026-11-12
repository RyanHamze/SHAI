# Third-party notices, credits and installation sources

## Scope, Ubuntu and non-affiliation

SHAI (Smart Home Automation and AI) is independent software from Aabey LLC.
It configures an existing Ubuntu installation after approval; it is not an
Ubuntu distribution, operating-system image or replacement shell. Ubuntu
remains the host operating system. Ubuntu is a trademark of Canonical Ltd.

SHAI and Aabey LLC are not affiliated with, sponsored by, endorsed by or
official support representatives of Canonical or **any individual project,
publisher or contributor listed in this document**. This disclaimer applies
separately to every entry. Names and trademarks identify compatibility,
sources and credits and remain their owners' property. No Canonical trademark
permission or approval is claimed. SHAI customizations are not Canonical
support commitments; approved settings may change update schedules.

Credit belongs to Canonical, Ubuntu/Debian maintainers, Linux developers and
all upstream contributors whose software runs on the host. References:
[Ubuntu](https://ubuntu.com/), [Ubuntu packages](https://packages.ubuntu.com/),
[Canonical trademarks](https://canonical.com/legal/trademarks),
[Canonical intellectual-property policy](https://canonical.com/legal/intellectual-property-policy).
A disclaimer does not replace applicable trademark or license obligations.

## Derived material

### Tecnativa Docker Socket Proxy

SHAI's private read-only container observation component is derived from
[Tecnativa/docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy),
copyright Tecnativa and contributors, under the Apache License 2.0.

SHEALTH uses this component for read-only container observation. The derived
component and observation policy are part of SHAI's monitoring backend; the
SHEALTH interface itself is SHAI application code, not an upstream proxy GUI.
Credit for the original component belongs to Tecnativa and its contributors.

SHAI uses the modified public fork at
[RyanHamze/docker-socket-proxy](https://github.com/RyanHamze/docker-socket-proxy).
The fork records its modifications in `CHANGES.md`, retains upstream
`LICENSE.txt`, and includes `NOTICE.md`. The SHAI package pins the published
multi-platform image by immutable digest.

Docker is a trademark of Docker, Inc. SHAI and Aabey LLC are not affiliated
with Docker, Inc. or Tecnativa.

The observer's own dependencies, including [HAProxy](https://www.haproxy.org/),
retain their separate notices. Consult the fork and exact image contents.

### GNOME Shell-derived theme

The shipped [SHAI GNOME Shell stylesheet](../licenses/shai-gnome-shell.css)
identifies GNOME Shell 50.1's dark stylesheet as its source. Its retained
header credits Red Hat, Inc. (2009, 2015), contributors and portions adapted
from Mx's stylesheet, copyright Intel Corporation (2009). SHAI changes colors.
This material retains its upstream copyright/license; SHAI does not claim it
as wholly original code or relicense it under project-wide terms.

The provenance header says LGPL-2.1-or-later; the retained upstream text
specifies LGPL version 2.1. Consult the actual source/license rather than
assuming broader permissions from this summary. References:
[GNOME Shell](https://gitlab.gnome.org/GNOME/gnome-shell),
[LGPL 2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html),
[included license text](../licenses/LGPL-2.1.txt).

The SHAI icon theme inherits installed
[Adwaita](https://gitlab.gnome.org/GNOME/adwaita-icon-theme) and
[hicolor](https://specifications.freedesktop.org/icon-theme-spec/latest/)
icons rather than claiming their authorship. Existing
[Yaru](https://github.com/ubuntu/yaru) components retain their own notices.
This document grants no third-party artwork rights.

## Runtime and host dependencies

The installer uses installed implementations of APT, Bash, coreutils, dconf,
GTK 4, grep, iproute2, GLib, Python 3, PyGObject, sed, systemd, util-linux and
xdg-utils. Other workflows call sudo/PolicyKit, wget/curl, GnuPG, CA
certificates, Python venv/pip, ALSA tools, Snap, Flatpak and fwupd when present
or explicitly installed. These are dependencies, not implementations authored
by SHAI. Their maintainers and contributors retain all applicable rights.

Project references: [APT](https://salsa.debian.org/apt-team/apt),
[GNU software](https://www.gnu.org/software/),
[dconf](https://gitlab.gnome.org/GNOME/dconf), [GTK/GLib](https://www.gtk.org/),
[Python](https://www.python.org/), [PyGObject](https://pygobject.gnome.org/),
[iproute2](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git/),
[systemd](https://github.com/systemd/systemd),
[util-linux](https://github.com/util-linux/util-linux),
[xdg-utils](https://gitlab.freedesktop.org/xdg/xdg-utils),
[sudo](https://www.sudo.ws/), [polkit](https://gitlab.freedesktop.org/polkit/polkit),
[curl](https://curl.se/), [GnuPG](https://gnupg.org/),
[pip](https://pip.pypa.io/), [ALSA](https://www.alsa-project.org/),
[Snap](https://snapcraft.io/), [Flatpak](https://flatpak.org/),
[fwupd](https://fwupd.org/), [App Center](https://github.com/ubuntu/app-center),
[Firefox](https://www.mozilla.org/firefox/).

Advanced architecture can install Docker Engine, CLI, containerd, Buildx and
Compose plugins from Docker's APT repository:
`https://download.docker.com/linux/ubuntu`, using its signing key. Credits:
[Moby](https://github.com/moby/moby), [Docker CLI](https://github.com/docker/cli),
[containerd](https://github.com/containerd/containerd),
[Buildx](https://github.com/docker/buildx), [Compose](https://github.com/docker/compose).
This does not imply affiliation with Docker, Inc.

Build/publication tooling uses GitHub Actions components
[checkout](https://github.com/actions/checkout),
[attest](https://github.com/actions/attest),
[upload-artifact](https://github.com/actions/upload-artifact) and
[download-artifact](https://github.com/actions/download-artifact), pinned in
the workflow, plus applicable GitHub provenance/verification services.
These build dependencies are not SHAI desktop applications. Credits belong
to their respective maintainers; GitHub hosting is not a product endorsement.
The bootstrap may temporarily download the official
[GitHub CLI](https://github.com/cli/cli) release binary to verify attestations;
it is not permanently installed by that bootstrap. Verification uses the
applicable [Sigstore](https://www.sigstore.dev/) trust/provenance infrastructure.

## Installation sources

Optional apps are generally installed by SHAI-generated commands after
approval, not bundled as their source code in SHAI. Recipes may also configure
services, networking, permissions and storage; they are not merely links.
An app listing is not a compatibility guarantee or successful installation.
User-modified repositories and externally installed apps may differ.

- **APT** means the machine's configured Ubuntu APT sources/mirrors, unless a
  publisher repository is explicitly listed. An upstream code link below is
  credit/reference, not a claim that APT clones it or that all configured
  repositories on an arbitrary PC are official Ubuntu sources.
- **PyPI** means isolated Python installation from `https://pypi.org/simple`
  and its artifact hosts, including dependencies.
- **Image** means Docker pulls that repository from Docker Hub or `ghcr.io`,
  not a source-code clone. Exact tags/digests are in the service catalog;
  not every image is claimed to be publisher-operated or immutable.
- **Setup only** means additional dedicated configuration, not a finished
  generic installer. Installing tools does not configure or validate a service.

The tables describe the configured sources. Exact versions and execution
details depend on the installed release; review the installation plan and
download origin before approval.
Each selected release, image, plugin, voice and model retains its own license
and terms; no blanket open-source license or publisher endorsement is implied.

## SHAPP app credits and sources

The non-affiliation statement above applies to **each row individually**.
Project links credit the respective maintainers and contributors.

| Catalog ID | Project / contributors | Actual configured source or limitation |
| --- | --- | --- |
| `vnstat` | [vnStat](https://github.com/vergoh/vnstat) | APT: `vnstat`. |
| `nethogs` | [NetHogs](https://github.com/raboof/nethogs) | APT: `nethogs`. |
| `exiftool` | [ExifTool / Phil Harvey and contributors](https://exiftool.org/) | APT: `libimage-exiftool-perl`; Metadata Cleaner is SHAI's separate frontend. |
| `sniffnet` | [Sniffnet](https://github.com/GyulyVGC/sniffnet) | Architecture-specific DEB from this repository's releases, selected through GitHub API with published SHA-256. |
| `home-assistant` | [Home Assistant](https://github.com/home-assistant/core) | Image: `ghcr.io/home-assistant/home-assistant`; advanced Docker path, not Home Assistant OS/Supervisor or a promised host-native installer. |
| `mosquitto` | [Eclipse Mosquitto](https://github.com/eclipse-mosquitto/mosquitto) | APT: `mosquitto`, `mosquitto-clients`; or image `eclipse-mosquitto`. |
| `zigbee2mqtt` | [Zigbee2MQTT](https://github.com/Koenkk/zigbee2mqtt) | Image: `ghcr.io/koenkk/zigbee2mqtt`; coordinator configuration separate. |
| `esphome` | [ESPHome](https://github.com/esphome/esphome) | PyPI: `esphome`; or image `ghcr.io/esphome/esphome`. |
| `zwavejs` | [Z-Wave JS UI](https://github.com/zwave-js/zwave-js-ui) | Image: `ghcr.io/zwave-js/zwave-js-ui`. |
| `speech-to-phrase` | [Speech-to-Phrase](https://github.com/OHF-Voice/speech-to-phrase) | Setup only: dedicated trained home-automation setup, not generic engine installation. |
| `piper` | [Piper](https://github.com/OHF-Voice/piper1-gpl) | PyPI: `piper-tts`; voice files and licenses separate. |
| `wyoming` | [Wyoming](https://github.com/OHF-Voice/wyoming) | PyPI: `wyoming`; protocol library, not a complete speech engine. |
| `jellyfin` | [Jellyfin](https://github.com/jellyfin/jellyfin) | Image: `jellyfin/jellyfin`. |
| `borgbackup` | [Borg](https://github.com/borgbackup/borg), [cryptsetup](https://gitlab.com/cryptsetup/cryptsetup) | APT: `borgbackup`, `cryptsetup`; no backup created by installation alone. |
| `keepassxc` | [KeePassXC](https://github.com/keepassxreboot/keepassxc) | APT: `keepassxc`. |
| `open-webui` | [Open WebUI](https://github.com/open-webui/open-webui) | Image: `ghcr.io/open-webui/open-webui`; consult selected version's license/branding terms. |
| `node-red` | [Node-RED](https://github.com/node-red/node-red) | Image: `nodered/node-red`. |
| `matter-server` | [matter.js](https://github.com/matter-js/matter.js) | Configured image: `ghcr.io/matter-js/matterjs-server`; currently download-only, not a functioning Thread border router or Home Assistant Python Matter Server claim. |
| `openhab` | [openHAB](https://github.com/openhab/openhab-core) | Image: `openhab/openhab`. |
| `whisper` | [faster-whisper](https://github.com/SYSTRAN/faster-whisper), [OpenAI Whisper](https://github.com/openai/whisper) | PyPI: `faster-whisper`; no OpenAI cloud API. Recognition models separate. |
| `openwakeword` | [openWakeWord](https://github.com/dscripka/openWakeWord) | PyPI: `openwakeword`; pretrained-model terms may differ. |
| `plex` | [Plex](https://www.plex.tv/), [container](https://github.com/plexinc/pms-docker) | Image: `plexinc/pms-docker`; proprietary features, accounts and network requirements may apply. |
| `emby` | [Emby](https://emby.media/) | Image: `emby/embyserver`; publisher terms/paid features may apply. |
| `navidrome` | [Navidrome](https://github.com/navidrome/navidrome) | Image: `deluan/navidrome`. |
| `kodi` | [Kodi](https://github.com/xbmc/xbmc) | APT: `kodi`. |
| `gerbera` | [Gerbera](https://github.com/gerbera/gerbera) | APT: `gerbera`. |
| `emoncms` | [Emoncms / OpenEnergyMonitor](https://github.com/emoncms/emoncms) | Image: `openenergymonitor/emoncms`; supporting `mariadb` and `redis` images retain [MariaDB](https://mariadb.org/) and [Redis](https://redis.io/) terms/credits. |
| `opensnitch` | [OpenSnitch](https://github.com/evilsocket/opensnitch) | APT: `opensnitch`. |
| `adguard-home` | [AdGuard Home](https://github.com/AdguardTeam/AdGuardHome) | Image: `adguard/adguardhome`. |
| `pi-hole` | [Pi-hole](https://github.com/pi-hole/pi-hole) | Image: `pihole/pihole`. |
| `suricata` | [Suricata / OISF](https://github.com/OISF/suricata) | APT: `suricata`. |
| `zeek` | [Zeek](https://github.com/zeek/zeek), [installation](https://zeek.org/get-zeek/) | Publisher APT: `https://download.opensuse.org/repositories/security:/zeek/xUbuntu_<release>/`, scoped signing key; recipe selects `zeek-9.0`. Not an Ubuntu archive package claim. |
| `ntopng` | [ntopng / ntop](https://github.com/ntop/ntopng) | Publisher APT: `https://packages.ntop.org/apt-stable/<release>/`; key: `https://packages.ntop.org/apt/ntop-minimal.key`. Edition/features may have different terms. |
| `luks-encryption` | [cryptsetup](https://gitlab.com/cryptsetup/cryptsetup) | APT: `cryptsetup`; installation does not encrypt disks. |
| `veracrypt` | [VeraCrypt](https://github.com/veracrypt/VeraCrypt) | Signed DEB from this project's GitHub releases; publisher key: `https://amcrypto.jp/VeraCrypt/VeraCrypt_PGP_public_key.asc`. No disks encrypted by installation. |

## Additional AIA runtime, voice and model credits

No affiliation or endorsement is implied for any entry. Models are not trained
by SHAI; original publishers and GGUF distributors are credited separately.

| Component | Credits / source | Configured download |
| --- | --- | --- |
| llama.cpp | [ggml-org and contributors](https://github.com/ggml-org/llama.cpp) | Ubuntu APT: `llama.cpp`; current AIA runtime, not a silent Ollama installation. |
| eSpeak NG | [eSpeak NG contributors](https://github.com/espeak-ng/espeak-ng) | APT: `espeak-ng`. |
| Piper | [Piper](https://github.com/OHF-Voice/piper1-gpl), [PyPI](https://pypi.org/project/piper-tts/) | Isolated PyPI `piper-tts`; pinned version in voice installer, voice assets separate. |
| faster-whisper | [SYSTRAN/contributors](https://github.com/SYSTRAN/faster-whisper), [PyPI](https://pypi.org/project/faster-whisper/) | Isolated PyPI `faster-whisper`, including dependencies such as [CTranslate2](https://github.com/OpenNMT/CTranslate2). |
| openWakeWord | [Contributors](https://github.com/dscripka/openWakeWord), [PyPI](https://pypi.org/project/openwakeword/) | Isolated PyPI `openwakeword`. |
| Wyoming | [Contributors](https://github.com/OHF-Voice/wyoming), [PyPI](https://pypi.org/project/wyoming/) | Isolated PyPI `wyoming`; external satellites/engines retain separate notices. |
| SmolLM2 135M Instruct | [Hugging Face TB](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct), [QuantFactory GGUF](https://huggingface.co/QuantFactory/SmolLM2-135M-Instruct-GGUF) | QuantFactory: `SmolLM2-135M-Instruct.Q4_K_M.gguf`; catalog records Apache-2.0. |
| SmolLM2 360M Instruct | [Hugging Face TB](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct), [LM Studio Community GGUF](https://huggingface.co/lmstudio-community/SmolLM2-360M-Instruct-GGUF) | lmstudio-community: `SmolLM2-360M-Instruct-Q4_K_M.gguf`; catalog records Apache-2.0. |
| Qwen 2.5 0.5B Instruct | [Qwen](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct), [Qwen GGUF](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF) | Qwen: `qwen2.5-0.5b-instruct-q4_k_m.gguf`; catalog records Apache-2.0. |
| Llama 3.2 1B Instruct | [Meta](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct), [bartowski GGUF](https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF) | bartowski: `Llama-3.2-1B-Instruct-Q4_K_M.gguf`; Llama 3.2 Community License and applicable use policy, not Apache-2.0. See [Meta license](https://www.llama.com/llama3_2/license/). |

Individual voice/model cards may have additional terms. User-imported GGUFs,
custom integrations/scripts and externally installed software are not vetted
or relicensed by SHAI. No user test output, logs or private configuration is
included in these public notices.

## Version-specific licenses and release review

This is a human-readable credit/source inventory, not a complete transitive
SBOM, legal opinion or guarantee of license compliance. Exact versions matter.
Inspect `/usr/share/doc/<package>/copyright` and package/source metadata for
Ubuntu software; Python `.dist-info` licenses, `install-report.json` and
`requirements.lock` where generated for Python runtimes; and exact image
digests, bundled license notices and source offers for containers. Upstream
LICENSE/NOTICE files and model/voice cards control over catalog summaries.

Redistribution or derivative works may require full license texts, preserved
copyright notices, corresponding source or additional permissions. Before a
release, review the actual artifact and its dependencies, retain required
licenses/source information and resolve unclear code/artwork provenance.
Credits and non-affiliation language do not discharge those obligations.
