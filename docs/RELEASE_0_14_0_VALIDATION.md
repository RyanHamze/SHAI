# SHAI 0.14.0 TA3 Validation

Date: 2026-11-04. Public **test candidate**, not production certification.
Ubuntu Desktop 26.04 amd64 remains the host OS. No fresh destructive Setup
replay was performed on the working VM; that is the next checkpoint test.

## Package

- DEB: `shai-installer_0.14.0_amd64.deb`.
- SHA-256: `3a9fa6c11ff5598cf53b0574ef83e19383b9cb5977d01813dd905efe70f784d9`.
- Signing: GitHub keyless SLSA workflow provenance for the DEB, SHA256SUMS and
  app catalog independently verified on 2026-11-09, including signatures,
  repository/workflow, source tag/commit and hosted-runner policy.
- No publisher GPG private key is available. No publisher-signed APT metadata
  or individual executable signature is claimed. App byte hashes are included
  in the attested catalog; the attested DEB authenticates its complete payload.
- Source/tag: `v0.14.0`, commit `8996f2eeba560c91505a7d1817748819899dd156`.
- PR #8 checks and main/tag CI passed. Tag build: run `42679922541`.
- Public attestation: https://github.com/RyanHamze/SHAI/attestations/65485717
- Clean local rebuild, both PR build downloads and the tag artifact have the
  exact package hash above. Package size: 3,773,350 bytes.
- Bootstrap is promoted in a later commit, with the unchanged exact release
  source and DEB pins. The release tag is not moved to the bootstrap commit.
- Public prerelease: https://github.com/RyanHamze/SHAI/releases/tag/v0.14.0
- After publication, independent public downloads matched SHA256SUMS. Actual
  rootless `install.sh --verify-only` passed on both the development host and
  Ubuntu VM, using isolated credential-free CLI homes and the verified portable
  verifier. No GitHub login, installation or Setup application occurred in those
  verification-only runs. Main-branch promotion is checked separately afterward.

## Diagnosed And Fixed

1. Model installation could start inference before creating its private API
   key. Explicit preparation now precedes startup; permanent configuration
   errors do not create an endless restart loop.
2. Fresh AIA memory startup referenced `sys` without importing it. A real GTK
   smoke test found it; the missing import and a startup regression were added.
3. Ubuntu user mount namespaces denied the gateway's `/proc/PID/fd` peer check.
   Removed those gateway namespace options, retained unprivileged execution,
   NoNewPrivileges, loopback restrictions/resource limits and strict peer checks.
4. Linux can briefly report a pre-accept socket with UID/inode zero. The gateway
   now retries that transient state without sending credentials or context.
   Persistently wrong ownership still fails closed; both cases have tests.
5. SHAPP's running-app identity, chat follow-end and ExifTool context references
   were corrected. Online install permission no longer depends on chat history.
6. Added shared private context/notes for AIA and managed Open WebUI. Secrets
   are masked; raw logs/chat are not silently shared; commands need approval.
7. Added scoped removal-only service cleanup. Personal overrides/data are not
   deleted. Verified actual uninstall stops packaged services, preserves models
   and configuration, and reinstall does not activate services by itself.
8. Cleared stale removed Ubuntu Insights failure markers; Setup now clears only
   the specific absent Insights units. No global failed-unit masking.
9. The VM clock was roughly eight hours behind the build host and HTTPS server
   Date. Corrected it once; retained Ubuntu's automatic time-management policy.

## Passing Evidence

- Full local package suite: 16 suites, 161 checks, one local compiler-dependent
  skip. All four policy/compiler checks pass on the Ubuntu VM. CI installs
  dconf-cli so that check runs there rather than silently skipping.
- Release CI runs bootstrap tests unprivileged, so its root container does not
  skip those checks. The tagged build passed all suites, including compiler
  and bootstrap validation. Nov 9 live recheck confirmed the final artifact
  hash, private shared memory and no failed user units on the VM.
- ShellCheck 0.11.0 passed for bootstrap/build/Setup/prerm/release/test/tool
  shell sources. Python compilation and shell syntax checks passed.
- Real installed GTK pages: all Setup, SHEALTH and AIA tabs construct.
- Real AIA inference: distinct arithmetic/color answers, actual chat callback,
  selected model/service-process matching, and installed-model switch/restore.
- Real authenticated context API: unauthorized access rejected, inference key
  absent from exported state, private 0700/0600 modes, temporary note visible
  immediately and removed after testing. Local calls still work with a dead
  HTTP proxy configured in the test environment.
- Real Open WebUI: Docker Engine/Compose installed through the managed path;
  pinned slim container healthy, authenticated model discovery and chat use the
  shared hostname context. Temporary test account removed by restoring the
  verified-empty initial database; no test login retained.
- All 16 managed Compose service definitions validate without deploying every
  service. SHAPP cart/backend/visible-terminal planning passed with execution
  mocked rather than installing the entire catalog.
- ExifTool cleaned temporary individual and nested-folder files, preserved
  original backups and rejected filesystem-root scope. Custom AIA integration
  save used an isolated configuration without making a network test.
- Actual package uninstall/reinstall and inert activation behavior passed on
  the VM. No user media/config/models were removed. The working app backup is
  private on the VM; raw logs, keys and test login credentials are not published.

## Remaining Limits

- A genuinely fresh Ubuntu Setup/debloat/first-login acceptance remains the
  user's next checkpoint test. Preserve the clean Ubuntu baseline and current
  working VM; an already-modified checkpoint is not a clean installation.
- No physical Zigbee/radio, GPU acceleration, microphone, media-library,
  every-optional-app installation or every catalog model certification.
- Ubuntu/Hyper-V vendor warnings remain: SPICE unit metadata, synthetic display
  EDID/Mesa warnings and stale vendor D-Bus account references. No vendor files
  were patched or warnings globally suppressed to manufacture clean logs.
- Proxy-based Web Offline is not a physical or host-wide air gap. Core inference
  and context use authenticated loopback; explicit online installs/verification
  still require internet access.
- All accounts in the managed Open WebUI share one desktop identity/context.
  There is no untrusted multi-user or pinned-TLS transport guarantee.
- Typed chat config editing, automatic model-written memory and broker-backed
  metadata execution remain deferred; existing approved GUI actions are real.

The new TA3 protocol is defined in `TA3_PROTOCOL.md`. It must stop on failed
publication/signature gates, not relabel checksums as signatures.
