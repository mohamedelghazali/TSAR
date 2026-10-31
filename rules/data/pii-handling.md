# PII Handling

## Classification
- Direct identifiers: name, email, phone, national ID.
- Indirect identifiers: IP, device ID, location.
- Sensitive: health, financial, biometric, sexual orientation, religion.

## Controls
- Encrypt at rest with per-tenant keys.
- Tokenize where full value is not required.
- Access logged and reviewed.
- Retention limits enforced by policy.
- Deletion propagates to backups and derived data.

## Logging
- Never log full PII.
- Redact or hash before logging.
