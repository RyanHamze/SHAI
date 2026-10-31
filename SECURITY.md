# Security policy

Report vulnerabilities privately to `shai@aabeyllc.com`. Do not put secrets,
private keys, personal data, or destructive proofs of concept in public issues.

Release verification requires GitHub provenance (`gh attestation verify FILE -R
RyanHamze/SHAI`) and an offline OpenPGP signature checked against a fingerprint
published independently by Aabey LLC. A checksum does not prove publisher
identity, and a GitHub access token is not a signing key.

SHAI must reject removal of protected Ubuntu packages in both its UI and
privileged backend. There is no SHAI override.
