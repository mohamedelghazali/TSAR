# Security Testing

## Types
| Type | Frequency | Scope |
|---|---|---|
| SAST | Every commit | Source code |
| SCA | Every build | Dependencies |
| Secret scan | Every commit | Source + history |
| DAST | Weekly + pre-release | Running application |
| IAST | Continuous (staging) | Instrumented app |
| Penetration test | Annually + major changes | Full system |
| Red team | Annually | Organization-wide |
| Threat modeling | Per feature | Design |

## SAST
- Semgrep, CodeQL, SonarQube.
- Block on HIGH/CRITICAL in CI.
- Triage false positives; document exclusions with expiry.

## DAST
- OWASP ZAP or Burp Suite.
- Authenticated scans for full coverage.
- Run against staging, never production.

## Penetration Testing
- External firm for Tier-1 systems.
- Scope documented; rules of engagement signed.
- Findings tracked to closure; retest after fixes.

## Bug Bounty
- Public or private program for customer-facing systems.
- Safe harbor policy published.
- Triage SLA: 72 hours for initial response.

## Forbidden
- Production DAST without explicit approval and rollback plan.
- Ignoring HIGH findings without documented risk acceptance.
- Penetration tests without remediation follow-up.
