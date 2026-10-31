# Offline SHAI key ceremony

Perform this on a dedicated offline Ubuntu system or encrypted live USB. Never
paste private keys, passphrases, backups, or token PINs into chat, GitHub, an
issue, a workflow secret, or a terminal recording.

Use two hardware OpenPGP tokens and two encrypted backup drives stored in
separate locations. Disconnect networking and create a fresh GnuPG home:

```bash
export GNUPGHOME="$HOME/shai-offline-gnupg"
install -d -m 0700 "$GNUPGHOME"
gpg --quick-generate-key \
  "SHAI APT Archive Signing <shai@aabeyllc.com>" rsa4096 cert 5y
gpg --fingerprint "SHAI APT Archive Signing <shai@aabeyllc.com>"
gpg --quick-add-key FULL_APT_PRIMARY_FINGERPRINT rsa4096 sign 1y

gpg --quick-generate-key \
  "SHAI App Catalog Signing <shai@aabeyllc.com>" rsa4096 cert 5y
gpg --fingerprint "SHAI App Catalog Signing <shai@aabeyllc.com>"
gpg --quick-add-key FULL_CATALOG_PRIMARY_FINGERPRINT rsa4096 sign 1y
```

Let GnuPG prompt locally for strong passphrases. Never use a command-line
passphrase. Before moving subkeys to tokens, export encrypted secret-key backups
to both offline drives and test restoration:

```bash
gpg --armor --export-secret-keys FULL_APT_FINGERPRINT > APT-SECRET-BACKUP.asc
gpg --armor --export-secret-keys FULL_CATALOG_FINGERPRINT > CATALOG-SECRET-BACKUP.asc
gpg --export-options export-minimal --armor --export FULL_APT_FINGERPRINT > shai-archive-key.asc
gpg --export-options export-minimal --armor --export FULL_CATALOG_FINGERPRINT > shai-catalog-key.asc
```

Preserve `$GNUPGHOME/openpgp-revocs.d/`. Provision only signing subkeys into
hardware signing slots using `gpg --edit-key`, subkey selection, and `keytocard`.
Restore a backup to provision the second token. Change factory PINs directly on
each token. Keep certification keys offline. Rotate signing subkeys at least 90
days before expiry.

Publish complete fingerprints independently on `aabeyllc.com`, GitHub, and
printed recovery documentation.
