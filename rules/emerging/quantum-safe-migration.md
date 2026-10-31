# Quantum-Safe Migration

## Timeline
- 2026-2029: Inventory, hybrid deployments.
- 2030-2035: Full migration for long-lived data.
- 2035+: All quantum-vulnerable algorithms retired.

## Inventory
- CBOM generated per release (see rules/crypto/post-quantum.md).
- Identify long-lived data (> 5 years).
- Identify systems that cannot rotate algorithms easily.
- Prioritize migration by data lifetime + exposure.

## Hybrid Deployments
- TLS: X25519MLKEM768 group.
- Signatures: Ed25519 + ML-DSA-44 dual-sign.
- Encryption: HPKE with hybrid KEM.

## Crypto-Agility
- Algorithm selection via configuration, not code.
- Versioned suites; support old + new during transition.
- Test vectors for each suite.

## High-Risk Assets
- Firmware, root certificates, signed updates.
- Long-term archival data.
- Key management systems.
- Hardware security modules (firmware upgrade path).

## Forbidden
- New code using only RSA/ECC without a PQ migration plan.
- Systems without algorithm rotation capability.
- Long-lived data under quantum-vulnerable algorithms after 2035.
