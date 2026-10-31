# Testing Guide

## Test Pyramid for Security
1. **Unit**: crypto primitives, input validators, auth logic.
2. **Integration**: auth flows, database access, API contracts.
3. **System**: end-to-end flows, multi-tenant isolation.
4. **DAST**: running app, authenticated.
5. **Penetration**: annual, external.
6. **Chaos**: resilience and fail-closed behavior.

## CI Gates
| Gate | Blocks Merge | Blocks Deploy |
|---|---|---|
| Unit tests | Yes | Yes |
| SAST | Yes (HIGH) | Yes |
| SCA | Yes (CRITICAL) | Yes |
| Secret scan | Yes | Yes |
| DAST | No | Yes (pre-prod) |
| Fuzzing | No | Yes (weekly) |

## Coverage Targets
- Critical paths: 100% branch coverage.
- Auth/crypto: 100%.
- Business logic: 80%.
- Overall: 70% minimum.

## Forbidden
- Merging with failing security tests.
- Disabling tests to ship faster.
- "Temporary" test skips without ticket.
