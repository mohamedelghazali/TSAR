# Kubernetes Security Baseline

## Workloads
- Pod Security Standards: \`restricted\` profile enforced.
- Non-root user, read-only root filesystem, dropped capabilities.
- seccomp and AppArmor profiles applied.
- No hostPath mounts except explicitly audited cases.

## Network
- NetworkPolicy default-deny; explicit allow per flow.
- mTLS between services (service mesh or manual).
- Ingress with TLS 1.3 and HSTS.

## Secrets
- External Secrets Operator or CSI driver pulling from KMS/Vault.
- Never in ConfigMaps or plain env vars.
- Encrypted etcd at rest.

## RBAC
- Least-privilege roles; no \`cluster-admin\` for workloads.
- ServiceAccount tokens: short-lived, audience-bound.

## Supply Chain
- Image signing (cosign) and admission control verifying signatures.
- SBOM attached to images.
- No \`:latest\` tags in production.
