# Open WebUI integration

Open WebUI is an optional browser interface, installed from SHAPP's Optional
catalog only after the user chooses Advanced Docker architecture. AIA remains
SHAI's primary assistant, model manager, and local integration surface.

## Deliberate architecture

- SHAI does not install Ollama for this feature. AIA already owns a persistent
  `llama.cpp` OpenAI-compatible server and its GGUF model files.
- The model server remains bound to `127.0.0.1:11435`; it is never changed to
  `0.0.0.0` or exposed to the LAN.
- Open WebUI uses host networking solely to reach that loopback model server.
  Its own process is explicitly bound to `127.0.0.1:3000`, so it is also local
  to the Ubuntu host by default.
- SHAI passes the existing local AIA API key and a generated persistent WebUI
  session secret through `/etc/shai/stack/.env` with mode `0600`. The file is
  root-owned and is not shown in SHAPP.
- The selected image is the smaller pinned `v0.12.5-slim` release. Offline mode
  and Hugging Face offline mode are enabled; document/RAG, built-in local voice,
  and code-interpreter features are intentionally outside this light frontend.
- Open WebUI has its own local account login. The user creates its initial
  administrator account when first opening `http://127.0.0.1:3000`.

## Preconditions and behavior

1. AIA must have an active local model and its persistent service must have
   created a local API key.
2. The user selects Open WebUI in SHAPP, reviews the planned changes, and
   approves the visible terminal operation.
3. SHAPP installs Docker Engine only when needed, pulls the pinned image, and
   stores WebUI data under `/var/lib/shai/stack/openwebui`.
4. SHAI registers port 3000 as a loopback-only local browser interface. SHEALTH
   can report it along with the owning container.

If AIA has no active model, SHAPP stops before image deployment and explains
what must be configured. This avoids installing a browser UI that cannot serve
a model.
