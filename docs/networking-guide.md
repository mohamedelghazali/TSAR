# Networking Security Guide

## Layers
| Layer | Controls |
|---|---|
| DNS | DNSSEC, CAA, DMARC, registrar lock |
| Transport | TLS 1.3, mTLS, PQC hybrid |
| Service mesh | Strict mTLS, default-deny, egress gateway |
| Edge | WAF inline, DDoS protection, rate limits |
| Load balancer | TLS termination, re-encryption, header hygiene |

## Zero Trust Checklist
- [ ] Identity verified per request.
- [ ] Network micro-segmented.
- [ ] Default-deny at every boundary.
- [ ] East-west traffic encrypted (mTLS).
- [ ] Access logged with context.
- [ ] Just-in-time privilege elevation.

## Verification
- Run `tsar scan` on Envoy, Cilium, and Terraform configs.
- Validate certificates with `openssl s_client -connect host:443 -tls1_3`.
- Verify DNSSEC with `dig +dnssec`.
- Test WAF with OWASP ZAP in staging.
