# Backup Strategy (3-2-1-1-0)

## Rule
- **3** copies of data (1 primary + 2 backups).
- **2** different media types (e.g., disk + object storage).
- **1** copy offsite (different region, cloud, or provider).
- **1** copy offline or immutable (ransomware resilience).
- **0** errors on restore (verified restores, not just backups).

## Backup Types
| Type | Frequency | Retention | Use |
|---|---|---|---|
| Full | Weekly | 4-12 weeks | Baseline restore |
| Incremental | Daily | 30-90 days | Point-in-time |
| Differential | Weekly | 4-8 weeks | Medium restore |
| Continuous (CDP) | Real-time | 7-30 days | Zero-loss RPO |
| Snapshot | Hourly | 7-30 days | Fast rollback |

## Retention Policy
| Data Class | Minimum Retention |
|---|---|
| Financial | 7 years |
| Healthcare | 6 years (or state-specific) |
| Legal hold | Until released |
| Operational | 90 days |
| Logs | 1 year |

## Encryption
- AES-256-GCM at rest with per-backup key.
- Keys in KMS/HSM, separate from backup storage.
- Envelope encryption: DEK per backup, KEK in KMS.
- Backups never readable by production application credentials.

## Integrity
- SHA-256 hash of every backup at creation.
- Hash stored in a separate system.
- Verify hash at restore; alert on mismatch.

## Forbidden
- 3 copies on the same storage system.
- Unencrypted backups.
- Backups accessible with production credentials.
- Backups never tested for restore.