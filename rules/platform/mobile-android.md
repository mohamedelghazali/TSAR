# Android Security Baseline (MASVS-L2 + MASVS-R)

## Storage
- Android Keystore with StrongBox when available.
- `EncryptedSharedPreferences` for tokens.
- No secrets in `SharedPreferences` plaintext or external storage.

## Crypto
- AES-256-GCM via Keystore-backed keys.
- `SecureRandom` for randomness.
- Hardware-backed key attestation for Tier-1.

## Network
- Network Security Config with cleartext disabled.
- Certificate pinning via `network_security_config.xml`.
- TLS 1.3 only.

## Resilience
- R8/ProGuard with obfuscation.
- Play Integrity API for Tier-1.
- Root and debugger detection.

## Permissions
- Runtime permissions with minimal scope.
- No `WRITE_EXTERNAL_STORAGE` for new apps.
