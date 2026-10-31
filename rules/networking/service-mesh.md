# Service Mesh Security (Istio, Linkerd, Cilium Service Mesh)

## mTLS
- Strict mTLS mode enforced mesh-wide; `PERMISSIVE` only during migration.
- Automatic certificate rotation via the mesh's control plane.
- SPIFFE-based identity for all workloads.

## Authorization
- Default-deny `AuthorizationPolicy` for all namespaces.
- Explicit allow per source/destination/operation.
- JWT validation at the edge proxy.
- Rate limiting at the mesh layer.

## Traffic Management
- Egress via egress gateway with allow-list.
- No direct egress from pods; route through the gateway.
- Retries with budget; no unbounded retries.
- Circuit breakers on all outbound.

## Observability
- Access logs at the proxy with redaction.
- Distributed tracing with PII scrubbing.
- Metrics per service, per route, per status.

## Control Plane
- Control plane isolated; API server not publicly exposed.
- RBAC on control plane resources.
- Audit logs on policy changes.
- Version pinning; no auto-upgrade in production.

## Forbidden
- `PERMISSIVE` mTLS in production.
- Mesh bypass via direct pod-to-pod traffic (sidecar-less without policy).
- Egress without gateway.
- Control plane without audit logging.
