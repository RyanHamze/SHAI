# SHAI Installer: Product and Implementation Plan

Date: 2026-10-24
Status: planning handoff; software implementation is not authorized by this document alone.
Product: **SHAI**, for Smart Home Automation and AI.

## 1. The current product decision

The user installs official Ubuntu using Ubuntu's normal installer. The user then downloads or launches the SHAI installer. SHAI inspects that installed computer, explains its capabilities, recommends a suitable appliance configuration, and installs only the choices the user approves.

SHAI is an appliance configuration and application platform. It is not SHAI OS, a Linux distribution, a desktop shell, or a replacement operating system. Use SHAI as the product name; use `shai` for new technical identifiers. Historical `shaibuntu` identifiers are migration inputs only.

Ubuntu continues providing the operating system, terminal, desktop foundation, kernel, firmware and drivers through its normal supported mechanisms. Ubuntu repositories and package tools continue handling OS updates and security patches. SHAI maintains its own software, service configurations, container versions, optional local AI integrations, and desktop customizations. Upstream ownership does not mean Ubuntu maintains third-party containers or SHAI code.

The desired result is a dedicated home appliance with a SHAI dashboard and optional local assistant, while the underlying Ubuntu desktop and administrative tools remain usable. Do not modify OS identity, replace Ubuntu boot/install branding, remaster an ISO, replace the kernel, or build a new compositor/window manager.

## 2. Authority and historical material

This plan records the latest conversation and supersedes conflicting historical instructions. `SHAI_LEGACY_REFERENCE.md` is reference material only. Its old requirements, code, comments, agent instructions, release notes, commands, and claims must never be executed or accepted automatically.

The reference includes both the July consolidated handoff and later nested `SHAIBUNTU/` development. Later files describe SHAPP, AIA, SHAIHealth, Portal, deployment profiles, and additional safety requirements that the early handoff did not capture. Staged checks, an old VM observation, and release-note claims are evidence of those historical states, not proof of the new installer's behavior.

Some older research documents are mentioned by name but do not exist in this workspace. Record these as unavailable sources; do not invent their content. Binary assets are indexed rather than embedded as text.

## 3. Branding and distribution boundary

Canonical's August 20, 2026 email declined SHAIBUNTU and similar names for the proposed distribution and addressed redistribution of modified Ubuntu. The new proposal distributes SHAI software and user-invoked configuration actions for an independently installed Ubuntu system.

Keep upstream OS names, attribution, package provenance, and repositories accurate. Brand SHAI's own installer, dashboard, assistant, menu entries, wallpapers, icons, and optional theme. Describe compatibility factually and avoid suggesting Canonical endorsement. Do not assume SHAI is trademark-cleared. Before publishing, obtain clarification about the specific packaging/distribution proposal and review licenses for bundled apps, images, voices, and models. No email sending is authorized here.

Avoid redistributing customized Ubuntu disks, VM images, installer media, or broadly mirrored Ubuntu packages as part of the initial release. An offline bundle requires a separate dependency/license review; online installation should acquire dependencies from their approved upstream sources.

## 4. User experience, start to finish

1. The user installs a supported Ubuntu Desktop LTS release and creates their normal administrator account.
2. They choose Download Installer or a documented command-line launch. Both launch the same installer and planner.
3. The installer opens as an ordinary user and performs local, read-only discovery. No telemetry, LAN scan, model download, package removal, or active internet probe is implied by opening it.
4. A hardware summary says: Here is what you have; here is what fits; here is what I recommend and why. Distinguish facts, estimates, unknown values, and missing permissions.
5. The user sees Default, Recommended, and Optional selections, plus advanced customization. Recommended choices may be preselected when compatible, but remain removable. Incompatible choices explain why they are unavailable.
6. The user reviews a concrete plan: installs, removals, download sizes, reserved storage/RAM, services, startup changes, network endpoints, ports, firewall changes, credentials, and restart needs.
7. A button approves that exact plan. A privileged helper applies its authorized system operations with visible progress and logs. Execution pauses for changed scope, new network destinations, unresolved secrets, or destructive data operations.
8. Health checks verify actual results. The final screen separates Working, Needs setup, Waiting for hardware, Failed, Skipped, and Unsupported. A started process or generated TODO file is not completion.
9. At desktop login the SHAI dashboard opens. The assistant can appear on the right, minimize, close, or be permanently removed. Terminal and Ubuntu settings remain available.
10. Later users can add/remove modules, change colors, inspect ports and connections, review logs, back up, update, repair, or remove SHAI.

The guided setup must not begin with a generic application shopping list. Explain hardware fit and household purpose. Hide infrastructure complexity unless it affects a meaningful decision.

## 5. Download versus bootstrap versus command line

Users can download the installer directly. A bootstrap is just a small launcher that selects the right installer release, verifies it, installs the SHAI package/repository configuration if approved, and opens setup. It is a convenience delivery path, not a separate required product.

Recommended delivery:

- A downloadable, versioned `.deb` for the installer, with release integrity/authenticity information.
- A verified command-line launcher for users who prefer a single command.
- A signed APT repository for subsequent SHAI package updates, using a repository-scoped key and package-origin constraints so it does not replace unrelated Ubuntu packages.
- A later offline/import path for independently reviewed dependency bundles and local model files.

The command must launch setup; it must not silently convert the computer. An eventual public command may download and verify a launcher, then run it unprivileged, obtaining narrowly scoped privileges when applying the approved plan. Specify how the first trusted key or installer digest is authenticated. A checksum downloaded alongside a file is not independent proof of authenticity.

No installer endpoint, domain, published package, repository, or working one-line command exists by virtue of this plan. Do not publish a fictional URL or suggest `curl ... | sudo bash` as the finished delivery mechanism. The next implementation should first support launching a locally built installer; publishing the public command comes after clean-system tests.

## 6. Platform and hardware scope

First qualify one supported Ubuntu Desktop LTS release on amd64. Evaluate 24.04 and 26.04 against current package, Docker, desktop, and hardware support, then lock the initial tested matrix. Do not claim both without tests. Lubuntu/LXQt support is a later adapter, not a reason to replace an existing user's GNOME desktop.

Detect CPU architecture/model/features, cores, total and available RAM, GPU vendor/model, VRAM when reliably measurable, firmware/driver state, storage filesystem/mount/free space, virtualization, USB controllers, audio devices, existing AI runtimes, existing workloads, container engines, network interfaces/routes, and current firewall/update configuration.

Unknown GPU data must not be inferred from CPU branding. Do not collect document contents, browser history, credentials, SSH keys, or unrelated personal files. Local reports require redaction controls before export.

Provisional hardware guidance from later historical work: 1 GB is a desktop-only aspiration, light automation starts around 3 GB, AI consideration around 8 GB, and larger AI/vision around 16 GB. These are historical planning hints, not validated minimums. Benchmark clean Ubuntu plus SHAI and reserve capacity for automation before selecting a model. Recommend No AI or connecting to an existing Home Assistant when the full workload does not fit.

Arm64/Raspberry Pi support follows separate qualification. No true 32-bit boot support is claimed. Phone access means an authenticated local browser portal, not installing Ubuntu/SHAI onto arbitrary phones.

## 7. Component boundaries

| Component | Responsibility | Privilege |
| --- | --- | --- |
| SHAI installer | Discovery, recommendations, choices, plan preview, progress | User |
| SHAI deployment engine | Validated desired state, operation journal, dependency resolution, repair | Narrow privileged operations |
| SHAI dashboard/portal | Local metrics, links, services, ports, settings, history | User/service account |
| SHAI assistant | Explain options, local chat, propose actions | Unprivileged; no Docker socket |
| AIA module | Hardware-aware model catalog, runtime/model installs and imports | User; scoped install helper |
| SHAPP/deployment module | Application/service catalog and lifecycle | Scoped helper |
| SHAIHealth | Monitoring and explicitly configured recovery rules | User; scoped recovery helper |
| Optional services | Home automation, radio, AI runtime, media, voice | Per-service permissions |

Use native packages for host integration, systemd units, desktop launchers, installer, and helper. Adopt one lightweight native GUI framework after reviewing the later PyQt6 and earlier Tk prototypes; reuse what works and measure startup/RAM. Do not automatically ship two GUI stacks or require a large web runtime.

Prefer typed Python modules and declarative JSON/YAML manifests over a chain of loosely coupled shell scripts. Shell wrappers may handle small integration tasks. The assistant may show commands, but privileged actions map to validated operation IDs, not arbitrary LLM-generated shell strings. Protect local HTTP mutation endpoints against unauthorized callers and cross-origin requests; loopback binding alone is insufficient authentication.

## 8. Container strategy: simple default, advanced choices

The user's goal is simple deployment of private-network services. Recommend **one Docker Engine, one SHAI Compose project, and one default shared private service network**, with separate containers for individual services and separate persistent storage. The UI presents one managed stack. Docker Compose is built for managing multiple services as one application.

Do not merge Home Assistant, MQTT, Zigbee, AI, and media daemons into one giant container. That would tie upgrades, failures, permissions, and removals together. Record the user's single-container suggestion as a simplicity preference; satisfy it through a single managed stack. An all-in-one container is not the recommended implementation.

Offer three comprehensible modes:

- Simple / recommended: shared SHAI stack/network with individually selectable service containers.
- Advanced isolation: separate service networks, explicit rules, and validated VLANs only when the environment supports them. Do not configure switches/routers automatically or assume VLAN isolation exists.
- Home Assistant OS VM: a separate supported HAOS deployment, recommended only when memory, virtualization, storage, networking, and radio passthrough fit.

Host-native apps such as KeePassXC, dashboard, assistant, and portal stay native. Host deployment for other modules is offered only when a tested, upstream-appropriate path exists. Do not make deprecated Home Assistant Core/direct Python deployment the default.

A private Docker bridge does not automatically prevent internet egress, and `internal: true` can prevent legitimate LAN integrations. Define and test WAN versus LAN access per service. Home Assistant discovery, Bluetooth, mDNS, IPv6/Matter/Thread, and radio/VM access may need explicit networking exceptions. A shared network is a default proposal, not a promise that all protocols work on it.

Bind administrative endpoints to loopback unless LAN access is selected. Keep LAN device communication separate from exposing administrative UIs. Verify host firewall, Docker forwarding, IPv4/IPv6, and service bindings together. No globally privileged containers by default; document and approve unavoidable permissions. Pin tested image versions/digests and give each deployment a distinct project name.

## 9. Home automation and application catalog

Home Assistant is strongly recommended and preselected if it fits; it remains deselectable. Show Container versus HAOS VM explicitly. Container does not provide HAOS Supervisor/apps; SHAI can manage MQTT, voice, and other companion services separately. Never imply those are HAOS-managed apps.

Carry forward candidates: Mosquitto, Zigbee2MQTT, Z-Wave JS UI, ESPHome, Node-RED, Matter Server/Thread integration, openHAB as an alternative, local voice, Jellyfin/media, monitoring, Emoncms/energy, KeePassXC, encrypted backups, and selected privacy/security tools. Distinguish incompatible controller alternatives and avoid enabling everything by default.

Do not start Zigbee and Z-Wave services without appropriate controllers/configuration. Use stable USB device paths, prevent conflicting ownership, detect removal/reconnection, and display Waiting for controller. Account for discovery and firmware requirements. Do not flash radio firmware without explicit approval.

Each catalog item needs: purpose, default/recommended/optional status, supported release/architecture, dependency graph, conflicts, resource estimate, download/import size, license/source, deployment modes, network endpoints, listener ports, credentials, persistent paths, install/remove/update/backup/restore hooks, and verified health criteria.

## 10. AI, assistant, and voice

Carry forward AIA's separate model-advisor concept within the SHAI product. The main installer recommends installing the lightweight advisor, not blindly installing model weights. Show top three fitting options, full eligible catalog, and a first-class No AI option. Detect existing local runtimes before installing another.

The older request for a 0.5B assistant is a performance goal, not a mandate to install an obsolete model or override later model policies. The later project excludes Chinese-origin model publishers, including Qwen and DeepSeek. Preserve that recorded policy until the user explicitly changes it. Review model provenance and licenses before recommendations; do not claim any small model is reliable enough to administer the host unsupervised.

Provide deterministic offline explanations before any LLM is installed. Models/runtimes are downloaded only after approval or imported from integrity-checked local bundles. Record available RAM after host/service reserves, CPU compatibility, VRAM, disk, runtime, model license, and expected idle/inference effects.

Voice modules: Whisper for general speech where hardware fits, Speech-to-Phrase for constrained home commands on smaller hardware, Piper for local speech output, Wyoming integration where supported, and optional wake-word/satellite devices. Explain microphone permission, listening state, mute, storage/retention, and performance. Voice cannot bypass installation approval or safety rules.

## 11. Dashboard, desktop, and appearance

Use the existing Ubuntu desktop. Apply selected SHAI wallpaper, icons, color accents, launchers, and dashboard autostart. Preserve original settings for removal. No mandatory replacement login manager or boot splash. No custom desktop session is required for this scope.

Palette: black/graphite with green `#33EE33`, mellow alternatives, user-selectable theme/accent, readable contrast, and accessibility settings. Use `branding/reference/` and later nested branding as historical visual inputs, with asset ownership/license review. Reference files being present does not prove all historic themes were generated from them.

Dashboard: CPU/load, RAM, storage, GPU when available, driver information, AI/runtimes/models, Home Assistant, media, local services, firewall state, listener ports and owners/purpose/scope, connections, known devices, update state, network access mode, backups, SHAIHealth, important filesystem locations, and optional energy score. Label unsupported/unavailable readings accurately. Known neighbors are not a complete inventory of all home devices.

Portal is local by default. LAN/phone use is opt-in with authentication, scoped sessions, and an appropriate transport-security design. Historical same-link MAC allowlisting may be offered only as a secondary advanced restriction; MAC addresses are spoofable, routed clients may have no neighbor entry, and phones can randomize MAC addresses. Do not substitute MAC filtering for authentication or claim VLAN boundaries from portal checks.

Keep System Tools and terminal readily accessible. Provide links to Ubuntu update/security/settings tools instead of maintaining competing OS-management interfaces. If all general browsers are removed, provide a tested limited local service viewer or another usable frontend for Home Assistant onboarding before approving removal.

## 12. Debloat and appliance hardening

Show a concrete recommended removal list after inventory. User can retain any item. Candidate categories: games, office suite, chat/contacts, unused photo/media apps, and printer components when printing is not needed. Inspect dependency consequences and preserve working desktop, login, networking, terminal, package tools, firmware, accessibility, required browser/viewer, and recovery capabilities.

Default appliance exposure: no newly enabled SSH, telnet, remote desktop, SMB/NFS, or public access. Existing enabled services must be detected and shown as proposed changes; never silently lock out the person applying setup over SSH. Use unique credentials and preserve the current administrator; no shared shai/shai password or forced hostname rename. Optional SHAI hostname requires confirmation and collision checks.

Use Ubuntu-supported AppArmor/firewall mechanisms; sudo password authentication remains required. If the user selects immediate sudo reauthentication, scope/document that policy and record the previous state. Do not disable OS security updates just because legacy documents requested manual-only operation. Preserve the user's Ubuntu update policy by default and explicitly offer manual or automatic policies. SHAI packages/container/model updates have separate user-visible settings; no hidden updater.

Explain internet use for acquiring packages, images, drivers, models, and updates. Normal configured core operation is local. Preserve required LAN traffic and make optional cloud integrations explicit. A dashboard cannot truthfully identify every byte or all data contents leaving the host without additional observation controls; distinguish observed connections, configured destinations, and estimates.

## 13. Storage, media, energy, privacy, and recovery

Inspect free space and available mounts; never repartition/format disks as an implicit setup action. Propose SHAI-owned data locations under `/srv/shai`, configuration under `/etc/shai`, and state under `/var/lib/shai`. Support importing legacy paths only after backup/review.

Offer five media choices with current feature/license/resource/network comparisons: Jellyfin, Plex, Emby, Kodi, and Gerbera. Kodi is primarily a player, so do not label all five equivalent media servers. Warn about accounts/cloud dependencies where applicable. Recommended library layout: `/srv/media/{movies,tv,music,photos,home-videos,books,downloads,transcode}`. Confirm storage ownership and transcode capacity.

Energy feature: optional estimated power/energy/cost, default USD 0.13/kWh editable by location; distinguish measured from modeled data. Carbon emissions require an explicit emissions factor (gCO2e/kWh); cost alone cannot establish a carbon score. Allow additional devices, local meters, validated custom adapters, and opt-in external data sources with clear provenance/permissions.

Privacy tool recommendations must say what they measure/block and their resource/maintenance costs. Clarify whether exfil means outbound leakage monitoring or ExifTool metadata inspection; do not silently choose one. Avoid blanket claims of exfiltration prevention.

Encrypted backups are optional and strongly recommended for service configuration and valuable data. Explain key recovery and test restore. SHAIHealth defaults to monitor-only; restart/reboot rules require explicit bounded approval with thresholds, cooldowns, attempt limits, and logs. The historical 30-minute threshold is an editable initial suggestion, not a mandatory policy.

Preserve high-impact automation safety: user-defined rules for locks, HVAC, alarms, valves, relays; manual override; emergency stop; explicit safe states; local audit. Emergency stop must not invent device states or claim to control external automations that are not integrated. Assistant/AIA cannot directly issue high-impact physical actions.

## 14. Deployment lifecycle and ownership

Implement inspect -> recommend -> plan -> approve -> apply -> verify -> report, with resume/repair for interrupted operations. Repeated execution must converge without duplicate services, data loss, or unintended reinstallation. Revalidate hardware/network/package state before applying a saved plan.

Journal plan hash, approved actions, state transitions, versions, source, results, timestamps, owned files/packages/networks/services, changed settings, and restoration information. Redact credentials. Handle APT locks, low disk, package conflicts, failed downloads, unsupported hardware, and reboot/resume explicitly. Use APT interfaces, not custom package-database edits.

Uninstall modes: remove assistant only; remove an optional module; remove SHAI platform; separately purge selected data. Never remove pre-existing workloads/dependencies just because SHAI used them. Restore owned settings only if they still match SHAI's last applied value. Explain where rollback requires a real snapshot/backup or cannot safely reverse a database migration.

## 15. Existing work: what to reuse and what to retire

Reuse after review: hardware probes; dashboard layouts/status collectors; option catalog; AIA detection/picker/history/import ideas; SHAPP application catalog and selected container actions; SHAIHealth rules/UI; local portal; storage conventions; themes/reference art; manifests; unit-test cases; later system-tools/menu ideas.

Rework: root-running assistant/backend; unprotected local mutation APIs; arbitrary command execution; hardcoded LAN ranges; suppressed firewall failures; blanket host networking; mutable image tags; incomplete uninstall; unverified service wrappers; privacy claims; later host-mode assumptions.

Retire from the new execution path: Cubic, ISO patching, Casper UUID edits, GRUB/EFI/kernel/initrd handling, Calamares/Ubuntu installer modification, OS rebranding, weak default identity, and release scripts that merely rename or alias an Ubuntu ISO.

Do not bulk-rename the legacy repository. Introduce clean SHAI packages and adapters, copy only reviewed components, and keep a provenance map. The historical V054 host-native default and per-service VLAN assumptions are superseded by the simpler recommended stack and supported HAOS option in this plan.

## 16. Implementation sequence and evidence gates

| Stage | Concrete result | Required evidence |
| --- | --- | --- |
| 0: inventory | Source/reuse map, approved platform matrix, requirements traceability | Distinguish complete, prototype, unsupported, and missing |
| 1: read-only installer | GUI/CLI hardware summary and deterministic recommendations | Clean VM and physical probe outputs; no unexpected writes/network |
| 2: lifecycle foundation | Native package, planner/helper, journal, repair/remove, signed release design | Interrupted/resumed/repeated install; authorization and ownership tests |
| 3: appliance desktop | Dashboard, theme, approved debloat, host-policy integration | Desktop/login/network/terminal remain usable; removal reversal |
| 4: automation | HA Container path, shared stack, MQTT and controller modules | Fresh onboarding, health, restart, USB absent/present, LAN/firewall tests |
| 5: HAOS option | Hardware-gated VM backend and backup/migration guidance | Supported virtualization, network/discovery, radio and resource tests |
| 6: AI and voice | AIA, local runtime/model import, working local voice | No-AI mode; provenance; no silent downloads; offline smoke tests |
| 7: expansion | Portal, SHAIHealth, media, energy/privacy, backups | Auth/recovery bounds; energy labels; restore tests |
| 8: distribution | Downloadable installer and genuine one-command entry point | Authenticated release chain, upgrades, failed update recovery, clean install |

Test minimum/normal/high-memory cases, existing Docker workloads, an occupied port, a different LAN subnet, no internet, IPv6, SSH-based setup, full disk, failed downloads, missing USB, changed config after install, and SHAI removal. Use Hyper-V plus another supported VM setup and at least one physical host. VM success does not validate physical radios/VLANs/GPU behavior.

A feature can be staged without being complete. Record which test ran, on which system/release, against which version; do not present old logs/checksums or file-presence tests as proof of new functionality.

## 17. Deliverables for the next build chat

- A clean SHAI source/package layout and README describing OS versus SHAI responsibilities.
- A read-only hardware report and explainable recommendation engine first.
- A versioned module catalog and requirements-to-test map.
- Installer GUI and CLI using the same planner and state model.
- Host packages and optional Compose/HAOS backends with explicit update ownership.
- Visible execution, authenticated privileged actions, plan journal, repair and uninstall.
- Brand assets and desktop integration scoped to SHAI.
- Clean-system validation logs and known limitations, before a public installer command.

The next chat should begin implementation in stages. Do not build an ISO. Do not run host debloat/hardening or install containers on Ryan's development computer merely to test an installer.

## 18. Remaining routine decisions

Initial LTS release, GUI framework, public domain/repository host, signing-key custody, SHAI update cadence, exact default application bundle, local viewer choice, HAOS resource thresholds, and whether to retain the AIA display name need concrete implementation decisions. Choose conservative defaults and document them; consult the user for product tradeoffs that materially change their appliance experience.

## 19. Sources and scope of research

Reviewed 2026-10-24; recheck these at implementation time:

- Canonical IP policy: https://canonical.com/legal/intellectual-property-policy
- Home Assistant installation methods: https://www.home-assistant.io/installation/linux
- Docker Compose application model: https://docs.docker.com/compose/intro/compose-application-model/
- Docker firewall behavior: https://docs.docker.com/engine/network/packet-filtering-firewalls/
- APT repository authentication: https://manpages.ubuntu.com/manpages/noble/man8/apt-secure.8.html
- Home Assistant local voice: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/

Architecture and product defaults in this document are recommendations based on the user's decisions and local code review. They are not legal clearance, published installer availability, measured minimum-resource guarantees, or validation of the old implementation.
