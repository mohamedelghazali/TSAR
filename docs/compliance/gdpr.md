# GDPR Mapping

## Principles (Article 5)
| Principle | TSAR Rules |
|---|---|
| Lawfulness, fairness, transparency | rules/data/pii-handling.md |
| Purpose limitation | rules/data/pii-handling.md |
| Data minimization | rules/data/pii-handling.md |
| Accuracy | rules/data/data-migration.md |
| Storage limitation | rules/data/backup-and-recovery.md (retention) |
| Integrity and confidentiality | rules/crypto/*.md, rules/data/database-encryption.md |
| Accountability | docs/operations-runbook.md, docs/incident-response.md |

## Data Subject Rights
| Right | TSAR Rules |
|---|---|
| Access (Art. 15) | rules/data/pii-handling.md (data mapping) |
| Rectification (Art. 16) | rules/data/data-migration.md |
| Erasure (Art. 17) | rules/data/secure-deletion.md |
| Restriction (Art. 18) | rules/iam/design.md |
| Portability (Art. 20) | rules/data/data-migration.md |
| Object (Art. 21) | rules/data/pii-handling.md |

## Security of Processing (Article 32)
- Encryption at rest and in transit (rules/crypto/algorithms.md).
- Confidentiality, integrity, availability (rules/data/backup-and-recovery.md).
- Regular testing (docs/operations-runbook.md).
- Pseudonymization (rules/data/pii-handling.md).

## Breach Notification (Articles 33-34)
- 72-hour notification to supervisory authority.
- Detect via rules/owasp-web/a09-logging-failures.md and rules/containers/runtime-security.md.
- Contain via docs/incident-response.md.
- Document in post-mortem template.

## Data Protection by Design (Article 25)
- Enforced by system/CORE_DIRECTIVE.md.
- Default-deny in rules/iam/design.md.
- Data minimization in rules/data/pii-handling.md.

## International Transfers (Chapter V)
- Encryption in transit (rules/crypto/algorithms.md).
- Data residency controls (rules/platform/distributed-systems.md).
- Record of processing activities (rules/data/pii-handling.md).

## Processor Obligations (Article 28)
- Vendor assessment per rules/supply-chain/dependency-integrity.md.
- Contractual clauses documented.
- Sub-processor list maintained.
