# ML-KEM (FIPS 203) — Key Encapsulation

## Parameters
| Variant | NIST Level | Public Key | Ciphertext | Shared Secret |
|---|---|---|---|---|
| ML-KEM-512 | 1 | 800 B | 768 B | 32 B |
| ML-KEM-768 | 3 | 1184 B | 1088 B | 32 B |
| ML-KEM-1024 | 5 | 1568 B | 1568 B | 32 B |

## Required Variant
- **ML-KEM-768** for all new code. Higher levels only when explicitly required by policy.

## Hybrid with Classical
- Combine with X25519 using X-Wing (draft-connolly-cfrg-xwing-kem).
- Concatenate shared secrets: `HKDF-SHA256(classical || pq, info="hybrid")`.
- Never use only one component.

## Failure Modes
- Reject on encapsulation/decapsulation failure.
- Zeroize intermediate buffers.
- Constant-time decapsulation is mandatory; use vetted implementations only.

## Approved Implementations
- BoringSSL (`EVP_KEM`), PQClean, liboqs, NIST reference.
- No hand-rolled implementations.
