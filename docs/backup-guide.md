# Backup Guide

## Strategy
Follow 3-2-1-1-0:
- 3 copies
- 2 media types
- 1 offsite
- 1 immutable
- 0 restore errors

## Implementation
| Tool | Use | Immutability |
|---|---|---|
| Restic | Encrypted, deduplicated | S3 Object Lock |
| BorgBackup | Encrypted, deduplicated | SSH target |
| Velero | Kubernetes | S3 Object Lock |
| AWS Backup | AWS resources | Vault Lock |

## Verification
- `restic check --read-data-subset=5%` weekly.
- Full restore test quarterly.
- Hash comparison at restore.

## Ransomware Response
1. Isolate.
2. Identify infection time.
3. Restore from pre-infection snapshot.
4. Verify in isolated environment.
5. Rejoin production after validation.