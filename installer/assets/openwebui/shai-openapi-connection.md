# SHAI Local Control connection

SHAI preconfigures this as an admin-owned OpenAPI Server when Open WebUI is
installed. The connection uses this local specification:

`http://127.0.0.1:11500/openapi.json`

The SHAI control credential stays inside the Open WebUI container; it is not
shown in the browser or given to the model. The connection can read the
sanitized inventory and create proposals only. It cannot approve a proposal,
read any secret, execute a shell command, or access Docker directly. Approve or
reject every proposal in **SHAI Control Center**.

This is intentionally an external OpenAPI connection instead of an in-process
Open WebUI Workspace Tool. Workspace Tools execute arbitrary Python inside the
WebUI server, which would unnecessarily expand the trust boundary.
