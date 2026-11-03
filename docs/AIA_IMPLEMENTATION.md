# AIA implementation

## Inspector policy

AIA is SHAI's read-only inspector and configuration assistant. It can report
hardware, services, integrations, and model status, but it does not execute
host or smart-home controls from chat. Advanced local models in Open WebUI use
the separately approved SHAI Control Broker; see `AIA_CONTROL_BROKER.md`.

AIA is SHAI's offline-first local model advisor and assistant. It is installed
as `/usr/bin/shai-aia` only when the user selects local AI during Setup.

## Current behavior

- Detects CPU, architecture, RAM, available storage, exposed GPU devices, and
  the local llama.cpp runtime without an online probe.
- Starts in deterministic mode and recommends models against a one-GiB reserve
  for Ubuntu and automation services.
- Offers SmolLM2 135M as the bootstrap fallback, SmolLM2 360M as a light
  fallback, Qwen 2.5 0.5B as the preferred lightweight default, and Llama 3.2
  1B when current capacity permits.
- Requires an AIA confirmation before opening a visible installation terminal.
  The reviewed command then runs automatically, with Ubuntu sudo authentication
  remaining visible when required.
- Uses IPv4 for AIA downloads and connection tests. It does not globally disable
  Ubuntu IPv6.
- Promotes a newly installed higher-ranked catalog model to active default,
  while retaining installed fallback models.
- Supports local GGUF import, model switching/removal, private optional chat
  history, and daily activity logs.
- Runs the selected model through a persistent per-user systemd service. The
  model loads during AIA initialization, remains resident after a chat or AIA
  window closes, and starts again at later desktop logins.
- Exposes llama.cpp only on `127.0.0.1:11435`, disables its web UI, and requires
  a private per-user API key. AIA uses the structured chat-completions endpoint
  so runtime diagnostics never become chat messages.
- Shows the active model, persistent-service state and PID, the last model-test
  result, and the last actionable model error in the chat surface.
- Tests the active model against two distinct local prompts. A passed test means
  the local API returned two non-empty, distinct answers; it does not claim that
  a small model is factually reliable.
- Pins every catalog download to an exact file size and SHA-256 from its stated
  Hugging Face source. The approved terminal flow validates both before making a
  model active and restarting the persistent service.
- Provides independent Application, Configuration, and Integration statuses for
  every SHAPP recommended integration, plus configure and retest workflows.
- Uses Home Assistant's token-authenticated REST endpoint, MQTT for Mosquitto
  and Zigbee2MQTT checks, a configured adapter to launch Sniffnet, and scoped
  endpoint checks for other local services.
- Opens maximized and provides separate Clear local chat and Reset active model
  actions. Neither action removes downloaded model files.

## Safety boundary

AIA chat never executes commands or controls physical devices. Downloads require
explicit approval, run visibly, and are logged. High-impact locks, alarms, HVAC,
valves, and relays remain outside automatic AIA control. Configuration and logs
are private to the desktop user. No telemetry or automatic online update check
is implemented.
