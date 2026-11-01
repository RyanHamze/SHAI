# SHAPP catalog provenance

Updated: 2026-11-01

The current SHAI catalog was reconstructed from the obsolete SHAIBUNTU archive.
Those files are reference material only; SHAIBUNTU names, branding, deployment
claims, and direct-host assumptions are not carried into SHAI.

Primary sources:

- `../sha-ubuntu/SHAIBUNTU/addons/shapp/package-catalog.json`
- `../sha-ubuntu/SHAIBUNTU/docs/V054_SHAPP_DEPLOYMENT_ARCHITECTURE.md`
- `docs/SHAI_APP_APPROVAL_CATALOG.md`

The active catalog is `installer/catalog/shapp-apps.json`. It contains 30
recommended and optional entries. An entry is selectable only when its current
`available` flag is true and its `packages` list contains audited Ubuntu package
names. Entries requiring a managed container, hardware workflow, model download,
third-party repository, network-role migration, or custom service backend remain
visible but disabled with an explanation. This prevents the recovered historical
catalog from presenting unfinished installers as working functionality.

SHAPP writes one append-only activity file per local calendar day under
`~/.local/state/shai/shapp/logs/`. Discovery scans, staged changes, successful
package operations, removals, completion, and failures use tab-separated records
with timestamps. The SHAPP window links directly to this folder.

SHAPP reads the initial architecture from Setup's
`/var/lib/shai-installer/setup-choices.json`. A user may change the effective
future-install architecture in SHAPP; that per-user override is stored at
`~/.config/shai/shapp.json`. The selector does not install Docker, migrate
services, or silently execute a deployment. Catalog entries become selectable
only when the chosen architecture has a validated install and uninstall backend.

Sniffnet is listed as highly recommended. It is not present in the enabled
Ubuntu or Snap catalogs on the test VM, so its official GitHub DEB workflow
remains disabled until release selection and integrity verification are
implemented. SHAPP does not replace that requirement with an unverified command.
