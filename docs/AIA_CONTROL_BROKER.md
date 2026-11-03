# AIA Inspector and SHAI Control Broker

## Boundary

AIA is an inspector and configurator. It reads local SHAI state, publishes a
sanitized inventory, and never performs a control action from chat. Open WebUI
is an optional local chat interface for a selected stronger model. Neither the
model nor Open WebUI receives root, a Docker socket, raw shell access, or secret
values.

`shai-control-broker` is the only privileged path. It binds to `127.0.0.1:11500`
and accepts only structured, allowlisted proposals. The local SHAI Control Center
is the only client that can approve or reject a proposal. Every proposal and
result is appended to `/var/log/shai/control/YYYY-MM-DD.log`.

## Secret handling

Integration values such as Home Assistant tokens and MQTT passwords are migrated
from `~/.config/shai/aia.json` into `/etc/shai/secrets/aia/<user>/<integration>.json`
with `0700` parent directories and `0600` records. AIA's configuration retains a
`vault://` reference only. The broker resolves a secret internally when an
approved adapter needs it; it never exposes it through inventory, proposal, or
chat output.

File permissions are access control, not encryption at rest. Full-disk encryption
through Ubuntu/LUKS remains the supported protection for an offline appliance at
rest. Do not invent an application encryption key stored on the same disk.

## Initial capability set

- Home Assistant service call with a vault-backed long-lived token.
- Restart of a small explicit SHAI service allowlist.
- SHAI managed Docker-stack apply restricted to known stack services.

Locks, alarms, covers, valves, garage doors, and climate requests are labelled
high risk. They still require explicit Control Center approval. The broker has no
generic shell, file read, Docker socket, or raw MQTT capability.

## Open WebUI integration

Open WebUI may be installed from SHAPP as a loopback-only optional interface.
It calls the selected llama.cpp model through its existing loopback API. The
control token is distinct from the model API key and can only create proposals;
it cannot approve or execute them. SHAI supplies `http://127.0.0.1:11500/openapi.json`
as an external OpenAPI connection, using `/v1/inventory` and `/v1/proposals`,
never the vault. We deliberately do not use an in-process Open WebUI Workspace
Tool because those run arbitrary Python inside the WebUI server.
