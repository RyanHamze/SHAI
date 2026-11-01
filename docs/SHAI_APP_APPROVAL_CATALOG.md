# SHAI application map and approval catalog

Date: 2026-10-31
Status: product review draft; this document does not authorize implementation
Product: SHAI, Smart Home Automation and AI

## How to review this document

This file is the central product map for SHAI's user-facing applications and
supporting modules. It reconciles the current SHAI installer, the old
SHAIBUNTU/Cubic prototypes, and the requirements recorded in this workspace.

Use these responses while reviewing with Codex:

- `Approve 1` accepts an app's proposed name, scope, and default behavior.
- `Change 3: ...` records a specific change before implementation.
- `Hold 6` keeps an app in the plan but postpones its build.
- `Remove 8` removes an app as a separate user-facing product.
- `Approve utilities` accepts the proposed consolidation of small tools.

Nothing marked `Historical prototype` is production software. Old files still
use SHAIBUNTU paths and names; they are evidence and possible source material,
not approved identifiers. New code uses lowercase `shai` identifiers. Ubuntu
remains the operating system and keeps its own name, settings, terminal,
drivers, firmware, repositories, package manager, and security maintenance.

## Status legend

| Status | Meaning |
| --- | --- |
| Current and tested | Present in the current SHAI workspace and validated on the Ubuntu VM |
| Current prototype | Present and partly validated, but not a complete product surface |
| Historical prototype | Located in the old Cubic export; requires review, rename, and migration |
| Planned | Required or recommended, but no accepted current implementation exists |
| Optional module | Installed or enabled only after a user decision and hardware check |

## Recommended product suite

The recommendation is eight user-facing surfaces. Smaller functions live
inside these apps so the desktop does not become a collection of overlapping
launchers.

| ID | Display name | Primary role | Default presence | Current evidence | Recommendation |
| --- | --- | --- | --- | --- | --- |
| 1 | SHAI Setup | Initial assessment, recommendation, plan, and appliance conversion | Core | Current terminal installer | Build the graphical planner around the tested engine |
| 2 | SHAI Home | Daily dashboard and main landing view | Core | Planned; old dashboards are references | Build as the default desktop landing app |
| 3 | SHAPP | Install, remove, repair, and update optional SHAI-managed apps | Core | Historical PyQt prototype | Keep the SHAPP name; rebuild on the shared planner |
| 4 | SHAI Health | Monitoring, diagnostics, and approved recovery rules | Core, monitor-only | Historical repaired prototype | Keep monitoring separate from deployment |
| 5 | AIA - AI Advisor | Hardware-aware runtime, model, and voice selection | Recommended | Historical PyQt prototype | Rename its role from assistant to advisor |
| 6 | SHAI Assistant | Local chat, explanations, and voice interaction | Recommended, removable | Planned plus old rule-based prototype | Keep separate from AIA and make removal permanent |
| 7 | SHAI Control | Network, update, service, access, backup, and system controls | Core | Historical System Tools prototype | Consolidate administrative tools into one app |
| 8 | SHAI Portal | Authenticated local directory for phone and browser access | Optional | Historical local web prototype | Keep read-only by default and opt in to LAN access |

Recommended naming rule:

- Product names use `SHAI`, `SHAI Health`, `SHAI Home`, and `SHAI Assistant`.
- `SHAPP` remains the short branded name for the SHAI App Manager.
- `AIA` means `AI Advisor`, not `AI Assistant`, to avoid conflicting with SHAI
  Assistant.
- Package names, commands, services, directories, and schema IDs use lowercase
  `shai`.

## Product navigation

SHAI Home is the common starting point. The normal Ubuntu dock and application
menu remain available.

```text
SHAI Home
  |-- Overview
  |-- Automations and devices  -> Home Assistant
  |-- Applications             -> SHAPP
  |-- Health and diagnostics   -> SHAI Health
  |-- Local AI                 -> AIA
  |-- Ask SHAI                 -> SHAI Assistant side panel
  |-- Services                 -> SHAI Portal
  `-- Settings and controls    -> SHAI Control
```

Do not create separate desktop apps for Updates, Containers, Carbon Score,
Media Storage, Open Ports, Firewall, or the internet switch. Those are views
or controls within SHAI Home, SHAPP, SHAI Health, or SHAI Control.

## Shared architecture

### Ownership boundary

| Owner | Responsibilities |
| --- | --- |
| Ubuntu | OS identity, kernel, boot, drivers, firmware, desktop foundation, terminal, APT/Snap, OS security updates |
| SHAI Setup | Discovery, recommendations, approved conversion plan, debloat policy, initial configuration |
| SHAPP | SHAI-managed application and service desired state |
| SHAI Control | User-approved administrative actions and update presentation |
| SHAI Health | Read-only monitoring and explicitly approved recovery rules |
| AIA | AI runtime/model/voice recommendations and lifecycle |
| SHAI Assistant | Explanations, chat, and proposals; no direct root or Docker authority |
| Third-party services | Their own data, credentials, listeners, upgrades, and health criteria |

### Central data registry

All apps should read common, typed records instead of scraping one another's
screens or inventing separate state files.

| Proposed path | Contents | Writer |
| --- | --- | --- |
| `/etc/shai/system-policy.json` | Approved update, network, privacy, and appliance policies | SHAI Setup / SHAI Control helper |
| `/etc/shai/desired-state.json` | User-approved enabled components and deployment modes | Shared planner |
| `/etc/shai/service-registry.json` | Services, owners, endpoints, health checks, data paths | SHAPP |
| `/etc/shai/port-registry.json` | Expected ports, protocols, bind scope, purpose, owner | SHAPP / SHAI Control helper |
| `/etc/shai/network-policy.json` | LAN/WAN permissions and approved destinations | SHAI Control helper |
| `/var/lib/shai/system-profile.json` | Local hardware and software assessment | Discovery service |
| `/var/lib/shai/operation-journal.jsonl` | Plans, approvals, results, rollback evidence | Shared execution engine |
| `/var/lib/shai/update-state.json` | Last checks, available updates, source, approval state | SHAI Control |
| `/var/lib/shai/health-state.json` | Current monitored state and recent transitions | SHAI Health |
| `/var/lib/shai/ai-profile.json` | Runtime, models, resource reserves, voice tools | AIA |
| `/var/lib/shai/app-catalog.json` | Signed SHAI app metadata plus local availability | SHAPP |
| `/srv/shai/` | User data managed by selected SHAI services | Individual services |

Debian-packaged program code belongs under `/usr/lib/shai` and read-only assets
under `/usr/share/shai`. Configuration belongs under `/etc/shai`; mutable state
belongs under `/var/lib/shai`. New packages should not copy the historical
`/opt/shaibuntu` and `/etc/shaibuntu` layout.

### Shared approval flow

Every app that changes the system uses the same operation model:

1. Read local state without network access.
2. Explain the recommendation and why it fits.
3. Show source, download size, disk/RAM impact, services, ports, data paths,
   credentials, and restart requirements.
4. Label any online step with its exact source.
5. Generate a fixed operation plan from validated action IDs.
6. Require a button approval for that exact plan.
7. Open visible progress or a visible terminal when terminal execution is
   appropriate.
8. Journal the command, result, health test, and changed state.
9. Pause if scope or network destinations change.

An LLM may explain or propose an operation ID. It never supplies arbitrary
text that a privileged helper executes as shell code.

### Shared visual direction

- Operational, calm, dense, and easy to scan rather than a marketing page.
- Default background: near-black `#050805`.
- Main panel: `#0B130B`.
- Primary accent: SHAI green `#33EE33`.
- Main text: `#E9FFE9`.
- Muted text: `#A8B6A8`.
- Warning: `#FFD166`; failure: `#FF5C5C`.
- Green indicates healthy or selected, never merely decoration.
- Offer mellow and high-contrast alternatives; do not force the terminal theme.
- Use familiar icons, compact tabs, tables, toggles, and status labels.
- No nested cards, oversized headings, decorative gradients, or hidden actions.

## 1. SHAI Setup

### Purpose

SHAI Setup is the first-run appliance planner. It turns a normal supported
Ubuntu Desktop installation into a user-approved SHAI configuration while
Ubuntu remains the OS.

### Responsibilities

- Read-only local hardware, storage, network, security, software, and workload
  assessment.
- Explain `Here is what you have`, `Here is what fits`, and `Here is what I
  recommend and why`.
- Offer `Choose for me`, `Recommended`, and `Advanced` paths.
- Present debloat selections, privacy settings, desktop changes, update mode,
  Home Assistant, containers, local AI, voice, media, and backups.
- Preview exact removals, installs, downloads, services, ports, and reboot needs.
- Apply only an approved immutable plan through the shared privileged helper.
- Verify outcomes and classify Working, Needs setup, Waiting for hardware,
  Failed, Skipped, and Unsupported.

### It must not

- Start conversion merely because the DEB was installed.
- Probe the internet, scan the LAN, remove packages, or enable services on open.
- use a default `shai` account/password or rename the computer silently.
- Replace Ubuntu branding, OS identity, kernel, terminal, or repositories.

### Current status

`shai-installer` 0.2.1 now contains the GTK setup, SHAI Brand v2 assets,
strict user-owned plan validation, visible-terminal execution, exact debloat
engine, high-level architecture choices, and honest post-setup application
shells. Package, plan-boundary, reproducibility, and Ubuntu GUI startup tests
passed. Version 0.2.0 completed a full apply and passed its recorded final
health checks before the VM reboot; 0.2.1 is the revised copy/UI and offline
plan schema now installed for review. Setup does not deploy Home Assistant,
Docker, Zigbee, models, or other optional
applications; those remain SHAPP work.

### Sample view

```text
+ SHAI Setup ---------------------------------------------------------------+
| Assessment  Recommendations  Review plan  Apply  Verify                  |
|                                                                          |
| This computer                                                            |
| Ubuntu 26.04 | 4 CPU cores | 8.0 GB RAM | 112 GB free | Intel GPU       |
| Home automation fit: Good       Local AI fit: Lightweight only           |
|                                                                          |
| Setup style                                                              |
| [ Choose for me ]  [ Recommended ]  [ Advanced ]                         |
|                                                                          |
| Recommended                                                              |
| [x] Remove selected desktop extras     Saves about 1.2 GB                |
| [x] Install SHAI core apps             Offline package                   |
| [x] Home Assistant stack               Online: approved image registry   |
| [ ] Local AI model                     Not selected; 2.4 GB required     |
|                                                                          |
| Why: reserves 3 GB RAM for Ubuntu and home automation.                   |
|                                              [Review exact plan]          |
+--------------------------------------------------------------------------+
```

### Approval requested

- Recommended: approve SHAI Setup as core and keep package installation inert.
- Recommended: graphical setup uses the tested engine rather than replacing it.
- Decision: approve the three setup styles and the six-step navigation above.

## 2. SHAI Home

### Purpose

SHAI Home is the default daily dashboard after setup. It summarizes the
machine, smart-home stack, AI, privacy, updates, storage, and energy estimate,
then routes the user to the app that owns each action.

### Responsibilities

- CPU/load, RAM, storage, temperature, GPU, and driver status when measurable.
- Home Assistant and local-device summary without pretending every LAN device
  is known.
- Local AI runtime/model status and resource use.
- Firewall, expected listeners, unexpected open ports, active network mode,
  and configured online services.
- Ubuntu update availability and SHAI-managed update availability as separate
  sections.
- Home Assistant, media, AI, backup, configuration, and log locations.
- Optional estimated energy, cost, and Carbon Footprint Score.
- Quick links to SHAPP, Health, AIA, Assistant, Control, Portal, Home Assistant,
  and visible Ubuntu tools.

### It must not

- Run privileged actions itself.
- Claim all connections or data exfiltration are understood from a socket list.
- Turn monitoring estimates into factual power measurements.
- Replace Ubuntu Settings, Terminal, or Software/App Center.

### Current status

Planned. The old Tk dashboard and historical SHAI Health dashboard supply field
ideas, but neither is an approved current SHAI Home implementation.

### Sample view

```text
+ SHAI Home --------------------------------------------------- [Ask SHAI] --+
| Overview | Automations | Services | Network | Updates | Locations          |
|                                                                            |
| SYSTEM        CPU 12%   RAM 3.1/8 GB   Storage 31%   Temperature 44 C       |
| HOME          Home Assistant: Healthy    Devices: 27    Alerts: 1           |
| AI            Runtime: Installed         Model: None    Voice: Off           |
| SECURITY      Firewall: On    Expected ports: 4    Review ports: 1          |
| NETWORK       LAN only         Internet: Off        Online apps: 0           |
| UPDATES       Ubuntu: Not checked        SHAI: Current                       |
|                                                                            |
| Attention                                                                  |
| - Zigbee adapter is disconnected.                         [Open Health]     |
| - Ubuntu update status is 14 days old.                    [Review updates]  |
|                                                                            |
| Locations: /srv/shai | /srv/media | Backups not configured                 |
+----------------------------------------------------------------------------+
```

### Approval requested

- Recommended: approve SHAI Home as the default login landing app.
- Recommended: keep it read-only and delegate changes to owning apps.
- Decision: choose whether it opens maximized or restores the last window size.

## 3. SHAPP - SHAI App Manager

### Purpose

SHAPP manages optional applications and services after setup. It is not a
generic Ubuntu package manager and cannot remove protected Ubuntu components.

### Responsibilities

- Show Installed, Available, Updates, Needs setup, and History views.
- Filter by Recommended, Smart Home, Voice, Media, AI, Privacy, Backup, and
  Advanced.
- Compare resource requirements, license/source, network need, ports, data
  paths, dependencies, conflicts, and deployment modes.
- Maintain one SHAI Compose project with separate service containers for the
  recommended stack.
- Install, repair, update, back up, restore, or remove only cataloged
  SHAI-managed components.
- Keep a protected `do not touch` list for Ubuntu-critical packages. SHAPP must
  direct users to Ubuntu tools for software outside SHAI ownership.

### It must not

- Offer broad package purge/autoremove.
- Install every recommended service merely because SHAPP is opened.
- Combine unrelated daemons into one giant container.
- Silently choose host installation when a container/VM was selected.
- Remove service data without separate explicit confirmation.

### Current status

Historical PyQt prototype. It had useful resource summaries and a catalog, but
its direct-host/physical-container/VM model predates the current recommendation
of one managed Compose project with separate containers. Its install helpers
were not completely present in the curated Cubic export.

### Sample view

```text
+ SHAPP - SHAI App Manager -----------------------------------------------+
| Installed | Available | Updates | Needs setup | History                   |
| Filter: [Smart Home v]  Hardware fit: [Compatible v]  Search: [________] |
|                                                                          |
| Application       Status       RAM       Disk      Network      Action    |
| Home Assistant    Recommended  0.9 GB    2.0 GB    LAN          [Select]  |
| Mosquitto MQTT    Recommended  64 MB     250 MB    Local        [Select]  |
| Zigbee2MQTT       Waiting HW   256 MB    800 MB    LAN          [Details] |
| Jellyfin          Optional     1.2 GB    2.0 GB    LAN/online*  [Select]  |
|                                                                          |
| * Online only for an approved image download and optional metadata.       |
| Selected: 2 | Added disk: 2.3 GB | Reserved RAM: 964 MB                  |
|                                                   [Review deployment]     |
+--------------------------------------------------------------------------+
```

### Approval requested

- Recommended: approve SHAPP as a core app and retain the short name.
- Recommended: default to one managed stack with separate service containers.
- Recommended: Home Assistant is preselected only when hardware fits and is
  always deselectable.

## 4. SHAI Health

### Purpose

SHAI Health monitors host resources, service health, expected ports, network
state, and hardware dependencies. Recovery is monitor-only until the user
approves narrowly scoped rules.

### Responsibilities

- Show host, service, network, listener, radio/controller, and storage health.
- Distinguish Healthy, Degraded, Failed, Disabled, Not installed, and Waiting
  for hardware.
- Keep a local transition/event history and export a redacted diagnostic report.
- Provide an emergency stop for approved recovery automation.
- Support per-target recovery rules with failure duration, action, attempts,
  cooldown, post-action verification, and audit logging.
- Feed read-only summaries to SHAI Home and optional Home Assistant entities.

### It must not

- Mount the unrestricted Docker socket.
- Restart containers/services or reboot by default.
- Treat loss of internet as failure of otherwise local services.
- Expose its status API beyond loopback unless explicitly designed and approved.

### Current status

Historical repaired standard-library prototype with a PyQt GUI. The audit found
the original handoff incomplete; the repaired version bound to loopback and
disabled recovery. It is useful source material but has not been migrated to
current SHAI packaging or retested on the new VM.

### Sample view

```text
+ SHAI Health -------------------------------------------------------------+
| Overview | Services | Network and ports | Hardware | Recovery | Events     |
|                                                                          |
| Overall: DEGRADED       Heartbeat: Live       Last check: 10 seconds ago   |
| Memory 39%              Disk 31%              Load 0.42                    |
|                                                                          |
| Target             State         Detail                         Action     |
| Home Assistant     Healthy       84 ms                          [Open]     |
| Mosquitto          Healthy       TCP 1883                       [Open]     |
| Zigbee2MQTT        Waiting HW    Adapter not detected           [Guide]    |
| Port 631/tcp       Review        Not in approved registry       [Inspect]  |
|                                                                          |
| Recovery mode: Monitor only                         [Configure rules]      |
+--------------------------------------------------------------------------+
```

### Approval requested

- Recommended: approve SHAI Health as core, monitor-only by default.
- Recommended: no host reboot rule in the initial release.
- Decision: whether Home Assistant health entities are enabled automatically
  when MQTT is installed or require a separate toggle.

## 5. AIA - AI Advisor

### Purpose

AIA is the hardware-aware AI runtime, model, and voice-component advisor. It
owns AI lifecycle decisions so SHAPP does not become a model catalog and SHAI
Assistant does not administer its own runtime.

### Responsibilities

- Detect CPU features, cores, RAM, GPU/VRAM, disk, power profile, existing AI
  runtimes, and reserved smart-home capacity without network access.
- Offer `No AI` as a first-class choice.
- Rank up to three reviewed models that fit after Ubuntu and automation reserves.
- Show model publisher, origin, license, version, source, integrity method,
  size, context, CPU/GPU requirements, and expected runtime impact.
- Manage an approved runtime, model download/import, verification, status,
  removal, and rollback history.
- Recommend Whisper, Speech-to-Phrase, Piper, openWakeWord, and Wyoming tools
  according to hardware and intended use.

### It must not

- Bundle model weights by default.
- Recommend a model solely from marketing size or CPU name.
- Download a runtime/model without per-operation network approval.
- Directly control physical devices or bypass Home Assistant safety rules.
- Assume the historical model catalog is current or license-approved.

### Current status

Historical PyQt/CLI prototype with local hardware detection, recommendation
budgets, No AI, visible command previews, network opt-in, and local imports.
Its catalog and policies require a fresh review. No AI runtime or weights are
part of the current SHAI package.

### Sample view

```text
+ AIA - AI Advisor --------------------------------------------------------+
| Hardware | Recommendations | Catalog | Installed | Voice | History         |
|                                                                          |
| 8.0 GB RAM | 4 cores | Intel GPU | 112 GB free                           |
| Reserved: Ubuntu 2.0 GB | Home automation 2.5 GB | AI budget 3.5 GB       |
|                                                                          |
| (x) No AI - best reliability and lowest resource use                     |
| ( ) Small local model A   2.1 GB RAM   CPU OK   License reviewed          |
| ( ) Small local model B   3.0 GB RAM   CPU OK   Slower response           |
|                                                                          |
| Voice: [ ] Speech-to-Phrase  [ ] Piper  [ ] Whisper                      |
| Network for this operation: Off                                          |
|                                               [Compare] [Review install]  |
+--------------------------------------------------------------------------+
```

### Approval requested

- Recommended: approve `AIA - AI Advisor` as the display name.
- Recommended: AIA is installed but no runtime/model is selected automatically.
- Decision: retain or revise the historical publisher-origin restriction after
  a separate documented model policy review.

## 6. SHAI Assistant

### Purpose

SHAI Assistant is the local conversational helper. It explains the system,
guides setup and troubleshooting, and proposes approved operations. It can dock
on the right, minimize, close, disable autostart, or be permanently removed.

### Responsibilities

- Provide deterministic offline explanations before any LLM is installed.
- Optionally use the AIA-selected local model.
- Explain recommendations in plain language and cite the local facts used.
- Show `Here is what I suggest`, the reason, impact, and exact proposed action.
- Offer buttons to view details, approve and open visible execution, postpone,
  or reject.
- Integrate with voice only when microphone/listening/retention settings are
  explicitly enabled.
- Provide settings for theme, accent, autostart, voice, local history, clear
  history, disable, and permanent removal.

### It must not

- Execute commands silently or hold unrestricted sudo/Docker privileges.
- Invent package names, ports, or shell commands and send them to a root shell.
- Contact an online model/API unless the user separately enables and sees it.
- Interpret spoken approval as sufficient for privileged execution; the user
  still presses the approval button.
- Hide microphone state or retain recordings by default.

### Current status

Planned for the new SHAI architecture. The early rule-based HTTP/Tk prototype
and its right-side-panel concept are historical references. Its suggested Qwen
0.5B model conflicts with the later historical publisher policy and therefore
is not an approved current default.

### Sample view

```text
                                      + SHAI Assistant --------------------+
                                      | Local mode | Microphone off     [_][x]
                                      |                                    |
                                      | You: Why is Zigbee unavailable?     |
                                      |                                    |
                                      | SHAI: No compatible coordinator is  |
                                      | currently detected. Zigbee2MQTT is  |
                                      | installed but intentionally stopped.|
                                      |                                    |
                                      | Suggested action                    |
                                      | Rescan USB devices. Read-only; no   |
                                      | internet connection required.       |
                                      |                                    |
                                      | [View details] [Approve scan]        |
                                      | [Not now]                           |
                                      |                                    |
                                      | [Type a message...]          [Send] |
                                      +------------------------------------+
```

### Approval requested

- Recommended: approve SHAI Assistant as recommended, removable, and optional
  at login.
- Recommended: deterministic mode remains useful without a model.
- Decision: approve `SHAI Assistant` or choose a more distinctive persona name.

## 7. SHAI Control

### Purpose

SHAI Control is the single administrative UI for SHAI-managed policy and
visible Ubuntu maintenance links. It replaces separate launchers for Network,
Manual Updates, Containers, Diagnostics, and Environment Updates.

### Responsibilities

- Network and access: firewall posture, SSH state, portal LAN access, internet
  mode, expected ports, and approved destinations.
- Updates: present Ubuntu OS/package/security/firmware status separately from
  SHAI packages, containers, models, and catalogs.
- Services: start/stop/restart only SHAI-managed services with confirmation.
- Storage and backups: locations, capacity, encrypted backup configuration,
  restore testing, and retention.
- Privacy: Ubuntu reporting/location policy, configured online integrations,
  microphone state, and local data retention.
- Diagnostics: local report generation, logs, repair operations, and links to
  Ubuntu Settings, Terminal, App Center, and Software Updater.
- Appearance: SHAI wallpaper, accent, dashboard autostart, and launcher choices.

### It must not

- Replace Ubuntu's package manager, firmware updater, terminal, or Settings.
- Claim an update is available without an approved online check or imported
  offline metadata.
- Disable the firewall or expose a service merely because it was installed.
- store sudo passwords or make sudo passwordless.

### Online labels

Every update action shows one of these before execution:

- `Offline: reads previously downloaded metadata only`
- `Online check: Ubuntu repositories`
- `Online download: Ubuntu repositories`
- `Online check: SHAI signed repository`
- `Online pull: named container registry and image`
- `Online download: named model publisher/source`

### Current status

The Web Offline/Online proxy control is a current tested prototype but is not a
host-wide firewall isolation mechanism. The historical System Tools PyQt app is
a useful layout reference; its helper and update assumptions require redesign.

### Sample view

```text
+ SHAI Control ------------------------------------------------------------+
| Network | Updates | Services | Storage | Privacy | Appearance | Support    |
|                                                                          |
| Ubuntu updates                                                           |
| Last online check: Never        Automatic installation: Off               |
| [Check Ubuntu sources online]   [Review imported metadata]                |
|                                                                          |
| SHAI updates                                                             |
| Installed 0.1.2 | Channel Stable | Signature policy Active               |
| [Check SHAI source online]      [Import offline update]                   |
|                                                                          |
| Container updates: No online check performed                             |
| Firmware updates: No online check performed                              |
|                                                                          |
| No action runs until its source, changes, and restart plan are approved.  |
+--------------------------------------------------------------------------+
```

### Approval requested

- Recommended: approve one consolidated SHAI Control app.
- Recommended: preserve Ubuntu tools and label ownership clearly.
- Decision: whether OS update notifications are fully suppressed or replaced
  with a quiet SHAI Home status indicator while critical alerts remain visible.

## 8. SHAI Portal

### Purpose

SHAI Portal is a phone-friendly directory of deployed local services. It is
loopback-only by default and becomes available to selected LAN clients only
after an explicit access decision.

### Responsibilities

- List only installed and healthy local service interfaces.
- Group Smart Home, Automation, Media, AI, Monitoring, and Administration.
- Open Home Assistant, Zigbee2MQTT, ESPHome, Node-RED, Jellyfin, and other
  approved local interfaces.
- Show service state and local address without exposing credentials.
- Use real authentication and scoped sessions for LAN mode.

### It must not

- Treat MAC allowlisting as authentication.
- Proxy SSH or become an unrestricted remote administration surface.
- Bind to all interfaces by default.
- expose service URLs that are not approved for the requesting network scope.
- Perform privileged mutations in the first release.

### Current status

Historical standard-library web prototype bound locally and supported an access
key plus same-link MAC filtering. The tile directory is reusable as a concept;
the security design is not sufficient for current LAN access requirements.

### Sample view

```text
+ SHAI Portal -------------------------------------------------------------+
| Local services                                  shai-vm | LAN access: Off |
|                                                                          |
| Smart Home                                                               |
| Home Assistant       Healthy       http://shai-vm.local:8123   [Open]    |
| Zigbee2MQTT          Waiting HW    Not started                 [Details] |
| ESPHome              Not installed                             [SHAPP]   |
|                                                                          |
| Media                                                                    |
| Jellyfin             Healthy       http://shai-vm.local:8096   [Open]    |
|                                                                          |
| Administration interfaces are available only on this computer.           |
+--------------------------------------------------------------------------+
```

### Approval requested

- Recommended: approve Portal as optional and loopback-only by default.
- Recommended: first release is a directory, not a remote control panel.
- Decision: postpone LAN/phone mode until authenticated TLS sessions are
  designed, or include that work in the first public release.

## Consolidated utilities

These functions should exist without becoming full standalone applications.

| Utility | Proposed home | Status | Recommendation |
| --- | --- | --- | --- |
| Web Offline/Online | SHAI Control plus panel quick toggle | Current proxy prototype | Keep accurately labeled; later add firewall-backed LAN-only mode |
| About SHAI | SHAI Control > Support | Historical prototype | Rebuild with accurate Ubuntu attribution and package versions |
| Terminal | Ubuntu dock/menu and links from plans | Existing Ubuntu app | Keep Ubuntu Terminal; do not brand it as a SHAI terminal |
| Updates | SHAI Control > Updates and SHAI Home summary | Historical separate apps | Consolidate |
| Containers and Services | SHAI Control > Services and SHAPP lifecycle | Historical separate launcher | Consolidate |
| Diagnostics and Recovery | SHAI Health plus SHAI Control > Support | Historical separate launcher | Consolidate |
| Carbon Footprint Score | SHAI Home optional module | Planned | Estimate label required; default electricity rate editable |
| Media storage wizard | SHAPP media category / SHAI Setup | Planned | Use `/srv/media`; never format implicitly |
| Open ports viewer | SHAI Health and SHAI Home summary | Historical prototype | Read-only with expected/review classification |

## SHAPP service catalog groups

These are deployable modules, not additional SHAI desktop apps.

### Smart home and automation

| Component | Default proposal | Notes |
| --- | --- | --- |
| Home Assistant Container | Strongly recommended when hardware fits | Main automation hub; explain lack of HAOS Supervisor/apps |
| HAOS virtual machine | Advanced alternative | Only when virtualization, RAM, storage, networking, and radio passthrough fit |
| Mosquitto MQTT | Recommended with MQTT-dependent services | Authenticated local broker; no anonymous default |
| Zigbee2MQTT | Optional, hardware-gated | Start only after compatible coordinator selection |
| Z-Wave JS UI | Optional, hardware-gated | Separate from Zigbee; stable controller path required |
| ESPHome | Optional | Useful for ESP devices; source/update behavior shown |
| Node-RED | Optional | Flow editor; protect admin UI and credentials |
| Matter Server / Thread | Optional, experimental until qualified | IPv6, discovery, border-router, and hardware implications shown |
| openHAB | Optional alternative | Do not preselect beside Home Assistant without explaining overlap |

### Local voice

| Component | Default proposal | Notes |
| --- | --- | --- |
| Speech-to-Phrase | Recommended for low-resource command use | Constrained commands, lighter than general transcription |
| Whisper | Optional based on hardware | General speech-to-text; show model and latency requirements |
| Piper | Recommended when voice output is selected | Local text-to-speech; voice license/source review required |
| openWakeWord | Optional | Listening state and mute must remain visible |
| Wyoming services | Recommended integration layer | Local protocol endpoints registered and scoped |

### Media

| Component | Best fit | Default proposal |
| --- | --- | --- |
| Jellyfin | Privacy-first local video/music/photo streaming | Recommended media choice |
| Plex | Polished clients and broad compatibility | Optional; account/cloud behavior disclosed |
| Emby | Commercial-freemium server alternative | Optional |
| Navidrome | Lightweight music-first server | Optional for old hardware |
| Kodi | TV-attached playback rather than central server | Optional client/player |
| Gerbera | Lightweight DLNA/UPnP serving | Optional advanced choice |

Recommended media paths:

```text
/srv/media/movies
/srv/media/tv
/srv/media/music
/srv/media/photos
/srv/media/home-videos
/srv/media/books
/srv/media/downloads
/srv/media/transcode
```

### Privacy, monitoring, and backup

| Component | Default proposal | Notes |
| --- | --- | --- |
| KeePassXC | Optional | Local encrypted credentials; not managed through browser/cloud |
| BorgBackup plus encryption | Recommended configuration, not automatic | Destination, schedule, retention, and restore test required |
| OpenSnitch | Advanced optional | Per-application outbound control; can be noisy and resource intensive |
| AdGuard Home or Pi-hole | Optional, mutually compared | Network-wide DNS role can disrupt a home if misconfigured |
| Suricata | Advanced/server hardware only | High resource/storage cost; not a default exfiltration solution |
| Zeek | Advanced/server hardware only | Metadata analysis and retention implications |
| ntopng | Optional monitoring | Port, retention, and resource use disclosed |

No tool should be marketed as guaranteed exfiltration prevention. SHAI should
describe configured destinations, observed connections, and policy violations
separately.

### Energy and carbon

The energy module belongs in SHAI Home and SHAI Health, with configuration in
SHAI Control. It may use measured device power when available or estimates from
CPU/GPU/storage/service utilization. The UI always labels estimates, uses a
default electricity rate of `$0.13/kWh`, permits location-specific rates, and
supports user-defined devices and reviewed data adapters. External APIs are
off by default and individually disclosed.

## Packaging proposal

One bootstrap installs the core signed package and launches SHAI Setup. The
internal package split keeps privileges and removability understandable.

| Package | Contents | Suggested default |
| --- | --- | --- |
| `shai-installer` | Bootstrap, Setup UI, discovery, plan creation | Required first package |
| `shai-core` | Shared schemas, registry reader, planner client, theme assets | Core |
| `shai-home` | Daily read-only dashboard | Core |
| `shai-shapp` | App catalog and lifecycle UI | Core |
| `shai-health` | Monitor and diagnostic UI/service | Core, monitor-only |
| `shai-control` | Administrative UI and validated helper client | Core |
| `shai-aia` | AI Advisor UI and model catalog | Recommended |
| `shai-assistant` | Chat panel, deterministic explanations, optional local model client | Recommended, removable |
| `shai-portal` | Local service directory | Optional |
| `shai-stack` | Compose manifests and service adapters, no bundled third-party images | Optional when services selected |

The package split is not permission to create many background daemons. SHAI
Home, SHAPP, AIA, Control, and Setup should normally be on-demand desktop apps.
Only Health, Assistant when enabled, Portal when enabled, and selected service
components need persistent processes.

## Resource and startup rules

- No Electron runtime is recommended for the first release.
- Select one native GUI toolkit after measuring startup time, installed size,
  idle RAM, accessibility, and Ubuntu integration. Historical PyQt6 is the
  leading reference, not an automatic dependency decision.
- SHAI Home may autostart after setup; every other main window is on demand.
- SHAI Assistant autostart is user-selectable and easy to disable.
- On low-memory hardware, background components reduce polling rates and no AI
  model is recommended.
- No service starts solely because its package files were unpacked unless that
  behavior was shown in the approved plan.

## Recommended implementation order

1. Freeze names, ownership boundaries, and this eight-app map.
2. Define shared schemas, state registry, operation IDs, journal, and protected
   Ubuntu package policy.
3. Add the SHAI Setup GUI around the current tested installer engine.
4. Build SHAI Home as a read-only consumer of mocked and then real registry data.
5. Rebuild SHAPP on the shared planner with one harmless reference component.
6. Migrate SHAI Health in monitor-only mode and verify expected port reporting.
7. Build SHAI Control around network/update/privacy state without duplicating
   Ubuntu maintenance engines.
8. Migrate AIA with a freshly reviewed catalog and No AI default.
9. Build deterministic SHAI Assistant, then optional AIA-selected model support.
10. Rebuild Portal locally; defer LAN mode until its authentication design passes
    security review.
11. Add Home Assistant and companion services one at a time with install,
    health, update, backup, restore, and removal tests.

## Approval worksheet

| ID | Decision | Notes |
| --- | --- | --- |
| 1. SHAI Setup | Wave A specified and built | Full reverted-VM apply remains pending |
| 2. SHAI Home | Pending | |
| 3. SHAPP | Pending | |
| 4. SHAI Health | Pending | |
| 5. AIA | Pending | |
| 6. SHAI Assistant | Pending | |
| 7. SHAI Control | Pending | |
| 8. SHAI Portal | Pending | |
| Consolidated utilities | Pending | |
| Service catalog groups | Pending | |
| Package split | Pending | |
| Implementation order | Pending | |

## Evidence used

Current authority:

- `PROJECT_CONTEXT.md`
- `docs/CURRENT_DECISIONS.md`
- `docs/SHAI_INSTALLER_PLAN.md`
- `artifacts/installer-development/2026-10-31/BUILD_REPORT.md`
- `connectivity/README.md`

Historical reference only:

- `reference/cubic-2026-10-30/`
- `../sha-ubuntu/SHAI_LEGACY_REFERENCE.md`
- `../sha-ubuntu/SHAIBUNTU/docs/AIA_PRODUCT_REQUIREMENTS.md`
- `../sha-ubuntu/SHAIBUNTU/docs/V054_SHAPP_DEPLOYMENT_ARCHITECTURE.md`
- `../sha-ubuntu/SHAIBUNTU/docs/REQUIREMENTS_LOCKED.md`
- `../sha-ubuntu/docs/shai-assistant.md`
- `../sha-ubuntu/docs/dashboard.md`
- `../sha-ubuntu/docs/media-server-options.md`

Historical requirements were accepted only when they remain compatible with
the current SHAI product decision, offline-first policy, Ubuntu ownership, and
manual approval boundary.
