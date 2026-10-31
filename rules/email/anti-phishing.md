# Anti-Phishing

## Technical Controls
- DMARC `p=reject` for all owned domains.
- Lookalike domain monitoring (typosquatting, homoglyphs).
- External sender banner on inbound mail.
- Reply-To and Return-Path validation.
- URL reputation and detonation.
- Attachment sandboxing.

## User Controls
- Phishing simulation program (monthly).
- Report button in email client.
- Fast triage of reported phishing (< 1 hour).
- Security awareness training annually.

## Response
- On confirmed phishing: block sender, pull messages from inboxes, notify affected users.
- On credential compromise: force password reset, revoke sessions, review activity.

## Forbidden
- Disabling external sender banners.
- Auto-forwarding phishing reports to a dead mailbox.
- Ignoring DMARC failure reports.
