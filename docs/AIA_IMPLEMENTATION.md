# AIA implementation

AIA is SHAI's offline-first local model advisor and assistant. It is installed
as `/usr/bin/shai-aia` only when the user selects local AI during Setup.

## Current behavior

- Detects CPU, architecture, RAM, available storage, exposed GPU devices, and
  the local llama.cpp runtime without an online probe.
- Starts in deterministic mode and recommends models against a one-GiB reserve
  for Ubuntu and automation services.
- Offers SmolLM2 135M as the bootstrap fallback, SmolLM2 360M as a light
  upgrade, and Llama 3.2 1B when current capacity permits.
- Requires an AIA confirmation before opening a visible installation terminal.
  The reviewed command then runs automatically, with Ubuntu sudo authentication
  remaining visible when required.
- Uses IPv4 for AIA downloads and connection tests. It does not globally disable
  Ubuntu IPv6.
- Promotes a newly installed higher-ranked catalog model to active default,
  while retaining installed fallback models.
- Supports local GGUF import, model switching/removal, single-turn llama.cpp
  inference, private optional chat history, and daily activity logs.
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
