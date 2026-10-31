# iOS Security Baseline (MASVS-L2 + MASVS-R)

## Storage
- Keychain: `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` for secrets.
- Never store tokens in `UserDefaults` or plists.
- File protection: `NSFileProtectionComplete` for sensitive files.

## Crypto
- CryptoKit or CommonCrypto with AES-256-GCM.
- `SecRandomCopyBytes` for randomness.
- Keys derived from Secure Enclave when available.

## Network
- App Transport Security (ATS) enabled, no exceptions.
- Certificate pinning for high-value endpoints.
- TLS 1.3 only.

## Resilience
- `-fobjc-arc`, stack canaries.
- Strip symbols in release builds.
- Jailbreak and debugger detection for Tier-1 apps.

## Hardware
- Secure Enclave for key generation and signing.
- Bind keys to biometric authentication (`kSecAccessControlBiometryCurrentSet`).
