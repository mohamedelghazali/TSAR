# Key Management

## Hierarchy
Root of Trust (HSM/TPM/Secure Enclave) -> Key Encryption Key (KEK) -> Data Encryption Keys (DEKs).

## Requirements
- DEKs generated from CSPRNG, rotated per message or per period.
- KEKs never exported in plaintext; use KMS/HSM for wrap/unwrap.
- Per-tenant keys; no cross-tenant key reuse.
- Envelope encryption for data at rest.
- Key version stored alongside ciphertext for rotation.

## Rotation
| Key type | Max lifetime |
|---|---|
| DEK | 2^32 messages or 30 days, whichever first |
| KEK | 90 days |
| Root / HSM keys | Annual with audit |

## Storage
- Never in environment variables for production secrets; use Vault / KMS references.
- Never in source, CI logs, or container images.
- Separate keys for encryption, signing, and MAC.

## Revocation
- Immediate revocation on employee exit, incident, or compromise.
- Re-encrypt affected data under new keys where feasible.
