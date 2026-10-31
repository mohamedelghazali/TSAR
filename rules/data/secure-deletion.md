# Secure Deletion

## Classification-Based Rules
| Data Class | Requirement |
|---|---|
| Restricted | Crypto-shred: destroy the key, then physical wipe of storage |
| Confidential | Multi-pass overwrite or crypto-shred |
| Internal | Standard delete + storage-level cleanup |
| Public | Standard delete |

## Crypto-Shredding
- Destroy the DEK in KMS/HSM; ciphertext becomes unrecoverable.
- Log the key destruction with two-person approval.
- Verify in backups: replication propagates destruction.

## Backups
- Deletion propagates to backups within the retention window.
- Document the propagation window per system.
- Legal hold overrides deletion; log and require legal approval.

## Physical Media
- NIST SP 800-88 Purge for SSDs and HDDs before disposal.
- Certificates of destruction retained.

## Derived Data
- Deletion cascades to derived tables, analytics warehouses, and caches.
- Verify with a data-flow map that no copies remain.

## Forbidden
- Deletion without logging who requested and who approved.
- Deleting source-of-truth without a verified backup outside the deletion scope.
