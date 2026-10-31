# DNS Security

## DNSSEC
- Sign all authoritative zones with DNSSEC (ECDSA P-256 or Ed25519).
- Publish DS records at the parent; verify chain of trust.
- Rotate ZSK every 90 days; KSK annually.
- Monitor for DNSSEC validation failures.

## Zone Transfer
- AXFR/IXFR restricted to authorized secondary servers by IP + TSIG.
- No public zone transfer.
- Log zone transfer attempts.

## Recursive Resolvers
- Use DNS-over-TLS (DoT, port 853) or DNS-over-HTTPS (DoH) for outbound.
- Validate DNSSEC at the resolver.
- No open resolvers exposed to the internet.

## Record Hygiene
- CAA records restrict certificate issuance to approved CAs.
- SPF, DKIM, DMARC for email domains:
  - `v=DMARC1; p=reject; rua=mailto:dmarc@example.com`
  - `p=reject` in production; no `p=none` without monitoring.
- MTA-STS and TLS-RPT for email transport security.

## Domain Registration
- Registrar lock enabled.
- Multi-year registration.
- WHOIS privacy where permitted.
- MFA on registrar account; monitor for unauthorized changes.

## Forbidden
- `p=none` DMARC in production without active monitoring.
- Open recursive resolvers.
- Zone transfers from any IP.
- Wildcard DNS `*.example.com` without business justification.
