# TSAR Roadmap

## Status Legend
- ✅ Shipped
- 🚧 In progress
- 📋 Planned
- 💡 Proposed

## v1.0 — Foundation (Current)
- ✅ Core directive, prohibitions, enforcement levels.
- ✅ Crypto rules (algorithms, key management, AEAD, PQC, constant-time).
- ✅ OWASP LLM Top 10 controls.
- ✅ OWASP Web Top 10 controls.
- ✅ Platform rules (web, mobile, desktop, embedded, distributed, edge, Kubernetes, IoT).
- ✅ Hardware rules (TPM, HSM, Secure Enclave, secure boot, side channels).
- ✅ Data rules (PII, logging, database encryption, backup, migration, deletion).
- ✅ Cloud rules (AWS, GCP, Azure, multi-cloud).
- ✅ Containers, API, IAM, supply chain.
- ✅ Messaging, database, observability, secrets.
- ✅ Networking, compute, testing, governance.
- ✅ Privacy, threat intel, forensics.
- ✅ Identity federation, email, endpoint.
- ✅ Backup, DR, legal hold.
- ✅ Application security, infrastructure, development, emerging tech.
- ✅ 15 agent prompts.
- ✅ CLI, orchestrator, report, LSP, web dashboard.
- ✅ CI integrations (GitHub, GitLab, Bitbucket, Azure).
- ✅ Compliance mappings (SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR).
- ✅ Examples in 9 languages.
- ✅ Test suite covering all domains.

## v1.1 — Depth and Reach
- 📋 SARIF output from all scanners (currently only secure-review).
- 📋 `tsar fix` command for auto-remediation of common patterns.
- 📋 Additional agent prompts: Aider, Codeium, Tabnine.
- 📋 Bloom filter for secret scanning at scale.
- 📋 Differential testing for crypto implementations.
- 📋 Formal verification integration for Tier-1 crypto.
- 📋 GraphQL-specific fuzzing integration.

## v1.2 — Ecosystem
- 📋 PyPI-published `tsar-cli` with `pipx install tsar`.
- 📋 Homebrew formula.
- 📋 Docker image for CI (`ghcr.io/mohamedelghazali/tsar`).
- 📋 GitHub Action marketplace listing.
- 📋 GitLab CI component registry.
- 📋 VS Code extension marketplace listing.
- 📋 JetBrains plugin.

## v1.3 — Intelligence
- 💡 Rule efficacy tracking (which rules catch real bugs).
- 💡 Adaptive strictness based on repository history.
- 💡 Integration with GitHub Code Scanning trends.
- 💡 Anonymous telemetry (opt-in) for rule improvement.
- 💡 Community-contributed rules with review workflow.

## v2.0 — Next Generation
- 💡 Formal spec for rules (machine-checkable beyond regex).
- 💡 Cross-language semantic analysis.
- 💡 Runtime enforcement via eBPF.
- 💡 Automatic rule generation from discovered vulnerabilities.
- 💡 Integration with AI agent frameworks (LangChain, LlamaIndex, AutoGen).

## Out of Scope
- Runtime WAF.
- Full SAST replacement.
- Vendor-specific locked features.
- Certification body functions.

## How to Contribute to Roadmap
- Open an issue with the `roadmap` label.
- Provide use case, expected benefit, and complexity estimate.
- Maintainers triage quarterly.
