# Security Pair Programming

## When Required
- Changes to authentication or authorization.
- Changes to cryptographic code.
- Changes to payment flows.
- Changes to PII handling.
- New third-party integrations.

## Format
- Two developers, one writes, one reviews continuously.
- Navigator focuses on security invariants.
- Session logged with start/end and participants.

## Review Points
- Every input validated before use.
- Every sink parameterized or sanitized.
- Every secret from secret manager.
- Every error handled without leaking.
- Every decision logged appropriately.

## Handoff
- Written summary of decisions and open questions.
- Security invariants documented in code comments (only essential).

## Forbidden
- Pairing without a security-trained reviewer for sensitive changes.
- Pairing without documented outcome.
