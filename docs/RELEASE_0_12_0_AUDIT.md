# SHAI 0.12.0 Release Audit

## Scope

Review Setup, SHAPP, AIA and SHEALTH, including button handlers, approved visible
terminal execution, install backends, capacity rules and local configuration.
Ubuntu remains the operating system. No ISO is produced.

## Fixes

- Setup opens the real SHAPP application and recovers from terminal-launch failure.
- SHAPP rechecks capacity on Apply, prevents duplicate execution, validates
  conflicting plans, and rejects collateral APT removals not explicitly approved.
- Container removals do not claim freed persistent storage, download images,
  restart retained apps, or fail because install capacity is low. Removing MQTT
  while retaining Zigbee is rejected instead of silently reversing the selection.
- Managed voice removal requires a SHAPP receipt. Unsupported VeraCrypt
  architectures are rejected before prerequisite installation.
- AIA handles malformed inference payloads and worker errors, interprets systemd
  properties by name, reports missing launchers, and identifies the desktop user
  when testing vault-backed integrations. Chat prompts are not copied into logs.
- Saving one vault field preserves other credentials through an atomic write.
- SHEALTH rejects stale/malformed container snapshots, distinguishes starting
  containers from healthy ones, and corrects CPU and duplicate-rollup accounting.

## Verification

Source regression tests cover Setup handoff/recovery, cart/backend safety,
inference errors, credential preservation, monitoring calculations and broker
approval/replay boundaries. Static checks cover all Python entrypoints and
self-bound signal handlers across the four applications. They do not prove
every possible click sequence works.

Live VM acceptance checks cover page construction, model inference/chat, custom
configuration, temporary-file metadata cleaning and Compose schema validation.
Exact final results are recorded alongside the candidate release. Publication
is conditional on final package and live smoke checks passing.

This is a tested development candidate, not production certification. Full
destructive Setup was not replayed against the user's configured VM. A fresh
checkpoint install/apply remains a separate acceptance test.

## Boundaries

No bulk install/removal plan is replayed. No disk is encrypted or reformatted.
Hardware-specific radio, GPU, firmware and full heavy-service acceptance tests
cannot be certified from the small Hyper-V VM. Matter staging is not pairing;
Speech-to-Phrase requires training; voice runtime installation is not a claim
that a speech model or microphone has been configured.

Package checksums identify bytes; they are not publisher signatures. GitHub
build provenance is distinct from offline APT repository signing.
