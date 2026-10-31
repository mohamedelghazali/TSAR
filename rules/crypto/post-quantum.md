# Post-Quantum Cryptography (PQC) Readiness

## Threat Model
"Harvest Now, Decrypt Later" (HNDL): encrypted traffic captured today may be decrypted once a cryptographically relevant quantum computer exists.

## Mandatory Hybrid Constructions
- Key exchange: X25519MLKEM768 (X-Wing) in TLS 1.3 and custom protocols.
- Signatures: ML-DSA-44 (FIPS 204) for new signing code. Dual-sign with Ed25519 during transition.
- Asymmetric encryption: HPKE with (MLKEM768-X25519, HKDF-SHA256, AES-128-GCM).
- Hash-based signatures: SLH-DSA (FIPS 205) for firmware and long-lived artifacts.

## Crypto-Agility Requirements
Every system MUST:
1. Maintain a Cryptographic Bill of Materials (CBOM).
2. Abstract algorithm selection behind an interface.
3. Support algorithm rotation without redeploying application code.
4. Log algorithm identifiers alongside ciphertexts.
5. Reject hardcoded algorithm names in business logic.

## Migration Clock (NIST IR 8547)
- 2026–2029: Hybrid PQC in all new deployments.
- 2030: RSA-2048 / P-256 deprecated for new code.
- 2035: Quantum-vulnerable algorithms disallowed.
