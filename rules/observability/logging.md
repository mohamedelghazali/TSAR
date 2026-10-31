# Logging Security

## Content
- Structured logs (JSON) with fixed schema.
- Never log secrets, tokens, passwords, session IDs.
- PII: hash or redact at emission.
- Error messages: generic to clients, detailed to internal logs (without secrets).

## Integrity
- Append-only storage; no modification by application.
- Hash chain or WORM for audit logs.
- Retention per classification; immutable during retention.

## Access
- Production logs require role-based access.
- Sensitive log streams (auth, payments) require elevated access.
- All access logged and reviewed.

## Volume
- Rate limits per logger; prevent log flooding.
- Bounded disk usage; drop debug logs before critical ones.

## Forbidden
- Logging raw request bodies for auth endpoints.
- Logging full PII.
- Logs writable by the application process.
- Logs forwarded over plaintext.
