# AIA AI Center, 2026-11-03

AIA remains the complete local AI center. The small assistant, hardware scanning,
model recommendations, catalog installation, GGUF import, model removal,
default selection, chat, voice recommendations, integrations, activity and
settings have not been replaced by the broker.

## Model lifecycle

- Catalog downloads require explicit online permission and a visible terminal.
- A manually downloaded GGUF can be imported through AIA. The file header is
  checked before activation; local import performs no download.
- Imported models have default-selection and removal controls. Removal unregisters
  an imported file without deleting the user's original. Catalog model removal
  deletes only its model file and checksum, with confirmation.
- AIA refreshes hardware when displaying recommendations. The selected default
  is authoritative; finding another model does not silently replace it.
- AIA chat and optional Open WebUI use the same authenticated loopback inference
  endpoint and active model. Switching a default restarts inference, not WebUI.
- Larger models are hardware-gated recommendations, not a requirement to run AIA.

## Control Center

Control Center is a tab inside AIA, not a replacement app. The old `shai-control`
command opens that tab. It displays actual inference/broker status and real
pending requests. The active-model restart has explicit confirmation. Proposals
have a review dialog, native authorization, asynchronous execution, and error
reporting. Historical diagnostic requests are excluded from the normal view.

Proposal and approval credentials are separate. Open WebUI receives only the
proposal credential; its key cannot approve or reject an action. The root-only
approval helper uses the distinct approval key. Request mutation is serialized
to prevent two simultaneous approvals from executing a request twice.

## VM scope

Open WebUI remains optional in SHAPP. Its existing VM container is stopped to
save memory; persistent data is preserved. No new model downloads or physical
smart-home actions are required to validate this AIA restoration. Full browser
chat/tool authorization testing remains a separate hardware-appropriate test.
