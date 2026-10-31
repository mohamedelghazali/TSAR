# SOC 2 Mapping

## Trust Services Criteria

### CC6.1 — Logical Access
| Criterion | TSAR Rules |
|---|---|
| Access is authorized | rules/iam/design.md, rules/owasp-web/a01-broken-access-control.md |
| Least privilege | rules/iam/design.md, rules/agentic-ai/tool-scoping.md |
| Authentication | rules/iam/oauth2-oidc.md, rules/owasp-web/a07-identification-failures.md |

### CC6.6 — Boundary Protection
| Criterion | TSAR Rules |
|---|---|
| Network segmentation | rules/cloud/aws.md, rules/platform/kubernetes.md |
| Encryption in transit | rules/crypto/algorithms.md (TLS 1.3) |
| Firewall rules | rules/cloud/*.md, rules/platform/kubernetes.md |

### CC6.7 — Data Transmission and Disposal
| Criterion | TSAR Rules |
|---|---|
| Encryption in transit | rules/crypto/algorithms.md |
| Encryption at rest | rules/data/database-encryption.md |
| Secure disposal | rules/data/secure-deletion.md |

### CC7.2 — Monitoring
| Criterion | TSAR Rules |
|---|---|
| Logging | rules/data/logging-redaction.md, rules/owasp-web/a09-logging-failures.md |
| Detection | rules/containers/runtime-security.md |
| Incident response | docs/incident-response.md |

### CC8.1 — Change Management
| Criterion | TSAR Rules |
|---|---|
| Change approval | docs/operations-runbook.md |
| Testing | skills/secure-review, tests/ |
| Separation of duties | rules/iam/design.md |

## Evidence Collection
- CI/CD logs showing TSAR scan on every PR.
- Signed artifacts with provenance.
- Access review records.
- Incident response post-mortems.
- Backup restore test results.
