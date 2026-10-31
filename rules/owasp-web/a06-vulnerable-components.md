# A06: Vulnerable and Outdated Components

## Controls
- SBOM generated on every build (CycloneDX or SPDX).
- Dependency pinning with lockfiles.
- Automated vulnerability scanning in CI.
- Critical CVEs block release; high CVEs require documented exception with expiry.
- Remove unused dependencies.

## Forbidden
- Floating version ranges in production manifests.
- Dependencies with no maintained upstream.
