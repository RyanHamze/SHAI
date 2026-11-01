# SHAI network policy

User decision recorded 2026-10-30. This supersedes any earlier assumption that background online checks are allowed by default.

## Default and terminology

SHAI must function offline, with internet access denied until the user explicitly authorizes an online operation. No automatic update/version checks, connectivity probes, telemetry, model downloads, registry queries, external DNS lookups, cloud calls or firmware metadata refreshes.

Distinguish three scopes accurately:

- **Offline / internet blocked:** no WAN communication. Approved local device networking may remain available.
- **LAN-only:** communicate only with explicitly approved local interfaces/devices/services; this supports Home Assistant, radios, local AI and phone access where selected.
- **Air-gapped / all network blocked:** no network communication, including LAN. Use USB/local files for imports. A real physical air gap requires physical network disconnection; software filtering alone must not be described as a physical air gap.

Start with no SHAI-initiated network access. User approval of a LAN setup plan may authorize its specified ongoing local integrations. LAN permission never implies internet permission. Avoid breaking an existing remote administrative connection without a clearly approved transition plan and a recovery path.

## Explicit online actions

Use clear labels such as:

- Check online source
- Download from online source
- Install from online source
- Refresh firmware information from online source
- Enable scheduled online checks

Before approval, show purpose, responsible app/service, destination source(s), information sent, expected downloads, required permissions and access duration. If redirects/CDNs require additional sources, disclose the provider scope and enforce the approved policy rather than silently enabling unrestricted internet.

Approval is scoped to the displayed operation or explicitly configured schedule. It does not permanently enable internet for the host, containers, assistant or other apps. Close temporary access on success, failure, cancellation and timeout. Revocation stops additional transfers; do not claim bytes already sent can be recalled.

Scheduled online checks, downloads and installations are separate opt-in policies and all default off. Cached/local checks must say when information was last obtained and must not imply current online freshness. Display Cached status, Never checked online, or Online check required as appropriate.

The initial command-line download or downloaded installer can require internet acquisition, but it must say so. Offer a local-file launch/import route. Dependencies absent from local media require a scoped download approval; do not silently run apt update, Docker pulls or AI model pulls.

## Enforcement and ownership

This is a host/appliance policy, not merely an assistant prompt. Inventory existing Ubuntu connectivity checks, APT timers, Snap refreshes, firmware refreshes, time sync, reporting services, DNS behavior and third-party updaters. Show the proposed changes for approval. Ubuntu remains the OS and supplies its update mechanisms; those mechanisms must still obey the approved network policy.

Cover IPv4, IPv6, host processes, Docker forwarding/egress, VM networking, DNS, proxies and browser/webview behavior. A private Docker bridge or internal address does not by itself prove internet isolation. Avoid globally opening WAN access for a single approved updater. If isolation cannot be enforced or a tool contacts undocumented sources, show the limitation and do not claim an air gap or strict offline compliance.

Use LAN/local time sources where available or explain offline clock limits. Optional cloud integrations require continuing explicit permission and a visible status; a one-time install approval does not authorize future cloud runtime traffic.

Dashboard must distinguish configured permission from observed traffic and unknown visibility. Record approvals/revocations and operation outcomes locally without exposing secrets. Do not claim to know every payload sent simply from a connection list.

## Offline imports and tests

Support local packages, approved dependency bundles, container-image archives, model/voice files and firmware files where upstream supports them. Validate authenticity/integrity, compatibility, licensing and metadata freshness. Missing trusted material must produce a clear blocked/pending state, not trigger a hidden network fallback.

Acceptance tests must include default startup, idle/background activity, discovery, cached update views, assistant use, failure/retry and each online action. Observe actual host/container/VM traffic, verify no unauthorized WAN/DNS traffic on IPv4/IPv6, and verify access closes after cancellation/failure. Test approved LAN integrations independently. Validate all-network-blocked mode separately. Do not describe the policy as implemented until enforcement and traffic tests pass.

## Proxy-based desktop prototype

The first tested desktop control is a proxy-based Web Offline / Online toggle. Web Offline is the system-wide dconf default for new users. It sends HTTP, HTTPS, FTP and SOCKS proxy-aware traffic to closed loopback port 1 while bypassing localhost, `.local` and common RFC1918 private-LAN addresses. Firefox is managed with a system-wide enterprise policy that locks it to the system proxy, so users cannot accidentally select a separate Firefox proxy mode.

This control is convenience and defense in depth, not complete enforcement. Applications that ignore GNOME proxy settings can still reach the internet. The dashboard must display this state as **Web Offline (proxy)** rather than **Internet blocked** or **Air-gapped** until firewall-backed LAN-only enforcement and traffic tests are complete.
