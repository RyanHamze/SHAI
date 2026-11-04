#!/usr/bin/env bash
# Development installer: fixed, previously verified CI package; no appliance changes.
set +x
set -Eeuo pipefail

readonly SHAI_VERSION=0.13.1
readonly PACKAGE="shai-installer_${SHAI_VERSION}_amd64.deb"
readonly SHA256=4535b5ee0a0d507f3969913e064cacfe7d1d902900566fad082625388a6e4c7a
readonly ARTIFACT_URL=https://api.github.com/repos/RyanHamze/SHAI/actions/artifacts/13293184732/zip
verify_only=false
case "${1:-}" in
    '') ;;
    --verify-only) verify_only=true ;;
    --help) printf 'Usage: bash install.sh [--verify-only]\nInstalls the verified SHAI candidate and opens Setup, without applying its changes.\n'; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
esac
[[ $# -le 1 ]] || { printf 'Too many arguments.\n' >&2; exit 2; }
[[ $EUID -ne 0 ]] || { printf 'Run as your desktop user, without sudo. Installation will ask for sudo separately.\n' >&2; exit 1; }
for command in gh curl python3 sha256sum dpkg-deb dpkg; do
    command -v "$command" >/dev/null || { printf 'Missing %s. Install prerequisites: sudo apt install gh curl python3 ca-certificates\n' "$command" >&2; exit 1; }
done
# shellcheck source=/dev/null
source /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 26.04 ]] || {
    printf 'This tested candidate requires Ubuntu Desktop 26.04.x LTS. No changes made.\n' >&2; exit 1;
}
[[ "$(dpkg --print-architecture)" == amd64 ]] || { printf 'This package supports amd64 only.\n' >&2; exit 1; }
if ! $verify_only; then
    [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]] || { printf 'Run this command inside the Ubuntu desktop terminal so Setup can open.\n' >&2; exit 1; }
    command -v sudo >/dev/null || { printf 'sudo is required for package installation.\n' >&2; exit 1; }
fi

umask 077
work="$(mktemp -d -t shai-download.XXXXXXXX)"
cleanup() { rm -rf -- "$work"; }
trap cleanup EXIT
printf 'Online source: private GitHub repository RyanHamze/SHAI.\n'
printf 'Downloading fixed SHAI %s candidate; verifying its pinned SHA-256 before sudo.\n' "$SHAI_VERSION"
if ! token="$(gh auth token --hostname github.com 2>/dev/null)"; then
    printf 'GitHub authentication required. Run: gh auth login --hostname github.com --web\n' >&2; exit 1;
fi
[[ -n "$token" && "$token" != *$'\n'* && "$token" != *$'\r'* ]] || { printf 'Invalid GitHub credential.\n' >&2; exit 1; }
printf 'Authorization: Bearer %s\nAccept: application/vnd.github+json\n' "$token" > "$work/headers"
unset token
# curl strips Authorization on cross-host redirects; never use --location-trusted.
if ! curl -q -4 --fail --silent --show-error --location --proto '=https' --proto-redir '=https' \
    --max-filesize 67108864 --header "@$work/headers" "$ARTIFACT_URL" -o "$work/bundle.zip"; then
    printf 'Download failed. Check GitHub access, internet/proxy settings, and artifact expiry. No package was installed.\n' >&2; exit 1;
fi
rm -f -- "$work/headers"
python3 - "$work" "$PACKAGE" <<'PY'
import pathlib, shutil, sys, zipfile
root = pathlib.Path(sys.argv[1])
allowed = {sys.argv[2], 'SHA256SUMS', 'SHAI-APP-CATALOG.json'}
with zipfile.ZipFile(root / 'bundle.zip') as archive:
    members = archive.infolist()
    names = [item.filename for item in members]
    if set(names) != allowed or len(names) != len(allowed) or sum(item.file_size for item in members) > 67108864:
        raise SystemExit('Unexpected artifact contents; refusing extraction')
    for item in members:
        if item.is_dir() or item.external_attr >> 16 & 0o170000 == 0o120000:
            raise SystemExit('Unsafe archive entry')
        with archive.open(item) as source, (root / item.filename).open('xb') as target:
            shutil.copyfileobj(source, target)
PY
printf '%s  %s\n' "$SHA256" "$work/$PACKAGE" | sha256sum --check --strict -
[[ "$(dpkg-deb --field "$work/$PACKAGE" Package)" == shai-installer ]]
[[ "$(dpkg-deb --field "$work/$PACKAGE" Version)" == "$SHAI_VERSION" ]]
[[ "$(dpkg-deb --field "$work/$PACKAGE" Architecture)" == amd64 ]]
printf 'Verified %s. This is a checksummed development candidate, not a publisher-signed APT release.\n' "$PACKAGE"
if $verify_only; then
    printf 'Verification complete. No software installed or Setup launched.\n'; exit 0;
fi
printf 'Installing the platform only. APT may contact Ubuntu for missing dependencies.\n'
printf 'Debloat, theming and appliance changes require your approval inside SHAI Setup.\n'
sudo apt-get -o Acquire::ForceIPv4=true --no-remove --no-install-recommends -y install "$work/$PACKAGE"
printf 'Opening SHAI Setup as your desktop user.\n'
/usr/bin/shai-setup
