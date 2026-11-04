# TA3 Protocol

Ryan defined TA3 on 2026-11-04. Future requests to "do TA3", "perform TA3" or
"TA3 protocol" request the following sequence, subject to available access and
actual validation. They do not authorize unrelated destructive operations.

1. Inspect available SHAI app/Setup/model/system/managed-container logs on the
   test VM; distinguish historical failures, current defects and Ubuntu or
   virtualization limitations. Keep raw/private logs out of public GitHub.
2. Diagnose and fix relevant source defects, preserve existing data/settings,
   and add focused regression tests. Do not replay destructive Setup to test
   it without a verified fresh rollback environment.
3. Build a new versioned DEB, test its contents/inert install/uninstall behavior,
   deploy it to the VM, and test real GUI, services, model and integrations where
   hardware/software permits. Retest after fixes; report skipped coverage.
4. Generate SHA-256 manifests; sign using established available release keys
   and/or GitHub build provenance. Verify signatures and exact artifact bytes.
   Checksums are not publisher signatures. Never invent missing key trust,
   export private keys into chat/GitHub, or label a test build production-ready.
5. Commit reviewed source and push to GitHub after validation gates pass.
   Confirm CI success, independently verify the downloaded published package,
   and update the public bootstrap's immutable version/hash/provenance pins.
6. Report commit, package location, checksum, signature type, remaining issues,
   and whether the release is ready for a fresh Ubuntu checkpoint test.
7. Give short, manually typeable Ubuntu terminal commands to fetch from the
   public RyanHamze/SHAI repository and launch Setup. Download/install does
   not itself approve debloat or appliance changes. Do not force IPv4 for the
   public bootstrap unless Ryan explicitly requests it.

Ubuntu remains the OS. A checkpoint of an already-modified VM is a rollback
point, not a clean Ubuntu baseline. Preserve the existing clean checkpoint and
the current working VM before testing fresh installation.

No available signing key, unreachable VM, failed CI, signature mismatch or failed
acceptance is a real blocker for the corresponding step, not permission to fake
completion. Explain what remains and withhold a final ready claim as needed.
