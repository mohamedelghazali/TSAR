# Secure Email Gateway

## Inbound
- Anti-malware with sandboxing for attachments.
- Anti-phishing with DMARC enforcement and lookalike domain detection.
- URL rewriting with detonation on click.
- Attachment filtering (block macros, executables, encrypted archives).
- Rate limits per sender and per recipient.

## Outbound
- DKIM signing at the gateway for messages not signed by the origin.
- DLP scanning for PII, credentials, and classified data.
- Encrypted delivery (TLS enforced) to known partners.
- Message encryption for sensitive content (S/MIME or PGP).

## Quarantine
- Quarantine reviewed daily by security team.
- Self-service release with MFA.
- Quarantine retention 30 days.

## Reporting
- Weekly phishing simulation results.
- Monthly DMARC aggregate report analysis.
- Alerting on sudden volume changes.

## Forbidden
- Auto-forwarding to external domains.
- Auto-reply to external senders with internal details.
- Bypassing the gateway for "trusted" senders without policy.
