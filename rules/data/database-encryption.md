# Database Encryption

## At Rest
- Full-disk encryption mandatory (LUKS, BitLocker, cloud provider equivalent).
- Column-level encryption for sensitive fields (PII, secrets, tokens).
- Use AEAD per rules/crypto/algorithms.md; AAD includes table + column + tenant ID.
- Per-tenant DEK wrapped by tenant KEK; KEK in KMS/HSM.

## In Transit
- TLS 1.3 only between application and database.
- Verify server certificate; reject unknown CAs.
- No plaintext replication links.

## Key Management
- Never store encryption keys in the database they protect.
- KMS/Vault for KEK; envelope encryption for DEK.
- Rotation: KEKs annually, DEKs per 2^32 rows or 90 days.

## Access Control
- Least-privilege DB roles; separate read and write roles.
- No shared credentials across services.
- Row-level security where the DB supports it (Postgres RLS, Oracle VPD).

## Backups
- Encrypted with a separate key from production.
- Integrity hash stored separately.
- Restore tested quarterly.

## Auditing
- Log DDL changes, privileged queries, and access to sensitive tables.
- Tamper-evident log with hash chain.

## Forbidden
- Application-level encryption with keys derived from passwords.
- Plaintext backups.
- `SELECT *` on tables containing encrypted columns without field-level access control.
