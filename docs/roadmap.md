# TSAR Roadmap

## v1.0 (current)
- Core rules, crypto rules, OWASP LLM and Web, platform and hardware baselines.
- 15 agent prompts.
- Scanners, threat modeler, crypto inventory.
- CI/CD integrations, pre-commit hooks.
- Examples in Python, Node.js, Go, Rust, Java, Swift, Kotlin.

## v1.1
- `rules/quantum/` expanded with ACVP test vectors.
- `tsar` CLI packaged on PyPI.
- Additional platform: React Native, Flutter.
- `rules/blockchain/` for smart contract security.

## v1.2
- Language server (LSP) exposing TSAR rules in IDEs.
- SARIF output from `tsar scan` for GitHub Code Scanning.
- Additional agent prompts: Aider, Codeium, Tabnine.

## v2.0
- Rule efficacy tracking: which rules catch real vulnerabilities in production.
- Adaptive strictness based on repository history.
- Formal verification integration for high-assurance modules.

## Out of Scope
- Runtime protection.
- Full SAST replacement.
- Vendor-specific locked features.
