# Change Management

## Classification
| Type | Approval | Testing |
|---|---|---|
| Standard | Auto-approved | CI + tests |
| Normal | Peer + owner | CI + staging |
| Emergency | Owner + security | Post-hoc review |

## Standard Changes
- Low risk, well-understood, repeatable.
- Pre-approved template.
- Automated testing required.
- Rollback plan documented.

## Normal Changes
- Security review for changes touching auth, crypto, PII.
- Staging verification before production.
- Change ticket with impact assessment.
- Communication to affected teams.

## Emergency Changes
- Break-glass procedure with MFA.
- Documented reason and approver.
- Retroactive review within 48 hours.
- Post-mortem if incident-related.

## Forbidden
- Direct production changes without ticket.
- Changes bypassing CI.
- Emergency changes without post-review.
- Changes to security controls without security team approval.
