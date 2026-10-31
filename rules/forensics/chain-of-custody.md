# Chain of Custody

## Requirements
- Every transfer documented: from, to, date, time, purpose.
- Signed by both parties.
- Stored with the evidence.
- Immutable record (hash-chained or WORM).

## Format
| Field | Description |
|---|---|
| Evidence ID | Unique identifier |
| Description | What was acquired |
| Hash | SHA-256 of image |
| Acquired by | Name, role, signature |
| Date/time | ISO 8601 |
| Location | Physical or logical |
| Transfers | Log of all transfers |
| Storage | Current location |

## Handling
- Tamper-evident packaging for physical.
- Encrypted storage for digital.
- Access restricted to authorized personnel.
- Access logged and reviewed.

## Forbidden
- Evidence without documented custody.
- Access without logging.
- Copying evidence without hashing.
- Storing on general-purpose systems.
