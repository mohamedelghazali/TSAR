# Zero Trust Architecture

## Principles
1. Never trust, always verify.
2. Assume breach.
3. Verify explicitly using all available signals.
4. Least privilege access.
5. Micro-segmentation.

## Identity
- Every request authenticated: user, device, service.
- Device posture checked (managed, patched, compliant).
- Continuous verification, not just at login.

## Network
- Micro-segmentation; no flat networks.
- Default-deny at every boundary (network, service, application).
- Encrypted traffic everywhere, including east-west.

## Access
- Application-level access (not network-level) via identity-aware proxy.
- Session-based access with short TTLs.
- Just-in-time elevation for privileged operations.

## Monitoring
- All access logged with identity and context.
- Anomaly detection on access patterns.
- Alert on impossible travel, unusual device, privilege escalation attempts.

## Implementation Path
1. Inventory assets and data flows.
2. Classify data and define policies.
3. Deploy identity-aware proxy.
4. Segment network.
5. Enforce least privilege.
6. Continuous monitoring.

## Forbidden
- Trust based on network location (VPN, internal IP).
- Permanent privileged access.
- Unencrypted east-west traffic.
