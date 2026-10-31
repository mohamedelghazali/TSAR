# PostgreSQL Security

## Authentication
- `scram-sha-256` in `pg_hba.conf`; no `trust` or `md5`.
- TLS required: `hostssl ... scram-sha-256` only.
- `ssl_min_protocol_version = 'TLSv1.3'`.
- Per-application users; no shared accounts.
- Passwords: Argon2id at application layer; no direct password auth for services.

## Authorization
- Least privilege per role.
- No `SUPERUSER` for application users.
- `CREATEDB`, `CREATEROLE` only for administrative roles.
- Row-level security (RLS) for multi-tenant tables.
- `search_path` explicitly set per user to prevent hijacking.

## Encryption
- `ssl = on` with valid certificates.
- At-rest encryption via filesystem (LUKS) or cloud-native.
- Column-level encryption for sensitive fields (application-layer AEAD).

## Auditing
- `pgaudit` enabled for DDL, role changes, and access to sensitive tables.
- Log connections, disconnections, and failed auth.
- Logs forwarded to SIEM with tamper-evident storage.

## Configuration
- `password_encryption = 'scram-sha-256'`.
- `log_connections = on`, `log_disconnections = on`.
- `log_statement = 'ddl'` minimum.
- Backups encrypted and tested quarterly.

## Forbidden
- `trust` in `pg_hba.conf`.
- `md5` authentication.
- `SUPERUSER` for application roles.
- Public schema writable by non-owner roles.
- Unencrypted replication links.
