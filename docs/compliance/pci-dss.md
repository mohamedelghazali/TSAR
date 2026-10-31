# PCI DSS 4.0 Mapping

## Requirement 2 — Secure Configurations
| Control | TSAR Rules |
|---|---|
| 2.2 System configuration | examples/secure/terraform/, rules/platform/kubernetes.md |
| 2.3 Wireless | (out of scope unless wireless) |

## Requirement 3 — Protect Stored Account Data
| Control | TSAR Rules |
|---|---|
| 3.4 PAN rendered unreadable | rules/data/database-encryption.md |
| 3.5 Keys protected | rules/crypto/key-management.md, rules/hardware/hsm.md |
| 3.6 Key management procedures | rules/crypto/key-management.md, rules/quantum/key-rotation.md |

## Requirement 4 — Encrypt Transmission
| Control | TSAR Rules |
|---|---|
| 4.2 Strong cryptography | rules/crypto/algorithms.md (TLS 1.3) |
| 4.2.1 Certificates verified | rules/platform/web.md, rules/crypto/algorithms.md |

## Requirement 6 — Secure Systems
| Control | TSAR Rules |
|---|---|
| 6.2 Secure development | system/CORE_DIRECTIVE.md, docs/agent-behavior.md |
| 6.3 Vulnerability management | rules/supply-chain/dependency-integrity.md |
| 6.4 Public-facing web apps | rules/owasp-web/*.md, rules/api/*.md |

## Requirement 8 — Identify and Authenticate
| Control | TSAR Rules |
|---|---|
| 8.3 MFA | rules/iam/design.md, rules/iam/oauth2-oidc.md |
| 8.4 Session management | rules/iam/session-management.md |
| 8.5 Authentication factors | rules/crypto/algorithms.md (Argon2id) |

## Requirement 10 — Log and Monitor
| Control | TSAR Rules |
|---|---|
| 10.2 Audit logs | rules/data/logging-redaction.md |
| 10.3 Log integrity | rules/data/logging-redaction.md |
| 10.4 Log review | docs/operations-runbook.md |

## Requirement 11 — Test Security
| Control | TSAR Rules |
|---|---|
| 11.3 Penetration testing | docs/operations-runbook.md |
| 11.5 Change detection | rules/supply-chain/artifact-signing.md |

## Compliance Boundaries
- Cardholder Data Environment (CDE) must apply rules/crypto/, rules/data/, rules/iam/.
- TSAR does not replace QSA assessment; it provides enforceable controls.
