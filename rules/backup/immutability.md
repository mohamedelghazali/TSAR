# Immutable Backups

## Requirement
Backups must be immutable for the retention period to resist ransomware,
insider threats, and accidental deletion.

## Mechanisms
| Mechanism | Provider | Retention |
|---|---|---|
| S3 Object Lock (Compliance mode) | AWS | 1-100 years |
| GCS Bucket Lock | GCP | Until policy expires |
| Azure Immutable Blob | Azure | Policy-defined |
| WORM storage | On-prem | Hardware-enforced |
| Air-gapped copy | Any | Physical |

## Configuration
- Compliance mode, not Governance mode, for regulated data.
- Legal hold overrides deletion regardless of retention.
- MFA delete required for retention policy changes (AWS).
- Key separation: delete permissions held by a different team.

## Verification
- Attempt deletion and verify rejection.
- Audit retention policy changes.
- Test restore from immutable copy quarterly.

## Forbidden
- Mutable backups of critical data.
- Single admin able to delete both backups and retention policy.
- Governance mode for regulated data without compensating controls.