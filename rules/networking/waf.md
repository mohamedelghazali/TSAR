# Web Application Firewall (WAF)

## Deployment
- Inline mode (blocking), not monitor-only, in production.
- Deployed at the edge (CDN, cloud WAF, or self-hosted).
- Behind the WAF: application servers not directly reachable.

## Rules
- OWASP Core Rule Set (CRS) enabled with paranoia level >= 2.
- Custom rules for application-specific threats.
- Bot management for login, signup, and payment endpoints.
- Geo-blocking per policy (not a substitute for auth).

## Tuning
- Review false positives weekly.
- Exclusions require a documented justification and expiry.
- Test rule changes in staging first.

## Logging
- Log all blocked requests with redacted bodies.
- Alert on rule anomalies (sudden spikes, new attack patterns).
- Retain logs per compliance requirements.

## DDoS
- Layer 3/4: cloud provider DDoS protection (AWS Shield, Cloud Armor, Azure DDoS).
- Layer 7: WAF rate limits, challenge pages, CAPTCHA.
- Auto-scaling behind the WAF for volumetric attacks.

## Forbidden
- Monitor-only WAF in production.
- Disabled CRS.
- Wildcard exclusions (`/api/*`) without per-endpoint review.
- WAF bypassable by direct IP access.
