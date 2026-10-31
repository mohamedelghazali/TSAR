# AI Inference Security

## Input
- Length limits per channel.
- Content-type validation.
- Rate limits per user and per key.
- Prompt injection defenses per rules/owasp-llm/llm01-prompt-injection.md.

## Output
- Secret and PII scanning before delivery.
- Markdown URL allow-listing to prevent exfiltration.
- No raw model metadata or system prompts in output.

## Isolation
- Tenant separation: no shared context between users.
- Deterministic replay forbidden for security decisions.

## Cost and Abuse
- Token budget per request and per user.
- Anomaly detection on usage patterns.
- Kill switch for runaway consumption.
