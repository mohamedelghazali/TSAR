# Secure Data Migration

## Pre-Migration
- Inventory source and destination: schemas, classifications, owners.
- Threat model the migration (see docs/threat-model-template.md).
- Define rollback plan with tested restore.
- Obtain data owner approval.

## In Transit
- Encrypted channel only (TLS 1.3).
- Mutual authentication between migration hosts.
- Transfer to a staging environment first; verify; then move to production.

## Transformation
- Preserve data lineage metadata.
- Validate transformations against sample data.
- Recompute and verify integrity hashes at every hop.

## PII Handling
- Minimize: transfer only fields required.
- Pseudonymize or tokenize where downstream does not need raw values.
- Redact from logs and error traces.

## Cutover
- Freeze writes or use change-data-capture to keep parity.
- Final reconciliation: row counts, checksums, sampled content.
- Explicit human sign-off before deleting source.

## Post-Migration
- Revoke old access credentials.
- Decommission source with secure wipe (see rules/data/secure-deletion.md).
- Archive migration logs per retention policy.

## Forbidden
- Copying production data to lower environments without masking.
- Running migrations with superuser credentials beyond the migration scope.
- Deleting source data before parity verification and sign-off.
