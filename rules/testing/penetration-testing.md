# Penetration Testing Program

## Scoping
- Annual full-scope test for Tier-1 systems.
- Pre-launch test for new high-risk features.
- Post-incident test after major vulnerabilities.
- Scope includes: web, mobile, API, cloud, network.

## Rules of Engagement
- Written authorization signed by both parties.
- Emergency contact and stop conditions.
- Testing windows agreed.
- Data handling: no exfiltration, no persistent access, no destruction.

## Methodology
- OWASP Testing Guide, PTES, MITRE ATT&CK.
- Authenticated and unauthenticated.
- Business logic and multi-tenant testing.

## Deliverables
- Executive summary.
- Technical findings with CVSS scores.
- Reproduction steps (without weaponization).
- Remediation guidance.

## Follow-Up
- Findings tracked in issue tracker.
- Retest within 30 days of fixes.
- Report retained for audit.

## Forbidden
- Testing without written authorization.
- Testing production without rollback plan.
- Exfiltrating real user data.
