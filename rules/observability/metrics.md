# Metrics Security

## Data Classification
- Metrics carry labels; labels can leak PII.
- Never use email, phone, session ID, IP, or user ID as label values.
- Use hashed or bucketed identifiers if cardinality requires differentiation.

## Cardinality
- Bound label cardinality; reject unbounded labels.
- User-controlled input never becomes a label value.
- Alert on cardinality explosions (potential DoS or leak).

## Exposure
- Metrics endpoints (`/metrics`) authenticated and network-restricted.
- No public exposure; scrape from monitoring network only.
- TLS between scraper and target.

## Sensitive Endpoints
- Admin dashboards require SSO + MFA.
- Role-based access for production dashboards.
- Audit access to sensitive dashboards.

## Forbidden
- PII in labels.
- Public `/metrics`.
- Unauthenticated admin dashboards.
- Metric names or labels derived from user input.
