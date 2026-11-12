# Security

Report vulnerabilities privately to **shai@aabeyllc.com**. Do not post
credentials, private keys, personal configuration or unredacted logs in public.

Download SHAI from this repository's releases and use the verified installer
entry point. It checks a pinned SHA-256, a signed GitHub release-validation
attestation and package identity before installation. The attestation describes
distribution checks, not a public-source build or independent source review.
It binds the exact artifact, validation policy, repository, release tag and
workflow commit. A checksum by itself is not a signature.
The current release does not claim publisher-GPG-signed APT metadata or a
separate publisher signature on every executable.

Review requested changes, use normal Ubuntu administrator authentication and
keep a recoverable backup. Do not bypass verification failures. SHAI is test
software; supported hardware and third-party services require user validation.

See [verification instructions](docs/INSTALL_FROM_GITHUB.md) and
[third-party terms](docs/THIRD_PARTY_NOTICES.md).
