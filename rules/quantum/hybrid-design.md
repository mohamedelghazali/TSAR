# Hybrid Cryptographic Design

## Principle
A hybrid combines one classical algorithm (X25519 or Ed25519) with one
post-quantum algorithm (ML-KEM or ML-DSA). Security holds if either holds.

## Construction Rules
1. **Concatenate**, never XOR, the shared secrets.
2. **HKDF** with distinct `info` labels per hybrid construction.
3. **Separate keys**: hybrid for confidentiality, hybrid for signatures,
   hybrid for key encapsulation — no cross-use.
4. **Version the hybrid suite**: store suite identifier with ciphertext/signature.
5. **Reject on downgrade**: if peer offers classical-only, refuse in strict mode.

## TLS 1.3
- Use `X25519MLKEM768` named group.
- Certificate signatures: dual-sign Ed25519 + ML-DSA-44.

## Custom Protocols
- Define a `hybrid_suite_id` (2 bytes).
- Document shared secret derivation in the protocol spec.
- Publish test vectors for interoperability.

## Test Vectors
- Include NIST ACVP vectors for each component.
- Include at least one hybrid KAT per suite.
