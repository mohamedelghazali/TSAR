# Supply Chain Security Guide

## Artifact Lifecycle
1. **Build**: isolated, reproducible, provenance generated.
2. **Sign**: keyless with CI identity; log to Rekor.
3. **Attest**: SBOM, SLSA provenance, vulnerability scan.
4. **Store**: immutable registry with access control.
5. **Verify**: admission controller checks signature and identity.
6. **Deploy**: only verified artifacts reach production.

## SBOM Requirements
- Format: CycloneDX 1.5+ or SPDX 2.3+.
- Includes all direct and transitive dependencies.
- Machine-readable and attached as attestation.

## SLSA Levels
- Minimum: SLSA Build Level 2.
- Tier-1: SLSA Build Level 3.

## Dependency Hygiene
- Lockfiles committed.
- Automated updates via Dependabot/Renovate.
- Allow-list registries; block typosquatting.
- Critical updates within 24 hours.

## Evidence for Audit
- Signed artifacts with Rekor entries.
- SBOM and provenance attestations.
- Dependency update logs.
- Vulnerability remediation records.
