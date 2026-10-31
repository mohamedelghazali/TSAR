# Serverless Security

## Function Permissions
- Per-function IAM role; no shared roles.
- Least privilege; no `*` actions in production.
- Time-bound execution; no long-running functions for security operations.

## Secrets
- Secrets manager references at runtime; no env vars for sensitive values.
- Ephemeral credentials; never persisted.

## Networking
- VPC-attached functions for private resource access.
- Egress via NAT with allow-list.
- No public IPs on functions.

## Input Validation
- Schema validation on every event source (API Gateway, SQS, S3).
- Reject unknown fields.
- Enforce payload size limits.

## Cold Start and State
- Stateless; no secrets cached across invocations beyond TTL.
- No local filesystem for persistent data.

## Supply Chain
- Pinned runtimes.
- Signed function bundles (where supported).
- SBOM per function.

## Forbidden
- `*` in IAM roles.
- Secrets in environment variables.
- Public function URLs without auth.
- Unbounded execution timeouts.
