# Artifact Signing (Sigstore)

## Signing
- Keyless signing with OIDC identity from CI workload.
- Sign: container images, binaries, SBOMs, SBOM attestations, provenance.
- Log to Rekor transparency log.

## Verification
- Policy engine (Kyverno, Connaisseur, OPA) verifies signature and identity.
- Identity binding: OIDC issuer + subject match expected CI.
- Timestamp verification: signature valid at the time of verification.

## Attestations
- SBOM attestation (CycloneDX).
- SLSA provenance attestation (in-toto).
- Vulnerability scan attestation (Trivy/Grype report).
- Policy check attestation (Conftest/OPA).

## Key Management
- No long-lived keys; keyless preferred.
- If keys are used, HSM-backed and rotated annually.

## Forbidden
- Signing with personal GitHub tokens.
- Deploying artifacts signed by unauthorized identities.
- Skipping verification in production.
