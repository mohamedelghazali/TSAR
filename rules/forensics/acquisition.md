# Forensic Acquisition

## Order of Volatility
1. CPU registers, cache.
2. Memory (RAM).
3. Network state, running processes.
4. Temporary filesystems.
5. Disk storage.
6. Remote logs and backups.
7. Archival media.

## Acquisition Types
| Type | Use | Integrity |
|---|---|---|
| Live | Running systems | Highest risk of alteration |
| Dead | Powered-off systems | Bit-for-bit copy |
| Logical | Files/directories | Hash-verified |
| Physical | Full disk | Bit-for-bit copy |

## Integrity
- Hash every image: SHA-256 (and SHA-1 for legacy compatibility).
- Write-blocker for physical acquisition.
- Multiple hashes from independent tools.
- Chain of custody documented.

## Tools
- Memory: Volatility, LiME, AVML.
- Disk: dd, dc3dd, FTK Imager, EnCase.
- Cloud: native snapshots + API audit logs.

## Documentation
- Who acquired, when, where, why.
- Tool versions and hashes.
- Any deviations from standard procedure.
- Witness signatures for legal cases.

## Forbidden
- Booting the system before memory acquisition.
- Writing to the original media.
- Acquisition without chain of custody.
- Unverified tooling.
