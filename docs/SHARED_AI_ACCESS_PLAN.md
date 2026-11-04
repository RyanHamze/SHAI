# Shared SHAI AI Access And Memory

Status: implemented in the 0.14.0 release candidate and tested on the Ubuntu VM.
See RELEASE_0_14_0_VALIDATION.md for evidence and remaining limitations.

## Private Local Store

An LLM does not automatically read its model directory or another app's files.
SHAI provides one private host-side context folder per desktop user:

| File | Purpose |
| --- | --- |
| `~/.local/share/shai/memory/context.json` | Generated structured snapshot |
| `~/.local/share/shai/memory/context.md` | Human-readable snapshot |
| `~/.local/share/shai/memory/notes.json` | Explicitly saved non-sensitive notes |
| `~/.local/share/shai/memory/events/YYYY-MM-DD.jsonl` | Timestamped changed-section names, not raw values |

Directories are 0700, generated files 0600. Writes are atomic, refresh/note
updates locked, and symlinked storage directories rejected. Refresh replaces
generated context without deleting notes. This is local context, not training.
The collector never uploads data, checks the internet or downloads anything.

The unprivileged `shai-context` helper collects this user's AIA configuration,
integration endpoints/settings and credential-present flags, model filenames,
SHEALTH settings/latest SQLite sample, SHAPP settings/catalog/installed Debian
packages, managed stack state/service registry, existing network/firewall
snapshot, and local ExifTool guide path/command recipes. Sources and timestamps
are included; missing samples are not fabricated. The Debian inventory does not
claim to include all manual, Snap or Flatpak installations.

The user timer refreshes every 30 seconds. Chats refresh on demand using a
15-second cache invalidated by changed settings, model directory, package
database, health database, network snapshot or notes. AIA Settings has
**Remember this note** and **Open local memory folder**. Note saving is explicit,
independent of saving chat history; contents pass over stdin, not process
arguments or activity logs. Up to 100 notes are retained; review/remove them
in `notes.json`. There is no automatic harvesting of conversations.

## Both Chat Frontends

`shai-context-gateway.service` runs unprivileged at `127.0.0.1:11437` using the
existing private inference bearer key. AIA and SHAI-managed Open WebUI now use
this gateway's `/v1` inference endpoint. It injects bounded, current local
context into each chat, retains the frontend's policy prompt, replaces prior
SHAI context blocks and prioritizes recent notes and question-relevant sections.

Real responses and streamed tokens still come from the selected llama.cpp model
at `127.0.0.1:11435`; no substitute answers are generated. The gateway verifies
that its established upstream socket belongs to this user's active model
service PID before sending credentials/context. Missing process visibility or
service identity fails closed. AIA bypasses HTTP proxies for these local calls.

Live Ubuntu testing found that a mount-namespaced gateway cannot inspect its
peer's `/proc/PID/fd` links. The gateway intentionally omits user filesystem
mount namespaces so the strict peer identity gate works. It remains an ordinary
desktop UID with NoNewPrivileges, loopback filtering, address-family/resource
limits and fixed paths; it gains no root access or arbitrary filesystem API.

Open WebUI also receives the authenticated **SHAI Local Memory** OpenAPI tools:

- Spec: `http://127.0.0.1:11437/openapi.json` (schema only; no private data).
- `GET /v1/shai/context`: full sanitized structured snapshot.
- `GET /v1/shai/memory`: shared notes, path and timestamp.

Automatic prompt context works without tool calling. Complete tool results may
exceed a small model's context window; availability does not guarantee competent
use. [Open WebUI documents this model limitation](https://docs.openwebui.com/features/extensibility/plugin/tools/openapi-servers/).
Prompt excerpts explicitly disclose truncation. Errors remain errors rather
than silently substituted responses. Four concurrent handlers and socket
timeouts limit gateway resource usage.

## Secrets And Permissions

Credential-named fields and marked custom-secret fields become configured flags.
Known secret values, including the inference key, are removed from other exported
strings. HTTP URL credentials/query strings/fragments are stripped, including
mixed-case schemes. The root vault is never opened. Activity exports contain
event names/counts only, not raw logs or chat text. Custom secret fields must
still be correctly marked: no heuristic can recognize every credential hidden
under an innocent field name. Suspected sensitive notes are rejected; never put
passwords or tokens in memory.

Context/memory/inference require bearer authentication. The API provides no
arbitrary file read, configuration write, memory write or command endpoint.
Open WebUI has no home-folder/vault/root-filesystem/Docker-socket mount. Its
existing proposal-only Control Broker at 11500 stays separate and gains no
additional capabilities. Metadata cleaning still uses the approved GUI flow.
Notes, filenames and retrieved metadata are reference data, never authorization.

This is a trusted single-owner workstation design. Processes under the desktop
UID can already read that user's files/key. All accounts in the managed WebUI
share its one host desktop identity; this is not per-WebUI-account isolation.
Loopback HTTP is not a general untrusted multi-user transport or pinned TLS.
Do not expose these ports to the LAN/internet or grant other WebUI users access
while expecting their host memory to be separate.

## Installation And Activation

The build recipe includes the helpers and three user units. DEB installation
alone remains inert. Approved Setup initializes the store/timer before recording
success. AIA and approved model/runtime install scripts prepare the private key,
refresh context and start the gateway. SHAPP's approved Open WebUI install path
also starts the user's context services.

After a later approved deployment, close/reopen any old AIA process. Existing
Open WebUI containers need managed Compose configuration reapplied/restarted to
receive the new endpoint/tools. Source edits alone do not alter live containers.
Direct raw-11435/Ollama/other manual provider connections do not get SHAI context.

## Deferred

- Typed, previewed and revision-bound AIA config edits from chat.
- Broker-mediated ExifTool inspection/cleanup with scoped approval.
- Remember/forget proposals from Open WebUI with user confirmation.
- Multi-user transport/identity isolation and paginated model tool retrieval.
- Live VM AIA/Open WebUI acceptance after deployment approval.

## Tests

`tests/test-shared-memory.py`: private modes, real config snapshots, secret
canaries/URL stripping, optional schema errors, cache invalidation, symlink
refusal, notes, raw-log exclusion, recent-note budgets, nonduplicated injection.
Real loopback HTTP tests cover auth, matching OpenAPI routes, unchanged upstream
responses, SSE, rejected writes/bad payloads, upstream identity rejection, key
permissions and concurrent limits. The upstream is a fixture, not a real LLM;
no new live VM GUI/container acceptance is claimed.
