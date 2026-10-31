# MongoDB Security

## Authentication
- SCRAM-SHA-256 for internal auth.
- Client X.509 certificates for service-to-service.
- No `--noauth` in production.
- Per-application users; no shared credentials.

## Authorization
- Built-in roles scoped: `read`, `readWrite` on specific DBs.
- Custom roles for fine-grained access.
- No `root` role for application users.
- `security.authorization: enabled`.

## TLS
- `net.tls.mode: requireTLS`.
- `net.tls.disabledProtocols: [TLS1_0, TLS1_1]`.
- Client certificate verification.

## Encryption
- WiredTiger encryption at rest with KMIP or cloud KMS.
- Field-level encryption (client-side) for PII.
- Encrypted backups.

## Auditing
- `auditLog` enabled with filters for auth, DDL, CRUD on sensitive collections.
- Logs to SIEM.

## Network
- Bind to private interfaces only.
- Firewall rules restrict to application subnets.
- No direct internet exposure.

## Forbidden
- `--noauth` or `--bind_ip 0.0.0.0` in production.
- `root` role for application users.
- Unencrypted backups.
- Field-level encryption disabled for PII collections.
