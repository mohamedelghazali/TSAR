# Secrets Management Guide

## Principles
1. Never commit secrets to Git.
2. Never put secrets in environment variables at deploy time.
3. Use a secret manager (Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager).
4. Rotate automatically where possible.
5. Fail closed if the secret manager is unreachable.

## Patterns
| Pattern | Use | Rules |
|---|---|---|
| Dynamic secrets | DB, cloud credentials | rules/secrets/vault.md |
| Static rotated secrets | API keys | rules/secrets/aws-secrets-manager.md |
| GitOps encrypted | Infrastructure secrets | rules/secrets/sops.md |

## Anti-Patterns
- Secrets in `.env` committed to Git.
- Secrets in CI/CD environment variables.
- Secrets in Docker images.
- Secrets in logs.
- Long-lived root/admin tokens.

## Rotation SLAs
| Secret type | Rotation |
|---|---|
| Database passwords | 30 days (auto) |
| API keys | 90 days |
| JWT signing keys | 180 days |
| Root/admin | Annual + on incident |
| TLS certificates | 90 days (ACME) |
