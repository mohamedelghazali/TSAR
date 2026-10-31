# Air-Gapped Backups

## Purpose
Ransomware resilience: an attacker who compromises the production network
cannot reach the air-gapped copy.

## Models
| Model | Isolation | Recovery Time |
|---|---|---|
| Physical air-gap | Full physical separation | Hours to days |
| Logical air-gap (firewall) | Network separation | Minutes to hours |
| Offline object storage | Write-only API | Minutes |

## Physical Air-Gap
- Dedicated hardware not joined to the production domain.
- Data transfer via signed, checksummed media.
- Media rotated; old media wiped per NIST 800-88.
- Access requires two-person approval.
- Storage location access-logged and video-monitored.

## Logical Air-Gap
- Separate cloud account / subscription with no trust to production.
- Firewall between production and backup: one-way push only.
- Backup credentials never available to production workloads.
- Immutable storage on the backup side.

## Offline Object Storage
- S3 Object Lock Compliance mode.
- Backup account has no `DeleteObject` permission.
- Cross-account replication to a separate account.
- KMS key in separate account with restricted policy.

## Recovery
- Document recovery procedure without relying on production.
- Test quarterly.
- Recovery credentials separate from production.

## Forbidden
- Air-gapped backups reachable from production network.
- Shared credentials between production and backup.
- Untested recovery procedures.