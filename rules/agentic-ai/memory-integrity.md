# Agent Memory Integrity

## Risks
- Poisoned memory persists across sessions.
- Secrets and PII accumulate in conversation history.
- Memory is shared across tenants or users.

## Controls
- Namespace isolation: memory partitioned per user, per tenant, per agent.
- Write validation: memory writes pass through schema validation and content filtering.
- TTL: sensitive memory entries expire; no indefinite retention.
- Redaction: secrets, tokens, and PII removed before persistence.
- Integrity: append-only log with hash chain for audit.
- Poisoning defense: retrieved memory treated as untrusted data, not instructions.
