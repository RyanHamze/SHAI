# SHAI Local Control connection

Pending source revision: the managed inference endpoint is now
`http://127.0.0.1:11437/v1`. An authenticated user gateway injects shared local
context for AIA and Open WebUI and forwards actual model responses. An existing
container must be reapplied/restarted after deployment to use the new endpoint.

The additional **SHAI Local Memory** OpenAPI connection uses
`http://127.0.0.1:11437/openapi.json` with the private inference key server-side.
`GET /v1/shai/context` reads sanitized AIA settings/integrations, SHAPP/SHEALTH
and system state; `GET /v1/shai/memory` reads shared user notes. Both are read-only.
Storage lives at `~/.local/share/shai/memory/` on the host, without a home-folder
mount. Vault contents, raw logs and chat history are excluded. All accounts in
this managed WebUI share its one host desktop identity, not separate host memory.

SHAI preconfigures this as an admin-owned OpenAPI Server when Open WebUI is
installed. The connection uses this local specification:

`http://127.0.0.1:11500/openapi.json`

The separate SHAI control credential stays inside the Open WebUI container; it is not
shown in the browser or given to the model. The connection can read the
sanitized inventory and create proposals only. It cannot approve a proposal,
read any secret, execute a shell command, or access Docker directly. Approve or
reject every proposal in **SHAI Control Center**.

This is intentionally an external OpenAPI connection instead of an in-process
Open WebUI Workspace Tool. Workspace Tools execute arbitrary Python inside the
WebUI server, which would unnecessarily expand the trust boundary.
