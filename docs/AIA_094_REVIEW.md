# AIA 0.9.4 Review

- AIA AI Assistant is the main desktop app with its own app-ID-matched launcher,
  window icon and header icon. Control Center is an internal tab; the old command
  remains a compatibility launcher but is not exposed as a separate menu app.
- Green model borders mean active default only. Recommended text remains
  informational. Open WebUI/SHAPP choices are below all models. Test-model
  buttons are removed.
- Reset active model meant unload, not delete. It is renamed Unload active model,
  explains that shared inference stops, and requires confirmation.
- Hardware includes a right-hand weight/quantization recommendation panel. The
  catalog budget is min(20% installed RAM, available RAM minus 1 GiB reserve).
  Inference uses a 20%-of-host CPU quota, MemoryHigh 20%, MemoryMax 25%, and
  conservative CPU threads. This is not a GPU or aggregate voice-services quota.
- Custom integration creation uses app name plus repeated key/value/secret
  fields. Secrets use the vault; generic text fields do not grant an API adapter
  or executable access. Configuration Save performs no connection test.
- Recommendation: keep this form as the default. Later add a validated JSON
  import/export editor for advanced users, with secret references only. Do not
  accept arbitrary executable scripts as integration configuration.
- Voice has approved visible-terminal install/remove actions for eSpeak NG,
  Piper, faster-whisper, openWakeWord and Wyoming. Python runtimes are isolated,
  top-level versions pinned, IPv4 downloads used, install reports and dependency
  locks saved. Binary-wheel-only installs fail rather than compile unsupported
  dependencies. Microphones and neural models are not automatically enabled.
- AIA detects known tools on PATH, Python packages, and installed Ubuntu speech
  components. External installations are listed but never silently adopted or
  removed. Speech-to-Phrase needs its separate home-automation training setup.

## Verification And Limits

Package tests and isolated voice lifecycle tests passed. Live VM tests render all
eight tabs, verify active-only styling and browser placement, exercise actual
chat and default switching, and save a custom integration into isolated storage
without any network test. Voice downloads and real audio pipelines were not
tested on the low-memory VM. Open WebUI remains stopped and optional in SHAPP.
SmolLM2 360M still produces poor arithmetic answers; no deterministic replacement
is used to disguise that limitation.

## Voice Sources

- https://github.com/OHF-Voice/wyoming-piper
- https://github.com/OHF-Voice/wyoming-faster-whisper
- https://github.com/OHF-Voice/speech-to-phrase
- PyPI package metadata for piper-tts, faster-whisper, openwakeword and wyoming.
