# SOPS Integration

## Use Case
- Encrypt secrets in Git for GitOps workflows.
- Appropriate for infrastructure secrets, not high-frequency rotation.

## Setup
- KMS-backed (AWS KMS, GCP KMS, Azure Key Vault) or age.
- `.sops.yaml` with creation rules per path.
- Encrypt only values, keep keys visible for diff review.

## Access
- Decryption requires KMS/age key access.
- CI uses short-lived credentials via OIDC.
- Developers decrypt only secrets for their environment.

## Rotation
- Rotate encrypted secrets per policy.
- Re-encrypt on key rotation.
- Audit rotation in Git history.

## Forbidden
- SOPS for secrets requiring automatic rotation.
- Shared age keys across teams.
- Decrypted secrets written to disk outside `apply` scope.
