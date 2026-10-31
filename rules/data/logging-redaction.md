# Logging and Redaction

## Never Log
- Passwords, tokens, API keys, session IDs.
- Full credit card numbers, national IDs, health records.
- Full request bodies on authentication endpoints.

## Redaction Rules
- Replace secrets with `[REDACTED:type]`.
- Hash identifiers where correlation is needed without exposure.
- Structured logs with field-level redaction policies.

## Integrity
- Append-only log storage.
- Hash chain or WORM storage for audit logs.
