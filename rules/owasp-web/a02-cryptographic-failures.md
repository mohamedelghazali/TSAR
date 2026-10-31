# A02: Cryptographic Failures

## Controls
- All sensitive data encrypted in transit (TLS 1.3) and at rest (AES-256-GCM).
- Password storage: Argon2id only (see rules/crypto/algorithms.md).
- Secrets managed by KMS/Vault, never in code or environment literals.
- PII classification enforced before storage and transmission.
- Deprecated algorithms refused at code review and CI.

## Forbidden
- MD5, SHA-1, DES, 3DES, RC4, ECB mode.
- Hardcoded keys, IVs, or salts.
- Custom cryptographic implementations.
- Disabled certificate verification.

## Testing
- CBOM generated via skills/crypto-inventory on every release.
- Dependency scanning blocks libraries using weak crypto.
