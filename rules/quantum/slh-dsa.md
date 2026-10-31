# SLH-DSA (FIPS 205) — Stateless Hash-Based Signatures

## Purpose
Long-lived artifacts: firmware, code signing roots, certificate roots,
artifacts stored for >10 years.

## Variants
| Variant | NIST Level | Public Key | Signature |
|---|---|---|---|
| SLH-DSA-SHA2-128s | 1 | 32 B | 7856 B |
| SLH-DSA-SHA2-192s | 3 | 48 B | 16224 B |
| SLH-DSA-SHA2-256s | 5 | 64 B | 29792 B |

## When to Use
- Firmware signatures with >10-year validity.
- Code signing root keys.
- Any artifact whose verification must survive quantum computers AND
  a break of ML-DSA.

## Trade-offs
- Large signatures.
- Slow signing.
- Fast verification.
- Suitable for infrequent signing of long-lived artifacts.

## Key Sizes
- Small public keys, so verifier trust anchors are compact.
