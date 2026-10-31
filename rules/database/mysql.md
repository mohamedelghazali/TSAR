# MySQL / MariaDB Security

## Authentication
- `caching_sha2_password` or `auth_socket` for local admin.
- No `mysql_native_password` (weak, deprecated).
- Per-application users with host restriction.
- `REQUIRE SSL` on all users.

## TLS
- `ssl-ca`, `ssl-cert`, `ssl-key` configured.
- `tls_version = 'TLSv1.3'`.
- `REQUIRE X509` for replication and admin.

## Authorization
- Least privilege: `SELECT`, `INSERT`, `UPDATE`, `DELETE` per table.
- No `GRANT ALL ON *.*` for application users.
- `FILE` privilege only for backup service.
- Separate replication user with `REPLICATION SLAVE` only.

## Encryption
- InnoDB tablespace encryption (`innodb_encrypt_tables = ON`).
- `innodb_encrypt_log = ON`.
- Keyring plugin (AWS KMS, HashiCorp Vault, or file-based with HSM).

## Auditing
- `audit_log` plugin enabled.
- Log DDL, grant changes, failed auth.
- Slow query log without sensitive data.

## Forbidden
- `GRANT ALL ON *.* TO 'app'@'%'`.
- `mysql_native_password`.
- `skip-grant-tables` in production.
- Public bind address for MySQL port.
