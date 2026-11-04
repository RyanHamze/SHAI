# Shared AI Memory Source Validation

Date: 2026-11-04 (America/Chicago).
Status: source-only. No new DEB, VM deployment, Git commit or GitHub push.
Canonical source: `C:\Users\ryan\Documents\SHAI`.

## Implemented

- Per-user local context/notes under `~/.local/share/shai/memory/`.
- Sanitized AIA/integration, SHEALTH, SHAPP, system and ExifTool references.
- Atomic private snapshots, change-only daily section events, explicit notes.
- Offline user refresh timer and authenticated loopback gateway on port 11437.
- AIA and managed Open WebUI inference wired through that gateway.
- Authenticated OpenAPI context/memory read tools for Open WebUI.
- Context injection preserves frontend policy and recent notes, avoids duplicate
  blocks, and enforces a 3500-character prompt budget including JSON escaping.
- Fixed upstream only; connected socket verified against the user model-service
  PID before sending keys/context. Bounded handlers and socket timeouts.
- Setup/model/runtime/Open WebUI startup hooks and package inclusion recipe.

## Passing Source Tests

| Suite | Checks |
| --- | ---: |
| test-shared-memory.py | 22 |
| test-aia-health-regressions.py | 13 |
| test-aia-install-controls.py | 10 |
| test-aia-runtime-startup.py | 5 |
| test-chat-context.py | 6 |
| test-launcher-sync.py | 5 |
| test-shapp-backends.py | 2 |
| test-setup-shapp-audit.py | 32 |
| test-ui-wiring.py | 2 |
| Total | 97 |

The shared-memory HTTP tests use real local sockets and a controlled upstream
fixture, not an LLM. They assert unchanged upstream responses, shared context
in both frontend-style payloads, SSE, auth rejection, invalid payload rejection,
no config/file-write routes and no payload sent on failed upstream identity.
Fixture systemctl output identifies the fixture PID; a real user manager and
real llama process were not started. Test modules mock privileged app/Setup
operations; the printed removal messages are fixtures, not real removals.

Python compilation passed for changed Python entry points. `bash -n` passed
for the build recipe and Setup engine. Direct `systemd-analyze --user verify`
could not complete because the new absolute ExecStart helpers are not installed
on this development host. Its file-mode warnings refer to the Windows-mounted
source files; the build recipe explicitly installs units 0644 and helpers 0755.
ShellCheck and Docker Compose are unavailable locally; neither was claimed run.

## Before Release

- Build/deploy only after approval; reopen AIA and reapply managed Open WebUI
  configuration so it actually uses 11437 rather than an old direct endpoint.
- Verify real user units, API-key handling, active model, visible remembered
  note and context freshness in each live frontend, with internet disconnected.
- Test real streaming and inference within the 2048-token model window; reject
  oversize prompts honestly. Full inventory tools may need a larger model.
- Verify package removal stops enabled user services; the existing installer
  has no general user-service uninstall lifecycle and that work remains pending.
- This remains a single-owner localhost deployment. No pinned-TLS transport or
  per-Open-WebUI-account host-memory isolation is claimed.
- Typed chat configuration edits, approved metadata actions and WebUI memory
  writes remain deferred. See `SHARED_AI_ACCESS_PLAN.md` for boundaries.
