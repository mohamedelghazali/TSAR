# IAM Design Principles

## Least Privilege
- Every identity gets the minimum permissions required for its function.
- No wildcard actions on production resources.
- Just-in-time elevation for admin tasks; short duration (<= 1 hour).
- Separation of duties: no single identity can both create and approve critical changes.

## Identity Types
| Type | Lifetime | Use |
|---|---|---|
| Human (SSO) | Session-bound | Interactive use |
| Workload (IRSA, Workload Identity, Managed Identity) | Token-bound | Service-to-service |
| Automation (CI/CD) | Run-bound | Pipelines |
| Break-glass | Approved session | Emergency |

## Authentication
- Humans: SSO with MFA; phishing-resistant FIDO2 for admin.
- Workloads: OIDC federation; no long-lived keys.
- CI/CD: OIDC to cloud provider; no stored secrets.

## Authorization Model
- RBAC for coarse-grained access; ABAC for fine-grained.
- Policy-as-code (OPA, Cedar) for complex rules.
- Consistent enforcement across services.

## Session Management
- Short-lived tokens (<= 1 hour for access, <= 24 hours for refresh).
- Rotate refresh tokens.
- Session revocation on password change, role change, or compromise.

## Audit
- Every authorization decision logged with identity, resource, action, decision.
- Logs tamper-evident (hash chain).
- Review logs quarterly for stale permissions.
