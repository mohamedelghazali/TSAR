# Container Image Signing (Sigstore / cosign)

## Signing
- Sign every image at build time with cosign in keyless mode (OIDC identity).
- Attach SBOM (CycloneDX or SPDX) as an attestation.
- Attach SLSA provenance as an attestation.
- Record the signature in Rekor (transparency log).

## Verification
- Admission controller (Kyverno, OPA Gatekeeper, Connaisseur) verifies signatures before allowing pod creation.
- Verify identity: OIDC issuer + subject match the CI workload.
- Reject unsigned or unverifiable images.
- Verify attestations match the expected SBOM/provenance format.

## Rotation
- Signing identity rotates with CI workload identity; no long-lived keys.
- Revocation via Rekor index or admission policy update.

## Forbidden
- Signing images on developer laptops with long-lived private keys.
- Deployment of unsigned images to production.
- Skipping verification "temporarily" during incidents without a documented exception.
