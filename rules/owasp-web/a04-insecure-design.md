# A04: Insecure Design

## Controls
- Threat model required before implementation of any Tier-1 feature.
- Abuse cases documented alongside use cases.
- Secure defaults: deny, fail closed, opt-in for elevated privileges.
- Rate limits and resource caps designed in, not added later.
- Separation of duties in admin flows.

## Deliverables per Feature
- STRIDE model via skills/threat-modeler.
- Data flow diagram with trust boundaries.
- List of security requirements traced to TSAR rules.

## Forbidden
- Shipping features without documented threat model for auth, payments, or PII flows.
