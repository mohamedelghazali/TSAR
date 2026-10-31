# Backup and Recovery Security

## Encryption
- Backups encrypted with a key distinct from production.
- Keys stored in KMS/HSM with a separate access policy.
- Multi-party approval for backup key access.

## Integrity
- Hash every backup artifact (SHA-256) at creation.
- Store hash in a separate system.
- Verify hash at restore time.

## Access Control
- Restore permissions restricted to a small break-glass group.
- Break-glass access requires MFA and logs the requesting identity.
- Restore actions trigger alerts to security team.

## Retention
- Per data classification:
  - Restricted: 7 years with legal hold support.
  - Confidential: 2 years.
  - Internal: 1 year.
  - Public: per policy.
- Automatic expiry; no orphaned backups.

## Immutability
- Object-lock or WORM storage for critical backups.
- Air-gapped copy for ransomware resilience.

## Restoration Testing
- Quarterly full restore test in an isolated environment.
- Document RTO and RPO achieved.
- Update the incident response plan with the results.

## Forbidden
- Backups readable by production application credentials.
- Unencrypted local dumps on developer machines.
- Restoring into production without a validation step.
