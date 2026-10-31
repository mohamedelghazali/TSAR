# Dependency Integrity

## Pinning
- Pin exact versions in lockfiles (`package-lock.json`, `poetry.lock`, `go.sum`).
- Verify lockfile checksums.
- No floating ranges in production manifests.

## Verification
- Verify package signatures where the ecosystem supports it (npm provenance, PyPI attestations, Go module checksums).
- Reject packages with mismatched hashes.

## Typosquatting and Confusion
- Use internal registry mirrors with allow-list.
- Configure scoped namespaces (`@company/*`) for internal packages.
- Block installation of packages not in the approved registry.
- Detect names similar to popular packages (Levenshtein distance heuristics).

## Updates
- Automated PRs for dependency updates (Dependabot, Renovate).
- Security updates applied within SLA (critical: 24h, high: 7 days).
- Major version bumps require review.

## Removal
- Remove unused dependencies.
- Audit transitive dependencies quarterly.

## Forbidden
- `npm install <package>` without lockfile in CI.
- `pip install` from unverified indexes.
- Disabling checksum verification.
