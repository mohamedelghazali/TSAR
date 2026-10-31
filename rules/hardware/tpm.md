# TPM 2.0 Integration Rules

## Key Binding
- Operational secrets sealed to expected PCR values.
- Unsealing fails on PCR deviation (detects boot tampering).

## Attestation
- Remote attestation required before joining a trust cluster.
- Quote PCRs 0–7 and verify against known-good baseline.

## Anti-Pattern
TPM + HSM + Secure Boot does not automatically provide defense-in-depth.
The trust chain MUST be verified at every boot; otherwise each component will sign whatever it is asked to after compromise.
