# SHAI release process

Public test candidates use verified GitHub keyless workflow provenance, SHA-256
manifests and app hashes in the attested catalog. They are NOT publisher-GPG-
signed APT releases. Their bootstrap pins the exact tag, commit, workflow and
DEB hash and verifies the public Sigstore bundle. Publish only as an explicitly
labelled prerelease after all TA3 gates pass, never production-certified.

The protected draft-release job below runs only when repository variable
`SHAI_ENABLE_OFFLINE_APT_RELEASE=true` is deliberately enabled for the offline
APT channel. Its protected environment remains required; the test route does
not alter that environment or manufacture publisher keys.

## Production Offline APT Channel

1. Merge reviewed source and create a protected `vX.Y.Z` tag.
2. GitHub Actions builds, tests, hashes, and attests the `.deb`.
3. GitHub creates a draft release.
4. Verify provenance, commit, source tag, package contents, and tests.
5. Transfer artifacts to the offline signing environment.
6. Run `release/sign-release-offline.sh` with both hardware-backed keys.
7. Return only public keys, signatures, and signed repository output.
8. Verify signatures and APT installation on a separate clean Ubuntu VM.
9. Attach signatures, then manually publish the release.
10. Publish the signed APT tree at `packages.aabeyllc.com`.

Never sign an artifact merely because a workflow produced it.
