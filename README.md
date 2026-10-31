# 🛡️ TSAR — The Ultimate Security Governance Layer for AI Coding Agents

> **Stop vulnerabilities at the source. Secure every line of AI-generated code.**

TSAR is an AI security governance layer for AI-assisted software development. It provides **171 active security rule files across 37 domains**, covering **Cryptography, Cloud Security, OWASP, and more**, together with dedicated instruction packs for **15 AI coding agents**.

Built for security-conscious engineering teams, TSAR brings security policy closer to the point where code is generated—then reinforces it with local scanners, repository hooks, CI checks, and policy validation.

**Security-first AI development. Governed at the source.**

**Repository version:** 1.1.1 (see VERSION, manifest.yaml, and tools/tsar-cli/pyproject.toml). The v2.0 roadmap is proposed work, not the current release. See [Release Qualification](docs/release-qualification.md) for current evidence and release status.

## Coverage

- **171 active rule files** across **37 rule domains** (rules/blockchain/README.md is an overview file, not a rule).
- **15 AI agents** with dedicated prompt/instruction files, plus one universal fallback.
- **9 programming languages** represented in secure reference examples.
- **5 compliance frameworks** mapped (SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR).
- CLI, orchestrator, reporting, LSP, dashboard, and CI/CD integrations.

## How Governance Is Enforced

TSAR uses multiple enforcement layers:

1. **Generation-time guidance:** agent-specific instruction files communicate the applicable TSAR rules to supported agents.
2. **Local verification:** scanners and project hooks inspect code and can block detected high-risk patterns.
3. **CI governance:** repository workflows validate rules, policies, examples, and project changes before merge.

**Important limitation:** prompt files are instruction-level integrations, not privileged native controls inside each AI provider. An agent may ignore or incompletely follow instructions. Actual enforcement depends on installing the relevant prompt/configuration and running the scanners and CI gates. TSAR does not guarantee vulnerability-free code or replace independent security review.

## Quick Start

    git clone https://github.com/mohamedelghazali/TSAR.git
    cd TSAR
    ./tools/tsar-cli/tsar.py init /path/to/project --agent cursor
    ./tools/tsar-cli/tsar.py scan /path/to/project
    ./tools/tsar-orchestrator/orchestrator.py /path/to/project

## Supported Agents

Claude, Claude Code, GPT, DeepSeek-Coder, Qwen-Coder, Gemini, Llama, Cursor, GitHub Copilot, Manus, Windsurf, SuperNinja, Replit Agent, Devin, Kimi.

## Structure

| Directory | Purpose |
|---|---|
| system/ | Core directive, prohibitions, enforcement levels |
| rules/ | 37 domains of security rules |
| skills/ | Scanners and security helpers |
| tools/ | CLI, orchestrator, report, LSP, dashboard |
| integrations/ | CI/CD templates and hooks |
| prompts/ | Agent-specific and universal instruction files |
| examples/ | Secure and anti-pattern code |
| docs/ | Guides, compliance mappings, architecture |
| policies/ | OPA/Cedar policies |
| tests/ | Automated test suite |

## Verification

Run ./verify-all.sh to execute the repository verification suite, including rule linting, manifest integrity, empty-file detection, security scanners, compliance references, tests, orchestration, reporting, and available OPA/LSP/Terraform checks.

## Design Principles

1. **Fail closed** — refuse Tier-1 work when required rules cannot be loaded.
2. **Structural over semantic** — keep policy, rules, and agent prompts distinct.
3. **Defense in depth** — combine generation guidance with scanners and CI.
4. **Time-bound exceptions** — every suppression should have an expiry.
5. **Evidence-driven** — produce reviewable verification artifacts.
6. **Portable** — avoid unnecessary vendor lock-in.
7. **Testable** — validate rules and integrations continuously.

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [Agent Integration](docs/agent-integration.md)
- [Agent Compatibility Matrix](docs/agent-compatibility-matrix.md)
- [Compliance Mappings](docs/compliance/README.md)
- [Roadmap](ROADMAP.md)
- [Final Review](docs/final-review.md)
- [Release Qualification](docs/release-qualification.md)

## License

TSAR uses a custom source-available license. Defined non-commercial uses are permitted; commercial use requires prior written authorization and a separate commercial license. This is not an OSI-approved Open Source license. See [LICENSE](LICENSE) for the full terms and the treatment of previously distributed MIT versions.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.
