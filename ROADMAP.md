# TSAR Roadmap

## Status Legend
- Shipped: implemented and present in the repository.
- In progress: actively being implemented.
- Planned: approved direction, not yet implemented.
- Proposed: under consideration; not a release commitment.

## Current repository version

The repository metadata and Python CLI currently identify the codebase as **1.1.1**.
This is a patch-level version on the 1.x line. It must not be represented as
v2.0.0: the v2.0 capabilities below remain proposed and are not implemented
release criteria for the current codebase.

## v1.0 — Foundation (Shipped)
- Core directive, prohibitions, and enforcement levels.
- Crypto rules (algorithms, key management, AEAD, PQC, constant-time).
- OWASP LLM Top 10 and OWASP Web Top 10 controls.
- Platform, hardware, data, cloud, container, API, IAM, and supply-chain rules.
- Messaging, database, observability, secrets, networking, and compute controls.
- Testing, governance, privacy, threat-intelligence, forensics, identity, email,
  endpoint, backup, disaster-recovery, legal-hold, application-security,
  infrastructure, development, and emerging-technology rule domains.
- Agent prompts, CLI, orchestrator, report, LSP, dashboard, and CI integrations.
- Compliance mappings and secure/anti-pattern examples.

## v1.1 — Depth and Reach (Planned / partially delivered)
- SARIF output from all scanners (currently only secure-review).
- `tsar fix` command for auto-remediation of common patterns.
- Additional agent prompts: Aider, Codeium, Tabnine.
- Bloom filter for secret scanning at scale.
- Differential testing for crypto implementations.
- Formal verification integration for Tier-1 crypto.
- GraphQL-specific fuzzing integration.

## v1.2 — Ecosystem (Planned)
- PyPI-published `tsar-cli` with `pipx install tsar`.
- Homebrew formula.
- Docker image for CI (`ghcr.io/mohamedelghazali/tsar`).
- GitHub Action marketplace listing.
- GitLab CI component registry.
- VS Code extension marketplace listing.
- JetBrains plugin.

## v1.3 — Intelligence (Proposed)
- Rule efficacy tracking.
- Adaptive strictness based on repository history.
- Integration with GitHub Code Scanning trends.
- Anonymous opt-in telemetry for rule improvement.
- Community-contributed rules with review workflow.

## v2.0 — Next Generation (Proposed; not implemented)
- Formal machine-checkable rule specifications beyond regex.
- Cross-language semantic analysis.
- Runtime enforcement via eBPF.
- Automatic rule generation from discovered vulnerabilities.
- Integration with AI agent frameworks (LangChain, LlamaIndex, AutoGen).

A v2.0.0 stable release must not be tagged until the intended v2.0 scope is
implemented, version metadata is updated consistently, and release gates pass.

## Out of Scope
- Runtime WAF.
- Full SAST replacement.
- Vendor-specific locked features.
- Certification body functions.

## How to Contribute to Roadmap
Open an issue with the `roadmap` label. Provide a use case, expected benefit,
and complexity estimate. Maintainers triage proposals periodically.
