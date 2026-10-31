# Email Authentication

## SPF
- One SPF record per domain; `~all` minimum, `-all` preferred.
- Max 10 DNS lookups; flatten if exceeded.
- Include only authorized senders.
- No `+all` or `?all`.

## DKIM
- 2048-bit RSA or Ed25519 keys.
- Rotate keys every 6 months; retain old keys for verification.
- Sign all outgoing mail, including transactional.
- Selectors unique per service (`s1`, `s2`, `service-name`).

## DMARC
- Start with `p=none` for 2-4 weeks with reporting.
- Move to `p=quarantine`, then `p=reject`.
- `sp=reject` for subdomains.
- `pct=100` once stable.
- `rua` and `ruf` reporting endpoints monitored.
- `adkim=s`, `aspf=s` strict alignment.

## MTA-STS
- `_mta-sts.example.com` TXT record with `v=STSv1`.
- `https://mta-sts.example.com/.well-known/mta-sts.txt` with `mode: enforce`.
- `max_age` >= 604800.

## TLS-RPT
- `_smtp._tls.example.com` TXT record with `v=TLSRPTv1; rua=mailto:...`.
- Monitor reports for TLS downgrade attempts.

## BIMI
- Optional; requires DMARC `p=quarantine` or `p=reject`.
- VMC certificate for verified mark.

## Forbidden
- No SPF record.
- DKIM key < 1024 bits.
- DMARC `p=none` indefinitely.
- MTA-STS `mode: testing` in production.
