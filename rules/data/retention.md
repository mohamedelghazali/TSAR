# Data Retention

## Retention Schedule
| Data Class | Retention | Justification |
|---|---|---|
| Financial records | 7 years | Tax and audit |
| Healthcare records | 6 years (or state) | Regulatory |
| Contract records | 7 years after expiry | Legal |
| Customer PII | Purpose + 30 days | GDPR minimization |
| Behavioral analytics | 90 days | Business need |
| Application logs | 90 days hot, 1 year cold | Security and debugging |
| Audit logs | 1 year (or per regulation) | Compliance |
| Backups | Per backup policy | Recovery |
| Test data | 30 days | Development |
| Marketing data | Until consent withdrawn | Consent |

Schedules are reviewed annually and whenever regulation changes.

## Enforcement
- Retention is enforced by automated jobs, not manual processes.
- Every data store has an owner and a retention policy in configuration.
- Deletion jobs log: records affected, store, policy ID, timestamp, executor.
- Manual deletion requires documented justification and approval.

## Legal Hold Override
- Active legal hold suspends all deletion for in-scope data.
- Hold state is checked before every deletion job.
- Release of hold is documented in writing by legal.
- Audit trail: every hold and release.

## Propagation
Deletion propagates to:
- Primary database.
- Read replicas.
- Backups (within retention window of backup policy).
- Analytics warehouse.
- Caches (Redis, CDN).
- Search indexes.
- Derived datasets.
- Third-party processors (via contractual obligation).

Propagation is verified by a data-flow map maintained per system.

## Verification
- Quarterly: sample records; confirm they are deleted from all stores.
- Quarterly: inspect backups; confirm propagation window respected.
- Annually: external audit of retention controls.
- On regulation change: re-assess schedule and propagate.

## Conflict Resolution
When two policies conflict (e.g., legal hold vs GDPR erasure):
- Legal hold wins until released.
- Document the conflict and the resolution.
- Erasure is executed immediately after hold release.

## Forbidden
- Retaining data past its scheduled deletion without documented exception.
- Deletion without logging.
- Deletion of data under legal hold.
- Ignoring derived data (analytics, backups) during deletion.
- Manual retention overrides without approval.
