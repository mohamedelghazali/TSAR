# Secure Development Guide

## Gates
1. Design gate: threat model.
2. Code gate: SAST, SCA, secrets.
3. Test gate: DAST, penetration.
4. Release gate: SBOM, signature.
5. Deploy gate: admission policy.

## Reviewer Requirements
- Security-trained reviewer for sensitive changes.
- Pair review for high-risk (auth, crypto, payments).

## Dependency SLA
| Severity | SLA |
|---|---|
| Critical | 24 hours |
| High | 7 days |
| Medium | 30 days |
| Low | Next cycle |
