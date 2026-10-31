# Changelog

All notable changes to TSAR are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

## [1.0.0] — 2026-10-31

### Added

#### Core
- `manifest.yaml` with lifecycle, enforcement, and active file list.
- `system/CORE_DIRECTIVE.md`, `DO_NOT_GENERATE.md`, `ENFORCEMENT_LEVELS.md`, `LIFECYCLE.md`.

#### Cryptography
- `rules/crypto/algorithms.md`, `key-management.md`, `nonce-and-aead.md`, `post-quantum.md`, `constant-time.md`, `anti-patterns.md`.
- `rules/quantum/ml-kem.md`, `ml-dsa.md`, `slh-dsa.md`, `hybrid-design.md`, `key-rotation.md`.

#### AI Security
- `rules/owasp-llm/` — LLM01, LLM03, LLM04, LLM08.
- `rules/agentic-ai/` — tool-scoping, memory-integrity.
- `rules/ai-models/` — training-pipeline, inference-security, model-supply-chain.

#### Web and API
- `rules/owasp-web/` — A01 through A10.
- `rules/api/` — REST, GraphQL, gRPC, WebSocket.
- `rules/application-security/` — SPA, CSP, mobile, desktop.

#### Platform
- `rules/platform/` — web, iOS, Android, desktop, embedded, distributed, serverless-edge, Kubernetes, IoT.
- `rules/containers/` — Docker, image signing, runtime security.
- `rules/infrastructure/` — hypervisor, container orchestration, virtualization.
- `rules/compute/` — serverless, confidential computing.

#### Data and Storage
- `rules/data/` — PII, logging, database encryption, backup, migration, deletion.
- `rules/database/` — PostgreSQL, MySQL, MongoDB, Redis, multi-tenant, replication.
- `rules/backup/` — strategy, immutability, air-gap, ransomware resilience.
- `rules/disaster-recovery/` — planning, testing, failover, communications.
- `rules/legal-hold/` — preservation, evidence handling, privilege.

#### Cloud and Identity
- `rules/cloud/` — AWS, GCP, Azure, multi-cloud.
- `rules/iam/` — design, OAuth/OIDC, SCIM, session management.
- `rules/identity-federation/` — SAML, OIDC federation, SCIM provisioning, IdP hardening.
- `rules/secrets/` — Vault, AWS Secrets Manager, SOPS.

#### Networking
- `rules/networking/` — DNS, mTLS, service mesh, WAF, zero trust, load balancer.
- `rules/email/` — authentication, gateway, encryption, anti-phishing.
- `rules/endpoint/` — EDR, MDM, disk encryption, patch management, application control.

#### Operations
- `rules/messaging/` — Kafka, RabbitMQ, NATS, Pub/Sub, idempotency, poison message.
- `rules/observability/` — metrics, tracing, logging, alerting.
- `rules/testing/` — security testing, fuzzing, chaos, penetration testing.
- `rules/governance/` — policy-as-code, exceptions, vendor risk, change management, risk assessment.
- `rules/development/` — secure SDLC, code review, pair programming, dependency review.

#### Security Domains
- `rules/hardware/` — TPM, HSM, Secure Enclave, secure boot, side channels.
- `rules/supply-chain/` — SBOM/SLSA, dependency integrity, artifact signing.
- `rules/privacy/` — data minimization, anonymization, differential privacy, consent, DSR, privacy-by-design.
- `rules/threat-intel/` — STIX/TAXII, IOC integration, detection engineering, threat hunting.
- `rules/forensics/` — acquisition, chain of custody, analysis.
- `rules/emerging/` — advanced AI agents, quantum-safe migration, IoMT, autonomous systems.

#### Skills
- `skills/secret-scanner` — 20+ patterns, entropy detection.
- `skills/secure-review` — SQL injection, command injection, eval, pickle, XSS, SSRF, path traversal, TLS bypass, weak crypto, weak random.
- `skills/threat-modeler` — STRIDE generator.
- `skills/crypto-inventory` — CBOM generator.

#### Tools
- `tools/tsar-cli` — scan, inventory, lint, version, drift, threat-model, report, compliance, init.
- `tools/tsar-orchestrator` — pipeline runner with JSON/Markdown output.
- `tools/tsar-report` — HTML/JSON report generator.
- `tools/tsar-lsp` — language server for editors.
- `tools/tsar-web` — read-only dashboard.

#### Examples
- Secure examples in Python, Node.js, Go, Rust, Java, Kotlin, Swift, React Native, Flutter.
- Infrastructure examples: Docker, docker-compose, seccomp, Kubernetes, Nomad, Terraform.
- Anti-patterns documented with secure replacements.

#### Integrations
- GitHub Actions, GitLab CI, Bitbucket Pipelines, Azure DevOps.
- Pre-commit hook with installer.

#### Compliance
- SOC 2, ISO 27001:2022, PCI DSS 4.0, HIPAA, GDPR mappings.
- Referenced-rules validation test.

#### Agents
- 15 prompt files: claude, claude-code, gpt, deepseek-coder, qwen-coder, gemini, llama, cursor, github-copilot, manus, windsurf, superninja, replit-agent, devin, kimi.

#### Tests
- Test suite covering every rule domain, all examples, CLI, orchestrator, reports, LSP build, policy compilation, compliance references.

#### Documentation
- Getting started, agent integration, agent behavior, compatibility matrix.
- CI/CD, threat model template, incident response, operations runbook.
- Benchmarks, rule authoring, SARIF, security model, coverage matrix.
- Cloud, ML-Ops, privacy, threat intel, forensics, dashboard, multi-cloud.
- Networking, compute, governance, testing, email, endpoint, identity federation, reporting, backup, DR, legal hold, operations CLI, appsec, infrastructure, development, emerging tech, orchestrator.
- Architecture, final review, roadmap, glossary, FAQ.
