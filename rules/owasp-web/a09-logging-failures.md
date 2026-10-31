# A09: Security Logging and Monitoring Failures

## Controls
- Log authentication events, authorization failures, and administrative actions.
- Append-only storage with hash chain for tamper evidence.
- Redaction applied at log emission (see rules/data/logging-redaction.md).
- Retention aligned with legal and regulatory requirements.
- Alerting on: repeated auth failures, privilege escalation, unexpected data access volume.

## Forbidden
- Logging secrets, tokens, passwords, or full PII.
- Silent failures on security events.
