# Ransomware Resilience

## Detection
- Anomalous encryption activity on endpoints and servers (EDR).
- Mass file rename/delete alerts.
- Backup deletion attempts.
- Unusual credential use for backup systems.

## Prevention
- Immutable backups (rules/backup/immutability.md).
- Air-gapped copies (rules/backup/air-gap.md).
- Least-privilege on backup systems.
- MFA on backup admin access.
- Separate credentials per backup target.

## Response
1. Isolate affected systems (network).
2. Identify patient zero and lateral movement.
3. Verify backup integrity (pre-infection snapshots).
4. Restore from clean backup into isolated environment.
5. Validate before rejoining production.
6. Do not pay ransom; report to authorities.

## Recovery Time Objective
- Critical systems: RTO <= 4 hours.
- Important systems: RTO <= 24 hours.
- Standard systems: RTO <= 72 hours.

## Forbidden
- Restoring from a backup taken after infection without validation.
- Paying ransom without law enforcement coordination.
- Single person able to disable backups.