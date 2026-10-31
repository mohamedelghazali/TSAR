# Model Registry Security

## Artifact Storage
- Models encrypted at rest (AES-256-GCM), per-tenant keys.
- Access via signed URLs with short TTL (<= 15 minutes).
- Registry API authenticated and authorized per operation.

## Versioning
- Immutable versions; no overwrite of published models.
- Every version has: hash, SBOM, AI-BOM, training lineage, evaluation report, signer identity.
- Signature via cosign or equivalent; verified at deployment.

## Promotion
- Stage gates: staging -> canary -> production.
- Each promotion requires: security scan clean, evaluation thresholds met, signer authorized.
- Human approval for production promotion.

## Decommission
- Deprecation policy documented.
- Revoke access; archive artifact with integrity hash.
- Re-encrypt archived models under long-term key.

## Forbidden
- Mutable model tags in production.
- Unsigned models in production.
- Cross-tenant model access without explicit grant.
