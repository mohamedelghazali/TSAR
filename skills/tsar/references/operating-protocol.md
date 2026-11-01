# TSAR Operating Protocol

## Rule selection

Use `manifest.yaml` as the inventory. Select rules by the actual technologies and risk surfaces in the task. Load core directives plus the smallest relevant domain set; expand only when dependencies or threat analysis require it.

## Risk-oriented checklist

- **Identity:** authentication, authorization, session lifecycle, privilege boundaries, service identities.
- **Input and output:** validation, canonicalization, injection, output encoding, deserialization.
- **Secrets and cryptography:** approved algorithms, key lifecycle, nonce/IV safety, rotation, secret storage.
- **Data protection:** classification, minimization, encryption, retention, deletion, backup, redaction.
- **Infrastructure:** least privilege, hardened defaults, network boundaries, image provenance, admission controls.
- **AI and agents:** prompt injection, untrusted tool output, excessive agency, scoped tools, memory integrity, data leakage.
- **Supply chain:** pinned dependencies, integrity, SBOM, provenance, artifact signing.
- **Operations:** auditability, monitoring, incident response, recovery, exception expiry.
- **Verification:** tests, static analysis, policy checks, configuration/schema validation, human review.

## Safe implementation behavior

1. Understand existing project conventions before changing files.
2. Prefer the least invasive secure change that satisfies the request.
3. Do not disable a control to hide a finding. If a temporary exception is unavoidable, document its owner, rationale, compensating controls, and expiry.
4. Never place real secrets in generated files or command examples.
5. Avoid destructive commands and production changes without explicit authorization.
6. Treat scanner output as evidence to investigate, not as complete proof of security.
7. Keep the user informed about material trade-offs and residual risk.

## Verification record

For each task, distinguish:
- checks executed and passed;
- checks executed and failed;
- checks not run, with reason;
- findings fixed;
- findings accepted or deferred, with rationale.

A clean scanner result does not prove the absence of vulnerabilities. A prompt-only review is advisory unless backed by deterministic controls.
