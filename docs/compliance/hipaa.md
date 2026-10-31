# HIPAA Security Rule Mapping

## Administrative Safeguards (164.308)
| Control | TSAR Rules |
|---|---|
| Risk analysis | docs/threat-model-template.md, docs/security-model.md |
| Workforce security | rules/iam/design.md |
| Access management | rules/iam/design.md, rules/iam/oauth2-oidc.md |
| Security awareness training | docs/agent-behavior.md, docs/operations-runbook.md |
| Incident procedures | docs/incident-response.md |
| Contingency plan | rules/data/backup-and-recovery.md |

## Physical Safeguards (164.310)
| Control | TSAR Rules |
|---|---|
| Facility access | rules/hardware/tpm.md, rules/hardware/secure-boot.md |
| Workstation use | rules/platform/desktop.md |
| Device and media controls | rules/data/secure-deletion.md |

## Technical Safeguards (164.312)
| Control | TSAR Rules |
|---|---|
| Access control | rules/iam/design.md, rules/iam/session-management.md |
| Audit controls | rules/data/logging-redaction.md, rules/owasp-web/a09-logging-failures.md |
| Integrity | rules/supply-chain/artifact-signing.md, rules/data/logging-redaction.md |
| Person or entity authentication | rules/iam/oauth2-oidc.md |
| Transmission security | rules/crypto/algorithms.md |

## Breach Notification
- Detect: rules/containers/runtime-security.md, rules/data/logging-redaction.md.
- Contain: docs/incident-response.md.
- Notify: within 60 days per HITECH.
- Document: post-mortem template.

## PHI Handling
- Encrypt PHI at rest and in transit (rules/data/database-encryption.md).
- Redact from logs (rules/data/logging-redaction.md).
- Minimize access (rules/iam/design.md).
- Retention per state and federal requirements (rules/data/backup-and-recovery.md).
