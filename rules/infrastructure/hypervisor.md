# Hypervisor Security

## Host Hardening
- Minimal install; only management agents.
- Dedicated management network; no internet exposure.
- BIOS/UEFI with Secure Boot; signed firmware.
- TPM 2.0 for measured boot and attestation.

## Hypervisor Configuration
- Latest patches within vendor SLA.
- Live migration encrypted (TLS 1.3, mTLS).
- Management APIs authenticated; no default credentials.
- RBAC with least privilege.
- Audit logs forwarded to SIEM.

## Guest Isolation
- No shared clipboard or file transfer between guests unless explicit.
- CPU features restricted where side channels are a concern (disable SMT for high-value).
- Memory scrubbing on VM teardown.
- Network isolation per tenant.

## Snapshots
- Encrypted at rest.
- Access controlled per tenant.
- Retention per policy; deletion propagates.

## Forbidden
- Default management credentials.
- Unencrypted live migration.
- Shared storage without per-tenant encryption.
- Disabled audit logging.
