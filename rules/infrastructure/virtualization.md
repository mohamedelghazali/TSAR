# Virtualization Security

## VM Lifecycle
- Golden images hardened per CIS.
- Immutable infrastructure; no in-place modification.
- Instance identity: IMDSv2, metadata tokens, or cloud provider identity.
- Snapshot encryption with per-VM keys.

## Networking
- Micro-segmentation; no flat networks.
- Security groups deny by default.
- Private subnets for compute; NAT for egress.
- No public IPs on internal workloads.

## Storage
- Encrypted volumes (AES-256-XTS or cloud equivalent).
- Per-tenant keys for sensitive data.
- Snapshot access controlled.

## Monitoring
- EDR on every VM.
- File integrity monitoring on critical paths.
- Audit logs forwarded.

## Decommissioning
- Secure wipe per NIST 800-88.
- Key destruction (crypto-shred) for encrypted volumes.
- Certificate of destruction for compliance.

## Forbidden
- Public IPs on internal VMs.
- Unencrypted volumes.
- Disabled EDR.
- Golden images from untrusted sources.
