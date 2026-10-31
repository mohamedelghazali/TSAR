# Load Balancer Security

## TLS Termination
- TLS 1.3 only at the edge.
- Valid certificates, auto-renewed.
- HSTS with preload.
- OCSP stapling enabled.
- Post-quantum hybrid where supported.

## Backend
- Re-encrypt to backends (TLS between LB and app).
- Health checks authenticated.
- Backend pools private; not internet-reachable.

## Headers
- `X-Forwarded-For` chain validated; trust only known proxies.
- `X-Forwarded-Proto` enforced; app rejects HTTP if behind HTTPS LB.
- Strip client-supplied security headers that the LB sets.

## Access Control
- IP allow-lists per listener where applicable.
- Client certificate authentication for high-value endpoints.
- Rate limits at the LB.

## Logging
- Access logs with redaction.
- Error logs without sensitive data.
- Forwarded to SIEM.

## Forbidden
- TLS termination without re-encryption to backend for sensitive data.
- Plaintext backend connections.
- Untrusted `X-Forwarded-For` accepted.
- LB admin interface exposed publicly.
