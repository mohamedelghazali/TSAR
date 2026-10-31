# Email Encryption

## Transport (TLS)
- Opportunistic TLS by default; MTA-STS enforces for known partners.
- DANE for domains publishing TLSA records.
- Reject plaintext delivery to partners requiring TLS.

## End-to-End
- S/MIME for enterprise; PGP for external secure comms.
- Keys distributed via signed certificates; no unverified keys.
- Key rotation annually; revocation published.
- Encryption at rest for archived mail.

## Signed Messages
- Sign all outbound mail with DKIM and S/MIME where possible.
- Verify signatures on inbound; alert on failures.

## Sensitive Content
- Subject lines never contain sensitive data.
- Attachments encrypted with a separate channel for the password.
- Classified content handled via secure portal, not email.

## Forbidden
- Sending credentials or PII over unencrypted email.
- Self-signed certificates for S/MIME in production.
- Shared S/MIME keys.
