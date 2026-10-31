# Email Security Guide

## Authentication Stack
1. SPF: authorize senders, `-all`.
2. DKIM: sign outgoing mail, 2048-bit RSA.
3. DMARC: `p=reject`, strict alignment.
4. MTA-STS: `mode: enforce`.
5. TLS-RPT: monitor transport.
6. CAA: restrict certificate issuance.

## Verification
- `dig +short TXT example.com` shows SPF.
- `dig +short TXT _dmarc.example.com` shows DMARC.
- `dig +short TXT selector1._domainkey.example.com` shows DKIM.
- `dig +short TXT _mta-sts.example.com` shows MTA-STS.
- `https://mta-sts.example.com/.well-known/mta-sts.txt` returns enforce policy.
- `dig +short CAA example.com` shows CAA records.

## Monitoring
- DMARC aggregate reports reviewed weekly.
- TLS-RPT reports reviewed weekly.
- Lookalike domain monitoring alert.

## Incident Response
- On spoofing: tighten DMARC, add lookalike domains, notify users.
- On phishing: pull messages, block sender, force password reset if credentials entered.
