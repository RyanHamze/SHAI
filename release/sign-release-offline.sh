#!/usr/bin/env bash
set -Eeuo pipefail
: "${SHAI_APT_SIGNING_FINGERPRINT:?Set full APT signing fingerprint}"
: "${SHAI_CATALOG_SIGNING_FINGERPRINT:?Set full catalog signing fingerprint}"
dist="${1:-dist}"; output="${2:-signed-release}"
deb="$(find "$dist" -maxdepth 1 -type f -name 'shai-installer_*_amd64.deb' -print -quit)"
[[ -n "$deb" ]] || { echo "No SHAI amd64 DEB found" >&2; exit 1; }
command -v apt-ftparchive >/dev/null || { echo "apt-utils is required" >&2; exit 1; }
install -d "$output/pool/main/s/shai-installer" "$output/dists/stable/main/binary-amd64"
install -m 0644 "$deb" "$output/pool/main/s/shai-installer/"
install -m 0644 "$dist/SHA256SUMS" "$dist/SHAI-APP-CATALOG.json" "$output/"
(
 cd "$output"
 apt-ftparchive packages pool > dists/stable/main/binary-amd64/Packages
 gzip -n -9 -k dists/stable/main/binary-amd64/Packages
 apt-ftparchive -o APT::FTPArchive::Release::Origin=SHAI \
  -o APT::FTPArchive::Release::Label=SHAI \
  -o APT::FTPArchive::Release::Suite=stable \
  -o APT::FTPArchive::Release::Codename=stable \
  -o APT::FTPArchive::Release::Architectures=amd64 \
  -o APT::FTPArchive::Release::Components=main \
  release dists/stable > dists/stable/Release
 gpg --local-user "$SHAI_APT_SIGNING_FINGERPRINT" --digest-algo SHA512 \
  --clearsign --output dists/stable/InRelease dists/stable/Release
 gpg --local-user "$SHAI_APT_SIGNING_FINGERPRINT" --digest-algo SHA512 \
  --armor --detach-sign --output dists/stable/Release.gpg dists/stable/Release
 gpg --local-user "$SHAI_APT_SIGNING_FINGERPRINT" --digest-algo SHA512 \
  --armor --detach-sign --output SHA256SUMS.asc SHA256SUMS
 gpg --local-user "$SHAI_CATALOG_SIGNING_FINGERPRINT" --digest-algo SHA512 \
  --armor --detach-sign --output SHAI-APP-CATALOG.json.asc SHAI-APP-CATALOG.json
 gpg --export-options export-minimal --armor --export "$SHAI_APT_SIGNING_FINGERPRINT" > shai-archive-key.asc
 gpg --export-options export-minimal --armor --export "$SHAI_CATALOG_SIGNING_FINGERPRINT" > shai-catalog-key.asc
 sha256sum pool/main/s/shai-installer/*.deb > published-deb.sha256
)
echo "Signed release created at $output"
