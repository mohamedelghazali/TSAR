# Redis Security

## Authentication
- `requirepass` with strong CSPRNG password (>= 32 bytes) or ACL users.
- Redis 6+ ACLs: per-user, per-command, per-key.
- No `default` user with full permissions for applications.

## TLS
- `tls-port` enabled; `port 0` to disable plaintext.
- `tls-auth-clients yes` for mutual TLS.
- `tls-protocols "TLSv1.3"`.

## Authorization
- ACL users scoped to commands and key patterns.
- `+@read`/`+@write` categories, not `+@all`.
- No `FLUSHALL`, `CONFIG`, `DEBUG` for application users.

## Network
- Bind to private interface only.
- Protected mode on for development.
- Firewall restrict to application subnets.

## Data Protection
- Encryption at rest: filesystem or Redis Enterprise encryption.
- Sensitive values: application-layer AEAD before storing.
- TTL on sensitive keys.

## Persistence
- RDB/AOF files encrypted at rest.
- Backups encrypted and tested.

## Forbidden
- `bind 0.0.0.0` in production.
- `requirepass` disabled.
- Application users with `+@all`.
- Storing PII plaintext in Redis.
