# Desktop Application Security (Windows, macOS, Linux)

## Storage
- Windows: DPAPI or Windows Credential Manager for secrets.
- macOS: Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`.
- Linux: Secret Service API (libsecret) or KWallet; fallback to encrypted file with user-derived key.
- Never store secrets in plaintext config files.

## Crypto
- OS-provided crypto libraries: CNG (Windows), CommonCrypto (macOS), OpenSSL (Linux).
- AES-256-GCM for data at rest.
- CSPRNG per platform for randomness.

## Network
- TLS 1.3 only with certificate verification.
- Certificate pinning for high-value APIs.

## Code Signing and Updates
- Signed binaries (Authenticode on Windows, Developer ID on macOS, GPG on Linux).
- Signed updates verified before installation.
- Rollback protection for update packages.

## Resilience
- ASLR, DEP, stack canaries enabled by default.
- Strip debug symbols in release.
- No debug interfaces exposed in production.
