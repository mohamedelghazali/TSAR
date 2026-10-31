# Confidential Computing

## When to Use
- Multi-tenant workloads processing sensitive data.
- Third-party data processing (healthcare, finance).
- Models or keys that must never be exposed to the cloud provider.

## Technologies
- Intel TDX, AMD SEV-SNP, ARM CCA for CPU enclaves.
- NVIDIA Confidential Computing for GPU workloads.
- Attestation via manufacturer service (Intel Trust Authority, AMD KDS).

## Key Management
- Keys sealed to the enclave; never leave the TEE.
- Attestation verified before key release.
- Key binding includes enclave measurement.

## Attestation
- Verify attestation report before releasing secrets.
- Bind to specific enclave measurement + policy.
- Log attestation failures.

## Limitations
- TEEs do not protect against side channels perfectly.
- I/O paths may leak metadata.
- Trust the manufacturer's attestation service.

## Forbidden
- Releasing secrets to unverified enclaves.
- Using TEEs as the only control (defense-in-depth still required).
- Skipping attestation verification.
