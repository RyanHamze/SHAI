#!/usr/bin/env bash
# Public release bootstrap. Verification and temporary CLI preparation are rootless.
set +x
set -Eeuo pipefail

readonly SHAI_VERSION=0.15.0
readonly PACKAGE="shai-installer_${SHAI_VERSION}_amd64.deb"
# Independent release pins; never substitute downloaded checksum metadata.
readonly SHA256=d0865636ae24c3d3fc63271e60e9e26db8e3fff1b2d7b2769faec0b6868112e5
readonly SOURCE_COMMIT=b164483ae0690abfeb7c380386073827fa3172d0
readonly VALIDATION_TYPE=https://aabeyllc.com/shai/release-validation/v1
readonly SOURCE_REF="refs/tags/v${SHAI_VERSION}"
readonly RELEASE_URL="https://github.com/RyanHamze/SHAI/releases/download/v${SHAI_VERSION}"
readonly ARTIFACT_URL="$RELEASE_URL/$PACKAGE"
readonly GH_VERSION=2.103.3
readonly GH_ARCHIVE="gh_${GH_VERSION}_linux_amd64.tar.gz"
# https://github.com/cli/cli/releases/download/v2.103.3/gh_2.103.3_checksums.txt
readonly GH_SHA256=4c806978ffce1cec70853302a56d70ac6da4f19bae7adca4e1a8ab00633dd91d
readonly GH_URL="https://github.com/cli/cli/releases/download/v${GH_VERSION}/$GH_ARCHIVE"

verify_only=false
case "${1:-}" in
    '') ;;
    --verify-only) verify_only=true ;;
    --help) printf 'Usage: bash install.sh [--verify-only]\nVerifies the public SHAI release before installation and opens Setup as your desktop user.\n'; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
esac
[[ $# -le 1 ]] || { printf 'Too many arguments.\n' >&2; exit 2; }
[[ $EUID -ne 0 ]] || { printf 'Run as your desktop user, without sudo. Installation will ask for sudo separately.\n' >&2; exit 1; }
for command in curl python3 sha256sum dpkg-deb dpkg mktemp chmod mkdir stat rm; do
    command -v "$command" >/dev/null || {
        printf 'Missing %s. Prerequisites from Ubuntu APT: sudo apt install curl python3 ca-certificates\n' "$command" >&2; exit 1;
    }
done
# shellcheck source=/dev/null
source /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 26.04 ]] || {
    printf 'This release requires Ubuntu Desktop 26.04.x LTS. No changes made.\n' >&2; exit 1;
}
[[ "$(dpkg --print-architecture)" == amd64 ]] || { printf 'This package supports amd64 only.\n' >&2; exit 1; }
[[ "$SHA256" =~ ^[0-9a-f]{64}$ && "$SHA256" != 0000000000000000000000000000000000000000000000000000000000000000 &&
   "$SOURCE_COMMIT" =~ ^[0-9a-f]{40}$ && "$SOURCE_COMMIT" != 0000000000000000000000000000000000000000 ]] || {
    printf 'Release pins are not finalized. Refusing download or installation.\n' >&2; exit 1;
}
if ! $verify_only; then
    [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]] || { printf 'Run this command inside the Ubuntu desktop terminal so Setup can open.\n' >&2; exit 1; }
    command -v sudo >/dev/null || { printf 'sudo is required for package installation.\n' >&2; exit 1; }
fi

umask 077
work="$(mktemp -d -t shai-download.XXXXXXXX)"
readonly work
cleanup() { rm -rf -- "$work"; }
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
chmod 0700 -- "$work"
mkdir -- "$work/home" "$work/config" "$work/cache" "$work/data" "$work/tmp"

download() {
    if ! curl -q --fail --silent --show-error --location --proto '=https' --proto-redir '=https' \
        --max-filesize "$3" --output "$2" "$1"; then
        printf 'Download failed. No package was installed.\n' >&2; return 1;
    fi
    [[ -f "$2" && ! -L "$2" && -s "$2" && "$(stat -c %s -- "$2")" -le "$3" ]] || {
        printf 'Unexpected download type or size. No package was installed.\n' >&2; return 1;
    }
}

# Keep credentials, CLI config and Sigstore trust caches outside the user's home.
gh_command=gh
run_gh() (
    unset GH_TOKEN GITHUB_TOKEN GH_ENTERPRISE_TOKEN GITHUB_ENTERPRISE_TOKEN GH_DEBUG
    export HOME="$work/home" GH_CONFIG_DIR="$work/config/gh" XDG_CONFIG_HOME="$work/config"
    export XDG_CACHE_HOME="$work/cache" XDG_DATA_HOME="$work/data" TMPDIR="$work/tmp"
    export GH_HOST=github.com GH_PROMPT_DISABLED=1 GH_NO_UPDATE_NOTIFIER=1 GH_NO_EXTENSION_UPDATE_NOTIFIER=1
    cd -- "$work"
    "$gh_command" "$@"
)
supports_attestations() {
    local help flag
    help="$(run_gh attestation verify --help 2>/dev/null)" || return 1
    for flag in --bundle --repo --signer-workflow --signer-digest --source-ref --source-digest --predicate-type --hostname; do
        [[ "$help" == *"$flag"* ]] || return 1
    done
}

printf 'Online source: public GitHub release RyanHamze/SHAI v%s. No GitHub login is needed.\n' "$SHAI_VERSION"
printf 'Downloading and verifying the pinned package before any sudo or APT action.\n'
download "$ARTIFACT_URL" "$work/$PACKAGE" 67108864
printf '%s  %s\n' "$SHA256" "$work/$PACKAGE" | sha256sum --check --strict -

if ! command -v gh >/dev/null || ! supports_attestations; then
    printf 'Preparing temporary official GitHub CLI %s; it will not be installed.\n' "$GH_VERSION"
    download "$GH_URL" "$work/$GH_ARCHIVE" 67108864
    printf '%s  %s\n' "$GH_SHA256" "$work/$GH_ARCHIVE" | sha256sum --check --strict -
    python3 -I -B - "$work/$GH_ARCHIVE" "$work/gh" "gh_${GH_VERSION}_linux_amd64" <<'PY'
import pathlib
import shutil
import sys
import tarfile

archive_path, target_path, prefix = sys.argv[1:]
target = pathlib.Path(target_path)
expected = prefix + '/bin/gh'
seen = set()
total = 0
found = False
with tarfile.open(archive_path, mode='r|gz') as archive:
    for item in archive:
        name = item.name.rstrip('/')
        parts = name.split('/')
        total += item.size
        if (len(seen) >= 1024 or name in seen or total > 134217728
                or item.size < 0 or item.size > 67108864
                or parts[0] != prefix or any(p in ('', '.', '..') for p in parts)
                or '\\' in name or not (item.isfile() or item.isdir())
                or item.issparse()):
            raise SystemExit('Unsafe GitHub CLI archive shape')
        seen.add(name)
        if name != expected:
            continue
        if not item.isfile() or item.size == 0:
            raise SystemExit('Expected a regular GitHub CLI binary')
        with archive.extractfile(item) as source, target.open('xb') as output:
            shutil.copyfileobj(source, output, length=65536)
        if target.stat().st_size != item.size:
            raise SystemExit('Truncated GitHub CLI binary')
        found = True
if not found:
    raise SystemExit('GitHub CLI binary missing from archive')
target.chmod(0o700)
PY
    gh_command="$work/gh"
    supports_attestations || { printf 'GitHub CLI lacks the required attestation verification flags.\n' >&2; exit 1; }
fi

# A public sidecar avoids gh's authenticated API lookup; signatures still bind the artifact.
download "$ARTIFACT_URL.intoto.jsonl" "$work/$PACKAGE.intoto.jsonl" 1048576
if ! run_gh attestation verify "$work/$PACKAGE" --bundle "$work/$PACKAGE.intoto.jsonl" \
    --hostname github.com --repo RyanHamze/SHAI \
    --signer-workflow RyanHamze/SHAI/.github/workflows/public-distribution.yml \
    --signer-digest "$SOURCE_COMMIT" --predicate-type "$VALIDATION_TYPE" \
    --source-ref "$SOURCE_REF" --source-digest "$SOURCE_COMMIT" --deny-self-hosted-runners; then
    printf 'Attestation verification failed. No package was installed.\n' >&2; exit 1;
fi
python3 -I -B - "$work/$PACKAGE.intoto.jsonl" "$SHAI_VERSION" "$SOURCE_COMMIT" "$SHA256" <<'PY'
import base64
import json
import pathlib
import sys

path, version, commit, digest = sys.argv[1:]
bundle = json.loads(pathlib.Path(path).read_text())
statement = json.loads(base64.b64decode(bundle['dsseEnvelope']['payload'], validate=True))
predicate = statement['predicate']
required = {'sha256', 'deb-identity', 'inert-install-controls', 'catalog-app-hashes', 'public-payload-policy'}
if (statement.get('predicateType') != 'https://aabeyllc.com/shai/release-validation/v1'
        or predicate.get('schemaVersion') != 1
        or predicate.get('version') != version
        or predicate.get('tag') != 'v' + version
        or predicate.get('repository') != 'RyanHamze/SHAI'
        or predicate.get('workflowCommit') != commit
        or not required <= set(predicate.get('checks', []))
        or not any(item.get('name') == f'shai-installer_{version}_amd64.deb'
                   and item.get('digest', {}).get('sha256') == digest
                   for item in statement.get('subject', []))):
    raise SystemExit('Signed release-validation policy mismatch. No software installed.')
PY
[[ "$(dpkg-deb --field "$work/$PACKAGE" Package)" == shai-installer &&
   "$(dpkg-deb --field "$work/$PACKAGE" Version)" == "$SHAI_VERSION" &&
   "$(dpkg-deb --field "$work/$PACKAGE" Architecture)" == amd64 ]] || {
    printf 'DEB package identity, version or architecture does not match the release.\n' >&2; exit 1;
}
printf 'Verified pinned SHA-256, signed release validation and DEB identity for %s.\n' "$PACKAGE"
if $verify_only; then
    printf 'Verification complete. No software installed or Setup launched.\n'; exit 0;
fi
printf 'Installing the platform only. APT may contact Ubuntu for missing dependencies.\n'
printf 'Debloat, theming and appliance changes require your approval inside SHAI Setup.\n'
sudo apt-get --no-remove --no-install-recommends -y install "$work/$PACKAGE"
printf 'Opening SHAI Setup as your desktop user.\n'
/usr/bin/shai-setup
