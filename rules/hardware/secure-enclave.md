# Secure Enclave / TEE Rules

## Key Binding
- Keys generated inside enclave; private key never leaves.
- Biometric or PIN binding for user-facing keys.

## Attestation
- Verify enclave attestation before trusting keys.
- Bind attestation to device identity and app signing identity.

## Fallback
- Define behavior when enclave is unavailable: fail closed for Tier-1 operations.
- Never downgrade to software key storage silently.
