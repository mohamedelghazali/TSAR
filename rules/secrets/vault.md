# HashiCorp Vault Integration

## Authentication
- Kubernetes auth for workloads; AppRole for non-K8s.
- OIDC for human access.
- No root token usage outside break-glass.

## Authorization
- Policies scoped per path and capability.
- `read` only for most workloads; `write` for rotation services.
- No `sudo` capability for applications.

## Secrets
- Dynamic secrets for databases (short TTL).
- Static secrets rotated per policy.
- Response wrapping for delivery to clients.
- Audit device enabled on every node.

## Storage
- Integrated storage (Raft) or Consul; encrypted at rest with auto-unseal via KMS.
- Auto-unseal key in HSM/KMS, not on disk.
- Seal/unseal operations audited.

## Client Integration
- Applications fetch secrets at startup and refresh before TTL.
- Cache TTL: <= 50% of secret TTL.
- Fail closed if Vault unreachable (for Tier-1).

## Forbidden
- Root token in code or CI.
- Long-lived tokens (> 24h).
- Secrets logged or cached beyond TTL.
- Vault exposed publicly.
