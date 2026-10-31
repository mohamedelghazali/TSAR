# Container Orchestration (beyond Kubernetes)

## Support Matrix
| Platform | Notes |
|---|---|
| Kubernetes | See rules/platform/kubernetes.md |
| Nomad | HashiCorp Nomad + Consul |
| ECS/Fargate | AWS managed |
| Cloud Run | GCP managed |
| Azure Container Apps | Azure managed |

## Nomad
- mTLS for server and client RPC.
- ACLs enabled with least-privilege policies.
- Namespaces for tenant isolation.
- Sentinel policies for governance.
- Vault integration for secrets.

## ECS
- Task roles scoped per task; no `*` actions.
- Secrets via `secrets` field, not environment literals.
- Private subnets; NAT for egress.
- Fargate for multi-tenant isolation.
- Container Insights for monitoring.

## Cloud Run / Container Apps
- Ingress restricted to internal or allow-list.
- Service accounts with minimal roles.
- Secrets via Secret Manager references.
- Binary Authorization / image verification.
- VPC connector for private resources.

## Common Requirements
- Signed images; admission control verifies.
- Per-workload identity.
- Network default-deny.
- Resource limits (CPU, memory, PID count).
- Audit logs to SIEM.

## Forbidden
- Unauthenticated RPC.
- Wildcard IAM roles.
- Public registry pulls without verification.
- Containers without resource limits.
