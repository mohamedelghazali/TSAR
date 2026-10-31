# ML-DSA (FIPS 204) — Digital Signatures

## Parameters
| Variant | NIST Level | Public Key | Signature | Security |
|---|---|---|---|---|
| ML-DSA-44 | 2 | 1312 B | 2420 B | NIST Cat 2 |
| ML-DSA-65 | 3 | 1952 B | 3309 B | NIST Cat 3 |
| ML-DSA-87 | 5 | 2592 B | 4627 B | NIST Cat 5 |

## Required Variant
- **ML-DSA-44** for general signing.
- **ML-DSA-87** for high-value (code signing, firmware, root artifacts).

## Transition
- Dual-sign: `Ed25519` + `ML-DSA-44` during migration.
- Verifiers MUST accept both until 2030, then require ML-DSA only.
- Reject signatures older than the current algorithm policy version.

## Context Binding
- Use the `ctx` parameter to bind signatures to their purpose.
- Never reuse a signing key across contexts.

## Forbidden
- Signing without context binding.
- Verifying with a key not bound to the expected algorithm family.
