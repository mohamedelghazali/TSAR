# Constant-Time Operations

## When Required
- Comparing secrets: tokens, MACs, password hashes, API keys.
- Verifying signatures before parsing payloads.
- Any comparison where an attacker controls one operand and can measure timing.

## Mandatory Primitives
| Language | Function |
|---|---|
| C | `timingsafe_bcmp`, `CRYPTO_memcmp` |
| Python | `hmac.compare_digest` |
| Java | `MessageDigest.isEqual` |
| Go | `crypto/subtle.ConstantTimeCompare` |
| Node.js | `crypto.timingSafeEqual` |
| Rust | `subtle::ConstantTimeEq` |

## Forbidden
- `==`, `!=`, `.equals()`, `strcmp()` on secrets.
- Early-return loops over secret bytes.
- Branching on secret bits.
