# AWS Secrets Manager

## Access
- IAM roles for workloads; no IAM users with secrets access.
- Resource policies scoped per secret ARN.
- Cross-account access via explicit resource policy, not wildcard.

## Rotation
- Automatic rotation enabled for RDS, Redshift, DocumentDB.
- Custom Lambda rotation for other secrets.
- Rotation period <= 30 days for high-value secrets.

## Encryption
- KMS CMK per application; not the default `aws/secretsmanager` key.
- Key policy restricts to the application role.

## Versioning
- Use `AWSCURRENT` and `AWSPREVIOUS` for zero-downtime rotation.
- Applications must handle rotation gracefully (refresh on error, retry).

## Monitoring
- CloudTrail data events for `GetSecretValue`.
- Alert on anomalous access patterns.

## Forbidden
- Secrets in environment variables at deploy time (inject at runtime).
- Shared secrets across services.
- Default KMS key for sensitive secrets.
