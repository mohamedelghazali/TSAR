# Database Integration Guide

## Supported Databases
| DB | Rules |
|---|---|
| PostgreSQL | rules/database/postgresql.md |
| MySQL / MariaDB | rules/database/mysql.md |
| MongoDB | rules/database/mongodb.md |
| Redis | rules/database/redis.md |

## Multi-Tenancy
- Use RLS (Postgres) or equivalent for row-level isolation.
- Never rely on application filtering alone.
- Test cross-tenant access in CI.

## Verification Checklist
- [ ] TLS 1.3 only, plaintext disabled.
- [ ] Strong authentication (SCRAM, X.509).
- [ ] Least-privilege roles; no wildcard grants.
- [ ] RLS enabled for multi-tenant tables.
- [ ] Encryption at rest (KMS-managed keys).
- [ ] Audit logs enabled and forwarded.
- [ ] Backups encrypted and tested.
- [ ] Replication links encrypted and authenticated.
